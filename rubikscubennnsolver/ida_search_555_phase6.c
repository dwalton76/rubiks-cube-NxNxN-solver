#include <ctype.h>
#include <errno.h>
#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ida_search_core.h"

#define CUBE_ARRAY_SIZE 151
#define EDGE_GROUPS 3
#define EDGE_GROUP_SIZE 8
#define CENTER_GROUPS 4
#define EDGE_DELTA_UNIVERSE UINT64_C(20160)
#define EDGE_UNIVERSE UINT64_C(812851200)
#define CENTER_UNIVERSE UINT64_C(176400)
#define DEFAULT_MAX_THRESHOLD 20
#define MAX_THRESHOLD 40
#define ROOT_ID_SIZE 128
#define SPLIT_DEPTH 2

static const unsigned int edge_squares[EDGE_GROUPS][EDGE_GROUP_SIZE] = {
    {2, 24, 16, 10, 127, 149, 141, 135},
    {3, 23, 11, 15, 128, 148, 136, 140},
    {4, 22, 6, 20, 129, 147, 131, 145},
};
static const unsigned int edge_partners[EDGE_GROUPS][EDGE_GROUP_SIZE] = {
    {104, 54, 29, 79, 72, 122, 47, 97},
    {103, 53, 28, 78, 73, 123, 48, 98},
    {102, 52, 27, 77, 74, 124, 49, 99},
};
static const unsigned int center_squares[CENTER_GROUPS][EDGE_GROUP_SIZE] = {
    {32, 44, 82, 94, 0, 0, 0, 0},
    {57, 69, 107, 119, 0, 0, 0, 0},
    {7, 9, 17, 19, 132, 134, 142, 144},
    {8, 12, 14, 18, 133, 137, 139, 143},
};
static const unsigned int center_group_size[CENTER_GROUPS] = {4, 4, 8, 8};
static const unsigned int center_selected_count[CENTER_GROUPS] = {2, 2, 4, 4};
static const unsigned int center_radix[CENTER_GROUPS] = {6, 6, 70, 70};

struct coordinate {
    uint64_t edge_rank;
    uint32_t center_rank;
};

/* Edge labels at each position for the high wings, midges, and low wings, plus each center group's rank. */
struct node {
    uint8_t edges[EDGE_GROUPS][EDGE_GROUP_SIZE];
    uint8_t centers[CENTER_GROUPS];
};

struct root {
    char id[ROOT_ID_SIZE];
    struct coordinate coordinate;
    struct node node;
    unsigned char initial_cost;
};

