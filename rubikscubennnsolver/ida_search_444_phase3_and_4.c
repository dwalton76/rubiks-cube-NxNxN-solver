#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

#include "ida_search_core.h"

#define CUBE_SIZE 4
#define CUBE_ARRAY_SIZE 97
#define PAIR_COUNT 12
#define EDGE_PAIRING_UNIVERSE UINT64_C(239500800)
#define CENTER_STATE_COUNT 840
#define CENTER_LEGAL_MOVE_COUNT 20
#define CENTER_ROW_SIZE (1 + (CENTER_LEGAL_MOVE_COUNT * 5))
#define CENTER_SOLVED_STATE 69
#define DEFAULT_MAX_THRESHOLD 24
#define MAX_THRESHOLD 40

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

static const unsigned int center_squares[24] = {
    6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43,
    54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91,
};
static const char center_targets[24] = {
    'U', 'U', 'U', 'U', 'L', 'L', 'L', 'L', 'F', 'F', 'F', 'F',
    'R', 'R', 'R', 'R', 'B', 'B', 'B', 'B', 'D', 'D', 'D', 'D',
};

static unsigned char *edge_costs;
static int edge_cost_fd = -1;
static unsigned char *center_graph;
static int center_graph_fd = -1;
static unsigned char center_distances[CENTER_STATE_COUNT];
static unsigned char move_column[MOVE_MAX];
static unsigned int requested_solutions = 1;
static unsigned int min_threshold;
static unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
static int avoid_pll;
static atomic_uint found_solutions;
static atomic_int stop_search;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;

struct worker {
    char cube[CUBE_ARRAY_SIZE];
    unsigned int center_state;
    unsigned int threshold;
    uint64_t nodes;
    move_type path[MAX_THRESHOLD + 1];
};

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE --edge-pairing-cost FILE "
        "--center-graph FILE --center-state-index N "
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

static unsigned char center_cost(const char cube[CUBE_ARRAY_SIZE])
{
    unsigned int misplaced = 0;
    for (unsigned int index = 0; index < 24; index++) {
        if (cube[center_squares[index]] != center_targets[index]) {
            misplaced++;
        }
    }
    return (unsigned char)((misplaced + 7) / 8);
}

