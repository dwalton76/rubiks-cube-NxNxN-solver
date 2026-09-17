#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <locale.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include "ida_search_core.h"

#define CUBE_SIZE 6
#define CUBE_ARRAY_SIZE 217
#define GROUP_SIZE 16
#define GROUP_U_COUNT 8
#define GROUP_UNIVERSE UINT64_C(12870)
#define PRODUCT_UNIVERSE UINT64_C(165636900)
#define AXIS_CENTER_UNIVERSE UINT64_C(735471)
#define OBLIQUE_PAIR_COUNT 24
#define DEFAULT_MAX_IDA_THRESHOLD 20
#define MAX_IDA_THRESHOLD 99
#define MAX_THREADS 64
#define MAX_SPLIT_PREFIX 4
#define NO_TASK UINT_MAX
#define PARITY_ANY 0
#define PARITY_ODD 1
#define PARITY_EVEN 2

/*
 * The staged U/D centers are a single point in the ranked coordinate, so any
 * maneuver that both starts and ends staged is a stabilizer element and the
 * shortest one that flips a given wide-turn parity is the same from every
 * staged state.  Exhaustive IDA from the staged state gives these minima:
 *
 *   one orbit    7   Lw U2 D2 Lw U2 D2 Lw
 *   both orbits  8   3Lw U2 D2 Lw 3Lw U2 D2 3Lw
 *
 * Without this floor a staged node whose parity is still wrong scores 0, so it
 * is never pruned and the search brute-forces every remaining ply beneath it.
 */
#define PARITY_FLOOR_ONE_ORBIT 7
#define PARITY_FLOOR_BOTH_ORBITS 8

#define ORBIT_OUTER_X 0
#define ORBIT_LEFT_OBLIQUE 1
#define ORBIT_RIGHT_OBLIQUE 2
#define ORBIT_COUNT 3
#define TABLE_COUNT 3
#define REQUIRED_TABLE_COUNT 3

/* These are the exact UFBD tuples in RubiksCube666.py. */
static const unsigned int outer_x_squares[GROUP_SIZE] = {
    8, 11, 26, 29, 80, 83, 98, 101, 152, 155, 170, 173, 188, 191, 206, 209,
};
static const unsigned int left_oblique_squares[GROUP_SIZE] = {
    9, 17, 20, 28, 81, 89, 92, 100, 153, 161, 164, 172, 189, 197, 200, 208,
};
static const unsigned int right_oblique_squares[GROUP_SIZE] = {
    10, 14, 23, 27, 82, 86, 95, 99, 154, 158, 167, 171, 190, 194, 203, 207,
};

static const unsigned int all_inner_x_squares[24] = {
    15, 16, 21, 22, 51, 52, 57, 58, 87, 88, 93, 94,
    123, 124, 129, 130, 159, 160, 165, 166, 195, 196, 201, 202,
};

static const unsigned int all_outer_x_squares[24] = {
    8, 11, 26, 29, 44, 47, 62, 65, 80, 83, 98, 101,
    116, 119, 134, 137, 152, 155, 170, 173, 188, 191, 206, 209,
};

/*
 * The two halves of every oblique edge pair, in matching order, so an oblique
 * is paired when both of its squares hold an L or an R.
 */
static const unsigned int all_left_oblique_squares[OBLIQUE_PAIR_COUNT] = {
    9, 20, 17, 28, 45, 56, 53, 64, 81, 92, 89, 100,
    117, 128, 125, 136, 153, 164, 161, 172, 189, 200, 197, 208,
};
static const unsigned int all_right_oblique_squares[OBLIQUE_PAIR_COUNT] = {
    10, 14, 23, 27, 46, 50, 59, 63, 82, 86, 95, 99,
    118, 122, 131, 135, 154, 158, 167, 171, 190, 194, 203, 207,
};

static const unsigned int *orbit_squares[ORBIT_COUNT] = {
    outer_x_squares,
    left_oblique_squares,
    right_oblique_squares,
};

/*
 * Each table holds the exact joint distance for one pair of orbits, so the
 * heuristic is the max over all three pairings of the remaining phase-4
 * orbits. A cost of 0 therefore means all three U/D center orbits are staged.
 */
static struct ranked_table {
    const char *flag;
    const char *label;
    unsigned char orbit_a;
    unsigned char orbit_b;
    const char *filename;
    unsigned char *costs;
    int fd;
} ranked_tables[TABLE_COUNT] = {
    {"--left-right-oblique-cost", "LROB", ORBIT_LEFT_OBLIQUE, ORBIT_RIGHT_OBLIQUE, NULL, NULL, -1},
    {"--left-oblique-outer-x-cost", "LOOX", ORBIT_LEFT_OBLIQUE, ORBIT_OUTER_X, NULL, NULL, -1},
    {"--right-oblique-outer-x-cost", "ROOX", ORBIT_RIGHT_OBLIQUE, ORBIT_OUTER_X, NULL, NULL, -1},
};

static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_666];
static move_type inverse_move[MOVE_MAX];
static unsigned char orbit0_requirement;
static unsigned char orbit1_requirement;
static float cost_to_goal_multiplier;
static int stage_lr_inner_x;
static int stage_ud_inner_x_pair_lr_obliques;
static const char *ud_inner_x_filename;
static const char *lr_inner_x_filename;
static unsigned char *ud_inner_x_costs;
static unsigned char *lr_inner_x_costs;
static int ud_inner_x_fd = -1;
static int lr_inner_x_fd = -1;
static move_type best_solution[MAX_IDA_THRESHOLD + 1];

static atomic_uint next_task;
static atomic_uint best_task = NO_TASK;
static pthread_mutex_t best_solution_lock = PTHREAD_MUTEX_INITIALIZER;
static struct split_task {
    unsigned char move_index[MAX_SPLIT_PREFIX];
} *split_tasks;
static unsigned int split_task_count;
static unsigned int split_task_capacity;

/*
 * Subtree sizes are heavy tailed, so a shallow split leaves one task holding a
 * large share of the search and caps the speedup regardless of thread count.
 * Splitting on two moves left one task with 37% of all nodes; each extra move
 * of prefix divides the hot subtree among its own children.
 */
static unsigned char split_task_depth = 2;

