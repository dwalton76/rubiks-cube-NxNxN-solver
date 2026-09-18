#include <inttypes.h>
#include <limits.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#include "ida_search_core.h"

#define CUBE_SIZE 4
#define CUBE_ARRAY_SIZE 97
#define PAIR_COUNT 12
#define EDGE_PAIRING_UNIVERSE UINT64_C(239500800)
#define CENTER_GROUP_SIZE 8
#define CENTER_GROUP_UNIVERSE UINT64_C(70)
#define CENTER_UNIVERSE UINT64_C(343000)
#define DEFAULT_MAX_THRESHOLD 24
#define MAX_THRESHOLD 40
#define PHASE2_EDGE_MAX 12
#define PHASE2_CENTER_MAX 9

/*
 * Combined heuristic matrix rebuilt by utils/build-444-heuristic-matrices.py
 * from 200 random cubes after replacing the LFRB-only graph with the exact
 * all-center table (58,800 reachable states in a 70^3 ranked universe).
 *
 * Temporarily unused: the searcher uses max(edge, center) only. Several cells
 * overestimate remaining length, so this table is not admissible.
 */
static const unsigned char phase2_cost_matrix_444[PHASE2_EDGE_MAX + 1][PHASE2_CENTER_MAX + 1] __attribute__((unused)) = {
    { 0,  1,  2,  3,  4,  5,  6,  7,  8,  9},  // edge cost 0
    { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9},  // edge cost 1
    { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9},  // edge cost 2
    { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9},  // edge cost 3
    { 4,  4,  4,  4,  4,  5,  6,  7,  8,  9},  // edge cost 4
    { 5,  5,  5,  5,  5,  5,  6,  7,  8,  9},  // edge cost 5
    { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9},  // edge cost 6
    { 7,  7,  7,  8,  8,  8,  8,  8, 12, 12},  // edge cost 7
    { 8,  8,  8,  8,  8,  8,  8,  8, 12, 12},  // edge cost 8
    { 9,  9,  9,  9,  9,  9,  9,  9, 12, 12},  // edge cost 9
    {10, 10, 10, 11, 11, 11, 11, 11, 12, 12},  // edge cost 10
    {11, 11, 11, 12, 12, 12, 12, 12, 12, 12},  // edge cost 11
    {12, 12, 13, 14, 14, 14, 14, 14, 14, 14},  // edge cost 12
};

void rotate_444(char *cube, char *cube_tmp, int array_size, move_type move);

/* Must match the dense-edge-pairing-cost-v1 metadata. */
static const unsigned int high_squares[PAIR_COUNT] = {
    15, 9, 2, 8, 95, 89, 82, 88, 24, 25, 56, 57,
};
static const unsigned int low_squares[PAIR_COUNT] = {
    14, 5, 3, 12, 94, 85, 83, 92, 28, 21, 60, 53,
};
static const unsigned int high_partners[PAIR_COUNT] = {
    35, 19, 67, 51, 78, 30, 46, 62, 37, 76, 69, 44,
};
static const unsigned int low_partners[PAIR_COUNT] = {
    34, 18, 66, 50, 79, 31, 47, 63, 41, 72, 73, 40,
};

/* Must match Build444Reduce333Centers ranked_cost_square_groups / dense-multiset-cost-v1. */
static const unsigned int ud_center_squares[CENTER_GROUP_SIZE] = {
    6, 7, 10, 11, 86, 87, 90, 91,
};
static const unsigned int lr_center_squares[CENTER_GROUP_SIZE] = {
    22, 23, 26, 27, 54, 55, 58, 59,
};
static const unsigned int fb_center_squares[CENTER_GROUP_SIZE] = {
    38, 39, 42, 43, 70, 71, 74, 75,
};

static unsigned char *edge_costs;
static int edge_cost_fd = -1;
static unsigned char *center_costs;
static int center_cost_fd = -1;
static unsigned int requested_solutions = 1;
static unsigned int min_threshold;
static unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
static int avoid_pll;
static atomic_uint found_solutions;
static atomic_int stop_search;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;
static char summary_root_cube[CUBE_ARRAY_SIZE];

