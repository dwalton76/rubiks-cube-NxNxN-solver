#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
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

#define CUBE_SIZE 7
#define CUBE_ARRAY_SIZE 295
#define GROUP_SIZE 16
#define GROUP_U_COUNT 8
#define GROUP_UNIVERSE UINT64_C(12870)
#define PRODUCT_UNIVERSE UINT64_C(165636900)
#define ORBIT_COUNT 4
#define TABLE_COUNT 6
#define DEFAULT_MAX_IDA_THRESHOLD 30
#define MAX_IDA_THRESHOLD 99
#define MAX_THREADS 64
#define NO_TASK UINT_MAX
#define PARITY_ANY 0
#define PARITY_ODD 1
#define PARITY_EVEN 2

/*
 * Any orbit0 parity correction needs at least one wide quarter turn, so one
 * move is an admissible parity floor.
 */
#define PARITY_FLOOR_ORBIT0 1

/*
 * Exact UFBD tuples from RubiksCube777.py. Every coordinate contains eight
 * U/D stickers and eight F/B stickers and is ranked as C(16, 8).
 */
enum orbit_index {
    ORBIT_OUTER_X,
    ORBIT_LEFT_OBLIQUE,
    ORBIT_MIDDLE_OBLIQUE,
    ORBIT_RIGHT_OBLIQUE,
};

static const unsigned int outer_x_squares[GROUP_SIZE] = {
    9, 13, 37, 41, 107, 111, 135, 139, 205, 209, 233, 237, 254, 258, 282, 286,
};
static const unsigned int left_oblique_squares[GROUP_SIZE] = {
    10, 20, 30, 40, 108, 118, 128, 138, 206, 216, 226, 236, 255, 265, 275, 285,
};
static const unsigned int middle_oblique_squares[GROUP_SIZE] = {
    11, 23, 27, 39, 109, 121, 125, 137, 207, 219, 223, 235, 256, 268, 272, 284,
};
static const unsigned int right_oblique_squares[GROUP_SIZE] = {
    12, 16, 34, 38, 110, 114, 132, 136, 208, 212, 230, 234, 257, 261, 279, 283,
};

static const unsigned int *orbit_squares[ORBIT_COUNT] = {
    outer_x_squares,
    left_oblique_squares,
    middle_oblique_squares,
    right_oblique_squares,
};

static struct ranked_table {
    const char *flag;
    const char *label;
    unsigned char orbit_a;
    unsigned char orbit_b;
    const char *filename;
    unsigned char *costs;
    int fd;
} ranked_tables[TABLE_COUNT] = {
    {"--left-middle-oblique-cost", "LOMO", ORBIT_LEFT_OBLIQUE, ORBIT_MIDDLE_OBLIQUE, NULL, NULL, -1},
    {"--left-right-oblique-cost", "LORO", ORBIT_LEFT_OBLIQUE, ORBIT_RIGHT_OBLIQUE, NULL, NULL, -1},
    {"--left-oblique-outer-x-cost", "LOOX", ORBIT_LEFT_OBLIQUE, ORBIT_OUTER_X, NULL, NULL, -1},
    {"--middle-right-oblique-cost", "MORO", ORBIT_MIDDLE_OBLIQUE, ORBIT_RIGHT_OBLIQUE, NULL, NULL, -1},
    {"--middle-oblique-outer-x-cost", "MOOX", ORBIT_MIDDLE_OBLIQUE, ORBIT_OUTER_X, NULL, NULL, -1},
    {"--right-oblique-outer-x-cost", "ROOX", ORBIT_RIGHT_OBLIQUE, ORBIT_OUTER_X, NULL, NULL, -1},
};

static move_type inverse_move[MOVE_MAX];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_777];
static move_type solution[MAX_IDA_THRESHOLD + 1];
static atomic_uint next_task;
static atomic_uint solution_task = NO_TASK;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned char search_threshold;
static float cost_to_goal_multiplier;
static unsigned char orbit0_requirement;
static int obliques_only;

struct heuristic_result {
    uint64_t orbit_rank[ORBIT_COUNT];
    uint64_t table_rank[TABLE_COUNT];
    unsigned char table_cost[TABLE_COUNT];
    unsigned char cost;
};