struct heuristic_result {
    uint64_t orbit_rank[ORBIT_COUNT];
    uint64_t table_rank[TABLE_COUNT];
    unsigned char table_cost[TABLE_COUNT];
    unsigned char unpaired_count;
    unsigned char ud_inner_x_cost;
    unsigned char lr_inner_x_cost;
    unsigned char cost;
};

struct search_root {
    unsigned int index;
    unsigned char orbit0_requirement;
    unsigned char orbit1_requirement;
    unsigned char initial_cost;
    char cube[CUBE_ARRAY_SIZE];
};

struct worker {
    const char *root_cube;
    unsigned char threshold;
    unsigned int task_id;
    unsigned char aborted;
    uint64_t ida_count;
    move_type solution[MAX_IDA_THRESHOLD + 1];
};

struct child {
    move_type move;
    unsigned char parity;
    unsigned char cost;
};

static void usage(const char *program)
{
    printf(
        "usage: %s {--kociemba STATE | --kociemba-file FILE} "
        "{--stage-lr-inner-x --lr-inner-x-cost FILE | "
        "--stage-ud-inner-x-pair-lr-obliques --ud-inner-x-cost FILE | "
        "--left-right-oblique-cost FILE --left-oblique-outer-x-cost FILE "
        "--right-oblique-outer-x-cost FILE} "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] "
        "[--multiplier FLOAT] "
        "[--orbit0-need-odd-w|--orbit0-need-even-w] "
        "[--orbit1-need-odd-w|--orbit1-need-even-w] "
        "[--apply-move MOVE] [--print-ranks] [--print-legal-moves] [--benchmark COUNT]\n",
        program
    );
    printf(
        "  --kociemba-file lines: ROOT_INDEX,ORBIT0_REQUIREMENT,ORBIT1_REQUIREMENT,STATE\n"
        "  parity requirements are 0=any, 1=odd, 2=even\n"
    );
}

/* Eight of the 24 oblique pairs hold the L/R obliques once they are all paired. */
static unsigned char unpaired_lr_oblique_count(const char *cube)
{
    unsigned char unpaired = 8;

    for (unsigned int index = 0; index < OBLIQUE_PAIR_COUNT; index++) {
        char left = cube[all_left_oblique_squares[index]];
        char right = cube[all_right_oblique_squares[index]];

        if ((left == 'L' || left == 'R') && (right == 'L' || right == 'R')) {
            unpaired--;
        }
    }
    return unpaired;
}

static uint64_t combination_rank_axis(
    const char *cube,
    const unsigned int *squares,
    unsigned int square_count,
    char first,
    char second
)
{
    uint64_t rank = 0;
    unsigned int selected_remaining = 8;

    for (unsigned int position = 0; position < square_count; position++) {
        unsigned int after = square_count - position - 1;
        char value = cube[squares[position]];

        if (value == first || value == second) {
            if (!selected_remaining) {
                return UINT64_MAX;
            }
            selected_remaining--;
        } else if (selected_remaining) {
            rank += binom[after][selected_remaining - 1];
        }
    }
    return selected_remaining ? UINT64_MAX : rank;
}

/*
 * Pairing is an intentionally fast, non-optimal phase. The admissible
 * ceil(unpaired / 4) bound takes tens of seconds even after phase 1, while the
 * unpaired count gives the search enough direction to finish quickly.
 */
static unsigned char oblique_pairing_cost(unsigned char unpaired)
{
    return ceil(unpaired / 4);
}

/*
 * Matches get_orbit0/1_wide_quarter_turn_count() in ida_search_core.c: every
 * wide quarter turn flips its orbit, half turns never do.
 */
static unsigned char parity_bit_of_move(move_type move)
{
    switch (move) {
        case Uw:
        case Uw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Dw:
        case Dw_PRIME:
            return 1;
        case threeUw:
        case threeUw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeFw:
        case threeFw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeDw:
        case threeDw_PRIME:
            return 2;
        default:
            return 0;
    }
}

static unsigned char parity_after_move(unsigned char parity, move_type move)
{
    return parity ^ parity_bit_of_move(move);
}

/* Bit 0 is set when orbit0 still needs a parity flip, bit 1 for orbit1. */
static unsigned char wrong_parity_orbits(unsigned char parity)
{
    unsigned char orbit0 = parity & 1;
    unsigned char orbit1 = (parity >> 1) & 1;
    unsigned char wrong = 0;

    if ((orbit0_requirement == PARITY_ODD && !orbit0) ||
        (orbit0_requirement == PARITY_EVEN && orbit0)) {
        wrong |= 1;
    }
    if ((orbit1_requirement == PARITY_ODD && !orbit1) ||
        (orbit1_requirement == PARITY_EVEN && orbit1)) {
        wrong |= 2;
    }
    return wrong;
}

/*
 * Flipping both orbits cannot be cheaper than flipping whichever one is more
 * expensive on its own, so the max of the two is an admissible floor.
 */
static unsigned char parity_flip_floor(unsigned char parity)
{
    unsigned char wrong = wrong_parity_orbits(parity);
    unsigned char orbit0_floor = PARITY_FLOOR_ONE_ORBIT;
    unsigned char orbit1_floor = PARITY_FLOOR_ONE_ORBIT;
    unsigned char floor = 0;

    if (wrong & 1) {
        floor = orbit0_floor;
    }
    if ((wrong & 2) && orbit1_floor > floor) {
        floor = orbit1_floor;
    }
    if (wrong == 3) {
        floor = PARITY_FLOOR_BOTH_ORBITS;
    }
    return floor;
}

static struct heuristic_result heuristic(const char *cube)
{
    struct heuristic_result result;
    int ranks_are_valid = 1;

    if (stage_lr_inner_x) {
        uint64_t lr_rank = combination_rank_axis(cube, all_inner_x_squares, 24, 'L', 'R');
        unsigned char encoded;

        memset(&result, 0, sizeof(result));
        if (lr_rank >= AXIS_CENTER_UNIVERSE) {
            result.cost = UINT8_MAX;
            return result;
        }
        encoded = lr_inner_x_costs[lr_rank];
        if (!encoded) {
            result.cost = UINT8_MAX;
            return result;
        }
        result.lr_inner_x_cost = decode_cost_byte(encoded);
        result.cost = result.lr_inner_x_cost;
        return result;
    }

