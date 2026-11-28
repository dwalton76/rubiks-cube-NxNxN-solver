#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ida_search_core.h"

#define CUBE_SIZE 5
#define CUBE_ARRAY_SIZE 151
#define GROUP_SIZE 24
#define SELECTED_COUNT 8
#define GROUP_UNIVERSE UINT64_C(735471)
#define DEFAULT_MAX_THRESHOLD 20
#define MAX_THRESHOLD 40
#define SPLIT_DEPTH 3

static const unsigned int t_squares[GROUP_SIZE] = {
    8, 12, 14, 18, 33, 37, 39, 43, 58, 62, 64, 68,
    83, 87, 89, 93, 108, 112, 114, 118, 133, 137, 139, 143,
};
static const unsigned int x_squares[GROUP_SIZE] = {
    7, 9, 17, 19, 32, 34, 42, 44, 57, 59, 67, 69,
    82, 84, 92, 94, 107, 109, 117, 119, 132, 134, 142, 144,
};

static unsigned char *t_costs;
static unsigned char *x_costs;
static int t_fd = -1;
static int x_fd = -1;
static uint32_t t_move_bits[MOVE_COUNT_555][GROUP_SIZE];
static uint32_t x_move_bits[MOVE_COUNT_555][GROUP_SIZE];
static uint32_t t_move_chunks[MOVE_COUNT_555][3][256];
static uint32_t x_move_chunks[MOVE_COUNT_555][3][256];
static uint32_t rank_chunks[3][SELECTED_COUNT + 1][256];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
static unsigned int solution_limit = 1;
static unsigned int solution_count;
static int t_centers_only;

struct node {
    uint32_t t_mask;
    uint32_t x_mask;
};

/* A subtree below the first few moves, searched by one thread. */
struct task {
    struct node node;
    unsigned char cost;
    unsigned char depth;
    move_type prefix[SPLIT_DEPTH];
    move_type *solutions;
    unsigned int solution_count;
    unsigned int solution_capacity;
};

struct search_context {
    struct ida_ordered_tasks *tasks;
    struct task *task;
    size_t task_index;
    unsigned int threshold;
    move_type path[MAX_THRESHOLD + 1];
};

static struct task *tasks;
static size_t task_count;
static size_t task_capacity;

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE --t-center-cost FILE "
        "(--x-center-cost FILE | --t-centers-only) "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--solution-count N] [--threads N] "
        "[--print-ranks] [--print-legal-moves]\n",
        program
    );
}

/*
 * buildercore.multiset_rank order for eight lower symbols followed by sixteen higher symbols. Each
 * byte of the mask adds one table entry, indexed by how many selected squares the earlier bytes held.
 */
static void init_rank_chunks(void)
{
    for (unsigned int chunk = 0; chunk < 3; chunk++) {
        for (unsigned int start = 0; start <= SELECTED_COUNT; start++) {
            for (unsigned int value = 0; value < 256; value++) {
                unsigned int remaining = start;
                uint32_t rank = 0;

                for (unsigned int bit = 0; bit < 8; bit++) {
                    unsigned int after = GROUP_SIZE - (8 * chunk + bit) - 1;

                    if (value & (1U << bit)) {
                        if (remaining) {
                            remaining--;
                        }
                    } else if (remaining) {
                        rank += (uint32_t)binom[after][remaining - 1];
                    }
                }
                rank_chunks[chunk][start][value] = rank;
            }
        }
    }
}

/* The mask must hold exactly SELECTED_COUNT bits. */
static uint32_t combination_rank(uint32_t selected)
{
    unsigned int low = selected & 0xffU;
    unsigned int middle = (selected >> 8) & 0xffU;
    unsigned int remaining = SELECTED_COUNT - (unsigned int)__builtin_popcount(low);

    return rank_chunks[0][SELECTED_COUNT][low] +
        rank_chunks[1][remaining][middle] +
        rank_chunks[2][remaining - (unsigned int)__builtin_popcount(middle)][selected >> 16];
}

static uint32_t mask_from_cube(const char cube[CUBE_ARRAY_SIZE], const unsigned int squares[GROUP_SIZE])
{
    uint32_t mask = 0;

    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        char sticker = cube[squares[position]];

        if (sticker == 'L' || sticker == 'R') {
            mask |= UINT32_C(1) << position;
        }
    }
    return __builtin_popcount(mask) == SELECTED_COUNT ? mask : UINT32_MAX;
}