struct worker {
    const char *root_cube;
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
        "(all six --*-cost FILE flags | --obliques-only and the three oblique-oblique FILE flags) "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] "
        "[--multiplier F] [--print-ida-summary] "
        "[--orbit0-need-odd-w|--orbit0-need-even-w] "
        "[--apply-move MOVE] [--print-ranks] [--print-legal-moves]\n",
        program
    );
    printf(
        "  --obliques-only  pair U/D left/middle/right obliques; do not load outer-x tables\n"
    );
}

static uint64_t combination_rank(const char *cube, const unsigned int squares[GROUP_SIZE])
{
    return ida_combination_rank_ud(cube, squares, GROUP_SIZE, GROUP_U_COUNT);
}

static int table_is_oblique_only(const struct ranked_table *table)
{
    return table->orbit_a != ORBIT_OUTER_X && table->orbit_b != ORBIT_OUTER_X;
}

static struct heuristic_result heuristic(const char *cube)
{
    struct heuristic_result result;
    int valid = 1;
    int loaded = 0;

    memset(&result, 0, sizeof(result));
    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        if (obliques_only && orbit == ORBIT_OUTER_X) {
            result.orbit_rank[orbit] = UINT64_MAX;
            continue;
        }
        result.orbit_rank[orbit] = combination_rank(cube, orbit_squares[orbit]);
        if (result.orbit_rank[orbit] == UINT64_MAX) {
            valid = 0;
        }
    }
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        const struct ranked_table *table = &ranked_tables[index];
        unsigned char encoded;

        if (!table->costs) {
            result.table_rank[index] = UINT64_MAX;
            result.table_cost[index] = UINT8_MAX;
            continue;
        }
        loaded = 1;
        if (!valid) {
            result.table_rank[index] = UINT64_MAX;
            result.table_cost[index] = UINT8_MAX;
            result.cost = UINT8_MAX;
            continue;
        }
        result.table_rank[index] =
            result.orbit_rank[table->orbit_a] * GROUP_UNIVERSE + result.orbit_rank[table->orbit_b];
        encoded = table->costs[result.table_rank[index]];
        result.table_cost[index] = encoded ? encoded - 1 : UINT8_MAX;
        if (!encoded) {
            result.cost = UINT8_MAX;
        } else if (result.cost != UINT8_MAX && result.table_cost[index] > result.cost) {
            result.cost = result.table_cost[index];
        }
    }
    if (!loaded) {
        result.cost = UINT8_MAX;
    }
    return result;
}

/* Bit 0 counts orbit0 wide quarter turns. */
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
        default:
            return 0;
    }
}

static unsigned char parity_after_move(unsigned char parity, move_type move)
{
    return parity ^ parity_bit_of_move(move);
}

/*
 * A solution that leaves an orbit on the wrong wide quarter turn parity hands
 * OLL parity to the edge pairing that follows, so keep searching past it. The
 * floor is what it costs to flip an orbit from a goal state.
 */
static unsigned char parity_flip_floor(unsigned char parity)
{
    unsigned char orbit0 = parity & 1;

    if ((orbit0_requirement == PARITY_ODD && !orbit0) ||
        (orbit0_requirement == PARITY_EVEN && orbit0)) {
        return PARITY_FLOOR_ORBIT0;
    }
    return 0;
}

static unsigned char cube_cost(const char *cube, unsigned char parity)
{
    unsigned char cost = heuristic(cube).cost;

    if (cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    if (cost && cost_to_goal_multiplier) {
        cost = (unsigned char)roundf(cost * cost_to_goal_multiplier);
    }
    return cost ? cost : parity_flip_floor(parity);
}

/*
 * Last ply must land on a goal: staged centers and orbit0 parity already
 * correct. A move that leaves orbit0 on the wrong parity still needs the
 * flip floor of 1, so it cannot finish a solution at this threshold. Skip
 * the rotate and table lookup for those moves.
 */
static int last_ply_can_be_goal(unsigned char parity, move_type move)
{
    return !parity_flip_floor(parity_after_move(parity, move));
}

static int move_is_allowed(move_type move)
{
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
        moves_777, MOVE_COUNT_777, move_is_allowed, legal_move_count, legal_move_index, inverse_move
    );
}

