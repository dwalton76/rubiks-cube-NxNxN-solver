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
#define OBLIQUE_COUNT 24
#define MATRIX_UNPAIRED_MAX 16
#define MATRIX_COST_MAX 12
#define DEFAULT_MAX_IDA_THRESHOLD 30
#define MAX_IDA_THRESHOLD 99
#define MAX_THREADS 64
#define NO_TASK UINT_MAX
#define PARITY_ODD 1
#define PARITY_EVEN 2

/*
 * Cheapest solution from a goal state that flips one orbit's wide quarter turn
 * parity, measured by running this binary from a solved cube with each
 * --orbitN-need-odd-w flag:
 *
 *   orbit0   1   Uw
 *   orbit1   7   3Lw' U2 D2 3Lw U2 D2 3Lw
 */
#define PARITY_FLOOR_ORBIT0 1
#define PARITY_FLOOR_ORBIT1 7

/*
 * These are UFBD_INNER_T_CENTERS_777 and UFBD_INNER_X_CENTERS_777 from
 * RubiksCube777.py. Their order must remain identical to the two rank groups
 * in Build777Phase2UDInnerCentersStage.
 */
static const unsigned int inner_t_centers[GROUP_SIZE] = {
    18, 24, 26, 32, 116, 122, 124, 130, 214, 220, 222, 228, 263, 269, 271, 277,
};
static const unsigned int inner_x_centers[GROUP_SIZE] = {
    17, 19, 31, 33, 115, 117, 129, 131, 213, 215, 227, 229, 262, 264, 276, 278,
};

/*
 * Matching left/middle/right positions for all 24 oblique triplets. Eight
 * triplets contain L/R centers once the obliques are fully paired.
 */
static const unsigned int left_obliques[OBLIQUE_COUNT] = {
    10, 30, 20, 40, 59, 79, 69, 89, 108, 128, 118, 138,
    157, 177, 167, 187, 206, 226, 216, 236, 255, 275, 265, 285,
};
static const unsigned int middle_obliques[OBLIQUE_COUNT] = {
    11, 23, 27, 39, 60, 72, 76, 88, 109, 121, 125, 137,
    158, 170, 174, 186, 207, 219, 223, 235, 256, 268, 272, 284,
};
static const unsigned int right_obliques[OBLIQUE_COUNT] = {
    12, 16, 34, 38, 61, 65, 83, 87, 110, 114, 132, 136,
    159, 163, 181, 185, 208, 212, 230, 234, 257, 261, 279, 283,
};

/*
 * Combined heuristic for staging the U/D inner t/x centers while pairing the
 * L/R obliques. Rows are the unpaired oblique count (0..16), columns are the
 * exact ranked table cost (0..12, the table's completed depth).
 *
 * The table only sees the U/D inner centers and one move pairs at most four
 * obliques, so max(table, ceil(unpaired/4)) is admissible yet far below the
 * real remaining distance, which makes the search crawl.
 *
 * Column 0 seeds from ida_heuristic_LR_oblique_edges_stage_777, the empirical
 * unpaired-count costs the old oblique-only phase 2 used. Every other cell is
 * the smallest remaining move count observed for that pair while sampling
 * solutions, never below max(column 0, table cost).
 *
 * utils/build-777-UD-inner-centers-oblique-matrix.py was used to build this.
 */