    if (stage_ud_inner_x_pair_lr_obliques) {
        uint64_t ud_rank = combination_rank_axis(cube, all_inner_x_squares, 24, 'U', 'D');
        unsigned char encoded;

        memset(&result, 0, sizeof(result));
        if (ud_rank >= AXIS_CENTER_UNIVERSE) {
            result.cost = UINT8_MAX;
            return result;
        }
        encoded = ud_inner_x_costs[ud_rank];
        if (!encoded) {
            result.cost = UINT8_MAX;
            return result;
        }
        result.ud_inner_x_cost = decode_cost_byte(encoded);
        result.unpaired_count = unpaired_lr_oblique_count(cube);
        result.cost = oblique_pairing_cost(result.unpaired_count);
        if (result.ud_inner_x_cost > result.cost) {
            result.cost = result.ud_inner_x_cost;
        }
        return result;
    }

    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        result.orbit_rank[orbit] = ida_combination_rank_ud(cube, orbit_squares[orbit], GROUP_SIZE, GROUP_U_COUNT);
        if (result.orbit_rank[orbit] == UINT64_MAX) {
            ranks_are_valid = 0;
        }
    }

    result.cost = 0;
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        const struct ranked_table *table = &ranked_tables[index];
        unsigned char encoded;

        if (!ranks_are_valid || !table->costs) {
            result.table_rank[index] = UINT64_MAX;
            result.table_cost[index] = UINT8_MAX;
            continue;
        }
        result.table_rank[index] =
            result.orbit_rank[table->orbit_a] * GROUP_UNIVERSE + result.orbit_rank[table->orbit_b];
        encoded = table->costs[result.table_rank[index]];
        result.table_cost[index] = decode_cost_byte(encoded);

        if (!encoded) {
            result.cost = UINT8_MAX;
        } else if (result.cost != UINT8_MAX && result.table_cost[index] > result.cost) {
            result.cost = result.table_cost[index];
        }
    }

    if (!ranks_are_valid) {
        result.cost = UINT8_MAX;
    }
    return result;
}

/*
 * A cost of 0 means "staged with the parity the caller asked for", so callers
 * can treat 0 as a solved node without testing the parity a second time.
 */
static unsigned char cube_cost(const char *cube, unsigned char parity)
{
    unsigned char cost = heuristic(cube).cost;

    if (cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    if (cost_to_goal_multiplier) {
        cost = (unsigned char)round(cost * cost_to_goal_multiplier);
    }
    return cost ? cost : parity_flip_floor(parity);
}

/*
 * Last ply must land on a goal: staged centers and both orbit parities already
 * correct. A move that leaves an orbit on the wrong parity still needs the
 * flip floor, so it cannot finish a solution at this threshold. Skip the
 * rotate and table lookup for those moves.
 */
static int last_ply_can_be_goal(unsigned char parity, move_type move)
{
    return !parity_flip_floor(parity_after_move(parity, move));
}

static int move_is_allowed(move_type move)
{
    if (stage_lr_inner_x) {
        return 1;
    }
    if (stage_ud_inner_x_pair_lr_obliques) {
        switch (move) {
            case threeUw:
            case threeUw_PRIME:
            case threeDw:
            case threeDw_PRIME:
            case threeFw:
            case threeFw_PRIME:
            case threeBw:
            case threeBw_PRIME:
                return 0;
            default:
                return 1;
        }
    }
    switch (move) {
        case threeUw:
        case threeUw_PRIME:
        case threeDw:
        case threeDw_PRIME:
        case threeFw:
        case threeFw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case Uw:
        case Uw_PRIME:
        case Dw:
        case Dw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
        case L:
        case L_PRIME:
        case L2:
        case R:
        case R_PRIME:
        case R2:
            return 0;
        default:
            return 1;
    }
}

static void init_move_tables(void)
{
    ida_init_move_tables(
        moves_666, MOVE_COUNT_666, move_is_allowed, legal_move_count, legal_move_index, inverse_move
    );
}

static void map_ranked_tables(void)
{
    if (stage_lr_inner_x) {
        struct mapped_cost_file lr = ida_map_cost_file(lr_inner_x_filename, AXIS_CENTER_UNIVERSE);

        lr_inner_x_fd = lr.fd;
        lr_inner_x_costs = lr.costs;
        return;
    }
    if (stage_ud_inner_x_pair_lr_obliques) {
        struct mapped_cost_file ud = ida_map_cost_file(ud_inner_x_filename, AXIS_CENTER_UNIVERSE);

        ud_inner_x_fd = ud.fd;
        ud_inner_x_costs = ud.costs;
        return;
    }

    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        struct ranked_table *table = &ranked_tables[index];
        struct mapped_cost_file file;

        if (!table->filename) {
            continue;
        }
        file = ida_map_cost_file(table->filename, PRODUCT_UNIVERSE);
        table->fd = file.fd;
        table->costs = file.costs;
    }
}

static void unmap_ranked_tables(void)
{
    if (ud_inner_x_costs) {
        ida_unmap_cost_file(ud_inner_x_fd, ud_inner_x_costs, AXIS_CENTER_UNIVERSE);
    }
    if (lr_inner_x_costs) {
        ida_unmap_cost_file(lr_inner_x_fd, lr_inner_x_costs, AXIS_CENTER_UNIVERSE);
    }
    ud_inner_x_fd = lr_inner_x_fd = -1;
    ud_inner_x_costs = lr_inner_x_costs = NULL;

    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        struct ranked_table *table = &ranked_tables[index];

        ida_unmap_cost_file(table->fd, table->costs, (size_t)PRODUCT_UNIVERSE);
        table->costs = NULL;
        table->fd = -1;
    }
}

static void init_cube_from_kociemba(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    ida_init_cube(cube, CUBE_SIZE, kociemba);
}

/*
 * Opposite faces are interchangeable for staging, and the search never uses
 * edges or corners.  Map D/R/B onto U/L/F and blank the unused stickers so
 * the printed cube matches the state the heuristic sees.
 */
