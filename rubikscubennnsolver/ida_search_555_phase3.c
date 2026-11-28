#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ida_search_core.h"

#define CUBE_SIZE 5
#define CUBE_ARRAY_SIZE 151
#define LR_GROUP_SIZE 8
#define LR_SELECTED 4
#define LR_GROUP_UNIVERSE 70
#define LR_UNIVERSE UINT64_C(4900)
#define OUTER_SIZE 24
#define OUTER_SELECTED 12
#define OUTER_UNIVERSE UINT64_C(2704156)
#define INNER_SIZE 12
#define INNER_UNIVERSE UINT64_C(4096)
#define DEFAULT_MAX_THRESHOLD 20
#define MAX_THRESHOLD 40
#define ROOT_ID_SIZE 128

static const unsigned int lr_t_squares[LR_GROUP_SIZE] = {
    33, 37, 39, 43, 83, 87, 89, 93,
};
static const unsigned int lr_x_squares[LR_GROUP_SIZE] = {
    32, 34, 42, 44, 82, 84, 92, 94,
};
static const unsigned int outer_squares[OUTER_SIZE] = {
    2, 4, 6, 10, 16, 20, 22, 24, 31, 35, 41, 45,
    81, 85, 91, 95, 127, 129, 131, 135, 141, 145, 147, 149,
};
static const unsigned int outer_partners[OUTER_SIZE] = {
    104, 102, 27, 79, 29, 77, 52, 54, 110, 56, 120, 66,
    60, 106, 70, 116, 72, 74, 49, 97, 47, 99, 124, 122,
};
static const unsigned int inner_squares[INNER_SIZE] = {
    3, 11, 15, 23, 36, 40, 86, 90, 128, 136, 140, 148,
};
static const unsigned int inner_partners[INNER_SIZE] = {
    103, 28, 78, 53, 115, 61, 65, 111, 73, 48, 98, 123,
};

#define OUTER_CHUNKS 3
#define INNER_CHUNKS 2
#define INNER_CHUNK_BITS 6
#define MAX_SPLIT_DEPTH 2
#define SPLIT_TARGET_TASKS 4096

struct node {
    uint32_t outer_mask;
    uint16_t inner_mask;
    uint8_t t_rank;
    uint8_t x_rank;
};

struct root {
    char id[ROOT_ID_SIZE];
    uint16_t lr_t_mask;
    uint16_t lr_x_mask;
    uint32_t outer_mask;
    uint16_t inner_mask;
    struct node node;
    unsigned char initial_cost;
};

/* A subtree below the first few moves of one root, searched by one thread. */
struct task {
    size_t root_index;
    struct node node;
    unsigned char cost;
    unsigned char depth;
    move_type prefix[MAX_SPLIT_DEPTH];
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

static unsigned char *lr_costs;
static unsigned char *outer_costs;
static unsigned char *inner_costs;
static int lr_fd = -1;
static int outer_fd = -1;
static int inner_fd = -1;
static uint16_t lr_t_move_bits[MOVE_COUNT_555][LR_GROUP_SIZE];
static uint16_t lr_x_move_bits[MOVE_COUNT_555][LR_GROUP_SIZE];
static uint32_t outer_move_bits[MOVE_COUNT_555][OUTER_SIZE];
static uint16_t inner_move_bits[MOVE_COUNT_555][INNER_SIZE];
static unsigned int inner_flip[MOVE_COUNT_555];
static uint8_t t_rank_next[LR_GROUP_UNIVERSE][MOVE_COUNT_555];
static uint8_t x_rank_next[LR_GROUP_UNIVERSE][MOVE_COUNT_555];
static uint32_t outer_chunk_bits[MOVE_COUNT_555][OUTER_CHUNKS][256];
static uint32_t outer_rank_chunk[OUTER_CHUNKS][OUTER_SELECTED + 1][256];
static uint16_t inner_chunk_bits[MOVE_COUNT_555][INNER_CHUNKS][1U << INNER_CHUNK_BITS];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
static unsigned int solution_limit = 1;
static unsigned int solution_count;
static struct root *roots;
static struct task *tasks;
static size_t task_count;
static size_t task_capacity;

static void usage(const char *program)
{
    printf(
        "usage: %s (--kociemba STATE | --roots-file FILE) "
        "--lr-center-cost FILE --eo-outer-cost FILE --eo-inner-cost FILE "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--solution-count N] [--threads N] "
        "[--print-ranks] [--print-legal-moves]\n",
        program
    );
    printf("roots file: ID,LR_RANK,OUTER_RANK,INNER_RANK (one root per line; # comments allowed)\n");
}