/* A subtree below the first SPLIT_DEPTH moves, searched by one thread. */
struct task {
    size_t root_index;
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

static unsigned char *edge_costs;
static unsigned char *center_costs;
static int edge_fd = -1;
static int center_fd = -1;
static uint8_t edge_permutation[EDGE_GROUPS][MOVE_COUNT_555][EDGE_GROUP_SIZE];
static uint8_t edge_source[MOVE_COUNT_555][EDGE_GROUPS][EDGE_GROUP_SIZE];
static uint8_t center_transition[CENTER_GROUPS][70][MOVE_COUNT_555];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
static unsigned int solution_limit = 1;
static unsigned int solutions_found;
static int find_extra;
static struct root *roots;
static struct task *tasks;
static size_t task_count;
static size_t task_capacity;

static void usage(const char *program)
{
    printf(
        "usage: %s --roots-file FILE --edge-cost FILE --center-cost FILE "
        "[--min-ida-threshold N] [--max-ida-threshold N] "
        "[--solution-count N] [--find-extra] [--threads N] [--print-ranks] "
        "[--print-legal-moves] [--print-transitions]\n",
        program
    );
    printf("roots file: ID,EDGE_RANK,CENTER_RANK (one root per line; # comments allowed)\n");
}

static int move_is_allowed(move_type move)
{
    switch (move) {
        case Uw:
        case Uw_PRIME:
        case Uw2:
        case Dw:
        case Dw_PRIME:
        case Dw2:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Rw:
        case Rw_PRIME:
        case L:
        case L_PRIME:
        case R:
        case R_PRIME:
        case F:
        case F_PRIME:
        case B:
        case B_PRIME:
            return 0;
        default:
            return 1;
    }
}

static uint32_t factorial(unsigned int value)
{
    uint32_t result = 1;

    while (value > 1) {
        result *= value--;
    }
    return result;
}

static int permutation_unrank(uint32_t rank, uint8_t permutation[EDGE_GROUP_SIZE])
{
    uint8_t digits[EDGE_GROUP_SIZE] = {0};
    uint8_t remaining[EDGE_GROUP_SIZE] = {0, 1, 2, 3, 4, 5, 6, 7};
    unsigned int remaining_count = EDGE_GROUP_SIZE;

    if (rank >= factorial(EDGE_GROUP_SIZE)) {
        return 0;
    }
    for (int index = EDGE_GROUP_SIZE - 1; index >= 0; index--) {
        unsigned int radix = EDGE_GROUP_SIZE - (unsigned int)index;
        digits[index] = (uint8_t)(rank % radix);
        rank /= radix;
    }
    for (unsigned int position = 0; position < EDGE_GROUP_SIZE; position++) {
        unsigned int digit = digits[position];

        permutation[position] = remaining[digit];
        memmove(
            &remaining[digit],
            &remaining[digit + 1],
            (remaining_count - digit - 1) * sizeof(remaining[0])
        );
        remaining_count--;
    }
    return 1;
}

static int even_permutation_unrank(uint32_t rank, uint8_t permutation[EDGE_GROUP_SIZE])
{
    uint8_t digits[EDGE_GROUP_SIZE] = {0};
    uint8_t remaining[EDGE_GROUP_SIZE] = {0, 1, 2, 3, 4, 5, 6, 7};
    unsigned int remaining_count = EDGE_GROUP_SIZE;
    unsigned int parity = 0;

    if (rank >= EDGE_DELTA_UNIVERSE) {
        return 0;
    }
    for (int index = EDGE_GROUP_SIZE - 3; index >= 0; index--) {
        unsigned int radix = EDGE_GROUP_SIZE - (unsigned int)index;
        digits[index] = (uint8_t)(rank % radix);
        rank /= radix;
        parity += digits[index];
    }
    digits[EDGE_GROUP_SIZE - 2] = (uint8_t)(parity & 1U);
    for (unsigned int position = 0; position < EDGE_GROUP_SIZE; position++) {
        unsigned int digit = digits[position];

        permutation[position] = remaining[digit];
        memmove(
            &remaining[digit],
            &remaining[digit + 1],
            (remaining_count - digit - 1) * sizeof(remaining[0])
        );
        remaining_count--;
    }
    return 1;
}

static int edge_unrank(
    uint64_t rank,
    uint8_t high[EDGE_GROUP_SIZE],
    uint8_t midge[EDGE_GROUP_SIZE],
    uint8_t low[EDGE_GROUP_SIZE])
{
    uint8_t delta[EDGE_GROUP_SIZE];

    if (rank >= EDGE_UNIVERSE ||
            !permutation_unrank((uint32_t)(rank / EDGE_DELTA_UNIVERSE), high) ||
            !even_permutation_unrank((uint32_t)(rank % EDGE_DELTA_UNIVERSE), delta)) {
        return 0;
    }
    for (unsigned int position = 0; position < EDGE_GROUP_SIZE; position++) {
        midge[position] = (uint8_t)position;
        low[position] = high[delta[position]];
    }
    return 1;
}

/*
 * The rank relabels pieces so the midges read 0..7: the high wings rank as a permutation and the
 * low wings as an even permutation relative to the high wings. Lehmer digits come from popcounts
 * of the labels not yet used.
 */
static uint64_t node_edge_rank(const struct node *node)
{
    uint8_t midge_position[EDGE_GROUP_SIZE];
    uint8_t inverse_high[EDGE_GROUP_SIZE];
    unsigned int remaining = 0xFFU;
    unsigned int parity = 0;
    uint32_t high_rank = 0;
    uint32_t delta_rank = 0;

    for (unsigned int position = 0; position < EDGE_GROUP_SIZE; position++) {
        midge_position[node->edges[1][position]] = (uint8_t)position;
    }
    for (unsigned int position = 0; position < EDGE_GROUP_SIZE; position++) {
        unsigned int value = midge_position[node->edges[0][position]];

        inverse_high[value] = (uint8_t)position;
        high_rank = high_rank * (EDGE_GROUP_SIZE - position) +
            (unsigned int)__builtin_popcount(remaining & ((1U << value) - 1U));
        remaining ^= 1U << value;
    }
    remaining = 0xFFU;
    for (unsigned int position = 0; position < EDGE_GROUP_SIZE; position++) {
        unsigned int value = inverse_high[midge_position[node->edges[2][position]]];
        unsigned int digit = (unsigned int)__builtin_popcount(remaining & ((1U << value) - 1U));

        parity += digit;
        if (position < EDGE_GROUP_SIZE - 2) {
            delta_rank = delta_rank * (EDGE_GROUP_SIZE - position) + digit;
        }
        remaining ^= 1U << value;
    }
    if (parity & 1U) {
        return UINT64_MAX;
    }
    return (uint64_t)high_rank * EDGE_DELTA_UNIVERSE + delta_rank;
}

static uint8_t combination_rank(uint8_t mask, unsigned int size, unsigned int selected)
{
    uint64_t rank = 0;
    unsigned int remaining = selected;

    if (__builtin_popcount((unsigned int)mask) != selected) {
        return UINT8_MAX;
    }
    for (unsigned int position = 0; position < size; position++) {
        unsigned int after = size - position - 1;

        if (mask & (1U << position)) {
            remaining--;
        } else if (remaining) {
            rank += binom[after][remaining - 1];
        }
    }
    return remaining ? UINT8_MAX : (uint8_t)rank;
}

static uint8_t combination_unrank(uint64_t rank, unsigned int size, unsigned int selected)
{
    uint8_t mask = 0;
    unsigned int remaining = selected;

    if (rank >= binom[size][selected]) {
        return UINT8_MAX;
    }
    for (unsigned int position = 0; position < size && remaining; position++) {
        unsigned int after = size - position - 1;
        uint64_t selected_prefix = binom[after][remaining - 1];

        if (rank < selected_prefix) {
            mask |= (uint8_t)(1U << position);
            remaining--;
        } else {
            rank -= selected_prefix;
        }
    }
    return remaining ? UINT8_MAX : mask;
}

static void init_edge_permutations(void)
{
    char marker[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];

    for (unsigned int group = 0; group < EDGE_GROUPS; group++) {
        memset(marker, 0, sizeof(marker));
        marker[0] = 'x';
        for (unsigned int position = 0; position < EDGE_GROUP_SIZE; position++) {
            marker[edge_squares[group][position]] = (char)(position + 1);
            marker[edge_partners[group][position]] = (char)(position + 1);
        }
        for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
            char moved[CUBE_ARRAY_SIZE];

            if (!move_is_allowed(moves_555[move_index])) {
                continue;
            }
            memcpy(moved, marker, sizeof(moved));
            rotate_555(moved, scratch, CUBE_ARRAY_SIZE, moves_555[move_index]);
            for (unsigned int destination = 0; destination < EDGE_GROUP_SIZE; destination++) {
                unsigned int source = (unsigned char)moved[edge_squares[group][destination]];

                if (!source || source > EDGE_GROUP_SIZE) {
                    fprintf(stderr, "ERROR: edge group %u is not closed under %s\n",
                            group, move2str[moves_555[move_index]]);
                    exit(1);
                }
                edge_permutation[group][move_index][source - 1] = (uint8_t)destination;
                edge_source[move_index][group][destination] = (uint8_t)(source - 1);
            }
        }
    }
}

