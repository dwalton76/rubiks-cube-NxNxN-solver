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
#include <unistd.h>

#include "ida_search_core.h"

#define CUBE_SIZE 6
#define CUBE_ARRAY_SIZE 217
#define GROUP_SIZE 16
#define GROUP_U_COUNT 8
#define GROUP_UNIVERSE UINT64_C(12870)
#define PRODUCT_UNIVERSE UINT64_C(165636900)
#define ALL_INNER_X_SIZE 24
#define ALL_INNER_X_UNIVERSE UINT64_C(9465511770)
#define OBLIQUE_PAIR_COUNT 24
#define BINOM_MAX ALL_INNER_X_SIZE
#define DEFAULT_UNPAIRED_MULTIPLIER 0.90f
#define DEFAULT_MAX_IDA_THRESHOLD 20
#define MAX_IDA_THRESHOLD 99
#define MAX_THREADS 64
#define MAX_SPLIT_TASKS (MOVE_COUNT_666 * MOVE_COUNT_666)
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

/*
 * The all-inner-x goal only pins the inner x-centers and the paired L/R
 * obliques, so its stabilizer is far larger and its floors are much lower.
 * Measured the same way, by running this binary from a phase-1 goal state
 * with each --orbitN-need-odd-w combination:
 *
 *   orbit0   1   Uw
 *   orbit1   7   3Lw U 3Fw2 3Lw 3Uw2 F 3Lw
 */
#define ALL_INNER_X_PARITY_FLOOR_ORBIT0 1
#define ALL_INNER_X_PARITY_FLOOR_ORBIT1 7

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

/*
 * All 24 inner x-centers in ascending square order, which is the rank order of
 * lookup-table-6x6x6-step05-inner-x-centers-stage-one-phase.cost-only.bin.  Its
 * goal state paints each pair of opposite faces with one of F, L, U, so the
 * ranked coordinate is the 24!/(8!^3) multiset over those three symbols.
 */
static const unsigned int all_inner_x_squares[ALL_INNER_X_SIZE] = {
    15, 16, 21, 22, 51, 52, 57, 58, 87, 88, 93, 94,
    123, 124, 129, 130, 159, 160, 165, 166, 195, 196, 201, 202,
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
 * heuristic is the max over all three pairings of the remaining phase-3
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

static uint64_t binom[BINOM_MAX + 1][BINOM_MAX + 1];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_666];
static move_type inverse_move[MOVE_MAX];
static unsigned char orbit0_requirement;
static unsigned char orbit1_requirement;
static float cost_to_goal_multiplier;
static const char *all_inner_x_filename;
static unsigned char *all_inner_x_costs;
static int all_inner_x_fd = -1;
static int stage_all_inner_x;
static float unpaired_multiplier = DEFAULT_UNPAIRED_MULTIPLIER;
static move_type best_solution[MAX_IDA_THRESHOLD + 1];

static atomic_uint next_task;
static atomic_uint best_task = NO_TASK;
static pthread_mutex_t best_solution_lock = PTHREAD_MUTEX_INITIALIZER;
static struct {
    unsigned char first_index;
    unsigned char second_index;
} split_tasks[MAX_SPLIT_TASKS];
static unsigned int split_task_count;

struct ranked_cost_file {
    int fd;
    unsigned char *costs;
};

struct heuristic_result {
    uint64_t orbit_rank[ORBIT_COUNT];
    uint64_t table_rank[TABLE_COUNT];
    uint64_t all_inner_x_rank;
    unsigned char table_cost[TABLE_COUNT];
    unsigned char all_inner_x_cost;
    unsigned char unpaired_count;
    unsigned char cost;
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
        "usage: %s --kociemba STATE "
        "{--all-inner-x-cost FILE [--unpaired-multiplier FLOAT] | "
        "--left-right-oblique-cost FILE --left-oblique-outer-x-cost FILE "
        "--right-oblique-outer-x-cost FILE} "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] "
        "[--multiplier FLOAT] "
        "[--orbit0-need-odd-w|--orbit0-need-even-w] "
        "[--orbit1-need-odd-w|--orbit1-need-even-w] "
        "[--apply-move MOVE] [--print-ranks] [--print-legal-moves]\n",
        program
    );
}