static uint32_t apply_move(uint32_t mask, const uint32_t chunks[3][256])
{
    return chunks[0][mask & 0xff] |
           chunks[1][(mask >> 8) & 0xff] |
           chunks[2][(mask >> 16) & 0xff];
}

static unsigned char table_cost(const unsigned char *costs, uint32_t rank)
{
    return rank < GROUP_UNIVERSE ? decode_cost_byte(costs[rank]) : UINT8_MAX;
}

static unsigned char heuristic(uint32_t t_rank, uint32_t x_rank)
{
    unsigned char t_cost = table_cost(t_costs, t_rank);
    unsigned char x_cost = t_centers_only ? 0 : table_cost(x_costs, x_rank);

    if (t_cost == UINT8_MAX || x_cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    return t_cost > x_cost ? t_cost : x_cost;
}

static int all_moves_allowed(move_type move)
{
    (void)move;
    return 1;
}

static void init_permutation(
    const unsigned int squares[GROUP_SIZE],
    uint32_t destination_bits[MOVE_COUNT_555][GROUP_SIZE])
{
    char marker[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];
    int square_to_position[CUBE_ARRAY_SIZE];

    for (unsigned int square = 0; square < CUBE_ARRAY_SIZE; square++) {
        marker[square] = (char)square;
        square_to_position[square] = -1;
    }
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        square_to_position[squares[position]] = (int)position;
    }
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        char moved[CUBE_ARRAY_SIZE];

        memcpy(moved, marker, sizeof(moved));
        rotate_555_centers(moved, scratch, CUBE_ARRAY_SIZE, moves_555[move_index]);
        for (unsigned int destination = 0; destination < GROUP_SIZE; destination++) {
            unsigned int source_square = (unsigned char)moved[squares[destination]];
            int source = source_square < CUBE_ARRAY_SIZE ? square_to_position[source_square] : -1;

            if (source < 0) {
                fprintf(stderr, "ERROR: center orbit is not closed under %s\n", move2str[moves_555[move_index]]);
                exit(1);
            }
            destination_bits[move_index][source] = UINT32_C(1) << destination;
        }
    }
}

static void init_move_chunks(
    const uint32_t bits[MOVE_COUNT_555][GROUP_SIZE],
    uint32_t chunks[MOVE_COUNT_555][3][256])
{
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        for (unsigned int chunk = 0; chunk < 3; chunk++) {
            for (unsigned int value = 0; value < 256; value++) {
                uint32_t transformed = 0;

                for (unsigned int bit = 0; bit < 8; bit++) {
                    if (value & (1U << bit)) {
                        transformed |= bits[move_index][chunk * 8 + bit];
                    }
                }
                chunks[move_index][chunk][value] = transformed;
            }
        }
    }
}

static unsigned char node_cost(const struct node *node)
{
    return heuristic(combination_rank(node->t_mask), t_centers_only ? 0 : combination_rank(node->x_mask));
}

static void node_apply_move(const struct node *node, unsigned int move_index, struct node *child)
{
    child->t_mask = apply_move(node->t_mask, t_move_chunks[move_index]);
    child->x_mask = t_centers_only ? 0 : apply_move(node->x_mask, x_move_chunks[move_index]);
}

static int record_solution(struct search_context *context)
{
    struct task *task = context->task;

    if (task->solution_count == task->solution_capacity) {
        unsigned int capacity = task->solution_capacity ? task->solution_capacity * 2 : 4;
        move_type *resized = realloc(task->solutions, (size_t)capacity * context->threshold * sizeof(move_type));

        if (!resized) {
            fprintf(stderr, "ERROR: could not allocate solutions\n");
            exit(1);
        }
        task->solutions = resized;
        task->solution_capacity = capacity;
    }
    memcpy(&task->solutions[(size_t)task->solution_count * context->threshold],
           context->path, context->threshold * sizeof(move_type));
    task->solution_count++;
    if (solution_limit && task->solution_count >= solution_limit) {
        ida_stop_tasks_after(context->tasks, context->task_index);
        return 1;
    }
    return 0;
}