struct worker {
    char cube[CUBE_ARRAY_SIZE];
    unsigned int threshold;
    uint64_t nodes;
    move_type path[MAX_THRESHOLD + 1];
};

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE --edge-pairing-cost FILE "
        "--center-cost FILE "
        "[--solution-count N] [--min-ida-threshold N] "
        "[--max-ida-threshold N] [--avoid-pll] [--print-rank]\n",
        program
    );
}

static unsigned int edge_id(char first, char second)
{
    unsigned int key;
    if (first > second) {
        char tmp = first;
        first = second;
        second = tmp;
    }
    key = ((unsigned int)(unsigned char)first << 8) | (unsigned char)second;

#define EDGE_KEY(a, b) (((unsigned int)(a) << 8) | (unsigned int)(b))
    switch (key) {
        case EDGE_KEY('B', 'U'): return 0;
        case EDGE_KEY('L', 'U'): return 1;
        case EDGE_KEY('R', 'U'): return 2;
        case EDGE_KEY('F', 'U'): return 3;
        case EDGE_KEY('B', 'L'): return 4;
        case EDGE_KEY('F', 'L'): return 5;
        case EDGE_KEY('B', 'R'): return 6;
        case EDGE_KEY('F', 'R'): return 7;
        case EDGE_KEY('B', 'D'): return 8;
        case EDGE_KEY('D', 'L'): return 9;
        case EDGE_KEY('D', 'R'): return 10;
        case EDGE_KEY('D', 'F'): return 11;
        default: return UINT_MAX;
    }
#undef EDGE_KEY
}

static uint64_t even_permutation_rank(const unsigned char permutation[PAIR_COUNT])
{
    unsigned char remaining[PAIR_COUNT];
    uint64_t rank = 0;
    unsigned int parity = 0;

    for (unsigned int index = 0; index < PAIR_COUNT; index++) {
        remaining[index] = (unsigned char)index;
    }
    for (unsigned int index = 0; index < PAIR_COUNT; index++) {
        unsigned int digit = 0;
        unsigned int remaining_count = PAIR_COUNT - index;

        while (digit < remaining_count && remaining[digit] != permutation[index]) {
            digit++;
        }
        if (digit == remaining_count) {
            return UINT64_MAX;
        }
        parity ^= digit & 1;
        if (index < PAIR_COUNT - 2) {
            rank = (rank * remaining_count) + digit;
        }
        memmove(&remaining[digit], &remaining[digit + 1], remaining_count - digit - 1);
    }
    return parity ? UINT64_MAX : rank;
}

static uint64_t edge_pairing_rank(const char cube[CUBE_ARRAY_SIZE])
{
    unsigned char low_position[PAIR_COUNT];
    unsigned char permutation[PAIR_COUNT];

    memset(low_position, 0xff, sizeof(low_position));
    for (unsigned int low = 0; low < PAIR_COUNT; low++) {
        unsigned int id = edge_id(cube[low_squares[low]], cube[low_partners[low]]);
        if (id >= PAIR_COUNT || low_position[id] != 0xff) {
            return UINT64_MAX;
        }
        low_position[id] = (unsigned char)low;
    }
    for (unsigned int high = 0; high < PAIR_COUNT; high++) {
        unsigned int id = edge_id(cube[high_squares[high]], cube[high_partners[high]]);
        if (id >= PAIR_COUNT || low_position[id] == 0xff) {
            return UINT64_MAX;
        }
        permutation[high] = low_position[id];
    }
    return even_permutation_rank(permutation);
}

static uint64_t center_rank(const char cube[CUBE_ARRAY_SIZE])
{
    uint64_t ranks[3];

    ranks[0] = ida_combination_rank_pair(
        cube, ud_center_squares, CENTER_GROUP_SIZE, 4, CENTER_GROUP_UNIVERSE, 'D', 'U');
    ranks[1] = ida_combination_rank_pair(
        cube, lr_center_squares, CENTER_GROUP_SIZE, 4, CENTER_GROUP_UNIVERSE, 'L', 'R');
    ranks[2] = ida_combination_rank_pair(
        cube, fb_center_squares, CENTER_GROUP_SIZE, 4, CENTER_GROUP_UNIVERSE, 'B', 'F');
    return ida_mixed_radix_rank(ranks, 3, CENTER_GROUP_UNIVERSE);
}