static int move_is_allowed(move_type move)
{
    switch (move) {
        case Uw:
        case Uw_PRIME:
        case Dw:
        case Dw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Rw:
        case Rw_PRIME:
            return 0;
        default:
            return 1;
    }
}

static uint64_t combination_rank_n(unsigned int mask, unsigned int group_size, unsigned int selected)
{
    uint64_t rank = 0;
    unsigned int remaining = selected;

    if (__builtin_popcount(mask) != (int)selected) {
        return UINT64_MAX;
    }
    for (unsigned int position = 0; position < group_size; position++) {
        unsigned int after = group_size - position - 1;

        if (mask & (1U << position)) {
            remaining--;
        } else if (remaining) {
            rank += binom[after][remaining - 1];
        }
    }
    return remaining ? UINT64_MAX : rank;
}

static unsigned int combination_unrank_n(
    uint64_t rank,
    unsigned int group_size,
    unsigned int selected,
    uint64_t universe)
{
    unsigned int mask = 0;
    unsigned int remaining = selected;

    if (rank >= universe) {
        return UINT_MAX;
    }
    for (unsigned int position = 0; position < group_size && remaining; position++) {
        unsigned int after = group_size - position - 1;
        uint64_t selected_prefix = binom[after][remaining - 1];

        if (rank < selected_prefix) {
            mask |= 1U << position;
            remaining--;
        } else {
            rank -= selected_prefix;
        }
    }
    return remaining ? UINT_MAX : mask;
}

static uint64_t lr_rank(uint16_t t_mask, uint16_t x_mask)
{
    uint64_t t_rank = combination_rank_n(t_mask, LR_GROUP_SIZE, LR_SELECTED);
    uint64_t x_rank = combination_rank_n(x_mask, LR_GROUP_SIZE, LR_SELECTED);

    if (t_rank >= LR_GROUP_UNIVERSE || x_rank >= LR_GROUP_UNIVERSE) {
        return UINT64_MAX;
    }
    return t_rank * LR_GROUP_UNIVERSE + x_rank;
}

static int lr_unrank(uint64_t rank, uint16_t *t_mask, uint16_t *x_mask)
{
    uint64_t t_rank;
    uint64_t x_rank;

    if (rank >= LR_UNIVERSE) {
        return 0;
    }
    t_rank = rank / LR_GROUP_UNIVERSE;
    x_rank = rank % LR_GROUP_UNIVERSE;
    *t_mask = (uint16_t)combination_unrank_n(t_rank, LR_GROUP_SIZE, LR_SELECTED, LR_GROUP_UNIVERSE);
    *x_mask = (uint16_t)combination_unrank_n(x_rank, LR_GROUP_SIZE, LR_SELECTED, LR_GROUP_UNIVERSE);
    return *t_mask != (uint16_t)UINT_MAX && *x_mask != (uint16_t)UINT_MAX;
}

static uint16_t mask8_from_cube(const char cube[CUBE_ARRAY_SIZE], const unsigned int squares[LR_GROUP_SIZE], char selected)
{
    uint16_t mask = 0;

    for (unsigned int position = 0; position < LR_GROUP_SIZE; position++) {
        if (cube[squares[position]] == selected) {
            mask |= (uint16_t)(1U << position);
        }
    }
    return __builtin_popcount((unsigned int)mask) == LR_SELECTED ? mask : UINT16_MAX;
}

static uint32_t outer_mask_from_cube(const char cube[CUBE_ARRAY_SIZE])
{
    uint32_t mask = 0;

    for (unsigned int position = 0; position < OUTER_SIZE; position++) {
        if (cube[outer_squares[position]] == 'D') {
            mask |= UINT32_C(1) << position;
        }
    }
    return __builtin_popcount(mask) == OUTER_SELECTED ? mask : UINT32_MAX;
}