/* The caller has already checked that depth + cost fits the threshold. */
static int search(
    struct search_context *context,
    const struct node *node,
    unsigned char cost,
    unsigned int depth,
    move_type previous)
{
    struct node children[IDA_MOVE_INDEX_MAX];
    uint32_t t_ranks[IDA_MOVE_INDEX_MAX];
    uint32_t x_ranks[IDA_MOVE_INDEX_MAX];
    unsigned int move_count = legal_move_count[previous];
    unsigned int threshold = context->threshold;

    if (!cost) {
        return depth == threshold ? record_solution(context) : 0;
    }
    if (depth >= threshold || ida_task_abandoned(context->tasks, context->task_index)) {
        return 0;
    }
    for (unsigned int legal = 0; legal < move_count; legal++) {
        node_apply_move(node, legal_move_index[previous][legal], &children[legal]);
        t_ranks[legal] = combination_rank(children[legal].t_mask);
        __builtin_prefetch(&t_costs[t_ranks[legal]]);
        if (!t_centers_only) {
            x_ranks[legal] = combination_rank(children[legal].x_mask);
            __builtin_prefetch(&x_costs[x_ranks[legal]]);
        }
    }
    for (unsigned int legal = 0; legal < move_count; legal++) {
        move_type move = moves_555[legal_move_index[previous][legal]];
        unsigned char child_cost = heuristic(t_ranks[legal], t_centers_only ? 0 : x_ranks[legal]);

        if (child_cost == UINT8_MAX || depth + 1 + child_cost > threshold) {
            continue;
        }
        context->path[depth] = move;
        if (search(context, &children[legal], child_cost, depth + 1, move)) {
            return 1;
        }
    }
    return 0;
}

static void add_task(const struct node *node, unsigned char cost, unsigned int depth, const move_type *prefix)
{
    struct task *task;

    if (task_count == task_capacity) {
        size_t capacity = task_capacity ? task_capacity * 2 : 1024;
        struct task *resized = realloc(tasks, capacity * sizeof(*tasks));

        if (!resized) {
            fprintf(stderr, "ERROR: could not allocate tasks\n");
            exit(1);
        }
        tasks = resized;
        task_capacity = capacity;
    }
    task = &tasks[task_count++];
    memset(task, 0, sizeof(*task));
    task->node = *node;
    task->cost = cost;
    task->depth = (unsigned char)depth;
    memcpy(task->prefix, prefix, depth * sizeof(move_type));
}

/* Walks the first SPLIT_DEPTH moves in search order, with the same pruning, and queues each subtree. */
static void split_tasks(const struct node *node, unsigned char cost, unsigned int depth, unsigned int split_depth,
                        unsigned int threshold, move_type previous, move_type *prefix)
{
    if (!cost || depth == split_depth || depth >= threshold) {
        add_task(node, cost, depth, prefix);
        return;
    }
    for (unsigned int legal = 0; legal < legal_move_count[previous]; legal++) {
        unsigned int move_index = legal_move_index[previous][legal];
        struct node child;
        unsigned char child_cost;

        node_apply_move(node, move_index, &child);
        child_cost = node_cost(&child);
        if (child_cost == UINT8_MAX || depth + 1 + child_cost > threshold) {
            continue;
        }
        prefix[depth] = moves_555[move_index];
        split_tasks(&child, child_cost, depth + 1, split_depth, threshold, moves_555[move_index], prefix);
    }
}

static void run_task(struct ida_ordered_tasks *ordered, size_t task_index)
{
    struct task *task = &tasks[task_index];
    struct search_context context;

    context.tasks = ordered;
    context.task = task;
    context.task_index = task_index;
    context.threshold = *(const unsigned int *)ordered->context;
    memcpy(context.path, task->prefix, task->depth * sizeof(move_type));
    search(&context, &task->node, task->cost, task->depth,
           task->depth ? task->prefix[task->depth - 1] : MOVE_NONE);
}

/* Prints solutions in single-threaded search order, stopping where that search would have stopped. */
static void print_solutions(unsigned int threshold)
{
    for (size_t task_index = 0; task_index < task_count; task_index++) {
        struct task *task = &tasks[task_index];

        for (unsigned int solution = 0; solution < task->solution_count; solution++) {
            const move_type *moves = &task->solutions[(size_t)solution * threshold];

            printf("SOLUTION (%u steps):", threshold);
            for (unsigned int index = 0; index < threshold; index++) {
                printf(" %s", move2str[moves[index]]);
            }
            printf("\n");
            solution_count++;
            if (solution_limit && solution_count >= solution_limit) {
                return;
            }
        }
    }
}