static const unsigned char unpaired_count_UD_inner_centers_777[MATRIX_UNPAIRED_MAX + 1][MATRIX_COST_MAX + 1] = {
    { 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // unpaired 0
    { 1,  1,  2,  3,  6,  7,  7,  7,  8,  9, 10, 11, 12},  // unpaired 1
    { 1,  1,  2,  3,  6,  7,  8,  9,  9,  9, 10, 11, 12},  // unpaired 2
    { 6,  6,  6,  6,  6,  7,  8,  9, 11, 13, 13, 13, 13},  // unpaired 3
    { 6,  6,  6,  7,  7,  7,  8,  9, 11, 13, 14, 15, 15},  // unpaired 4
    { 8,  8,  8,  8,  8,  8,  8,  9, 11, 13, 15, 15, 15},  // unpaired 5
    { 8, 10, 10, 11, 11, 11, 11, 11, 11, 13, 15, 15, 15},  // unpaired 6
    { 8, 10, 10, 12, 12, 12, 12, 12, 12, 13, 15, 16, 16},  // unpaired 7
    { 9, 10, 11, 12, 12, 12, 12, 12, 12, 13, 15, 16, 16},  // unpaired 8
    { 9, 11, 12, 14, 14, 14, 14, 14, 14, 14, 15, 16, 16},  // unpaired 9
    {10, 11, 12, 14, 14, 14, 14, 14, 14, 14, 15, 18, 18},  // unpaired 10
    {11, 11, 12, 14, 14, 14, 14, 17, 17, 17, 17, 18, 18},  // unpaired 11
    {11, 11, 12, 14, 14, 14, 15, 17, 17, 17, 17, 18, 18},  // unpaired 12
    {12, 12, 12, 14, 14, 14, 15, 18, 18, 18, 18, 18, 18},  // unpaired 13
    {12, 12, 12, 14, 14, 14, 15, 18, 18, 18, 19, 19, 19},  // unpaired 14
    {12, 12, 12, 14, 14, 14, 15, 18, 18, 18, 19, 19, 19},  // unpaired 15
    {12, 12, 12, 14, 14, 14, 15, 18, 18, 18, 19, 19, 19},  // unpaired 16
};

static uint64_t binom[GROUP_SIZE + 1][GROUP_SIZE + 1];
static unsigned char *ranked_costs;
static int ranked_cost_fd = -1;
static move_type inverse_move[MOVE_MAX];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_777];
static move_type solution[MAX_IDA_THRESHOLD + 1];
static atomic_uint next_task;
static atomic_uint solution_task = NO_TASK;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned char search_threshold;
static float unpaired_multiplier = 0.25f;
static int use_unpaired_multiplier;
static float cost_to_goal_multiplier;
static unsigned char orbit0_requirement;
static unsigned char orbit1_requirement;

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
        "usage: %s --kociemba STATE --ranked-UD-inner-centers-cost FILE "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] "
        "[--multiplier F] [--unpaired-multiplier F] [--print-ida-summary] "
        "[--orbit0-need-odd-w] [--orbit0-need-even-w] "
        "[--orbit1-need-odd-w] [--orbit1-need-even-w]\n",
        program
    );
    printf(
        "  --multiplier F           scale the cost to goal by F to trade solution length for\n"
        "                           search speed, used to bootstrap the matrix samples\n"
        "  --unpaired-multiplier F  use max(table, ceil(unpaired * F)) instead of the combined\n"
        "                           matrix, 0.25 is admissible and larger values are not\n"
        "  --print-ida-summary      print the table cost and unpaired count along the solution\n"
    );
}

static void init_binom(void)
{
    for (unsigned int n = 0; n <= GROUP_SIZE; n++) {
        binom[n][0] = 1;
        binom[n][n] = 1;
        for (unsigned int k = 1; k < n; k++) {
            binom[n][k] = binom[n - 1][k - 1] + binom[n - 1][k];
        }
    }
}

/*
 * Rank lexicographically among strings containing eight U/D stickers and
 * eight other stickers. This matches the builder's sorted U/x rank.
 */
static uint64_t combination_rank(const char *cube, const unsigned int squares[GROUP_SIZE])
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

static int is_lr(char sticker)
{
    return sticker == 'L' || sticker == 'R';
}

static unsigned char unpaired_oblique_count(const char *cube)
{
    unsigned char paired = 0;

    for (unsigned int index = 0; index < OBLIQUE_COUNT; index++) {
        if (is_lr(cube[middle_obliques[index]])) {
            paired += is_lr(cube[left_obliques[index]]);
            paired += is_lr(cube[right_obliques[index]]);
        }
    }
    return 16 - paired;
}

/*
 * One move can pair at most four obliques, so a multiplier of 0.25 is
 * admissible. Larger multipliers are inadmissible but are the only way to
 * solve enough cubes to sample the matrix.
 */