static uint16_t inner_mask_from_cube(const char cube[CUBE_ARRAY_SIZE])
{
    uint16_t mask = 0;

    for (unsigned int position = 0; position < INNER_SIZE; position++) {
        if (cube[inner_squares[position]] == 'D') {
            mask |= (uint16_t)(1U << position);
        }
    }
    return mask;
}

static uint16_t apply_mask16(uint16_t mask, const uint16_t bits[], unsigned int flip, unsigned int width)
{
    uint16_t result = 0;

    while (mask) {
        unsigned int source = (unsigned int)__builtin_ctz((unsigned int)mask);
        result |= bits[source];
        mask &= (uint16_t)(mask - 1);
    }
    (void)width;
    return (uint16_t)(result ^ flip);
}

static uint32_t apply_mask32(uint32_t mask, const uint32_t bits[OUTER_SIZE])
{
    uint32_t result = 0;

    while (mask) {
        unsigned int source = (unsigned int)__builtin_ctz(mask);
        result |= bits[source];
        mask &= mask - 1;
    }
    return result;
}

static void init_center_permutation(
    const unsigned int squares[LR_GROUP_SIZE],
    uint16_t destination_bits[MOVE_COUNT_555][LR_GROUP_SIZE])
{
    char marker[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];
    int square_to_position[CUBE_ARRAY_SIZE];

    for (unsigned int square = 0; square < CUBE_ARRAY_SIZE; square++) {
        marker[square] = (char)square;
        square_to_position[square] = -1;
    }
    for (unsigned int position = 0; position < LR_GROUP_SIZE; position++) {
        square_to_position[squares[position]] = (int)position;
    }
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        char moved[CUBE_ARRAY_SIZE];

        if (!move_is_allowed(moves_555[move_index])) {
            continue;
        }
        memcpy(moved, marker, sizeof(moved));
        rotate_555_centers(moved, scratch, CUBE_ARRAY_SIZE, moves_555[move_index]);
        for (unsigned int destination = 0; destination < LR_GROUP_SIZE; destination++) {
            unsigned int source_square = (unsigned char)moved[squares[destination]];
            int source = source_square < CUBE_ARRAY_SIZE ? square_to_position[source_square] : -1;

            if (source < 0) {
                fprintf(stderr, "ERROR: LR center orbit is not closed under %s\n", move2str[moves_555[move_index]]);
                exit(1);
            }
            destination_bits[move_index][source] = (uint16_t)(1U << destination);
        }
    }
}

static void init_wing_permutation(
    const unsigned int squares[],
    const unsigned int partners[],
    unsigned int count,
    uint32_t destination_bits[][24],
    int use_outer)
{
    char marker[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];

    for (unsigned int square = 0; square < CUBE_ARRAY_SIZE; square++) {
        marker[square] = 0;
    }
    marker[0] = 'x';
    for (unsigned int position = 0; position < count; position++) {
        marker[squares[position]] = (char)(position + 1);
        marker[partners[position]] = (char)(position + 1);
    }
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        char moved[CUBE_ARRAY_SIZE];

        if (!move_is_allowed(moves_555[move_index])) {
            continue;
        }
        memcpy(moved, marker, sizeof(moved));
        rotate_555(moved, scratch, CUBE_ARRAY_SIZE, moves_555[move_index]);
        for (unsigned int destination = 0; destination < count; destination++) {
            unsigned char source_id = (unsigned char)moved[squares[destination]];
            int source = source_id ? (int)source_id - 1 : -1;

            if (source < 0 || (unsigned int)source >= count) {
                fprintf(stderr, "ERROR: edge orbit is not closed under %s\n", move2str[moves_555[move_index]]);
                exit(1);
            }
            if (use_outer) {
                destination_bits[move_index][source] = UINT32_C(1) << destination;
            } else {
                inner_move_bits[move_index][source] = (uint16_t)(1U << destination);
            }
        }
    }
}