static void init_binom(void)
{
    for (unsigned int n = 0; n <= BINOM_MAX; n++) {
        binom[n][0] = 1;
        binom[n][n] = 1;
        for (unsigned int k = 1; k < n; k++) {
            binom[n][k] = binom[n - 1][k - 1] + binom[n - 1][k];
        }
    }
}

/*
 * Rank lexicographically among all 16-character strings containing eight U
 * stickers and eight non-U stickers.  This is the ordering of the generated
 * .state_index files because 'U' sorts before 'x'.
 */
static uint64_t combination_rank_cube(const char *cube, const unsigned int squares[GROUP_SIZE])
{
    unsigned int u_remaining = GROUP_U_COUNT;
    uint64_t rank = 0;

    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        unsigned int positions_after = GROUP_SIZE - position - 1;
        char sticker = cube[squares[position]];

        if (sticker == 'U' || sticker == 'D') {
            if (!u_remaining) {
                return UINT64_MAX;
            }
            u_remaining--;
        } else if (u_remaining) {
            rank += binom[positions_after][u_remaining - 1];
        }
    }
    return u_remaining ? UINT64_MAX : rank;
}

static unsigned char decoded_cost(unsigned char encoded)
{
    return encoded ? encoded - 1 : UINT8_MAX;
}

/* The builder ranks with the symbols sorted, so F is 0, L is 1 and U is 2. */
static unsigned int staged_symbol(char sticker)
{
    switch (sticker) {
        case 'F':
        case 'B':
            return 0;
        case 'L':
        case 'R':
            return 1;
        case 'U':
        case 'D':
            return 2;
        default:
            return UINT_MAX;
    }
}

static uint64_t multiset_permutations(const unsigned int counts[3])
{
    unsigned int total = counts[0] + counts[1] + counts[2];

    return binom[total][counts[0]] * binom[total - counts[0]][counts[1]];
}

static uint64_t all_inner_x_rank_cube(const char *cube)
{
    unsigned int counts[3] = {8, 8, 8};
    uint64_t rank = 0;

    for (unsigned int position = 0; position < ALL_INNER_X_SIZE; position++) {
        unsigned int selected = staged_symbol(cube[all_inner_x_squares[position]]);

        if (selected > 2 || !counts[selected]) {
            return UINT64_MAX;
        }
        for (unsigned int smaller = 0; smaller < selected; smaller++) {
            if (!counts[smaller]) {
                continue;
            }
            counts[smaller]--;
            rank += multiset_permutations(counts);
            counts[smaller]++;
        }
        counts[selected]--;
    }
    return rank;
}

/* Eight of the 24 oblique pairs hold the L/R obliques once they are all paired. */
static unsigned char unpaired_oblique_count(const char *cube)
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

/*
 * One turn can pair at most four obliques, so unpaired/4 is the only admissible
 * bound, but it is far too optimistic to prune with.  --unpaired-multiplier
 * scales the count so the estimate can be tuned between that floor (0.25) and
 * the count itself (1.0), which is what the matrix in ida_search_via_graph.c
 * uses for the L/R version of this phase.
 */
static unsigned char unpaired_cost(unsigned char unpaired)
{
    float scaled = unpaired * unpaired_multiplier;
    unsigned char cost = (unsigned char)ceilf(scaled);

    return unpaired && !cost ? 1 : cost;
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
    unsigned char orbit0_floor = stage_all_inner_x ? ALL_INNER_X_PARITY_FLOOR_ORBIT0 : PARITY_FLOOR_ONE_ORBIT;
    unsigned char orbit1_floor = stage_all_inner_x ? ALL_INNER_X_PARITY_FLOOR_ORBIT1 : PARITY_FLOOR_ONE_ORBIT;
    unsigned char floor = 0;

    if (wrong & 1) {
        floor = orbit0_floor;
    }
    if ((wrong & 2) && orbit1_floor > floor) {
        floor = orbit1_floor;
    }
    if (wrong == 3 && !stage_all_inner_x) {
        floor = PARITY_FLOOR_BOTH_ORBITS;
    }
    return floor;
}