static unsigned char unpaired_cost(unsigned char unpaired)
{
    unsigned char cost = (unsigned char)ceilf(unpaired * unpaired_multiplier);

    return unpaired && !cost ? 1 : cost;
}

static unsigned char centers_table_cost(const char *cube)
{
    uint64_t t_rank = combination_rank(cube, inner_t_centers);
    uint64_t x_rank = combination_rank(cube, inner_x_centers);
    unsigned char encoded;

    if (t_rank == UINT64_MAX || x_rank == UINT64_MAX) {
        return UINT8_MAX;
    }
    encoded = ranked_costs[(t_rank * GROUP_UNIVERSE) + x_rank];
    return encoded ? encoded - 1 : UINT8_MAX;
}

static unsigned char combined_cost(unsigned char centers_cost, unsigned char unpaired)
{
    unsigned char obliques_cost;

    if (!use_unpaired_multiplier && centers_cost <= MATRIX_COST_MAX) {
        return unpaired_count_UD_inner_centers_777[unpaired][centers_cost];
    }
    obliques_cost = unpaired_cost(unpaired);
    return centers_cost > obliques_cost ? centers_cost : obliques_cost;
}

/* Bit 0 counts orbit0 wide quarter turns, bit 1 counts orbit1 wide quarter turns. */
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

/*
 * A solution that leaves an orbit on the wrong wide quarter turn parity hands
 * OLL parity to the edge pairing that follows, so keep searching past it. The
 * floor is what it costs to flip an orbit from a goal state.
 */
static unsigned char parity_flip_floor(unsigned char parity)
{
    unsigned char orbit0 = parity & 1;
    unsigned char orbit1 = (parity >> 1) & 1;
    unsigned char floor = 0;

    if ((orbit0_requirement == PARITY_ODD && !orbit0) ||
        (orbit0_requirement == PARITY_EVEN && orbit0)) {
        floor = PARITY_FLOOR_ORBIT0;
    }
    if (((orbit1_requirement == PARITY_ODD && !orbit1) ||
         (orbit1_requirement == PARITY_EVEN && orbit1)) &&
        PARITY_FLOOR_ORBIT1 > floor) {
        floor = PARITY_FLOOR_ORBIT1;
    }
    return floor;
}