static unsigned char encoded_cost(const unsigned char *table, uint64_t rank, uint64_t universe)
{
    unsigned char encoded;

    if (rank >= universe) {
        return UINT8_MAX;
    }
    encoded = table[rank];
    if (!encoded) {
        return UINT8_MAX;
    }
    return encoded - 1;
}

static unsigned char heuristic(const char cube[CUBE_ARRAY_SIZE])
{
    unsigned char edge_cost = encoded_cost(edge_costs, edge_pairing_rank(cube), EDGE_PAIRING_UNIVERSE);
    unsigned char centers = encoded_cost(center_costs, center_rank(cube), CENTER_UNIVERSE);

    if (edge_cost == UINT8_MAX || centers == UINT8_MAX) {
        return UINT8_MAX;
    }
    /* Matrix temporarily disabled; max of the two exact tables is admissible. */
    return edge_cost > centers ? edge_cost : centers;
}

static int move_is_allowed(move_type move)
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
        case L:
        case L_PRIME:
        case R:
        case R_PRIME:
            return 0;
        default:
            return 1;
    }
}

static int move_follows(move_type previous, move_type move)
{
    if (previous == MOVE_NONE) {
        return 1;
    }
    return !steps_on_same_face_and_layer(previous, move) &&
           steps_on_same_face_in_order(previous, move) &&
           steps_on_opposite_faces_in_order(previous, move);
}

static void print_solution(const move_type path[MAX_THRESHOLD + 1], unsigned int depth)
{
    printf("SOLUTION (%u steps):", depth);
    for (unsigned int index = 0; index < depth; index++) {
        printf(" %s", move2str[path[index]]);
    }
    printf("\n");
    fflush(stdout);
}

static unsigned int solved_color(unsigned int square)
{
    static const char colors[] = {'U', 'L', 'F', 'R', 'B', 'D'};
    return (unsigned int)colors[(square - 1) / 16];
}

static unsigned int color_bit(char color)
{
    switch (color) {
        case 'U': return 1U << 0;
        case 'L': return 1U << 1;
        case 'F': return 1U << 2;
        case 'R': return 1U << 3;
        case 'B': return 1U << 4;
        case 'D': return 1U << 5;
        default: return 0;
    }
}

static unsigned int corner_id(char first, char second, char third)
{
    return color_bit(first) | color_bit(second) | color_bit(third);
}

static int permutation_is_even(const unsigned int *current, const unsigned int *target, unsigned int count)
{
    unsigned int permutation[PAIR_COUNT];
    unsigned int seen = 0;
    unsigned int parity = 0;

    for (unsigned int position = 0; position < count; position++) {
        unsigned int solved_position = 0;

        while (solved_position < count && target[solved_position] != current[position]) {
            solved_position++;
        }
        if (solved_position == count || (seen & (1U << solved_position))) {
            return 0;
        }
        seen |= 1U << solved_position;
        permutation[position] = solved_position;
    }
    for (unsigned int left = 0; left < count; left++) {
        for (unsigned int right = left + 1; right < count; right++) {
            parity ^= permutation[left] > permutation[right];
        }
    }
    return !parity;
}

static int reduction_has_pll_parity(const char cube[CUBE_ARRAY_SIZE])
{
    static const unsigned int corner_squares[8][3] = {
        {1, 17, 68}, {4, 52, 65}, {13, 20, 33}, {16, 36, 49},
        {81, 32, 45}, {84, 48, 61}, {93, 29, 80}, {96, 64, 77},
    };
    unsigned int current_edges[PAIR_COUNT];
    unsigned int target_edges[PAIR_COUNT];
    unsigned int current_corners[8];
    unsigned int target_corners[8];

    for (unsigned int index = 0; index < PAIR_COUNT; index++) {
        current_edges[index] = edge_id(cube[high_squares[index]], cube[high_partners[index]]);
        target_edges[index] = edge_id(
            (char)solved_color(high_squares[index]),
            (char)solved_color(high_partners[index])
        );
    }
    for (unsigned int index = 0; index < 8; index++) {
        const unsigned int *squares = corner_squares[index];

        current_corners[index] = corner_id(cube[squares[0]], cube[squares[1]], cube[squares[2]]);
        target_corners[index] = corner_id(
            (char)solved_color(squares[0]),
            (char)solved_color(squares[1]),
            (char)solved_color(squares[2])
        );
    }
    return permutation_is_even(current_edges, target_edges, PAIR_COUNT) !=
           permutation_is_even(current_corners, target_corners, 8);
}