/*
 * Moves act on one byte (outer) or six bits (inner) of a mask at a time, and the outer rank adds one
 * table entry per byte, indexed by how many selected wings the earlier bytes held.
 */
static void init_fast_tables(void)
{
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        if (!move_is_allowed(moves_555[move_index])) {
            continue;
        }
        for (unsigned int chunk = 0; chunk < OUTER_CHUNKS; chunk++) {
            for (unsigned int value = 0; value < 256; value++) {
                outer_chunk_bits[move_index][chunk][value] =
                    apply_mask32((uint32_t)value << (8 * chunk), outer_move_bits[move_index]);
            }
        }
        for (unsigned int chunk = 0; chunk < INNER_CHUNKS; chunk++) {
            for (unsigned int value = 0; value < (1U << INNER_CHUNK_BITS); value++) {
                inner_chunk_bits[move_index][chunk][value] = apply_mask16(
                    (uint16_t)(value << (INNER_CHUNK_BITS * chunk)), inner_move_bits[move_index], 0, INNER_SIZE
                );
            }
        }
        for (unsigned int rank = 0; rank < LR_GROUP_UNIVERSE; rank++) {
            uint16_t mask = (uint16_t)combination_unrank_n(rank, LR_GROUP_SIZE, LR_SELECTED, LR_GROUP_UNIVERSE);

            t_rank_next[rank][move_index] = (uint8_t)combination_rank_n(
                apply_mask16(mask, lr_t_move_bits[move_index], 0, LR_GROUP_SIZE), LR_GROUP_SIZE, LR_SELECTED
            );
            x_rank_next[rank][move_index] = (uint8_t)combination_rank_n(
                apply_mask16(mask, lr_x_move_bits[move_index], 0, LR_GROUP_SIZE), LR_GROUP_SIZE, LR_SELECTED
            );
        }
    }
    for (unsigned int chunk = 0; chunk < OUTER_CHUNKS; chunk++) {
        for (unsigned int start = 0; start <= OUTER_SELECTED; start++) {
            for (unsigned int value = 0; value < 256; value++) {
                unsigned int remaining = start;
                uint32_t rank = 0;

                for (unsigned int bit = 0; bit < 8; bit++) {
                    unsigned int after = OUTER_SIZE - (8 * chunk + bit) - 1;

                    if (value & (1U << bit)) {
                        if (remaining) {
                            remaining--;
                        }
                    } else if (remaining) {
                        rank += (uint32_t)binom[after][remaining - 1];
                    }
                }
                outer_rank_chunk[chunk][start][value] = rank;
            }
        }
    }
}

static uint32_t outer_rank(uint32_t mask)
{
    unsigned int low = mask & 0xFFU;
    unsigned int middle = (mask >> 8) & 0xFFU;
    unsigned int remaining = OUTER_SELECTED - (unsigned int)__builtin_popcount(low);

    return outer_rank_chunk[0][OUTER_SELECTED][low] +
        outer_rank_chunk[1][remaining][middle] +
        outer_rank_chunk[2][remaining - (unsigned int)__builtin_popcount(middle)][mask >> 16];
}

static void node_apply_move(const struct node *node, unsigned int move_index, struct node *child)
{
    uint32_t outer = node->outer_mask;
    unsigned int inner = node->inner_mask;

    child->t_rank = t_rank_next[node->t_rank][move_index];
    child->x_rank = x_rank_next[node->x_rank][move_index];
    child->outer_mask = outer_chunk_bits[move_index][0][outer & 0xFFU] |
        outer_chunk_bits[move_index][1][(outer >> 8) & 0xFFU] |
        outer_chunk_bits[move_index][2][outer >> 16];
    child->inner_mask = (uint16_t)((inner_chunk_bits[move_index][0][inner & 0x3FU] |
                                    inner_chunk_bits[move_index][1][inner >> INNER_CHUNK_BITS]) ^
                                   inner_flip[move_index]);
}