static struct heuristic_result heuristic(const char *cube)
{
    struct heuristic_result result;
    int ranks_are_valid = 1;

    if (stage_all_inner_x) {
        unsigned char encoded;
        unsigned char oblique_cost;

        memset(&result, 0, sizeof(result));
        result.all_inner_x_rank = all_inner_x_rank_cube(cube);

        if (result.all_inner_x_rank == UINT64_MAX) {
            result.cost = UINT8_MAX;
            return result;
        }
        encoded = all_inner_x_costs[result.all_inner_x_rank];
        result.all_inner_x_cost = decoded_cost(encoded);
        result.unpaired_count = unpaired_oblique_count(cube);
        oblique_cost = unpaired_cost(result.unpaired_count);

        if (!encoded) {
            result.cost = UINT8_MAX;
        } else {
            result.cost = result.all_inner_x_cost > oblique_cost ? result.all_inner_x_cost : oblique_cost;
        }
        return result;
    }

    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        result.orbit_rank[orbit] = combination_rank_cube(cube, orbit_squares[orbit]);
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
        result.table_cost[index] = decoded_cost(encoded);

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

static int move_is_allowed(move_type move)
{
    /* Staging every inner x-center and pairing the obliques needs the full move set. */
    if (stage_all_inner_x) {
        return 1;
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
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_666; move_index++) {
        move_type move = moves_666[move_index];
        unsigned int quarter_turn_offset = ((unsigned int)move - 1) % 3;

        inverse_move[move] = quarter_turn_offset == 0 ? move + 1 :
                             quarter_turn_offset == 1 ? move - 1 : move;
        if (move_is_allowed(move)) {
            legal_move_index[MOVE_NONE][legal_move_count[MOVE_NONE]++] = (unsigned char)move_index;
        }
    }

    for (unsigned int previous_index = 0; previous_index < MOVE_COUNT_666; previous_index++) {
        move_type previous_move = moves_666[previous_index];

        if (!move_is_allowed(previous_move)) {
            continue;
        }
        for (unsigned int move_index = 0; move_index < MOVE_COUNT_666; move_index++) {
            move_type move = moves_666[move_index];

            if (!move_is_allowed(move) ||
                steps_on_same_face_and_layer(previous_move, move) ||
                !outer_layer_moves_in_order(previous_move, move) ||
                !steps_on_same_face_in_order(previous_move, move) ||
                !steps_on_opposite_faces_in_order(previous_move, move)) {
                continue;
            }
            legal_move_index[previous_move][legal_move_count[previous_move]++] = (unsigned char)move_index;
        }
    }
}

static struct ranked_cost_file map_ranked_cost_file(const char *filename, uint64_t universe)
{
    struct ranked_cost_file result = {-1, NULL};
    struct stat file_stat;
    int mmap_flags = MAP_SHARED;