static void map_ranked_tables(void)
{
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        struct ranked_table *table = &ranked_tables[index];

        if (!table->filename || (obliques_only && !table_is_oblique_only(table))) {
            continue;
        }
        struct mapped_cost_file file = ida_map_cost_file(table->filename, PRODUCT_UNIVERSE);

        table->fd = file.fd;
        table->costs = file.costs;
    }
}

static void unmap_ranked_tables(void)
{
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        struct ranked_table *table = &ranked_tables[index];

        ida_unmap_cost_file(table->fd, table->costs, (size_t)PRODUCT_UNIVERSE);
        table->costs = NULL;
        table->fd = -1;
    }
}

static void init_cube(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    ida_init_cube(cube, CUBE_SIZE, kociemba);
}

static void recolor_cube(char cube[CUBE_ARRAY_SIZE])
{
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (ida_is_edge_or_corner(square, CUBE_SIZE)) {
            cube[square] = '.';
        } else if (cube[square] == 'R') {
            cube[square] = 'L';
        } else if (cube[square] == 'D') {
            cube[square] = 'U';
        } else if (cube[square] == 'B') {
            cube[square] = 'F';
        }
    }
}

static move_type parse_move(const char *move_string)
{
    return ida_parse_move(move_string, moves_777, MOVE_COUNT_777);
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
    struct child children[MOVE_COUNT_777];
    unsigned int child_count = 0;
    unsigned char next_depth = depth + 1;
    int last_ply = next_depth == threshold;
    char rotate_tmp[CUBE_ARRAY_SIZE];

    if (atomic_load_explicit(&solution_task, memory_order_relaxed) != NO_TASK) {
        return 0;
    }
    for (unsigned int index = 0; index < legal_move_count[previous_move]; index++) {
        move_type move = moves_777[legal_move_index[previous_move][index]];
        unsigned char next_parity;
        unsigned char cost;

        if (last_ply && !last_ply_can_be_goal(parity, move)) {
            continue;
        }
        next_parity = parity_after_move(parity, move);
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        cost = cube_cost(cube, next_parity);
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[move]);
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
        move_type move = children[index].move;

        worker->solution[depth] = move;
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        if (ida_search(worker, cube, next_depth, threshold, move, children[index].parity)) {
            return 1;
        }
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[move]);
    }
    worker->solution[depth] = MOVE_NONE;
    return 0;
}

static void *search_root_moves(void *argument)
{
    struct worker *worker = argument;

    while (1) {
        unsigned int task = atomic_fetch_add(&next_task, 1);
        char cube[CUBE_ARRAY_SIZE];
        char rotate_tmp[CUBE_ARRAY_SIZE];
        move_type first;
        unsigned char parity;
        unsigned char cost;
        int found;

        if (task >= legal_move_count[MOVE_NONE] || atomic_load(&solution_task) != NO_TASK) {
            break;
        }
        first = moves_777[legal_move_index[MOVE_NONE][task]];
        if (search_threshold == 1 && !last_ply_can_be_goal(0, first)) {
            continue;
        }
        parity = parity_after_move(0, first);
        memcpy(cube, worker->root_cube, CUBE_ARRAY_SIZE);
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, first);
        worker->ida_count++;
        cost = cube_cost(cube, parity);

        if (cost == UINT8_MAX || 1 + cost > search_threshold) {
            continue;
        }
        worker->solution[0] = first;
        if (!cost) {
            worker->solution[1] = MOVE_NONE;
            found = 1;
        } else if (search_threshold <= 1) {
            continue;
        } else {
            found = ida_search(worker, cube, 1, search_threshold, first, parity);
        }

        if (found) {
            pthread_mutex_lock(&solution_lock);
            if (atomic_load(&solution_task) == NO_TASK) {
                memcpy(solution, worker->solution, sizeof(solution));
                atomic_store(&solution_task, task);
            }
            pthread_mutex_unlock(&solution_lock);
            break;
        }
    }
    return NULL;
}