static void print_ida_summary(const move_type path[MAX_THRESHOLD + 1], unsigned int length)
{
    char cube[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];

    memcpy(cube, summary_root_cube, sizeof(cube));
    printf("\n       EDGE  CTR  CTG  TRU  IDX\n");
    printf("       ====  ===  ===  ===  ===\n");
    for (unsigned int step = 0; step <= length; step++) {
        unsigned char edge = encoded_cost(edge_costs, edge_pairing_rank(cube), EDGE_PAIRING_UNIVERSE);
        unsigned char centers = encoded_cost(center_costs, center_rank(cube), CENTER_UNIVERSE);
        if (step) {
            printf("%5s ", move2str[path[step - 1]]);
        } else {
            printf(" INIT ");
        }
        printf(
            " %4u  %3u  %3u  %3u  %3u\n",
            edge,
            centers,
            edge > centers ? edge : centers,
            length - step,
            step
        );
        if (step < length) {
            rotate_444(cube, scratch, CUBE_ARRAY_SIZE, path[step]);
        }
    }
    printf("\n");
}

static int search(
    struct worker *worker,
    const char cube[CUBE_ARRAY_SIZE],
    unsigned int depth,
    unsigned int threshold,
    move_type previous)
{
    unsigned char cost = heuristic(cube);
    char child[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];

    worker->nodes++;
    if (atomic_load_explicit(&stop_search, memory_order_relaxed)) {
        return 1;
    }
    if (cost == UINT8_MAX || depth + cost > threshold) {
        return 0;
    }
    if (!cost) {
        if (depth == threshold) {
            if (avoid_pll && reduction_has_pll_parity(cube)) {
                return 0;
            }
            pthread_mutex_lock(&solution_lock);
            if (!atomic_load_explicit(&stop_search, memory_order_relaxed)) {
                print_solution(worker->path, depth);
                print_ida_summary(worker->path, depth);
                if (atomic_fetch_add_explicit(&found_solutions, 1, memory_order_relaxed) + 1 >= requested_solutions) {
                    atomic_store_explicit(&stop_search, 1, memory_order_relaxed);
                }
            }
            pthread_mutex_unlock(&solution_lock);
        }
        return atomic_load_explicit(&stop_search, memory_order_relaxed);
    }
    if (depth == threshold) {
        return 0;
    }

    for (unsigned int index = 0; index < MOVE_COUNT_444; index++) {
        move_type move = moves_444[index];
        if (!move_is_allowed(move) || !move_follows(previous, move)) {
            continue;
        }
        memcpy(child, cube, sizeof(child));
        rotate_444(child, scratch, CUBE_ARRAY_SIZE, move);
        worker->path[depth] = move;
        if (search(worker, child, depth + 1, threshold, move)) {
            return 1;
        }
    }
    return 0;
}

static void *search_worker(void *argument)
{
    struct worker *worker = argument;
    search(worker, worker->cube, 1, worker->threshold, worker->path[0]);
    return NULL;
}

static double elapsed_seconds(const struct timeval *start, const struct timeval *end)
{
    return (end->tv_sec - start->tv_sec) + (end->tv_usec - start->tv_usec) / 1000000.0;
}

static uint64_t search_threshold(
    const char cube[CUBE_ARRAY_SIZE],
    unsigned int threshold)
{
    pthread_t threads[MOVE_COUNT_444];
    struct worker workers[MOVE_COUNT_444];
    unsigned int thread_count = 0;
    uint64_t total_nodes = 1;

    atomic_store(&found_solutions, 0);
    atomic_store(&stop_search, 0);

    for (unsigned int index = 0; index < MOVE_COUNT_444; index++) {
        move_type move = moves_444[index];
        char scratch[CUBE_ARRAY_SIZE];
        struct worker *worker;

        if (!move_is_allowed(move)) {
            continue;
        }
        worker = &workers[thread_count];
        memset(worker, 0, sizeof(*worker));
        memcpy(worker->cube, cube, CUBE_ARRAY_SIZE);
        rotate_444(worker->cube, scratch, CUBE_ARRAY_SIZE, move);
        worker->threshold = threshold;
        worker->path[0] = move;
        if (pthread_create(&threads[thread_count], NULL, search_worker, worker) != 0) {
            fprintf(stderr, "ERROR: could not create search thread\n");
            exit(1);
        }
        thread_count++;
    }
    for (unsigned int index = 0; index < thread_count; index++) {
        pthread_join(threads[index], NULL);
        total_nodes += workers[index].nodes;
    }
    return total_nodes;
}