static void recolor_cube(char cube[CUBE_ARRAY_SIZE])
{
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (cube[square] == 'D') {
            cube[square] = 'U';
        } else if (cube[square] == 'R') {
            cube[square] = 'L';
        } else if (cube[square] == 'B') {
            cube[square] = 'F';
        }

        if (ida_is_edge_or_corner(square, CUBE_SIZE)) {
            cube[square] = '.';
        }
    }

    /*
     * The inner-x phases score inner x-centers and L/R obliques only, so the
     * outer x-centers carry no information and every oblique that is not L/R
     * is interchangeable. Blanking both keeps the printed cube honest about
     * what the heuristic actually sees.
     */
    if (stage_lr_inner_x || stage_ud_inner_x_pair_lr_obliques) {
        for (unsigned int index = 0; index < 24; index++) {
            cube[all_outer_x_squares[index]] = '.';
            if (cube[all_left_oblique_squares[index]] != 'L') {
                cube[all_left_oblique_squares[index]] = 'x';
            }
            if (cube[all_right_oblique_squares[index]] != 'L') {
                cube[all_right_oblique_squares[index]] = 'x';
            }
        }
    }
}

/*
 * A parity requirement can only be met if some legal move flips that orbit.
 * A mode can only satisfy a parity request when its legal moves include a
 * quarter turn that flips the requested wing orbit.
 */
static int parity_requirements_are_reachable(void)
{
    unsigned char flippable = 0;

    for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
        flippable |= parity_bit_of_move(moves_666[legal_move_index[MOVE_NONE][index]]);
    }

    if (orbit0_requirement == PARITY_ODD && !(flippable & 1)) {
        fprintf(stderr, "ERROR: --orbit0-need-odd-w but no legal move is an orbit0 wide quarter turn\n");
        return 0;
    }
    if (orbit1_requirement == PARITY_ODD && !(flippable & 2)) {
        fprintf(stderr, "ERROR: --orbit1-need-odd-w but no legal move is an orbit1 wide quarter turn\n");
        return 0;
    }
    return 1;
}

static move_type parse_move(const char *move_string)
{
    return ida_parse_move(move_string, moves_666, MOVE_COUNT_666);
}

static void prepare_cube(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    init_cube_from_kociemba(cube, kociemba);
    recolor_cube(cube);
}

static struct search_root *read_search_roots(const char *filename, unsigned int *root_count)
{
    FILE *stream;
    char *line = NULL;
    size_t capacity = 0;
    ssize_t length;
    unsigned int allocated = 0;
    unsigned int line_number = 0;
    struct search_root *roots = NULL;

    stream = fopen(filename, "r");
    if (!stream) {
        fprintf(stderr, "ERROR: could not open --kociemba-file %s: %s\n", filename, strerror(errno));
        exit(1);
    }

    while ((length = getline(&line, &capacity, stream)) != -1) {
        unsigned int index;
        unsigned int orbit0;
        unsigned int orbit1;
        char kociemba[CUBE_ARRAY_SIZE];

        line_number++;
        if (length == 0 || line[0] == '\n' || line[0] == '\r') {
            continue;
        }
        if (sscanf(line, "%u,%u,%u,%216[^\r\n]", &index, &orbit0, &orbit1, kociemba) != 4 ||
            strlen(kociemba) != CUBE_ARRAY_SIZE - 1 || orbit0 > PARITY_EVEN || orbit1 > PARITY_EVEN) {
            fprintf(
                stderr,
                "ERROR: invalid --kociemba-file line %u; expected "
                "ROOT_INDEX,ORBIT0_REQUIREMENT,ORBIT1_REQUIREMENT,216-STICKER-STATE\n",
                line_number
            );
            free(line);
            free(roots);
            fclose(stream);
            exit(1);
        }

        if (*root_count == allocated) {
            struct search_root *grown;
            allocated = allocated ? allocated * 2 : 16;
            grown = realloc(roots, allocated * sizeof(*roots));
            if (!grown) {
                fprintf(stderr, "ERROR: could not allocate search roots\n");
                free(line);
                free(roots);
                fclose(stream);
                exit(1);
            }
            roots = grown;
        }

        roots[*root_count].index = index;
        roots[*root_count].orbit0_requirement = (unsigned char)orbit0;
        roots[*root_count].orbit1_requirement = (unsigned char)orbit1;
        roots[*root_count].initial_cost = UINT8_MAX;
        prepare_cube(roots[*root_count].cube, kociemba);
        (*root_count)++;
    }

    free(line);
    fclose(stream);
    if (!*root_count) {
        fprintf(stderr, "ERROR: --kociemba-file %s contains no roots\n", filename);
        free(roots);
        exit(1);
    }
    return roots;
}

static int ida_search(
    struct worker *worker,
    char cube[CUBE_ARRAY_SIZE],
    unsigned char depth,
    unsigned char threshold,
    move_type previous_move,
    unsigned char parity
)
{
    struct child children[MOVE_COUNT_666];
    unsigned int child_count = 0;
    unsigned char count = legal_move_count[previous_move];
    unsigned char next_depth = depth + 1;
    int last_ply = next_depth == threshold;
    char rotate_tmp[CUBE_ARRAY_SIZE];

    if (atomic_load_explicit(&best_task, memory_order_relaxed) < worker->task_id) {
        worker->aborted = 1;
        return 0;
    }

    for (unsigned int index = 0; index < count; index++) {
        move_type move = moves_666[legal_move_index[previous_move][index]];
        unsigned char next_parity;
        unsigned char cost;

        if (last_ply && !last_ply_can_be_goal(parity, move)) {
            continue;
        }
        next_parity = parity_after_move(parity, move);
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        cost = cube_cost(cube, next_parity);
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[move]);
        worker->ida_count++;

        if (cost == UINT8_MAX || next_depth + cost > threshold) {
            continue;
        }
        if (!cost) {
            worker->solution[depth] = move;
            worker->solution[next_depth] = MOVE_NONE;
            return 1;
        }
        children[child_count].move = move;
        children[child_count].parity = next_parity;
        children[child_count].cost = cost;
        child_count++;
    }

    if (next_depth >= threshold || next_depth >= MAX_IDA_THRESHOLD) {
        worker->solution[depth] = MOVE_NONE;
        return 0;
    }

    for (unsigned int index = 1; index < child_count; index++) {
        struct child pending = children[index];
        unsigned int destination = index;

        while (destination && children[destination - 1].cost > pending.cost) {
            children[destination] = children[destination - 1];
            destination--;
        }
        children[destination] = pending;
    }

    for (unsigned int index = 0; index < child_count; index++) {
        struct child child = children[index];

        worker->solution[depth] = child.move;
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, child.move);
        if (ida_search(worker, cube, next_depth, threshold, child.move, child.parity)) {
            return 1;
        }
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[child.move]);
        if (worker->aborted) {
            return 0;
        }
    }
    worker->solution[depth] = MOVE_NONE;
    return 0;
}