static unsigned char cube_cost(const char *cube, unsigned char parity)
{
    unsigned char centers_cost = centers_table_cost(cube);
    unsigned char cost;

    if (centers_cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    cost = combined_cost(centers_cost, unpaired_oblique_count(cube));
    if (cost && cost_to_goal_multiplier) {
        cost = (unsigned char)roundf(cost * cost_to_goal_multiplier);
    }
    return cost ? cost : parity_flip_floor(parity);
}

/*
 * Last ply must land on a goal: staged centers and both orbit parities already
 * correct. A move that leaves an orbit on the wrong parity still needs the
 * flip floor (1 for orbit0, 7 for orbit1), so it cannot be the 12th move of a
 * depth-12 solution. Skip the rotate and table lookup for those moves.
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
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeDw:
        case threeDw_PRIME:
            return 0;
        default:
            return 1;
    }
}

static void init_move_tables(void)
{
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_777; move_index++) {
        move_type move = moves_777[move_index];
        unsigned int quarter_turn_offset = ((unsigned int)move - 1) % 3;

        inverse_move[move] = quarter_turn_offset == 0 ? move + 1 :
                             quarter_turn_offset == 1 ? move - 1 : move;
        if (move_is_allowed(move)) {
            legal_move_index[MOVE_NONE][legal_move_count[MOVE_NONE]++] = (unsigned char)move_index;
        }
    }

    for (unsigned int previous_index = 0; previous_index < MOVE_COUNT_777; previous_index++) {
        move_type previous_move = moves_777[previous_index];

        if (!move_is_allowed(previous_move)) {
            continue;
        }
        for (unsigned int move_index = 0; move_index < MOVE_COUNT_777; move_index++) {
            move_type move = moves_777[move_index];

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

static void map_ranked_cost_file(const char *filename)
{
    struct stat file_stat;
    int mmap_flags = MAP_SHARED;

    ranked_cost_fd = open(filename, O_RDONLY);
    if (ranked_cost_fd < 0) {
        fprintf(stderr, "ERROR: could not open %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if (fstat(ranked_cost_fd, &file_stat) != 0) {
        fprintf(stderr, "ERROR: could not stat %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if ((uint64_t)file_stat.st_size != PRODUCT_UNIVERSE) {
        fprintf(
            stderr,
            "ERROR: %s is %" PRIu64 " bytes, expected %" PRIu64 "\n",
            filename,
            (uint64_t)file_stat.st_size,
            PRODUCT_UNIVERSE
        );
        exit(1);
    }
#ifdef MAP_POPULATE
    if ((uint64_t)file_stat.st_blocks * 512 >= PRODUCT_UNIVERSE) {
        mmap_flags |= MAP_POPULATE;
    }
#endif
    ranked_costs = mmap(NULL, (size_t)PRODUCT_UNIVERSE, PROT_READ, mmap_flags, ranked_cost_fd, 0);
    if (ranked_costs == MAP_FAILED) {
        fprintf(stderr, "ERROR: could not mmap %s: %s\n", filename, strerror(errno));
        exit(1);
    }
}

static void init_cube(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    const unsigned int face_size = CUBE_SIZE * CUBE_SIZE;

    if (strlen(kociemba) != face_size * 6) {
        fprintf(stderr, "ERROR: --kociemba must contain 294 stickers for a 7x7x7 cube\n");
        exit(1);
    }
    cube[0] = 'x';
    memcpy(&cube[1], &kociemba[0], face_size);                            /* U */
    memcpy(&cube[1 + face_size], &kociemba[face_size * 4], face_size);    /* L */
    memcpy(&cube[1 + face_size * 2], &kociemba[face_size * 2], face_size); /* F */
    memcpy(&cube[1 + face_size * 3], &kociemba[face_size], face_size);    /* R */
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

static int is_outer_x_center(unsigned int square)
{
    unsigned int face_offset = (square - 1) % (CUBE_SIZE * CUBE_SIZE);

    return face_offset == 8 || face_offset == 12 || face_offset == 36 || face_offset == 40;
}

static int is_oblique(unsigned int square)
{
    unsigned int face_offset = (square - 1) % (CUBE_SIZE * CUBE_SIZE);

    switch (face_offset) {
        case 9:
        case 10:
        case 11:
        case 15:
        case 19:
        case 22:
        case 26:
        case 29:
        case 33:
        case 37:
        case 38:
        case 39:
            return 1;
        default:
            return 0;
    }
}

static void recolor_cube(char cube[CUBE_ARRAY_SIZE])
{
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (is_edge_or_corner(square) || is_outer_x_center(square)) {
            cube[square] = '.';
        } else if (is_oblique(square)) {
            cube[square] = is_lr(cube[square]) ? 'L' : 'x';
        } else if (cube[square] == 'R') {
            cube[square] = 'L';
        } else if (cube[square] == 'D') {
            cube[square] = 'U';
        } else if (cube[square] == 'B') {
            cube[square] = 'F';
        }
    }
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

/*
 * One row per state along the solution. TRU is the true remaining distance,
 * which is what the matrix builder samples for each (UNPR, TBL) pair.
 */
static void print_ida_summary(const char cube[CUBE_ARRAY_SIZE], unsigned int length)
{
    char walk[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];

    memcpy(walk, cube, CUBE_ARRAY_SIZE);
    printf("\n       TBL UNPR  CTG  TRU  IDX\n      ==== ====  ===  ===  ===\n");
    for (unsigned int step = 0; step <= length; step++) {
        unsigned char centers_cost = centers_table_cost(walk);
        unsigned char unpaired = unpaired_oblique_count(walk);

        if (step) {
            printf("%5s ", move2str[solution[step - 1]]);
        } else {
            printf(" INIT ");
        }
        printf(
            " %4u %4u  %3u  %3u  %3u\n",
            centers_cost,
            unpaired,
            combined_cost(centers_cost, unpaired),
            length - step,
            step
        );
        if (step < length) {
            rotate_777_centers(walk, rotate_tmp, CUBE_ARRAY_SIZE, solution[step]);
        }
    }
    printf("\n");
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *ranked_filename = NULL;
    unsigned char min_threshold = 0;
    unsigned char max_threshold = DEFAULT_MAX_IDA_THRESHOLD;
    long detected_cpus = sysconf(_SC_NPROCESSORS_ONLN);
    unsigned int thread_count = detected_cpus > 0 ? (unsigned int)detected_cpus : 1;
    int print_summary = 0;
    char cube[CUBE_ARRAY_SIZE];

    if (thread_count > MAX_THREADS) {
        thread_count = MAX_THREADS;
    }
    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--ranked-UD-inner-centers-cost") && index + 1 < argc) {
            ranked_filename = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--threads") && index + 1 < argc) {
            thread_count = (unsigned int)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--unpaired-multiplier") && index + 1 < argc) {
            unpaired_multiplier = (float)atof(argv[++index]);
            use_unpaired_multiplier = 1;
        } else if (!strcmp(argv[index], "--multiplier") && index + 1 < argc) {
            cost_to_goal_multiplier = (float)atof(argv[++index]);
        } else if (!strcmp(argv[index], "--orbit0-need-odd-w")) {
            orbit0_requirement = PARITY_ODD;
        } else if (!strcmp(argv[index], "--orbit0-need-even-w")) {
            orbit0_requirement = PARITY_EVEN;
        } else if (!strcmp(argv[index], "--orbit1-need-odd-w")) {
            orbit1_requirement = PARITY_ODD;
        } else if (!strcmp(argv[index], "--orbit1-need-even-w")) {
            orbit1_requirement = PARITY_EVEN;
        } else if (!strcmp(argv[index], "--print-ida-summary")) {
            print_summary = 1;
        } else {
            usage(argv[0]);
            return 1;
        }
    }
    if (!kociemba || !ranked_filename || !thread_count || thread_count > MAX_THREADS ||
        min_threshold > max_threshold || max_threshold > MAX_IDA_THRESHOLD) {
        usage(argv[0]);
        return 1;
    }
    if (use_unpaired_multiplier && (unpaired_multiplier <= 0.0f || unpaired_multiplier > 1.0f)) {
        fprintf(stderr, "ERROR: --unpaired-multiplier must be in (0.0, 1.0]\n");
        return 1;
    }
    /* Below 1.0 would weaken the heuristic rather than inflate it. */
    if (cost_to_goal_multiplier && cost_to_goal_multiplier < 1.0f) {
        fprintf(stderr, "ERROR: --multiplier must be at least 1.0\n");
        return 1;
    }

    init_binom();
    init_move_tables();
    map_ranked_cost_file(ranked_filename);
    init_cube(cube, kociemba);
    recolor_cube(cube);
    printf("START\n");
    print_cube(cube, CUBE_SIZE);

    unsigned char initial_cost = cube_cost(cube, 0);
    if (initial_cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial ranked state is absent from the table\n");
        return 1;
    }
    if (use_unpaired_multiplier) {
        LOG("searching with unpaired multiplier %.2f\n", unpaired_multiplier);
    } else {
        LOG("searching with the empirical unpaired-count matrix\n");
    }
    LOG(
        "initial cost %u, unpaired obliques %u, threads %u\n",
        initial_cost,
        unpaired_oblique_count(cube),
        thread_count
    );
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
            char rotate_tmp[CUBE_ARRAY_SIZE];
            for (unsigned int index = 0; index < length; index++) {
                rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, solution[index]);
            }
            printf("END\n");
            print_cube(cube, CUBE_SIZE);
            munmap(ranked_costs, (size_t)PRODUCT_UNIVERSE);
            close(ranked_cost_fd);
            return 0;
        }
    }

    fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
    munmap(ranked_costs, (size_t)PRODUCT_UNIVERSE);
    close(ranked_cost_fd);
    return 1;
}