static int search_at_threshold(
    const char cube[CUBE_ARRAY_SIZE],
    unsigned char threshold,
    unsigned int thread_count,
    uint64_t *nodes
)
{
    struct worker workers[MAX_THREADS];
    pthread_t threads[MAX_THREADS];
    unsigned int worker_count = thread_count < legal_move_count[MOVE_NONE] ?
                                thread_count : legal_move_count[MOVE_NONE];

    *nodes = 1;
    search_threshold = threshold;
    atomic_store(&next_task, 0);
    atomic_store(&solution_task, NO_TASK);
    for (unsigned int index = 0; index < worker_count; index++) {
        memset(&workers[index], 0, sizeof(workers[index]));
        workers[index].root_cube = cube;
        if (pthread_create(&threads[index], NULL, search_root_moves, &workers[index]) != 0) {
            fprintf(stderr, "ERROR: could not create search thread %u\n", index);
            exit(1);
        }
    }
    for (unsigned int index = 0; index < worker_count; index++) {
        pthread_join(threads[index], NULL);
        *nodes += workers[index].ida_count;
    }
    return atomic_load(&solution_task) != NO_TASK;
}

static double elapsed_seconds(const struct timeval *start, const struct timeval *end)
{
    return (end->tv_sec - start->tv_sec) + (end->tv_usec - start->tv_usec) / 1000000.0;
}