static void init_center_transitions(void)
{
    char marker[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];

    for (unsigned int group = 0; group < CENTER_GROUPS; group++) {
        int square_to_position[CUBE_ARRAY_SIZE];

        for (unsigned int square = 0; square < CUBE_ARRAY_SIZE; square++) {
            marker[square] = (char)square;
            square_to_position[square] = -1;
        }
        for (unsigned int position = 0; position < center_group_size[group]; position++) {
            square_to_position[center_squares[group][position]] = (int)position;
        }
        for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
            uint8_t permutation[EDGE_GROUP_SIZE] = {0};
            char moved[CUBE_ARRAY_SIZE];

            if (!move_is_allowed(moves_555[move_index])) {
                continue;
            }
            memcpy(moved, marker, sizeof(moved));
            rotate_555_centers(moved, scratch, CUBE_ARRAY_SIZE, moves_555[move_index]);
            for (unsigned int destination = 0; destination < center_group_size[group]; destination++) {
                unsigned int source_square = (unsigned char)moved[center_squares[group][destination]];
                int source = source_square < CUBE_ARRAY_SIZE ? square_to_position[source_square] : -1;

                if (source < 0) {
                    fprintf(stderr, "ERROR: center group %u is not closed under %s\n",
                            group, move2str[moves_555[move_index]]);
                    exit(1);
                }
                permutation[source] = (uint8_t)destination;
            }
            for (unsigned int rank = 0; rank < center_radix[group]; rank++) {
                uint8_t mask = combination_unrank(
                    rank, center_group_size[group], center_selected_count[group]
                );
                uint8_t child = 0;

                for (unsigned int source = 0; source < center_group_size[group]; source++) {
                    if (mask & (1U << source)) {
                        child |= (uint8_t)(1U << permutation[source]);
                    }
                }
                center_transition[group][rank][move_index] = combination_rank(
                    child, center_group_size[group], center_selected_count[group]
                );
            }
        }
    }
}