/* The LR and inner tables fit in L1, so they are checked before the 2.7 MB outer table. */
static unsigned char small_cost(const struct node *node)
{
    unsigned char lr = decode_cost_byte(lr_costs[node->t_rank * LR_GROUP_UNIVERSE + node->x_rank]);
    unsigned char inner = decode_cost_byte(inner_costs[node->inner_mask]);

    if (lr == UINT8_MAX || inner == UINT8_MAX) {
        return UINT8_MAX;
    }
    return lr > inner ? lr : inner;
}

static unsigned char max_cost(unsigned char small, unsigned char outer)
{
    if (small == UINT8_MAX || outer == UINT8_MAX) {
        return UINT8_MAX;
    }
    return small > outer ? small : outer;
}

static unsigned char node_cost(const struct node *node)
{
    return max_cost(small_cost(node), decode_cost_byte(outer_costs[outer_rank(node->outer_mask)]));
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
    uint32_t outer_ranks[IDA_MOVE_INDEX_MAX];
    unsigned char small_costs[IDA_MOVE_INDEX_MAX];
    unsigned char child_moves[IDA_MOVE_INDEX_MAX];
    unsigned int child_count = 0;
    unsigned int threshold = context->threshold;

    if (!cost) {
        return depth == threshold ? record_solution(context) : 0;
    }
    if (depth >= threshold || ida_task_abandoned(context->tasks, context->task_index)) {
        return 0;
    }
    for (unsigned int legal = 0; legal < legal_move_count[previous]; legal++) {
        unsigned int move_index = legal_move_index[previous][legal];
        struct node *child = &children[child_count];
        unsigned char small;

        node_apply_move(node, move_index, child);
        small = small_cost(child);
        if (small == UINT8_MAX || depth + 1 + small > threshold) {
            continue;
        }
        outer_ranks[child_count] = outer_rank(child->outer_mask);
        __builtin_prefetch(&outer_costs[outer_ranks[child_count]]);
        small_costs[child_count] = small;
        child_moves[child_count] = (unsigned char)move_index;
        child_count++;
    }
    for (unsigned int index = 0; index < child_count; index++) {
        unsigned char child_cost = max_cost(small_costs[index], decode_cost_byte(outer_costs[outer_ranks[index]]));
        move_type move = moves_555[child_moves[index]];

        if (child_cost == UINT8_MAX || depth + 1 + child_cost > threshold) {
            continue;
        }
        context->path[depth] = move;
        if (search(context, &children[index], child_cost, depth + 1, move)) {
            return 1;
        }
    }
    return 0;
}

static void add_task(size_t root_index, const struct node *node, unsigned char cost,
                     unsigned int depth, const move_type *prefix)
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
    task->root_index = root_index;
    task->node = *node;
    task->cost = cost;
    task->depth = (unsigned char)depth;
    memcpy(task->prefix, prefix, depth * sizeof(move_type));
}