static void print_ida_summary(const char cube[CUBE_ARRAY_SIZE], unsigned int length)
{
    char walk[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];

    memcpy(walk, cube, CUBE_ARRAY_SIZE);
    printf("\n      ");
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        printf(" %4s", ranked_tables[index].label);
    }
    printf("  CTG  TRU  IDX\n      ");
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        printf(" ====");
    }
    printf("  ===  ===  ===\n");
    for (unsigned int step = 0; step <= length; step++) {
        struct heuristic_result h = heuristic(walk);

        if (step) {
            printf("%5s ", move2str[solution[step - 1]]);
        } else {
            printf(" INIT ");
        }
        for (unsigned int index = 0; index < TABLE_COUNT; index++) {
            printf(" %4u", h.table_cost[index]);
        }
        printf("  %3u  %3u  %3u\n", h.cost, length - step, step);
        if (step < length) {
            rotate_777_centers(walk, rotate_tmp, CUBE_ARRAY_SIZE, solution[step]);
        }
    }
    printf("\n");
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *apply_move_string = NULL;
    unsigned char min_threshold = 0;
    unsigned char max_threshold = DEFAULT_MAX_IDA_THRESHOLD;
    long detected_cpus = sysconf(_SC_NPROCESSORS_ONLN);
    unsigned int thread_count = detected_cpus > 0 ? (unsigned int)detected_cpus : 1;
    int print_summary = 0;
    int print_ranks = 0;
    int print_legal_moves = 0;
    char cube[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];

    if (thread_count > MAX_THREADS) {
        thread_count = MAX_THREADS;
    }
    for (int index = 1; index < argc; index++) {
        int matched_table = 0;

        for (unsigned int table = 0; table < TABLE_COUNT; table++) {
            if (!strcmp(argv[index], ranked_tables[table].flag) && index + 1 < argc) {
                ranked_tables[table].filename = argv[++index];
                matched_table = 1;
                break;
            }
        }
        if (matched_table) {
            continue;
        }
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--threads") && index + 1 < argc) {
            thread_count = (unsigned int)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--multiplier") && index + 1 < argc) {
            cost_to_goal_multiplier = (float)atof(argv[++index]);
        } else if (!strcmp(argv[index], "--orbit0-need-odd-w")) {
            orbit0_requirement = PARITY_ODD;
        } else if (!strcmp(argv[index], "--orbit0-need-even-w")) {
            orbit0_requirement = PARITY_EVEN;
        } else if (!strcmp(argv[index], "--apply-move") && index + 1 < argc) {
            apply_move_string = argv[++index];
        } else if (!strcmp(argv[index], "--print-rank") || !strcmp(argv[index], "--print-ranks")) {
            print_ranks = 1;
        } else if (!strcmp(argv[index], "--print-legal-moves")) {
            print_legal_moves = 1;
        } else if (!strcmp(argv[index], "--obliques-only")) {
            obliques_only = 1;
        } else if (!strcmp(argv[index], "--print-ida-summary")) {
            print_summary = 1;
        } else {
            usage(argv[0]);
            return 1;
        }
    }
    if (!kociemba || !thread_count || thread_count > MAX_THREADS ||
        min_threshold > max_threshold || max_threshold > MAX_IDA_THRESHOLD) {
        usage(argv[0]);
        return 2;
    }
    for (unsigned int table = 0; table < TABLE_COUNT; table++) {
        if (table_is_oblique_only(&ranked_tables[table]) || !obliques_only) {
            if (!ranked_tables[table].filename) {
                usage(argv[0]);
                return 2;
            }
        }
    }
    /* Below 1.0 would weaken the heuristic rather than inflate it. */
    if (cost_to_goal_multiplier && cost_to_goal_multiplier < 1.0f) {
        fprintf(stderr, "ERROR: --multiplier must be at least 1.0\n");
        return 1;
    }

    init_binom();
    init_move_tables();
    map_ranked_tables();
    init_cube(cube, kociemba);
    if (apply_move_string) {
        move_type move = parse_move(apply_move_string);

        if (move == MOVE_NONE) {
            fprintf(stderr, "ERROR: invalid --apply-move %s\n", apply_move_string);
            unmap_ranked_tables();
            return 2;
        }
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
    }
    recolor_cube(cube);

    struct heuristic_result initial = heuristic(cube);
    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_777[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }
    if (print_ranks) {
        printf(
            "OUTER_RANK %" PRIu64 " LEFT_RANK %" PRIu64 " MIDDLE_RANK %" PRIu64
            " RIGHT_RANK %" PRIu64,
            initial.orbit_rank[ORBIT_OUTER_X], initial.orbit_rank[ORBIT_LEFT_OBLIQUE],
            initial.orbit_rank[ORBIT_MIDDLE_OBLIQUE], initial.orbit_rank[ORBIT_RIGHT_OBLIQUE]
        );
        for (unsigned int index = 0; index < TABLE_COUNT; index++) {
            printf(
                " %s_RANK %" PRIu64 " %s_COST %u",
                ranked_tables[index].label, initial.table_rank[index],
                ranked_tables[index].label, initial.table_cost[index]
            );
        }
        printf(" COST %u\n", initial.cost);
        unmap_ranked_tables();
        return initial.cost == UINT8_MAX;
    }

    printf("START\n");
    print_cube(cube, CUBE_SIZE);

    unsigned char initial_cost = cube_cost(cube, 0);
    if (initial_cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial center state is absent from a ranked cost table\n");
        unmap_ranked_tables();
        return 1;
    }
    LOG("initial cost %u, threads %u, ranked tables %s\n",
        initial_cost, thread_count, obliques_only ? "3 (obliques only)" : "6");
    if (min_threshold < initial_cost) {
        min_threshold = initial_cost;
    }

    for (unsigned char threshold = min_threshold; threshold <= max_threshold; threshold++) {
        struct timeval start;
        struct timeval end;
        uint64_t threshold_nodes = 1;

        gettimeofday(&start, NULL);
        int found = !initial_cost || search_at_threshold(cube, threshold, thread_count, &threshold_nodes);
        gettimeofday(&end, NULL);
        LOG(
            "IDA threshold %u, explored %" PRIu64 " nodes, took %.3fs\n",
            threshold,
            threshold_nodes,
            elapsed_seconds(&start, &end)
        );
        if (found) {
            unsigned int length = 0;

            while (solution[length] != MOVE_NONE) {
                length++;
            }
            printf("SOLUTION (%u steps):", length);
            for (unsigned int index = 0; index < length; index++) {
                printf(" %s", move2str[solution[index]]);
            }
            printf("\n");
            if (print_summary) {
                print_ida_summary(cube, length);
            }
            for (unsigned int index = 0; index < length; index++) {
                rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, solution[index]);
            }
            printf("END\n");
            print_cube(cube, CUBE_SIZE);
            unmap_ranked_tables();
            return 0;
        }
    }

    fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
    unmap_ranked_tables();
    return 1;
}