static void search_threshold(const struct node *root, unsigned char cost, unsigned int threshold,
                             unsigned int thread_count)
{
    struct ida_ordered_tasks ordered = {0};
    move_type prefix[SPLIT_DEPTH];

    split_tasks(root, cost, 0, SPLIT_DEPTH, threshold, MOVE_NONE, prefix);
    ordered.task_count = task_count;
    ordered.run = run_task;
    ordered.context = &threshold;
    ida_run_ordered_tasks(&ordered, thread_count);
    print_solutions(threshold);
    for (size_t task_index = 0; task_index < task_count; task_index++) {
        free(tasks[task_index].solutions);
    }
    task_count = 0;
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *t_filename = NULL;
    const char *x_filename = NULL;
    unsigned int min_threshold = 0;
    unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
    int print_ranks = 0;
    int print_legal_moves = 0;
    char cube[CUBE_ARRAY_SIZE];
    uint32_t t_mask;
    uint32_t x_mask;
    uint32_t t_rank;
    uint32_t x_rank;
    unsigned int thread_count = 0;
    struct node root;

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--t-center-cost") && index + 1 < argc) {
            t_filename = argv[++index];
        } else if (!strcmp(argv[index], "--x-center-cost") && index + 1 < argc) {
            x_filename = argv[++index];
        } else if (!strcmp(argv[index], "--t-centers-only")) {
            t_centers_only = 1;
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--solution-count") && index + 1 < argc) {
            solution_limit = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--threads") && index + 1 < argc) {
            thread_count = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--print-rank") || !strcmp(argv[index], "--print-ranks")) {
            print_ranks = 1;
        } else if (!strcmp(argv[index], "--print-legal-moves")) {
            print_legal_moves = 1;
        } else if (!strcmp(argv[index], "-h") || !strcmp(argv[index], "--help")) {
            usage(argv[0]);
            return 0;
        } else {
            fprintf(stderr, "ERROR: invalid argument %s\n", argv[index]);
            usage(argv[0]);
            return 2;
        }
    }
    if (!kociemba || !t_filename || (!t_centers_only && !x_filename) ||
            (t_centers_only && x_filename) ||
            min_threshold > max_threshold || max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 2;
    }

    init_binom();
    ida_init_move_tables(
        moves_555, MOVE_COUNT_555, all_moves_allowed,
        legal_move_count, legal_move_index, inverse_move
    );
    init_permutation(t_squares, t_move_bits);
    init_permutation(x_squares, x_move_bits);
    init_move_chunks(t_move_bits, t_move_chunks);
    init_move_chunks(x_move_bits, x_move_chunks);
    init_rank_chunks();
    ida_init_cube(cube, CUBE_SIZE, kociemba);
    t_mask = mask_from_cube(cube, t_squares);
    x_mask = t_centers_only ? 0 : mask_from_cube(cube, x_squares);
    if (t_mask == UINT32_MAX || (!t_centers_only && x_mask == UINT32_MAX)) {
        fprintf(
            stderr,
            "ERROR: %s center coordinate must contain eight L/R stickers\n",
            t_centers_only ? "the t" : "each"
        );
        return 1;
    }
    t_rank = combination_rank(t_mask);
    x_rank = t_centers_only ? 0 : combination_rank(x_mask);
    root.t_mask = t_mask;
    root.x_mask = x_mask;

    {
        struct mapped_cost_file mapped = ida_map_cost_file(t_filename, GROUP_UNIVERSE);
        t_fd = mapped.fd;
        t_costs = mapped.costs;
        if (!t_centers_only) {
            mapped = ida_map_cost_file(x_filename, GROUP_UNIVERSE);
            x_fd = mapped.fd;
            x_costs = mapped.costs;
        }
    }
    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_555[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }
    if (print_ranks) {
        printf(
            "T_RANK %" PRIu32 " T_COST %u X_RANK %" PRIu32 " X_COST %u COST %u\n",
            t_rank, table_cost(t_costs, t_rank),
            x_rank, t_centers_only ? 0 : table_cost(x_costs, x_rank),
            heuristic(t_rank, x_rank)
        );
    }

    unsigned char initial_cost = heuristic(t_rank, x_rank);
    if (initial_cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial state is absent from a ranked cost table\n");
        ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
        if (!t_centers_only) {
            ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
        }
        return 1;
    }
    if (min_threshold < initial_cost) {
        min_threshold = initial_cost;
    }
    /* solution-count zero means all solutions at the first solved threshold */
    for (unsigned int threshold = min_threshold; threshold <= max_threshold && !solution_count; threshold++) {
        search_threshold(&root, initial_cost, threshold, thread_count);
    }

    ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
    if (!t_centers_only) {
        ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
    }
    free(tasks);
    if (!solution_count) {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
        return 1;
    }
    return 0;
}