static void init_cube(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    ida_init_cube(cube, CUBE_SIZE, kociemba);
}

static void map_cost_file(const char *filename, uint64_t universe, int *fd, unsigned char **costs)
{
    struct mapped_cost_file mapped = ida_map_cost_file(filename, universe);

    *fd = mapped.fd;
    *costs = mapped.costs;
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *cost_filename = NULL;
    const char *center_cost_filename = NULL;
    int print_rank = 0;
    char cube[CUBE_ARRAY_SIZE];

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--edge-pairing-cost") && index + 1 < argc) {
            cost_filename = argv[++index];
        } else if (!strcmp(argv[index], "--center-cost") && index + 1 < argc) {
            center_cost_filename = argv[++index];
        } else if (!strcmp(argv[index], "--solution-count") && index + 1 < argc) {
            requested_solutions = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--avoid-pll")) {
            avoid_pll = 1;
        } else if (!strcmp(argv[index], "--print-rank")) {
            print_rank = 1;
        } else if (!strcmp(argv[index], "-h") || !strcmp(argv[index], "--help")) {
            usage(argv[0]);
            return 0;
        } else {
            fprintf(stderr, "ERROR: invalid argument %s\n", argv[index]);
            usage(argv[0]);
            return 1;
        }
    }
    if (!kociemba || !cost_filename || !center_cost_filename ||
        !requested_solutions || max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 1;
    }

    init_cube(cube, kociemba);
    map_cost_file(cost_filename, EDGE_PAIRING_UNIVERSE, &edge_cost_fd, &edge_costs);
    map_cost_file(center_cost_filename, CENTER_UNIVERSE, &center_cost_fd, &center_costs);
    memcpy(summary_root_cube, cube, sizeof(summary_root_cube));
    if (print_rank) {
        printf("EDGE_PAIRING_RANK %" PRIu64 "\n", edge_pairing_rank(cube));
        printf("CENTER_RANK %" PRIu64 "\n", center_rank(cube));
        printf("CENTER_EXACT_COST %u\n", encoded_cost(center_costs, center_rank(cube), CENTER_UNIVERSE));
        printf("HEURISTIC %u\n", heuristic(cube));
    }

    unsigned char initial_cost = heuristic(cube);
    if (initial_cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: cube is outside the phase 2 tables\n");
        return 1;
    }
    fprintf(stderr, "searching with max(edge, center); matrix disabled\n");
    if (!initial_cost) {
        move_type empty[MAX_THRESHOLD + 1] = {MOVE_NONE};
        print_solution(empty, 0);
        found_solutions = 1;
    }
    unsigned int first_threshold = initial_cost > min_threshold ? initial_cost : min_threshold;
    for (unsigned int threshold = first_threshold; initial_cost && threshold <= max_threshold; threshold++) {
        struct timeval start;
        struct timeval end;
        uint64_t nodes;
        double seconds;
        uint64_t nodes_per_sec;

        gettimeofday(&start, NULL);
        nodes = search_threshold(cube, threshold);
        gettimeofday(&end, NULL);
        seconds = elapsed_seconds(&start, &end);
        nodes_per_sec = seconds > 0.0 ? (uint64_t)(nodes / seconds) : 0;
        fprintf(
            stderr,
            "IDA threshold %u, explored %" PRIu64 " nodes, took %.3fs, %" PRIu64 " nodes-per-sec\n",
            threshold,
            nodes,
            seconds,
            nodes_per_sec
        );
        if (atomic_load(&stop_search)) {
            break;
        }
    }

    ida_unmap_cost_file(edge_cost_fd, edge_costs, EDGE_PAIRING_UNIVERSE);
    ida_unmap_cost_file(center_cost_fd, center_costs, CENTER_UNIVERSE);
    return atomic_load(&found_solutions) ? 0 : 1;
}