    result.fd = open(filename, O_RDONLY);
    if (result.fd < 0) {
        fprintf(stderr, "ERROR: could not open %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if (fstat(result.fd, &file_stat) != 0) {
        fprintf(stderr, "ERROR: could not stat %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if ((uint64_t)file_stat.st_size != universe) {
        fprintf(
            stderr,
            "ERROR: %s is %" PRIu64 " bytes, expected %" PRIu64 "\n",
            filename,
            (uint64_t)file_stat.st_size,
            universe
        );
        exit(1);
    }
#ifdef MAP_POPULATE
    if ((uint64_t)file_stat.st_blocks * 512 >= universe) {
        mmap_flags |= MAP_POPULATE;
    }
#endif
    result.costs = mmap(NULL, (size_t)universe, PROT_READ, mmap_flags, result.fd, 0);
    if (result.costs == MAP_FAILED) {
        fprintf(stderr, "ERROR: could not mmap %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    return result;
}

static void map_ranked_tables(void)
{
    if (stage_all_inner_x) {
        struct ranked_cost_file file = map_ranked_cost_file(all_inner_x_filename, ALL_INNER_X_UNIVERSE);

        all_inner_x_fd = file.fd;
        all_inner_x_costs = file.costs;
        return;
    }

    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        struct ranked_table *table = &ranked_tables[index];
        struct ranked_cost_file file;

        if (!table->filename) {
            continue;
        }
        file = map_ranked_cost_file(table->filename, PRODUCT_UNIVERSE);
        table->fd = file.fd;
        table->costs = file.costs;
    }
}

static void unmap_ranked_tables(void)
{
    if (all_inner_x_costs && all_inner_x_costs != MAP_FAILED) {
        munmap(all_inner_x_costs, (size_t)ALL_INNER_X_UNIVERSE);
    }
    if (all_inner_x_fd >= 0) {
        close(all_inner_x_fd);
    }
    all_inner_x_costs = NULL;
    all_inner_x_fd = -1;

    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        struct ranked_table *table = &ranked_tables[index];

        if (table->costs && table->costs != MAP_FAILED) {
            munmap(table->costs, (size_t)PRODUCT_UNIVERSE);
        }
        if (table->fd >= 0) {
            close(table->fd);
        }
        table->costs = NULL;
        table->fd = -1;
    }
}

static void init_cube_from_kociemba(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    const unsigned int face_size = CUBE_SIZE * CUBE_SIZE;

    if (strlen(kociemba) != face_size * 6) {
        fprintf(stderr, "ERROR: --kociemba must contain 216 stickers for a 6x6x6 cube\n");
        exit(1);
    }
    cube[0] = 'x';
    memcpy(&cube[1], &kociemba[0], face_size);                 /* U */
    memcpy(&cube[1 + face_size], &kociemba[face_size * 4], face_size); /* L */
    memcpy(&cube[1 + face_size * 2], &kociemba[face_size * 2], face_size); /* F */
    memcpy(&cube[1 + face_size * 3], &kociemba[face_size], face_size); /* R */
    memcpy(&cube[1 + face_size * 4], &kociemba[face_size * 5], face_size); /* B */
    memcpy(&cube[1 + face_size * 5], &kociemba[face_size * 3], face_size); /* D */
}

static int is_edge_or_corner(unsigned int square)
{
    unsigned int face_offset = (square - 1) % (CUBE_SIZE * CUBE_SIZE);
    unsigned int row = face_offset / CUBE_SIZE;
    unsigned int col = face_offset % CUBE_SIZE;

    return row == 0 || row == CUBE_SIZE - 1 || col == 0 || col == CUBE_SIZE - 1;
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

        if (is_edge_or_corner(square)) {
            cube[square] = '.';
        }
    }
}

/*
 * The all-inner-x ranked table and the unpaired-oblique count only care about
 * inner x-centers (as U/L/F) and whether an oblique is L/R.  Blank everything
 * else so the printed cube matches the search state.
 */
static void recolor_for_all_inner_x(char cube[CUBE_ARRAY_SIZE])
{
    unsigned char is_inner_x[CUBE_ARRAY_SIZE] = {0};
    unsigned char is_oblique[CUBE_ARRAY_SIZE] = {0};

    for (unsigned int index = 0; index < ALL_INNER_X_SIZE; index++) {
        is_inner_x[all_inner_x_squares[index]] = 1;
    }
    for (unsigned int index = 0; index < OBLIQUE_PAIR_COUNT; index++) {
        is_oblique[all_left_oblique_squares[index]] = 1;
        is_oblique[all_right_oblique_squares[index]] = 1;
    }

    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (is_inner_x[square]) {
            continue;
        }
        if (is_oblique[square]) {
            if (cube[square] != 'L') {
                cube[square] = 'x';
            }
            continue;
        }
        cube[square] = '.';
    }
}

/*
 * A parity requirement can only be met if some legal move flips that orbit.
 * Preserving the staged inner x-centers rules out every 3Xw quarter turn, so
 * orbit1 is frozen for this phase and asking it to flip is unsatisfiable.
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
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_666; move_index++) {
        move_type move = moves_666[move_index];

        if (strmatch((char *)move2str[move], (char *)move_string)) {
            return move;
        }
    }
    return MOVE_NONE;
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
    char rotate_tmp[CUBE_ARRAY_SIZE];

    if (atomic_load_explicit(&best_task, memory_order_relaxed) < worker->task_id) {
        worker->aborted = 1;
        return 0;
    }

    for (unsigned int index = 0; index < count; index++) {
        move_type move = moves_666[legal_move_index[previous_move][index]];
        unsigned char next_parity = parity_after_move(parity, move);
        unsigned char cost;

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

static int build_split_tasks(
    const char *root,
    unsigned char threshold,
    uint64_t *nodes,
    move_type *one_move_solution
)
{
    char cube[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];

    split_task_count = 0;
    *one_move_solution = MOVE_NONE;
    for (unsigned int first_index = 0; first_index < legal_move_count[MOVE_NONE]; first_index++) {
        move_type first = moves_666[legal_move_index[MOVE_NONE][first_index]];
        unsigned char cost;
        unsigned char parity = parity_after_move(0, first);

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
        for (unsigned int second_index = 0; second_index < legal_move_count[first]; second_index++) {
            split_tasks[split_task_count].first_index = (unsigned char)first_index;
            split_tasks[split_task_count].second_index = (unsigned char)second_index;
            split_task_count++;
        }
    }
    return 0;
}

static void *search_split_tasks(void *argument)
{
    struct worker *worker = argument;

    while (1) {
        unsigned int task = atomic_fetch_add(&next_task, 1);
        char cube[CUBE_ARRAY_SIZE];
        char rotate_tmp[CUBE_ARRAY_SIZE];
        move_type first;
        move_type second;
        unsigned char parity;
        unsigned char cost;
        int found;

        if (task >= split_task_count || atomic_load(&best_task) < task) {
            break;
        }
        worker->task_id = task;
        worker->aborted = 0;
        first = moves_666[legal_move_index[MOVE_NONE][split_tasks[task].first_index]];
        second = moves_666[legal_move_index[first][split_tasks[task].second_index]];
        parity = parity_after_move(parity_after_move(0, first), second);

        memcpy(cube, worker->root_cube, CUBE_ARRAY_SIZE);
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, first);
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, second);
        worker->solution[0] = first;
        worker->solution[1] = second;
        worker->ida_count++;
        cost = cube_cost(cube, parity);

        if (cost == UINT8_MAX || 2 + cost > worker->threshold) {
            continue;
        }
        if (!cost) {
            worker->solution[2] = MOVE_NONE;
            found = 1;
        } else if (worker->threshold <= 2) {
            continue;
        } else {
            found = ida_search(worker, cube, 2, worker->threshold, second, parity);
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

static void print_ida_summary(char cube[CUBE_ARRAY_SIZE], const move_type *solution)
{
    char rotate_tmp[CUBE_ARRAY_SIZE];
    unsigned char solution_len = 0;
    unsigned char parity = 0;

    while (solution[solution_len] != MOVE_NONE) {
        solution_len++;
    }
    printf("\n      ");
    if (stage_all_inner_x) {
        printf(" %4s %4s", "IXAL", "UNPR");
    } else {
        for (unsigned int index = 0; index < TABLE_COUNT; index++) {
            if (ranked_tables[index].costs) {
                printf(" %4s", ranked_tables[index].label);
            }
        }
    }
    printf("  CTG  TRU  IDX\n      ");
    if (stage_all_inner_x) {
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
        if (stage_all_inner_x) {
            printf(" %4u %4u", h.all_inner_x_cost, h.unpaired_count);
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
    const char *apply_move_string = NULL;
    unsigned char min_threshold = UINT8_MAX;
    unsigned char max_threshold = DEFAULT_MAX_IDA_THRESHOLD;
    unsigned int thread_count = 0;
    unsigned int loaded_table_count = 0;
    int print_ranks = 0;
    int print_legal_moves = 0;
    char cube[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];
    struct heuristic_result initial;
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

        if (strmatch(argv[index], "--all-inner-x-cost") && index + 1 < argc) {
            all_inner_x_filename = argv[++index];
            stage_all_inner_x = 1;
        } else if (strmatch(argv[index], "--unpaired-multiplier") && index + 1 < argc) {
            unpaired_multiplier = atof(argv[++index]);
        } else if (strmatch(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
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
        } else if (strmatch(argv[index], "--print-rank") || strmatch(argv[index], "--print-ranks")) {
            print_ranks = 1;
        } else if (strmatch(argv[index], "--print-legal-moves")) {
            print_legal_moves = 1;
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if (!kociemba) {
        usage(argv[0]);
        return 2;
    }
    if (!stage_all_inner_x) {
        for (unsigned int table = 0; table < REQUIRED_TABLE_COUNT; table++) {
            if (!ranked_tables[table].filename) {
                usage(argv[0]);
                return 2;
            }
        }
    }
    /*
     * A multiplier of 0 would score an unstaged cube as solved, and anything
     * above 1.0 is a worse estimate than simply counting the unpaired obliques.
     */
    if (unpaired_multiplier <= 0.0 || unpaired_multiplier > 1.0) {
        fprintf(stderr, "ERROR: --unpaired-multiplier must be in (0.0, 1.0]\n");
        return 2;
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
    if (!parity_requirements_are_reachable()) {
        return 2;
    }
    init_cube_from_kociemba(cube, kociemba);
    if (apply_move_string) {
        move_type move = parse_move(apply_move_string);
        if (move == MOVE_NONE) {
            fprintf(stderr, "ERROR: invalid --apply-move %s\n", apply_move_string);
            return 2;
        }
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
    }
    recolor_cube(cube);
    if (stage_all_inner_x) {
        recolor_for_all_inner_x(cube);
    }
    map_ranked_tables();
    initial = heuristic(cube);

    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_666[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }
    if (print_ranks) {
        if (stage_all_inner_x) {
            printf(
                "IXAL_RANK %" PRIu64 " IXAL_COST %u UNPAIRED %u",
                initial.all_inner_x_rank, initial.all_inner_x_cost, initial.unpaired_count
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
        return initial.cost == UINT8_MAX;
    }
    if (initial.cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial center state is absent from a ranked cost table\n");
        unmap_ranked_tables();
        return 1;
    }
    if (min_threshold == UINT8_MAX) {
        min_threshold = cube_cost(cube, 0);
    }

    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        if (ranked_tables[index].costs) {
            loaded_table_count++;
        }
    }
    if (stage_all_inner_x) {
        loaded_table_count = 1;
    }
    print_cube(cube, CUBE_SIZE);
    if (stage_all_inner_x) {
        LOG("staging all inner x-centers with unpaired multiplier %.2f\n", unpaired_multiplier);
    }
    LOG("searching with %u threads over %u ranked tables\n", thread_count, loaded_table_count);
    memset(best_solution, 0, sizeof(best_solution));
    gettimeofday(&start, NULL);
    for (unsigned char threshold = min_threshold; threshold <= max_threshold; threshold++) {
        struct timeval threshold_start;
        struct timeval stop;
        uint64_t nodes;
        float us;
        float nodes_per_us;
        unsigned int nodes_per_sec;
        int found_solution;

        gettimeofday(&threshold_start, NULL);
        found_solution = search_threshold(cube, threshold, thread_count, &nodes);
        gettimeofday(&stop, NULL);
        total_nodes += nodes;

        us = ((stop.tv_sec - threshold_start.tv_sec) * 1000000) +
             ((stop.tv_usec - threshold_start.tv_usec));
        nodes_per_us = us ? nodes / us : 0;
        nodes_per_sec = nodes_per_us * 1000000;
        LOG("IDA threshold %u, explored %'llu nodes, took %.3fs, %'llu nodes-per-sec\n",
            threshold, (unsigned long long)nodes, us / 1000000, (unsigned long long)nodes_per_sec);

        if (found_solution) {
            us = ((stop.tv_sec - start.tv_sec) * 1000000) + ((stop.tv_usec - start.tv_usec));
            nodes_per_us = us ? total_nodes / us : 0;
            nodes_per_sec = nodes_per_us * 1000000;
            LOG("IDA found solution, explored %'llu total nodes, took %.3fs, %'llu nodes-per-sec\n\n",
                (unsigned long long)total_nodes, us / 1000000, (unsigned long long)nodes_per_sec);
            print_moves(best_solution, threshold);
            print_ida_summary(cube, best_solution);
            print_cube(cube, CUBE_SIZE);
            unmap_ranked_tables();
            return 0;
        }
    }

    LOG("IDA failed with range %u->%u\n", min_threshold, max_threshold);
    unmap_ranked_tables();
    return 1;
}