/*
 * Every move sequence of MAX_SPLIT_PREFIX legal moves is a possible task, so
 * counting them gives the exact worst case to allocate once up front.
 */
static unsigned int count_move_prefixes(move_type previous, unsigned char depth)
{
    unsigned int total = 0;

    if (depth == MAX_SPLIT_PREFIX) {
        return 1;
    }
    for (unsigned int index = 0; index < legal_move_count[previous]; index++) {
        total += count_move_prefixes(moves_666[legal_move_index[previous][index]], depth + 1);
    }
    return total;
}

static void allocate_split_tasks(void)
{
    split_task_capacity = count_move_prefixes(MOVE_NONE, 0);
    split_tasks = malloc(sizeof(*split_tasks) * (size_t) split_task_capacity);
    if (!split_tasks) {
        fprintf(stderr, "ERROR: could not allocate %u split tasks\n", split_task_capacity);
        exit(1);
    }
}

static void add_split_tasks(move_type previous, unsigned char depth, unsigned char *prefix)
{
    if (depth == split_task_depth) {
        if (split_task_count >= split_task_capacity) {
            fprintf(stderr, "ERROR: more than %u split tasks\n", split_task_capacity);
            exit(1);
        }
        memcpy(split_tasks[split_task_count].move_index, prefix, MAX_SPLIT_PREFIX);
        split_task_count++;
        return;
    }
    for (unsigned int index = 0; index < legal_move_count[previous]; index++) {
        prefix[depth] = (unsigned char)index;
        add_split_tasks(moves_666[legal_move_index[previous][index]], depth + 1, prefix);
    }
    prefix[depth] = 0;
}

static int build_split_tasks(
    const char *root,
    unsigned char threshold,
    uint64_t *nodes,
    move_type *one_move_solution
)
{
    unsigned char prefix[MAX_SPLIT_PREFIX] = {0};
    char cube[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];

    split_task_count = 0;
    split_task_depth = threshold < MAX_SPLIT_PREFIX ? (threshold < 2 ? 2 : threshold) : MAX_SPLIT_PREFIX;
    *one_move_solution = MOVE_NONE;
    for (unsigned int first_index = 0; first_index < legal_move_count[MOVE_NONE]; first_index++) {
        move_type first = moves_666[legal_move_index[MOVE_NONE][first_index]];
        unsigned char cost;
        unsigned char parity;

        if (threshold == 1 && !last_ply_can_be_goal(0, first)) {
            continue;
        }
        parity = parity_after_move(0, first);
        memcpy(cube, root, CUBE_ARRAY_SIZE);
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, first);
        (*nodes)++;
        cost = cube_cost(cube, parity);
        if (cost == UINT8_MAX || 1 + cost > threshold) {
            continue;
        }
        if (!cost) {
            *one_move_solution = first;
            return 1;
        }
        if (threshold < 2) {
            continue;
        }
        prefix[0] = (unsigned char)first_index;
        add_split_tasks(first, 1, prefix);
    }
    return 0;
}

/*
 * A prefix of length depth is walked by every task that shares it. Those tasks
 * are contiguous and the first of them has zeros in all the deeper slots.
 */
static int is_first_task_of_prefix(unsigned int task, unsigned char depth)
{
    for (unsigned char step = depth; step < split_task_depth; step++) {
        if (split_tasks[task].move_index[step]) {
            return 0;
        }
    }
    return 1;
}

static void *search_split_tasks(void *argument)
{
    struct worker *worker = argument;

    while (1) {
        unsigned int task = atomic_fetch_add(&next_task, 1);
        char cube[CUBE_ARRAY_SIZE];
        char rotate_tmp[CUBE_ARRAY_SIZE];
        move_type previous;
        unsigned char parity;
        unsigned char cost;
        int found;
        int pruned;

        if (task >= split_task_count || atomic_load(&best_task) < task) {
            break;
        }
        worker->task_id = task;
        worker->aborted = 0;
        memcpy(cube, worker->root_cube, CUBE_ARRAY_SIZE);
        previous = MOVE_NONE;
        parity = 0;
        found = 0;
        pruned = 0;

        for (unsigned char step = 0; step < split_task_depth; step++) {
            unsigned char move_index = split_tasks[task].move_index[step];
            move_type move = moves_666[legal_move_index[previous][move_index]];
            unsigned char depth = step + 1;

            if (depth == worker->threshold && !last_ply_can_be_goal(parity, move)) {
                pruned = 1;
                break;
            }
            parity = parity_after_move(parity, move);
            rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
            worker->solution[step] = move;
            previous = move;

            /*
             * Tasks sharing a prefix all re-walk it, so only the first task of
             * each group counts these nodes.
             */
            if (is_first_task_of_prefix(task, depth)) {
                worker->ida_count++;
            }
            cost = cube_cost(cube, parity);

            if (cost == UINT8_MAX || depth + cost > worker->threshold) {
                pruned = 1;
                break;
            }
            if (!cost) {
                worker->solution[depth] = MOVE_NONE;
                found = 1;
                break;
            }
        }

        if (pruned) {
            continue;
        }
        if (!found) {
            if (worker->threshold <= split_task_depth) {
                continue;
            }
            found = ida_search(
                worker, cube, split_task_depth, worker->threshold, previous, parity
            );
        }

        if (found) {
            pthread_mutex_lock(&best_solution_lock);
            if (task < atomic_load(&best_task)) {
                memcpy(best_solution, worker->solution, sizeof(best_solution));
                atomic_store(&best_task, task);
            }
            pthread_mutex_unlock(&best_solution_lock);
            break;
        }
        if (worker->aborted) {
            break;
        }
    }
    return NULL;
}