/* Walks the first split_depth moves in search order, with the same pruning, and queues each subtree. */
static void split_tasks(size_t root_index, const struct node *node, unsigned char cost, unsigned int depth,
                        unsigned int split_depth, unsigned int threshold, move_type previous, move_type *prefix)
{
    if (!cost || depth == split_depth || depth >= threshold) {
        add_task(root_index, node, cost, depth, prefix);
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
        split_tasks(root_index, &child, child_cost, depth + 1, split_depth, threshold, moves_555[move_index], prefix);
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

            printf("SOLUTION ROOT %s (%u steps):", roots[task->root_index].id, threshold);
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

static void search_threshold(size_t root_count, unsigned int threshold, unsigned int thread_count)
{
    struct ida_ordered_tasks ordered = {0};
    move_type prefix[MAX_SPLIT_DEPTH];
    size_t active = 0;
    unsigned int split_depth = 0;

    for (size_t index = 0; index < root_count; index++) {
        active += roots[index].initial_cost <= threshold;
    }
    for (size_t estimate = active; estimate && estimate < SPLIT_TARGET_TASKS && split_depth < MAX_SPLIT_DEPTH;
            estimate *= 24) {
        split_depth++;
    }
    for (size_t index = 0; index < root_count; index++) {
        if (roots[index].initial_cost <= threshold) {
            split_tasks(index, &roots[index].node, roots[index].initial_cost, 0, split_depth, threshold,
                        MOVE_NONE, prefix);
        }
    }
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

static void append_root(struct root **roots, size_t *count, size_t *capacity, const struct root *root)
{
    if (*count == *capacity) {
        size_t new_capacity = *capacity ? *capacity * 2 : 64;
        struct root *resized = realloc(*roots, new_capacity * sizeof(**roots));

        if (!resized) {
            fprintf(stderr, "ERROR: could not allocate roots\n");
            exit(1);
        }
        *roots = resized;
        *capacity = new_capacity;
    }
    (*roots)[(*count)++] = *root;
}

static int parse_root_line(const char *line, unsigned int line_number, struct root *root)
{
    uint64_t lr;
    uint64_t outer;
    uint64_t inner;
    char trailing;

    memset(root, 0, sizeof(*root));
    if (sscanf(line, "%127[^,],%" SCNu64 ",%" SCNu64 ",%" SCNu64 " %c", root->id, &lr, &outer, &inner, &trailing) == 4) {
        if (!lr_unrank(lr, &root->lr_t_mask, &root->lr_x_mask)) {
            fprintf(stderr, "ERROR: roots file line %u has an invalid LR rank\n", line_number);
            return 0;
        }
        root->outer_mask = combination_unrank_n(outer, OUTER_SIZE, OUTER_SELECTED, OUTER_UNIVERSE);
        if (root->outer_mask == UINT_MAX) {
            fprintf(stderr, "ERROR: roots file line %u has an invalid outer rank\n", line_number);
            return 0;
        }
        if (inner >= INNER_UNIVERSE) {
            fprintf(stderr, "ERROR: roots file line %u has an invalid inner rank\n", line_number);
            return 0;
        }
        root->inner_mask = (uint16_t)inner;
        return 1;
    }
    fprintf(stderr, "ERROR: roots file line %u must be ID,LR_RANK,OUTER_RANK,INNER_RANK\n", line_number);
    return 0;
}

static void load_roots_file(const char *filename, struct root **roots, size_t *root_count)
{
    FILE *file = fopen(filename, "r");
    char line[512];
    size_t capacity = 0;
    unsigned int line_number = 0;

    if (!file) {
        fprintf(stderr, "ERROR: could not open roots file %s\n", filename);
        exit(1);
    }
    while (fgets(line, sizeof(line), file)) {
        struct root root;
        char *hash;

        line_number++;
        hash = strchr(line, '#');
        if (hash) {
            *hash = '\0';
        }
        if (line[0] == '\0' || line[0] == '\n') {
            continue;
        }
        if (!parse_root_line(line, line_number, &root)) {
            fclose(file);
            exit(1);
        }
        append_root(roots, root_count, &capacity, &root);
    }
    fclose(file);
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *roots_filename = NULL;
    const char *lr_filename = NULL;
    const char *outer_filename = NULL;
    const char *inner_filename = NULL;
    unsigned int min_threshold = 0;
    unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
    int print_ranks = 0;
    int print_legal_moves = 0;
    unsigned int thread_count = 0;
    size_t root_count = 0;
    char cube[CUBE_ARRAY_SIZE];

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--roots-file") && index + 1 < argc) {
            roots_filename = argv[++index];
        } else if (!strcmp(argv[index], "--lr-center-cost") && index + 1 < argc) {
            lr_filename = argv[++index];
        } else if (!strcmp(argv[index], "--eo-outer-cost") && index + 1 < argc) {
            outer_filename = argv[++index];
        } else if (!strcmp(argv[index], "--eo-inner-cost") && index + 1 < argc) {
            inner_filename = argv[++index];
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
    if ((kociemba && roots_filename) || (!kociemba && !roots_filename) ||
            !lr_filename || !outer_filename || !inner_filename ||
            min_threshold > max_threshold || max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 2;
    }

    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        if (moves_555[move_index] == L || moves_555[move_index] == L_PRIME) {
            inner_flip[move_index] = 562;
        } else if (moves_555[move_index] == R || moves_555[move_index] == R_PRIME) {
            inner_flip[move_index] = 1220;
        }
    }

    init_binom();
    ida_init_move_tables(
        moves_555, MOVE_COUNT_555, move_is_allowed,
        legal_move_count, legal_move_index, inverse_move
    );
    init_center_permutation(lr_t_squares, lr_t_move_bits);
    init_center_permutation(lr_x_squares, lr_x_move_bits);
    init_wing_permutation(outer_squares, outer_partners, OUTER_SIZE, outer_move_bits, 1);
    init_wing_permutation(inner_squares, inner_partners, INNER_SIZE, outer_move_bits, 0);
    init_fast_tables();

    {
        struct mapped_cost_file mapped = ida_map_cost_file(lr_filename, LR_UNIVERSE);
        lr_fd = mapped.fd;
        lr_costs = mapped.costs;
        mapped = ida_map_cost_file(outer_filename, OUTER_UNIVERSE);
        outer_fd = mapped.fd;
        outer_costs = mapped.costs;
        mapped = ida_map_cost_file(inner_filename, INNER_UNIVERSE);
        inner_fd = mapped.fd;
        inner_costs = mapped.costs;
    }

    if (roots_filename) {
        load_roots_file(roots_filename, &roots, &root_count);
    } else {
        struct root root;

        memset(&root, 0, sizeof(root));
        memcpy(root.id, "0", 2);
        ida_init_cube(cube, CUBE_SIZE, kociemba);
        root.lr_t_mask = mask8_from_cube(cube, lr_t_squares, 'L');
        root.lr_x_mask = mask8_from_cube(cube, lr_x_squares, 'L');
        root.outer_mask = outer_mask_from_cube(cube);
        root.inner_mask = inner_mask_from_cube(cube);
        if (root.lr_t_mask == UINT16_MAX || root.lr_x_mask == UINT16_MAX || root.outer_mask == UINT32_MAX) {
            fprintf(stderr, "ERROR: kociemba state is not a valid phase-3 coordinate\n");
            return 1;
        }
        {
            size_t capacity = 0;

            append_root(&roots, &root_count, &capacity, &root);
        }
    }
    if (!root_count) {
        fprintf(stderr, "ERROR: no roots to search\n");
        return 1;
    }

    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_555[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }

    {
        unsigned int cheapest = UINT8_MAX;

        for (size_t index = 0; index < root_count; index++) {
            struct node *node = &roots[index].node;

            node->t_rank = (uint8_t)combination_rank_n(roots[index].lr_t_mask, LR_GROUP_SIZE, LR_SELECTED);
            node->x_rank = (uint8_t)combination_rank_n(roots[index].lr_x_mask, LR_GROUP_SIZE, LR_SELECTED);
            node->outer_mask = roots[index].outer_mask;
            node->inner_mask = roots[index].inner_mask;
            roots[index].initial_cost = node_cost(node);
            if (roots[index].initial_cost == UINT8_MAX) {
                fprintf(stderr, "ERROR: root %s is absent from a ranked cost table\n", roots[index].id);
                return 1;
            }
            if (print_ranks) {
                printf(
                    "ROOT %s LR_RANK %" PRIu64 " OUTER_RANK %" PRIu64 " INNER_RANK %u COST %u\n",
                    roots[index].id,
                    lr_rank(roots[index].lr_t_mask, roots[index].lr_x_mask),
                    combination_rank_n(roots[index].outer_mask, OUTER_SIZE, OUTER_SELECTED),
                    roots[index].inner_mask,
                    roots[index].initial_cost
                );
            }
            if (roots[index].initial_cost < cheapest) {
                cheapest = roots[index].initial_cost;
            }
        }
        if (min_threshold < cheapest) {
            min_threshold = cheapest;
        }
    }

    for (unsigned int threshold = min_threshold; threshold <= max_threshold && !solution_count; threshold++) {
        search_threshold(root_count, threshold, thread_count);
    }

    ida_unmap_cost_file(lr_fd, lr_costs, LR_UNIVERSE);
    ida_unmap_cost_file(outer_fd, outer_costs, OUTER_UNIVERSE);
    ida_unmap_cost_file(inner_fd, inner_costs, INNER_UNIVERSE);
    free(tasks);
    free(roots);
    if (!solution_count) {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
        return 1;
    }
    return 0;
}