static void center_unrank(uint32_t rank, uint8_t groups[CENTER_GROUPS])
{
    for (int group = CENTER_GROUPS - 1; group >= 0; group--) {
        groups[group] = (uint8_t)(rank % center_radix[group]);
        rank /= center_radix[group];
    }
}

static uint32_t center_rank(const uint8_t groups[CENTER_GROUPS])
{
    uint32_t rank = 0;

    for (unsigned int group = 0; group < CENTER_GROUPS; group++) {
        rank = rank * center_radix[group] + groups[group];
    }
    return rank;
}

static int node_from_coordinate(const struct coordinate *coordinate, struct node *node)
{
    if (!edge_unrank(coordinate->edge_rank, node->edges[0], node->edges[1], node->edges[2])) {
        return 0;
    }
    center_unrank(coordinate->center_rank, node->centers);
    return 1;
}

static void node_apply_move(const struct node *node, unsigned int move_index, struct node *child)
{
    for (unsigned int group = 0; group < EDGE_GROUPS; group++) {
        const uint8_t *source = edge_source[move_index][group];

        for (unsigned int destination = 0; destination < EDGE_GROUP_SIZE; destination++) {
            child->edges[group][destination] = node->edges[group][source[destination]];
        }
    }
    for (unsigned int group = 0; group < CENTER_GROUPS; group++) {
        child->centers[group] = center_transition[group][node->centers[group]][move_index];
    }
}

static unsigned char max_cost(unsigned char edge, unsigned char center)
{
    if (edge == UINT8_MAX || center == UINT8_MAX) {
        return UINT8_MAX;
    }
    return edge > center ? edge : center;
}

static unsigned char node_cost(const struct node *node)
{
    uint64_t edge_rank = node_edge_rank(node);

    if (edge_rank == UINT64_MAX) {
        return UINT8_MAX;
    }
    return max_cost(decode_cost_byte(edge_costs[edge_rank]),
                    decode_cost_byte(center_costs[center_rank(node->centers)]));
}

static int record_solution(struct search_context *context)
{
    struct task *task = context->task;
    unsigned int cap = find_extra ? solution_limit : 1;

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
    if (cap && task->solution_count >= cap) {
        ida_stop_tasks_after(context->tasks, context->task_index);
        return 1;
    }
    return 0;
}

/*
 * The caller has already checked that depth + cost fits the threshold. Children are pruned on the
 * small center table before their edge rank is computed, and the edge-table bytes of every survivor
 * are prefetched before any is read.
 */