static int search_threshold(
    const char cube[CUBE_ARRAY_SIZE],
    unsigned char threshold,
    unsigned int thread_count,
    uint64_t *nodes
)
{
    struct worker workers[MAX_THREADS];
    pthread_t threads[MAX_THREADS];
    unsigned char cost = cube_cost(cube, 0);
    move_type one_move_solution = MOVE_NONE;
    unsigned int worker_count;

    *nodes = 1;
    if (cost == UINT8_MAX || cost > threshold) {
        return 0;
    }
    if (!cost) {
        best_solution[0] = MOVE_NONE;
        return 1;
    }
    if (!threshold) {
        return 0;
    }
    if (build_split_tasks(cube, threshold, nodes, &one_move_solution)) {
        best_solution[0] = one_move_solution;
        best_solution[1] = MOVE_NONE;
        return 1;
    }
    if (!split_task_count) {
        return 0;
    }

    worker_count = thread_count < split_task_count ? thread_count : split_task_count;
    atomic_store(&next_task, 0);
    atomic_store(&best_task, NO_TASK);
    for (unsigned int index = 0; index < worker_count; index++) {
        memset(&workers[index], 0, sizeof(workers[index]));
        workers[index].root_cube = cube;
        workers[index].threshold = threshold;
        workers[index].task_id = NO_TASK;
        if (pthread_create(&threads[index], NULL, search_split_tasks, &workers[index]) != 0) {
            fprintf(stderr, "ERROR: could not create search thread %u\n", index);
            exit(1);
        }
    }
    for (unsigned int index = 0; index < worker_count; index++) {
        pthread_join(threads[index], NULL);
        *nodes += workers[index].ida_count;
    }
    return atomic_load(&best_task) != NO_TASK;
}

/*
 * --benchmark attributes per-node time to a stage. Every pass walks the same
 * captured states single threaded, so the difference between two passes is the
 * cost of whatever the later pass added.
 */
static double seconds_since(struct timespec start)
{
    struct timespec now;

    clock_gettime(CLOCK_MONOTONIC, &now);
    return (now.tv_sec - start.tv_sec) + (now.tv_nsec - start.tv_nsec) / 1e9;
}

static void run_benchmark(const char *root, unsigned int count)
{
    char (*states)[CUBE_ARRAY_SIZE] = malloc(CUBE_ARRAY_SIZE * (size_t) count);
    char rotate_tmp[CUBE_ARRAY_SIZE];
    char cube[CUBE_ARRAY_SIZE];
    struct timespec start;
    uint64_t sink = 0;

    if (!states) {
        printf("benchmark: could not allocate %u states\n", count);
        return;
    }

    srandom(20260915);
    memcpy(cube, root, CUBE_ARRAY_SIZE);
    for (unsigned int index = 0; index < count; index++) {
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, moves_666[random() % MOVE_COUNT_666]);
        memcpy(states[index], cube, CUBE_ARRAY_SIZE);
    }

    clock_gettime(CLOCK_MONOTONIC, &start);
    for (unsigned int index = 0; index < count; index++) {
        move_type move = moves_666[index % MOVE_COUNT_666];

        rotate_666_centers(states[index], rotate_tmp, CUBE_ARRAY_SIZE, move);
        rotate_666_centers(states[index], rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[move]);
        sink += (unsigned char) states[index][1];
    }
    printf("rotate do+undo           %8.0f ns/op\n", seconds_since(start) * 1e9 / count);

    clock_gettime(CLOCK_MONOTONIC, &start);
    for (unsigned int index = 0; index < count; index++) {
        sink += unpaired_lr_oblique_count(states[index]);
    }
    printf("oblique pairing count    %8.0f ns/op\n", seconds_since(start) * 1e9 / count);

    clock_gettime(CLOCK_MONOTONIC, &start);
    for (unsigned int index = 0; index < count; index++) {
        sink += heuristic(states[index]).cost;
    }
    printf("full heuristic           %8.0f ns/op\n", seconds_since(start) * 1e9 / count);

    printf("checksum %" PRIu64 "\n", sink);
    free(states);
}