static unsigned char heuristic(const char cube[CUBE_ARRAY_SIZE], unsigned int center_state)
{
    uint64_t rank = edge_pairing_rank(cube);
    unsigned char edge_cost;
    unsigned char centers;

    if (rank >= EDGE_PAIRING_UNIVERSE) {
        return UINT8_MAX;
    }
    edge_cost = edge_costs[rank];
    if (!edge_cost) {
        return UINT8_MAX;
    }
    edge_cost--;
    centers = center_cost(cube);
    if (center_state >= CENTER_STATE_COUNT) {
        return UINT8_MAX;
    }
    if (center_distances[center_state] > centers) {
        centers = center_distances[center_state];
    }
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

static unsigned int center_next_state(unsigned int state, move_type move)
{
    typedef uint32_t unaligned_u32 __attribute__((aligned(1), may_alias));
    unsigned char column = move_column[move];
    size_t offset;

    if (state >= CENTER_STATE_COUNT || column >= CENTER_LEGAL_MOVE_COUNT) {
        return UINT_MAX;
    }
    offset = ((size_t)state * CENTER_ROW_SIZE) + 1 + ((size_t)column * 5);
    return *(const unaligned_u32 *)(center_graph + offset);
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

static int search(
    struct worker *worker,
    const char cube[CUBE_ARRAY_SIZE],
    unsigned int center_state,
    unsigned int depth,
    unsigned int threshold,
    move_type previous)
{
    unsigned char cost = heuristic(cube, center_state);
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
        if (search(worker, child, center_next_state(center_state, move), depth + 1, threshold, move)) {
            return 1;
        }
    }
    return 0;
}

static void *search_worker(void *argument)
{
    struct worker *worker = argument;
    search(worker, worker->cube, worker->center_state, 1, worker->threshold, worker->path[0]);
    return NULL;
}

static uint64_t search_threshold(
    const char cube[CUBE_ARRAY_SIZE],
    unsigned int center_state,
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
        worker->center_state = center_next_state(center_state, move);
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

static void map_cost_file(const char *filename)
{
    struct mapped_cost_file mapped = ida_map_cost_file(filename, EDGE_PAIRING_UNIVERSE);

    edge_cost_fd = mapped.fd;
    edge_costs = mapped.costs;
}

static void map_center_graph(const char *filename)
{
    struct stat file_stat;
    unsigned int queue[CENTER_STATE_COUNT];
    unsigned int queue_start = 0;
    unsigned int queue_end = 0;

    center_graph_fd = open(filename, O_RDONLY);
    if (center_graph_fd < 0 || fstat(center_graph_fd, &file_stat) != 0) {
        fprintf(stderr, "ERROR: could not open %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if ((size_t)file_stat.st_size != CENTER_STATE_COUNT * CENTER_ROW_SIZE) {
        fprintf(stderr, "ERROR: center graph has unexpected size %jd\n", (intmax_t)file_stat.st_size);
        exit(1);
    }
    center_graph = mmap(NULL, file_stat.st_size, PROT_READ, MAP_SHARED, center_graph_fd, 0);
    if (center_graph == MAP_FAILED) {
        fprintf(stderr, "ERROR: could not mmap %s: %s\n", filename, strerror(errno));
        exit(1);
    }

    memset(center_distances, 0xff, sizeof(center_distances));
    center_distances[CENTER_SOLVED_STATE] = 0;
    queue[queue_end++] = CENTER_SOLVED_STATE;
    while (queue_start < queue_end) {
        unsigned int state = queue[queue_start++];
        for (unsigned int column = 0; column < CENTER_LEGAL_MOVE_COUNT; column++) {
            typedef uint32_t unaligned_u32 __attribute__((aligned(1), may_alias));
            size_t offset = ((size_t)state * CENTER_ROW_SIZE) + 1 + ((size_t)column * 5);
            unsigned int child = *(const unaligned_u32 *)(center_graph + offset);
            if (child >= CENTER_STATE_COUNT) {
                fprintf(stderr, "ERROR: center graph points outside its state space\n");
                exit(1);
            }
            if (center_distances[child] == UINT8_MAX) {
                center_distances[child] = center_distances[state] + 1;
                queue[queue_end++] = child;
            }
        }
    }
    if (queue_end != CENTER_STATE_COUNT) {
        fprintf(stderr, "ERROR: center graph reached only %u of %u states\n", queue_end, CENTER_STATE_COUNT);
        exit(1);
    }
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *cost_filename = NULL;
    const char *center_graph_filename = NULL;
    unsigned int center_state = UINT_MAX;
    int print_rank = 0;
    char cube[CUBE_ARRAY_SIZE];

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--edge-pairing-cost") && index + 1 < argc) {
            cost_filename = argv[++index];
        } else if (!strcmp(argv[index], "--center-graph") && index + 1 < argc) {
            center_graph_filename = argv[++index];
        } else if (!strcmp(argv[index], "--center-state-index") && index + 1 < argc) {
            center_state = (unsigned int)strtoul(argv[++index], NULL, 10);
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
    if (!kociemba || !cost_filename || !center_graph_filename ||
        center_state >= CENTER_STATE_COUNT || !requested_solutions ||
        max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 1;
    }

    init_cube(cube, kociemba);
    map_cost_file(cost_filename);
    unsigned char column = 0;
    memset(move_column, 0xff, sizeof(move_column));
    for (unsigned int index = 0; index < MOVE_COUNT_444; index++) {
        if (move_is_allowed(moves_444[index])) {
            move_column[moves_444[index]] = column++;
        }
    }
    if (column != CENTER_LEGAL_MOVE_COUNT) {
        fprintf(stderr, "ERROR: expected %u legal center moves, found %u\n", CENTER_LEGAL_MOVE_COUNT, column);
        return 1;
    }
    map_center_graph(center_graph_filename);
    if (print_rank) {
        printf("EDGE_PAIRING_RANK %" PRIu64 "\n", edge_pairing_rank(cube));
        printf("CENTER_COST %u\n", center_cost(cube));
        printf("CENTER_EXACT_COST %u\n", center_distances[center_state]);
        printf("HEURISTIC %u\n", heuristic(cube, center_state));
    }

    unsigned char initial_cost = heuristic(cube, center_state);
    if (initial_cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: cube is outside the all-edge pairing table\n");
        return 1;
    }
    if (!initial_cost) {
        move_type empty[MAX_THRESHOLD + 1] = {MOVE_NONE};
        print_solution(empty, 0);
        found_solutions = 1;
    }
    unsigned int first_threshold = initial_cost > min_threshold ? initial_cost : min_threshold;
    for (unsigned int threshold = first_threshold; initial_cost && threshold <= max_threshold; threshold++) {
        uint64_t nodes = search_threshold(cube, center_state, threshold);
        if (atomic_load(&stop_search)) {
            break;
        }
        fprintf(
            stderr, "threshold %u searched %" PRIu64 " nodes, found %u solutions\n",
            threshold, nodes, atomic_load(&found_solutions)
        );
    }

    ida_unmap_cost_file(edge_cost_fd, edge_costs, EDGE_PAIRING_UNIVERSE);
    munmap(center_graph, CENTER_STATE_COUNT * CENTER_ROW_SIZE);
    close(center_graph_fd);
    return atomic_load(&found_solutions) ? 0 : 1;
}