static int search(
    struct search_context *context,
    const struct node *node,
    unsigned char cost,
    unsigned int depth,
    move_type previous)
{
    struct node children[IDA_MOVE_INDEX_MAX];
    uint64_t edge_ranks[IDA_MOVE_INDEX_MAX];
    unsigned char center_child_costs[IDA_MOVE_INDEX_MAX];
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
        unsigned char center;

        node_apply_move(node, move_index, child);
        center = decode_cost_byte(center_costs[center_rank(child->centers)]);
        if (center == UINT8_MAX || depth + 1 + center > threshold) {
            continue;
        }
        edge_ranks[child_count] = node_edge_rank(child);
        if (edge_ranks[child_count] == UINT64_MAX) {
            continue;
        }
        __builtin_prefetch(&edge_costs[edge_ranks[child_count]]);
        center_child_costs[child_count] = center;
        child_moves[child_count] = (unsigned char)move_index;
        child_count++;
    }
    for (unsigned int index = 0; index < child_count; index++) {
        unsigned char child_cost = max_cost(decode_cost_byte(edge_costs[edge_ranks[index]]),
                                            center_child_costs[index]);
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

/* Walks the first SPLIT_DEPTH moves in search order, with the same pruning, and queues each subtree. */
static void split_tasks(size_t root_index, const struct node *node, unsigned char cost,
                        unsigned int depth, unsigned int threshold, move_type previous, move_type *prefix)
{
    if (!cost || depth == SPLIT_DEPTH || depth >= threshold) {
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
        split_tasks(root_index, &child, child_cost, depth + 1, threshold, moves_555[move_index], prefix);
    }
}

struct threshold_run {
    unsigned int threshold;
};

static void run_task(struct ida_ordered_tasks *ordered, size_t task_index)
{
    struct threshold_run *run = ordered->context;
    struct task *task = &tasks[task_index];
    struct search_context context;

    context.tasks = ordered;
    context.task = task;
    context.task_index = task_index;
    context.threshold = run->threshold;
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
            solutions_found++;
            if (!find_extra || (solution_limit && solutions_found >= solution_limit)) {
                return;
            }
        }
    }
}

static void free_tasks(void)
{
    for (size_t task_index = 0; task_index < task_count; task_index++) {
        free(tasks[task_index].solutions);
    }
    task_count = 0;
}

static void search_threshold(size_t root_count, unsigned int threshold, unsigned int thread_count)
{
    struct threshold_run run = {threshold};
    struct ida_ordered_tasks ordered = {0};
    move_type prefix[SPLIT_DEPTH];

    for (size_t index = 0; index < root_count; index++) {
        if (roots[index].initial_cost <= threshold) {
            split_tasks(index, &roots[index].node, roots[index].initial_cost, 0, threshold, MOVE_NONE, prefix);
        }
    }
    ordered.task_count = task_count;
    ordered.run = run_task;
    ordered.context = &run;
    ida_run_ordered_tasks(&ordered, thread_count);
    print_solutions(threshold);
    free_tasks();
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

static char *trim(char *value)
{
    char *end;

    while (isspace((unsigned char)*value)) {
        value++;
    }
    end = value + strlen(value);
    while (end > value && isspace((unsigned char)end[-1])) {
        *--end = '\0';
    }
    return value;
}

static int parse_rank(const char *value, uint64_t limit, uint64_t *rank)
{
    char *end;

    errno = 0;
    *rank = strtoull(value, &end, 10);
    while (isspace((unsigned char)*end)) {
        end++;
    }
    return !errno && end != value && !*end && *rank < limit;
}

static int parse_root_line(char *line, unsigned int line_number, struct root *root)
{
    char *first = strchr(line, ',');
    char *second = first ? strchr(first + 1, ',') : NULL;
    char *id;
    char *edge_text;
    char *center_text;
    uint64_t edge;
    uint64_t center;

    memset(root, 0, sizeof(*root));
    if (!first || !second || strchr(second + 1, ',')) {
        goto invalid;
    }
    *first = '\0';
    *second = '\0';
    id = trim(line);
    edge_text = trim(first + 1);
    center_text = trim(second + 1);
    if (!*id || strlen(id) >= sizeof(root->id) ||
            !parse_rank(edge_text, EDGE_UNIVERSE, &edge) ||
            !parse_rank(center_text, CENTER_UNIVERSE, &center)) {
        goto invalid;
    }
    strcpy(root->id, id);
    root->coordinate.edge_rank = edge;
    root->coordinate.center_rank = (uint32_t)center;
    return 1;

invalid:
    fprintf(
        stderr,
        "ERROR: roots file line %u must be ID,EDGE_RANK,CENTER_RANK with valid ranks\n",
        line_number
    );
    return 0;
}

static void load_roots(const char *filename, struct root **roots, size_t *root_count)
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
        char *content;

        line_number++;
        if (!strchr(line, '\n') && !feof(file)) {
            fprintf(stderr, "ERROR: roots file line %u is too long\n", line_number);
            fclose(file);
            exit(1);
        }
        hash = strchr(line, '#');
        if (hash) {
            *hash = '\0';
        }
        content = trim(line);
        if (!*content) {
            continue;
        }
        if (!parse_root_line(content, line_number, &root)) {
            fclose(file);
            exit(1);
        }
        append_root(roots, root_count, &capacity, &root);
    }
    fclose(file);
}