static void print_ida_summary(char cube[CUBE_ARRAY_SIZE], const move_type *solution)
{
    char rotate_tmp[CUBE_ARRAY_SIZE];
    unsigned char solution_len = 0;
    unsigned char parity = 0;

    while (solution[solution_len] != MOVE_NONE) {
        solution_len++;
    }
    printf("\n      ");
    if (stage_lr_inner_x) {
        printf(" %4s", "LRIX");
    } else if (stage_ud_inner_x_pair_lr_obliques) {
        printf(" %4s %4s", "UDIX", "UNPR");
    } else {
        for (unsigned int index = 0; index < TABLE_COUNT; index++) {
            if (ranked_tables[index].costs) {
                printf(" %4s", ranked_tables[index].label);
            }
        }
    }
    printf("  CTG  TRU  IDX\n      ");
    if (stage_lr_inner_x) {
        printf(" ====");
    } else if (stage_ud_inner_x_pair_lr_obliques) {
        printf(" ==== ====");
    } else {
        for (unsigned int index = 0; index < TABLE_COUNT; index++) {
            if (ranked_tables[index].costs) {
                printf(" ====");
            }
        }
    }
    printf("  ===  ===  ===\n");

    for (unsigned char step = 0; step <= solution_len; step++) {
        struct heuristic_result h = heuristic(cube);

        if (step) {
            printf("%5s ", move2str[solution[step - 1]]);
        } else {
            printf(" INIT ");
        }
        if (stage_lr_inner_x) {
            printf(" %4u", h.lr_inner_x_cost);
        } else if (stage_ud_inner_x_pair_lr_obliques) {
            printf(" %4u %4u", h.ud_inner_x_cost, h.unpaired_count);
        } else {
            for (unsigned int index = 0; index < TABLE_COUNT; index++) {
                if (ranked_tables[index].costs) {
                    printf(" %4u", h.table_cost[index]);
                }
            }
        }
        printf("  %3u  %3u  %3u\n", cube_cost(cube, parity), solution_len - step, step);
        if (step < solution_len) {
            parity = parity_after_move(parity, solution[step]);
            rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, solution[step]);
        }
    }
    printf("\n");
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *kociemba_filename = NULL;
    const char *apply_move_string = NULL;
    unsigned char min_threshold = UINT8_MAX;
    unsigned char max_threshold = DEFAULT_MAX_IDA_THRESHOLD;
    unsigned int thread_count = 0;
    unsigned int loaded_table_count = 0;
    int print_ranks = 0;
    int print_legal_moves = 0;
    unsigned int benchmark_count = 0;
    char cube[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];
    struct heuristic_result initial;
    struct search_root *roots = NULL;
    unsigned int root_count = 0;
    struct timeval start;
    uint64_t total_nodes = 0;

    for (int index = 1; index < argc; index++) {
        int matched_table = 0;

        for (unsigned int table = 0; table < TABLE_COUNT; table++) {
            if (strmatch(argv[index], (char *)ranked_tables[table].flag) && index + 1 < argc) {
                ranked_tables[table].filename = argv[++index];
                matched_table = 1;
                break;
            }
        }
        if (matched_table) {
            continue;
        }

        if (strmatch(argv[index], "--stage-lr-inner-x")) {
            stage_lr_inner_x = 1;
        } else if (strmatch(argv[index], "--stage-ud-inner-x-pair-lr-obliques")) {
            stage_ud_inner_x_pair_lr_obliques = 1;
        } else if (strmatch(argv[index], "--ud-inner-x-cost") && index + 1 < argc) {
            ud_inner_x_filename = argv[++index];
        } else if (strmatch(argv[index], "--lr-inner-x-cost") && index + 1 < argc) {
            lr_inner_x_filename = argv[++index];
        } else if (strmatch(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (strmatch(argv[index], "--kociemba-file") && index + 1 < argc) {
            kociemba_filename = argv[++index];
        } else if (strmatch(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned char)strtoul(argv[++index], NULL, 10);
        } else if (strmatch(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned char)strtoul(argv[++index], NULL, 10);
        } else if (strmatch(argv[index], "--threads") && index + 1 < argc) {
            thread_count = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (strmatch(argv[index], "--multiplier") && index + 1 < argc) {
            cost_to_goal_multiplier = atof(argv[++index]);
        } else if (strmatch(argv[index], "--orbit0-need-odd-w")) {
            orbit0_requirement = PARITY_ODD;
        } else if (strmatch(argv[index], "--orbit0-need-even-w")) {
            orbit0_requirement = PARITY_EVEN;
        } else if (strmatch(argv[index], "--orbit1-need-odd-w")) {
            orbit1_requirement = PARITY_ODD;
        } else if (strmatch(argv[index], "--orbit1-need-even-w")) {
            orbit1_requirement = PARITY_EVEN;
        } else if (strmatch(argv[index], "--apply-move") && index + 1 < argc) {
            apply_move_string = argv[++index];
        } else if (strmatch(argv[index], "--benchmark")) {
            index++;
            benchmark_count = (unsigned int) atoi(argv[index]);
        } else if (strmatch(argv[index], "--print-rank") || strmatch(argv[index], "--print-ranks")) {
            print_ranks = 1;
        } else if (strmatch(argv[index], "--print-legal-moves")) {
            print_legal_moves = 1;
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if ((!kociemba && !kociemba_filename) || (kociemba && kociemba_filename)) {
        usage(argv[0]);
        return 2;
    }
    if (kociemba_filename &&
        (apply_move_string || print_ranks || orbit0_requirement != PARITY_ANY ||
         orbit1_requirement != PARITY_ANY)) {
        fprintf(
            stderr,
            "ERROR: --kociemba-file supplies per-root parity and cannot be combined with "
            "--apply-move, --print-ranks, or global parity flags\n"
        );
        return 2;
    }
    if (stage_lr_inner_x && stage_ud_inner_x_pair_lr_obliques) {
        fprintf(stderr, "ERROR: select only one center-stage mode\n");
        return 2;
    }
    if ((stage_lr_inner_x && !lr_inner_x_filename) ||
        (stage_ud_inner_x_pair_lr_obliques && !ud_inner_x_filename)) {
        usage(argv[0]);
        return 2;
    }
    if (stage_lr_inner_x || stage_ud_inner_x_pair_lr_obliques) {
        for (unsigned int table = 0; table < TABLE_COUNT; table++) {
            if (ranked_tables[table].filename) {
                fprintf(stderr, "ERROR: inner-x modes cannot be combined with ranked tables\n");
                return 2;
            }
        }
    }
    if (!stage_lr_inner_x && !stage_ud_inner_x_pair_lr_obliques) {
        for (unsigned int table = 0; table < REQUIRED_TABLE_COUNT; table++) {
            if (!ranked_tables[table].filename) {
                usage(argv[0]);
                return 2;
            }
        }
    }
    if (!thread_count) {
        long online = sysconf(_SC_NPROCESSORS_ONLN);
        thread_count = online > 1 ? (unsigned int)online : 1;
    }
    if (thread_count > MAX_THREADS) {
        thread_count = MAX_THREADS;
    }
    if (max_threshold > MAX_IDA_THRESHOLD ||
        (min_threshold != UINT8_MAX && min_threshold > max_threshold)) {
        fprintf(stderr, "ERROR: invalid IDA threshold range\n");
        return 2;
    }
    /*
     * Anything below 1.0 would weaken an already admissible bound, and could
     * round a non-zero cost down to 0 and report an unstaged cube as solved.
     */
    if (cost_to_goal_multiplier && cost_to_goal_multiplier < 1.0) {
        fprintf(stderr, "ERROR: --multiplier must be at least 1.0\n");
        return 2;
    }

    /* Line buffer so threshold progress still appears when stdout is a pipe. */
    setvbuf(stdout, NULL, _IOLBF, 0);
    setlocale(LC_NUMERIC, "");
    init_binom();
    init_move_tables();
    allocate_split_tasks();

    if (kociemba_filename) {
        roots = read_search_roots(kociemba_filename, &root_count);
    } else {
        roots = calloc(1, sizeof(*roots));
        if (!roots) {
            fprintf(stderr, "ERROR: could not allocate search root\n");
            return 1;
        }
        root_count = 1;
        roots[0].index = 0;
        roots[0].orbit0_requirement = orbit0_requirement;
        roots[0].orbit1_requirement = orbit1_requirement;
        init_cube_from_kociemba(roots[0].cube, kociemba);
        if (apply_move_string) {
            move_type move = parse_move(apply_move_string);
            if (move == MOVE_NONE) {
                fprintf(stderr, "ERROR: invalid --apply-move %s\n", apply_move_string);
                free(roots);
                return 2;
            }
            rotate_666_centers(roots[0].cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        }
        recolor_cube(roots[0].cube);
    }

    for (unsigned int root_index = 0; root_index < root_count; root_index++) {
        orbit0_requirement = roots[root_index].orbit0_requirement;
        orbit1_requirement = roots[root_index].orbit1_requirement;
        if (!parity_requirements_are_reachable()) {
            free(roots);
            return 2;
        }
    }

    map_ranked_tables();
    memcpy(cube, roots[0].cube, sizeof(cube));
    orbit0_requirement = roots[0].orbit0_requirement;
    orbit1_requirement = roots[0].orbit1_requirement;
    initial = heuristic(roots[0].cube);

    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_666[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }
    if (benchmark_count) {
        run_benchmark(roots[0].cube, benchmark_count);
        unmap_ranked_tables();
        free(roots);
        return 0;
    }
    if (print_ranks) {
        if (stage_lr_inner_x) {
            printf(
                "LR_INNER_X_COST %u",
                initial.lr_inner_x_cost
            );
        } else if (stage_ud_inner_x_pair_lr_obliques) {
            printf(
                "UD_INNER_X_COST %u UNPAIRED %u",
                initial.ud_inner_x_cost,
                initial.unpaired_count
            );
        } else {
            printf(
                "OUTER_RANK %" PRIu64 " LEFT_RANK %" PRIu64 " RIGHT_RANK %" PRIu64,
                initial.orbit_rank[ORBIT_OUTER_X],
                initial.orbit_rank[ORBIT_LEFT_OBLIQUE], initial.orbit_rank[ORBIT_RIGHT_OBLIQUE]
            );
            for (unsigned int index = 0; index < TABLE_COUNT; index++) {
                if (!ranked_tables[index].costs) {
                    continue;
                }
                printf(
                    " %s_RANK %" PRIu64 " %s_COST %u",
                    ranked_tables[index].label, initial.table_rank[index],
                    ranked_tables[index].label, initial.table_cost[index]
                );
            }
        }
        printf(" COST %u\n", initial.cost);
        unmap_ranked_tables();
        free(roots);
        return initial.cost == UINT8_MAX;
    }

    for (unsigned int root_index = 0; root_index < root_count; root_index++) {
        orbit0_requirement = roots[root_index].orbit0_requirement;
        orbit1_requirement = roots[root_index].orbit1_requirement;
        if (heuristic(roots[root_index].cube).cost == UINT8_MAX) {
            fprintf(
                stderr,
                "ERROR: root %u center state is absent from a ranked cost table\n",
                roots[root_index].index
            );
            unmap_ranked_tables();
            free(roots);
            return 1;
        }
        roots[root_index].initial_cost = cube_cost(roots[root_index].cube, 0);
    }

    if (min_threshold == UINT8_MAX) {
        min_threshold = roots[0].initial_cost;
        for (unsigned int root_index = 1; root_index < root_count; root_index++) {
            if (roots[root_index].initial_cost < min_threshold) {
                min_threshold = roots[root_index].initial_cost;
            }
        }
    }

    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        if (ranked_tables[index].costs) {
            loaded_table_count++;
        }
    }
    if (stage_lr_inner_x || stage_ud_inner_x_pair_lr_obliques) {
        loaded_table_count = 1;
    }
    if (root_count == 1) {
        print_cube(cube, CUBE_SIZE);
    } else {
        LOG("loaded %u starting states from %s\n", root_count, kociemba_filename);
    }
    if (stage_lr_inner_x) {
        LOG("staging L/R inner x-centers\n");
    } else if (stage_ud_inner_x_pair_lr_obliques) {
        LOG("staging U/D inner x-centers while pairing L/R obliques anywhere\n");
    }
    LOG("searching with %u threads over %u ranked tables\n", thread_count, loaded_table_count);
    memset(best_solution, 0, sizeof(best_solution));
    gettimeofday(&start, NULL);
    for (unsigned char threshold = min_threshold; threshold <= max_threshold; threshold++) {
        struct timeval threshold_start;
        struct timeval stop;
        uint64_t threshold_nodes = 0;
        float us;
        float nodes_per_us;
        unsigned int nodes_per_sec;
        struct search_root *selected_root = NULL;

        gettimeofday(&threshold_start, NULL);
        for (unsigned int root_index = 0; root_index < root_count; root_index++) {
            uint64_t root_nodes;

            if (roots[root_index].initial_cost > threshold) {
                continue;
            }
            orbit0_requirement = roots[root_index].orbit0_requirement;
            orbit1_requirement = roots[root_index].orbit1_requirement;
            memset(best_solution, 0, sizeof(best_solution));
            if (search_threshold(roots[root_index].cube, threshold, thread_count, &root_nodes)) {
                threshold_nodes += root_nodes;
                selected_root = &roots[root_index];
                break;
            }
            threshold_nodes += root_nodes;
        }
        gettimeofday(&stop, NULL);
        total_nodes += threshold_nodes;

        us = ((stop.tv_sec - threshold_start.tv_sec) * 1000000) +
             ((stop.tv_usec - threshold_start.tv_usec));
        nodes_per_us = us ? threshold_nodes / us : 0;
        nodes_per_sec = nodes_per_us * 1000000;
        LOG("IDA threshold %u, explored %'llu nodes, took %.3fs, %'llu nodes-per-sec\n",
            threshold, (unsigned long long)threshold_nodes, us / 1000000, (unsigned long long)nodes_per_sec);

        if (selected_root) {
            us = ((stop.tv_sec - start.tv_sec) * 1000000) + ((stop.tv_usec - start.tv_usec));
            nodes_per_us = us ? total_nodes / us : 0;
            nodes_per_sec = nodes_per_us * 1000000;
            LOG("IDA found solution, explored %'llu total nodes, took %.3fs, %'llu nodes-per-sec\n\n",
                (unsigned long long)total_nodes, us / 1000000, (unsigned long long)nodes_per_sec);
            if (root_count > 1) {
                printf("ROOT_INDEX %u\n", selected_root->index);
            }
            print_moves(best_solution, threshold);
            print_ida_summary(selected_root->cube, best_solution);
            print_cube(selected_root->cube, CUBE_SIZE);
            unmap_ranked_tables();
            free(roots);
            return 0;
        }
    }

    LOG("IDA failed with range %u->%u\n", min_threshold, max_threshold);
    unmap_ranked_tables();
    free(roots);
    return 1;
}