int main(int argc, char **argv)
{
    const char *roots_filename = NULL;
    const char *edge_filename = NULL;
    const char *center_filename = NULL;
    unsigned int min_threshold = 0;
    unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
    int print_ranks = 0;
    int print_legal_moves = 0;
    int print_transitions = 0;
    unsigned int thread_count = 0;
    size_t root_count = 0;

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--roots-file") && index + 1 < argc) {
            roots_filename = argv[++index];
        } else if (!strcmp(argv[index], "--edge-cost") && index + 1 < argc) {
            edge_filename = argv[++index];
        } else if (!strcmp(argv[index], "--center-cost") && index + 1 < argc) {
            center_filename = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--solution-count") && index + 1 < argc) {
            solution_limit = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--find-extra")) {
            find_extra = 1;
        } else if (!strcmp(argv[index], "--threads") && index + 1 < argc) {
            thread_count = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--print-rank") || !strcmp(argv[index], "--print-ranks")) {
            print_ranks = 1;
        } else if (!strcmp(argv[index], "--print-legal-moves")) {
            print_legal_moves = 1;
        } else if (!strcmp(argv[index], "--print-transitions")) {
            print_transitions = 1;
        } else if (!strcmp(argv[index], "-h") || !strcmp(argv[index], "--help")) {
            usage(argv[0]);
            return 0;
        } else {
            fprintf(stderr, "ERROR: invalid argument %s\n", argv[index]);
            usage(argv[0]);
            return 2;
        }
    }
    if (!roots_filename || !edge_filename || !center_filename ||
            min_threshold > max_threshold || max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 2;
    }

    init_binom();
    ida_init_move_tables(
        moves_555, MOVE_COUNT_555, move_is_allowed,
        legal_move_count, legal_move_index, inverse_move
    );
    init_edge_permutations();
    init_center_transitions();
    {
        struct mapped_cost_file mapped = ida_map_cost_file(edge_filename, EDGE_UNIVERSE);
        edge_fd = mapped.fd;
        edge_costs = mapped.costs;
        mapped = ida_map_cost_file(center_filename, CENTER_UNIVERSE);
        center_fd = mapped.fd;
        center_costs = mapped.costs;
    }
    load_roots(roots_filename, &roots, &root_count);
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
            if (!node_from_coordinate(&roots[index].coordinate, &roots[index].node)) {
                fprintf(stderr, "ERROR: root %s has an invalid edge rank\n", roots[index].id);
                return 1;
            }
            roots[index].initial_cost = node_cost(&roots[index].node);
            if (roots[index].initial_cost == UINT8_MAX) {
                fprintf(stderr, "ERROR: root %s is absent from a ranked cost table\n", roots[index].id);
                return 1;
            }
            if (print_ranks) {
                printf(
                    "ROOT %s EDGE_RANK %" PRIu64 " CENTER_RANK %" PRIu32 " COST %u\n",
                    roots[index].id,
                    roots[index].coordinate.edge_rank,
                    roots[index].coordinate.center_rank,
                    roots[index].initial_cost
                );
            }
            if (print_transitions) {
                for (unsigned int legal = 0; legal < legal_move_count[MOVE_NONE]; legal++) {
                    unsigned int move_index = legal_move_index[MOVE_NONE][legal];
                    struct node child;

                    node_apply_move(&roots[index].node, move_index, &child);
                    printf(
                        "TRANSITION ROOT %s MOVE %s EDGE_RANK %" PRIu64 " CENTER_RANK %" PRIu32 "\n",
                        roots[index].id,
                        move2str[moves_555[move_index]],
                        node_edge_rank(&child),
                        center_rank(child.centers)
                    );
                }
            }
            if (roots[index].initial_cost < cheapest) {
                cheapest = roots[index].initial_cost;
            }
        }
        if (min_threshold < cheapest) {
            min_threshold = cheapest;
        }
    }

    for (unsigned int threshold = min_threshold; threshold <= max_threshold && !solutions_found; threshold++) {
        search_threshold(root_count, threshold, thread_count);
    }

    ida_unmap_cost_file(edge_fd, edge_costs, EDGE_UNIVERSE);
    ida_unmap_cost_file(center_fd, center_costs, CENTER_UNIVERSE);
    free(tasks);
    free(roots);
    if (!solutions_found) {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
        return 1;
    }
    return 0;
}
