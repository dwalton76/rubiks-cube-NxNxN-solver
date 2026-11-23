#include <inttypes.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/time.h>

#include "goal_ball_555.h"
#include "ida_search_core.h"
#include "lr_joint_555.h"

#define CUBE_SIZE 5
#define CUBE_ARRAY_SIZE 151
#define GROUP_SIZE 24
#define GROUP_MASK UINT32_C(0xFFFFFF)
#define GROUP_UNIVERSE UINT64_C(9465511770)
#define DEFAULT_MAX_THRESHOLD 24
#define MAX_THRESHOLD 40
#define SEARCH_THREADS 22
#define MAX_SEARCH_THREADS 256
#define PARITY_UNSET 0
#define PARITY_ODD 1
#define PARITY_EVEN 2

/* Square order matches t_centers_without_middles_555 and x_centers_without_middles_555.
 * Symbols are the sorted FLU order used by the ranked builders: F=0, L=1, U=2. */
static const unsigned int t_squares[GROUP_SIZE] = {
    8, 12, 14, 18, 33, 37, 39, 43, 58, 62, 64, 68,
    83, 87, 89, 93, 108, 112, 114, 118, 133, 137, 139, 143,
};
static const unsigned int x_squares[GROUP_SIZE] = {
    7, 9, 17, 19, 32, 34, 42, 44, 57, 59, 67, 69,
    82, 84, 92, 94, 107, 109, 117, 119, 132, 134, 142, 144,
};

/* One 24-bit mask per FLU symbol for each orbit; bit i is position i of t_squares or x_squares.
 * A move is three table reads per mask (lr_joint_555.h), and the joint table and goal ball key on
 * these masks directly. */
struct centers {
    uint32_t t[3];
    uint32_t x[3];
};

struct child {
    struct centers state;
    uint64_t cells[3];
    uint32_t t_rank;
    move_type move;
    unsigned char parity;
    unsigned char cost;
    unsigned char axis;
};

struct worker {
    unsigned int threshold;
    uint64_t nodes;
    unsigned int max_depth;
    move_type path[MAX_THRESHOLD + 1];
};

/* Two-move prefixes, so the pool has far more tasks than threads. */
struct root_task {
    unsigned char first;
    unsigned char second;
};

static unsigned char *t_costs;
static unsigned char *x_costs;
static int t_fd = -1;
static int x_fd = -1;
/* Optional joint LR t+x table from build-555-lr-joint. Enabled by --lr-joint-cost, which also
 * makes the t/x tables optional; t_costs and x_costs stay NULL when they are not given.
 * --lr-joint-parity-cost loads the parity-aware 6-bit file instead (build-555-lr-joint --parity). */
static const unsigned char *joint_cells;
static uint64_t joint_bytes;
static int joint_fd = -1;
static int joint_enabled;
static int joint_parity_aware;
static const char *joint_axis_name[3] = {"L", "U", "F"};
/* Optional goal ball from build-555-goal-ball (--goal-ball). At threshold T the forward search stops at
 * depth T - ball_depth and the ball decides the rest exactly, including the parity. */
static const unsigned char *ball_file;
static const uint64_t *ball_slots;
static uint64_t ball_bytes;
static int ball_fd = -1;
static int ball_enabled;
static unsigned int ball_depth;
static unsigned int ball_slots_log2;
static unsigned int root_horizon;
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
/* rank_offset[F left][L left][U left][symbol]: lexicographic permutations skipped by placing symbol next. */
static uint64_t rank_offset[9][9][9][3];
static char start_cube[CUBE_ARRAY_SIZE];
static unsigned int search_threads = SEARCH_THREADS;
static unsigned int solution_limit = 1;
static unsigned int solution_count;
static unsigned char parity_requirement;
static struct root_task root_tasks[MOVE_COUNT_555 * MOVE_COUNT_555];
static unsigned int root_task_count;
static unsigned int root_threshold;
static struct centers root_state;
static atomic_int stop_search;
static atomic_uint next_root_task;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE [--t-center-cost FILE --x-center-cost FILE] "
        "[--lr-joint-cost FILE | --lr-joint-parity-cost FILE] (the t/x pair, a joint table, or both) "
        "[--goal-ball FILE] "
        "[--orbit0-need-even-w | --orbit0-need-odd-w] "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--solution-count N] [--threads N] "
        "[--print-ranks] [--print-legal-moves]\n",
        program
    );
}

/* buildercore.multiset_rank for symbols FLU and counts 8, 8, 8. */
static uint64_t multiset_rank_flu(const unsigned char symbols[GROUP_SIZE])
{
    unsigned int remaining[3] = {8, 8, 8};
    uint64_t permutations = GROUP_UNIVERSE;
    uint64_t rank = 0;

    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        unsigned int slots = GROUP_SIZE - position;
        unsigned int symbol = symbols[position];

        if (symbol > 2 || !remaining[symbol]) {
            return UINT64_MAX;
        }
        for (unsigned int smaller = 0; smaller < symbol; smaller++) {
            rank += permutations * remaining[smaller] / slots;
        }
        permutations = permutations * remaining[symbol] / slots;
        remaining[symbol]--;
    }
    return rank;
}

static void init_rank_offsets(void)
{
    static uint64_t multinomial[9][9][9];

    for (unsigned int f = 0; f <= 8; f++) {
        for (unsigned int l = 0; l <= 8; l++) {
            for (unsigned int u = 0; u <= 8; u++) {
                uint64_t count = 0;

                if (!f && !l && !u) {
                    count = 1;
                } else {
                    count += f ? multinomial[f - 1][l][u] : 0;
                    count += l ? multinomial[f][l - 1][u] : 0;
                    count += u ? multinomial[f][l][u - 1] : 0;
                }
                multinomial[f][l][u] = count;
                rank_offset[f][l][u][0] = 0;
                rank_offset[f][l][u][1] = f ? multinomial[f - 1][l][u] : 0;
                rank_offset[f][l][u][2] = rank_offset[f][l][u][1] + (l ? multinomial[f][l - 1][u] : 0);
            }
        }
    }
}

/* Same value as multiset_rank_flu for a valid 8/8/8 state given as FLU masks, without the divisions. */
static inline uint64_t fast_rank_flu(const uint32_t masks[3])
{
    unsigned int remaining[3] = {8, 8, 8};
    uint64_t rank = 0;

    for (unsigned int position = 0; position < GROUP_SIZE - 1; position++) {
        unsigned int symbol = ((masks[1] >> position) & 1) | (((masks[2] >> position) & 1) << 1);

        rank += rank_offset[remaining[0]][remaining[1]][remaining[2]][symbol];
        remaining[symbol]--;
    }
    return rank;
}

static int axis_symbol(char sticker)
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
            return -1;
    }
}

static int state_from_cube(
    const char cube[CUBE_ARRAY_SIZE],
    const unsigned int squares[GROUP_SIZE],
    unsigned char symbols[GROUP_SIZE])
{
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        int symbol = axis_symbol(cube[squares[position]]);

        if (symbol < 0) {
            return 0;
        }
        symbols[position] = (unsigned char)symbol;
    }
    return multiset_rank_flu(symbols) < GROUP_UNIVERSE;
}

static int centers_from_cube(const char cube[CUBE_ARRAY_SIZE], struct centers *state)
{
    unsigned char t_symbols[GROUP_SIZE];
    unsigned char x_symbols[GROUP_SIZE];

    if (!state_from_cube(cube, t_squares, t_symbols) || !state_from_cube(cube, x_squares, x_symbols)) {
        return 0;
    }
    lrj_symbol_masks(t_symbols, state->t);
    lrj_symbol_masks(x_symbols, state->x);
    return 1;
}

static int move_is_allowed(move_type move)
{
    (void)move;
    return 1;
}

/* Shared with the parity-aware table builder, so the search and the table agree on parity. */
static unsigned char move_parity(move_type move)
{
    return lrj_move_parity(move);
}

/* moves_555 index order is lr_joint_555.h's move order, so its mask tables apply here. */
static inline void apply_move(const struct centers *state, struct centers *child, unsigned int move_index)
{
    child->t[1] = lrj_apply_t(move_index, state->t[1]);
    child->t[2] = lrj_apply_t(move_index, state->t[2]);
    child->t[0] = ~(child->t[1] | child->t[2]) & GROUP_MASK;
    child->x[1] = lrj_apply_x(move_index, state->x[1]);
    child->x[2] = lrj_apply_x(move_index, state->x[2]);
    child->x[0] = ~(child->x[1] | child->x[2]) & GROUP_MASK;
}

static inline int same_centers(const struct centers *a, const struct centers *b)
{
    return a->t[1] == b->t[1] && a->t[2] == b->t[2] && a->x[1] == b->x[1] && a->x[2] == b->x[2];
}

/* An outer turn cycles one face. When that face is already one color, both center
 * coordinates and the parity bit stay put, and the branch is the same state a ply deeper. */
static int move_is_center_noop(
    const struct centers *before,
    const struct centers *after,
    unsigned char parity_before,
    unsigned char parity_after)
{
    /* With no wing-parity goal, a wide quarter that only flips parity is the same center state. */
    if (parity_requirement != PARITY_UNSET && parity_before != parity_after) {
        return 0;
    }
    return same_centers(before, after);
}

/* A table that was not loaded (joint-only mode) gives no bound. */
static unsigned char table_cost(const unsigned char *costs, uint64_t rank)
{
    if (!costs) {
        return 0;
    }
    return rank < GROUP_UNIVERSE ? decode_cost_byte(costs[rank]) : UINT8_MAX;
}

static unsigned char parity_floor(unsigned char parity)
{
    if ((parity_requirement == PARITY_ODD && !parity) ||
            (parity_requirement == PARITY_EVEN && parity)) {
        return 1;
    }
    return 0;
}

static int parity_is_goal(unsigned char parity)
{
    if (parity_requirement == PARITY_UNSET) {
        return 1;
    }
    return (parity_requirement == PARITY_ODD && parity) ||
           (parity_requirement == PARITY_EVEN && !parity);
}

#define REMAINING_PARITY_ANY 2

/* Parity (0 even, 1 odd) the rest of the path must have, given the parity played so far,
 * or REMAINING_PARITY_ANY when no orbit-0 OLL parity is required. */
static unsigned int remaining_parity(unsigned char parity)
{
    if (parity_requirement == PARITY_UNSET) {
        return REMAINING_PARITY_ANY;
    }
    return (unsigned int)((parity_requirement == PARITY_ODD ? 1 : 0) ^ parity);
}

/* Bound from one joint table cell. An unseen cell gives no bound, so partial tables stay admissible.
 * The parity-aware table adds 1 when the cell has no flag for the remaining parity. */
static inline unsigned int joint_axis_bound(uint64_t cell, unsigned int need_parity)
{
    unsigned int entry;
    unsigned int nibble;
    unsigned int bound;

    if (!joint_parity_aware) {
        nibble = lrj_nibble_get(joint_cells, cell);
        return nibble ? nibble - 1 : 0;
    }
    entry = lrj_parity_get(joint_cells, cell);
    nibble = entry & 15;
    bound = nibble ? nibble - 1 : 0;
    if (nibble && need_parity != REMAINING_PARITY_ANY && !((entry >> (4 + need_parity)) & 1)) {
        bound++;
    }
    return bound;
}

static inline void joint_prefetch(uint64_t cell)
{
    __builtin_prefetch(joint_cells + (joint_parity_aware ? cell * LRJ_PARITY_BITS / 8 : cell >> 1));
}

/* Largest bound from the joint LR table over the L, U, and F axes, or UINT8_MAX as soon as one axis
 * exceeds budget. One axis alone prunes most search calls, so first_axis is read first and the other
 * two reads, which land far apart in the table, are only issued (together) when it does not prune.
 * *axis_out is the axis that pruned, or the axis with the largest bound when none did. */
static unsigned char joint_cost_from(
    const struct centers *state,
    unsigned int budget,
    unsigned int need_parity,
    unsigned int first_axis,
    unsigned int *axis_out)
{
    unsigned int cost = joint_axis_bound(lrj_axis_cell_from_masks(first_axis, state->t, state->x), need_parity);
    unsigned int best_axis = first_axis;
    uint64_t cells[3];

    if (cost > budget) {
        *axis_out = first_axis;
        return UINT8_MAX;
    }
    for (unsigned int step = 1; step < 3; step++) {
        unsigned int axis = (first_axis + step) % 3;

        cells[axis] = lrj_axis_cell_from_masks(axis, state->t, state->x);
        joint_prefetch(cells[axis]);
    }
    for (unsigned int step = 1; step < 3; step++) {
        unsigned int axis = (first_axis + step) % 3;
        unsigned int bound = joint_axis_bound(cells[axis], need_parity);

        if (bound > budget) {
            *axis_out = axis;
            return UINT8_MAX;
        }
        if (bound > cost) {
            cost = bound;
            best_axis = axis;
        }
    }
    *axis_out = best_axis;
    return (unsigned char)cost;
}

static unsigned char joint_cost(const struct centers *state, unsigned int budget, unsigned int need_parity)
{
    unsigned int axis;

    return joint_cost_from(state, budget, need_parity, 0, &axis);
}

static unsigned char heuristic(const struct centers *state, unsigned char parity)
{
    uint64_t t_rank = fast_rank_flu(state->t);
    uint64_t x_rank = fast_rank_flu(state->x);
    unsigned char t_cost;
    unsigned char x_cost;
    unsigned char cost;

    t_cost = table_cost(t_costs, t_rank);
    x_cost = table_cost(x_costs, x_rank);
    if (t_cost == UINT8_MAX || x_cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    cost = t_cost > x_cost ? t_cost : x_cost;
    if (joint_enabled) {
        unsigned char joint = joint_cost(state, UINT8_MAX, remaining_parity(parity));

        cost = joint > cost ? joint : cost;
    }
    return cost ? cost : parity_floor(parity);
}

/* Returns UINT8_MAX as soon as a table proves the node exceeds budget,
 * so the x-center read is skipped whenever the t-center cost already prunes.
 * The joint table is read last, and only for nodes the t and x tables (when loaded) do not prune.
 * first_axis and *axis_out are as in joint_cost_from; *axis_out is first_axis when the joint table is not read. */
static unsigned char bounded_heuristic(
    const struct centers *state,
    unsigned char parity,
    unsigned int budget,
    unsigned int first_axis,
    unsigned int *axis_out)
{
    *axis_out = first_axis;
    unsigned char cost = 0;

    if (t_costs) {
        unsigned char t_cost = decode_cost_byte(t_costs[fast_rank_flu(state->t)]);
        unsigned char x_cost;

        if (t_cost == UINT8_MAX || t_cost > budget) {
            return UINT8_MAX;
        }
        x_cost = decode_cost_byte(x_costs[fast_rank_flu(state->x)]);
        if (x_cost == UINT8_MAX || x_cost > budget) {
            return UINT8_MAX;
        }
        cost = t_cost > x_cost ? t_cost : x_cost;
    }
    if (joint_enabled) {
        unsigned char joint = joint_cost_from(state, budget, remaining_parity(parity), first_axis, axis_out);

        if (joint == UINT8_MAX) {
            return UINT8_MAX;
        }
        cost = joint > cost ? joint : cost;
    }
    cost = cost ? cost : parity_floor(parity);
    return cost > budget ? UINT8_MAX : cost;
}

static void print_centers_cube(const char *label, const char *source)
{
    char display[CUBE_ARRAY_SIZE];

    memcpy(display, source, CUBE_ARRAY_SIZE);
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (ida_is_edge_or_corner(square, CUBE_SIZE)) {
            display[square] = 'x';
        }
    }
    printf("%s\n", label);
    print_cube(display, CUBE_SIZE);
    fflush(stdout);
}

static void print_ida_summary(const move_type *path, unsigned int length)
{
    char walk[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];
    unsigned char parity = 0;

    memcpy(walk, start_cube, CUBE_ARRAY_SIZE);
    /* T-CTR and X-CTR appear only when the step10 tables are loaded, LR-TX only with the joint table. */
    printf("\n      ");
    if (t_costs) {
        printf(" T-CTR  X-CTR");
    }
    if (joint_enabled) {
        printf("  LR-TX");
    }
    printf("  PAR  CTG  TRU  IDX\n      ");
    if (t_costs) {
        printf(" =====  =====");
    }
    if (joint_enabled) {
        printf("  =====");
    }
    printf("  ===  ===  ===  ===\n");
    for (unsigned int step = 0; step <= length; step++) {
        struct centers state;

        centers_from_cube(walk, &state);
        if (step) {
            printf("%5s ", move2str[path[step - 1]]);
        } else {
            printf(" INIT ");
        }
        if (t_costs) {
            printf(
                " %5u  %5u",
                table_cost(t_costs, fast_rank_flu(state.t)),
                table_cost(x_costs, fast_rank_flu(state.x))
            );
        }
        if (joint_enabled) {
            printf("  %5u", joint_cost(&state, UINT8_MAX, remaining_parity(parity)));
        }
        printf(
            "  %3u  %3u  %3u  %3u\n",
            parity_floor(parity),
            heuristic(&state, parity),
            length - step,
            step
        );
        if (step < length) {
            rotate_555(walk, scratch, CUBE_ARRAY_SIZE, path[step]);
            parity ^= move_parity(path[step]);
        }
    }
    printf("\n");
}

/* Caller holds solution_lock. */
static void emit_solution(const move_type *path, unsigned int depth)
{
    char ended[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];

    printf("SOLUTION (%u steps):", depth);
    for (unsigned int index = 0; index < depth; index++) {
        printf(" %s", move2str[path[index]]);
    }
    printf("\n");
    memcpy(ended, start_cube, CUBE_ARRAY_SIZE);
    for (unsigned int index = 0; index < depth; index++) {
        rotate_555(ended, scratch, CUBE_ARRAY_SIZE, path[index]);
    }
    print_centers_cube("ending cube", ended);
    print_ida_summary(path, depth);
    solution_count++;
    if (solution_limit && solution_count >= solution_limit) {
        atomic_store_explicit(&stop_search, 1, memory_order_relaxed);
    }
}

static unsigned int ball_nibbles(const struct centers *state)
{
    return gb_lookup(ball_slots, ball_slots_log2, gb_canonical_key(state->t, state->x));
}

/* A node at the horizon has threshold - depth <= ball_depth moves left, so the ball's exact distance
 * for the parity still needed decides it. On a hit the tail is read back from the ball one move at a
 * time: some move always leads to a state one closer at the parity left after that move. */
static int ball_finish(
    struct worker *worker,
    const struct centers *state,
    unsigned int depth,
    move_type previous,
    unsigned char parity)
{
    unsigned int remaining = worker->threshold - depth;
    unsigned int nibbles = ball_nibbles(state);
    unsigned int need = 0;
    struct centers walk = *state;

    if (!nibbles) {
        return 0;
    }
    if (parity_requirement == PARITY_UNSET) {
        if (gb_distance(nibbles, 0) == remaining) {
            need = 0;
        } else if (gb_distance(nibbles, 1) == remaining) {
            need = 1;
        } else {
            return 0;
        }
    } else {
        need = remaining_parity(parity);
        if (gb_distance(nibbles, need) != remaining) {
            return 0;
        }
    }
    for (unsigned int step = 0; step < remaining; step++) {
        unsigned int want = remaining - step - 1;
        int found = -1;

        /* Prefer a move the forward search could have played after the previous one. */
        for (unsigned int pass = 0; pass < 2 && found < 0; pass++) {
            unsigned int count = pass ? MOVE_COUNT_555 : legal_move_count[previous];

            for (unsigned int index = 0; index < count && found < 0; index++) {
                unsigned int move_index = pass ? index : legal_move_index[previous][index];
                struct centers child;

                apply_move(&walk, &child, move_index);
                if (gb_distance(ball_nibbles(&child), need ^ move_parity(moves_555[move_index])) == want) {
                    found = (int)move_index;
                    walk = child;
                }
            }
        }
        if (found < 0) {
            fprintf(stderr, "BUG: goal ball has no move from distance %u to %u\n", want + 1, want);
            exit(1);
        }
        previous = moves_555[found];
        need ^= move_parity(previous);
        worker->path[depth + step] = previous;
    }
    if (!gb_is_goal(walk.t, walk.x) || need) {
        fprintf(stderr, "BUG: goal ball tail does not end staged with even parity left\n");
        exit(1);
    }
    pthread_mutex_lock(&solution_lock);
    if (!atomic_load_explicit(&stop_search, memory_order_relaxed)) {
        emit_solution(worker->path, worker->threshold);
    }
    pthread_mutex_unlock(&solution_lock);
    return atomic_load_explicit(&stop_search, memory_order_relaxed);
}

static int search_node(
    struct worker *worker,
    const struct centers *state,
    unsigned int depth,
    move_type previous,
    unsigned char parity,
    unsigned char cost,
    unsigned int axis);

static int search(
    struct worker *worker,
    const struct centers *state,
    unsigned int depth,
    move_type previous,
    unsigned char parity,
    unsigned int first_axis)
{
    unsigned int axis;
    unsigned char cost;

    worker->nodes++;
    if (depth > worker->max_depth) {
        worker->max_depth = depth;
    }
    if (atomic_load_explicit(&stop_search, memory_order_relaxed)) {
        return 1;
    }
    if (ball_enabled && depth >= root_horizon) {
        if (depth > root_horizon) {
            fprintf(stderr, "BUG: search reached depth %u past the goal ball horizon %u\n", depth, root_horizon);
            exit(1);
        }
        return ball_finish(worker, state, depth, previous, parity);
    }
    cost = bounded_heuristic(state, parity, worker->threshold - depth, first_axis, &axis);
    if (cost == UINT8_MAX) {
        return 0;
    }
    return search_node(worker, state, depth, previous, parity, cost, axis);
}

/* A node that passed its heuristic with this cost; axis is its largest-bound joint axis. */
static int search_node(
    struct worker *worker,
    const struct centers *state,
    unsigned int depth,
    move_type previous,
    unsigned char parity,
    unsigned char cost,
    unsigned int axis)
{
    unsigned int threshold = worker->threshold;

    if (!cost) {
        if (depth == threshold) {
            pthread_mutex_lock(&solution_lock);
            if (!atomic_load_explicit(&stop_search, memory_order_relaxed)) {
                emit_solution(worker->path, depth);
            }
            pthread_mutex_unlock(&solution_lock);
            return atomic_load_explicit(&stop_search, memory_order_relaxed);
        }
        return 0;
    }

    /* Most children are pruned by their first joint read, a random DRAM access. Building every child
     * and prefetching its first-axis cell before evaluating any of them overlaps those reads.
     * The first axis is this node's largest-bound axis: a child survives only if that bound drops,
     * so it is the axis most likely to prune the child. */
    struct child children[MOVE_COUNT_555];
    unsigned char survivors[MOVE_COUNT_555];
    unsigned int child_count = 0;
    unsigned int survivor_count = 0;
    unsigned int child_axis = axis;
    unsigned int second_axis = (axis + 1) % 3;
    unsigned int third_axis = (axis + 2) % 3;
    unsigned int child_budget = threshold - depth - 1;
    int prefetch = joint_enabled && !(ball_enabled && depth + 1 >= root_horizon);
    /* With only the joint table, the children are evaluated here in stages so the second-round reads
     * of every surviving child overlap too. The search tree and node counts are unchanged. */
    int batch = prefetch && !t_costs;

    for (unsigned int legal = 0; legal < legal_move_count[previous]; legal++) {
        unsigned int move_index = legal_move_index[previous][legal];
        move_type move = moves_555[move_index];
        struct child *child = &children[child_count];
        unsigned char child_parity = parity ^ move_parity(move);

        if (depth + 1 == threshold && !parity_is_goal(child_parity)) {
            continue;
        }
        apply_move(state, &child->state, move_index);
        if (move_is_center_noop(state, &child->state, parity, child_parity)) {
            continue;
        }
        child->move = move;
        child->parity = child_parity;
        if (prefetch) {
            child->t_rank = lrj_axis_t_rank(child_axis, child->state.t);
            __builtin_prefetch(&lrj.class_of[child->t_rank]);
        }
        child_count++;
    }
    /* class_of (2.9 MB) misses the cache too, so every child's entry is in flight before any cell is built. */
    if (prefetch) {
        for (unsigned int index = 0; index < child_count; index++) {
            struct child *child = &children[index];

            child->cells[child_axis] = lrj_axis_cell_from_t_rank(child_axis, child->t_rank, child->state.x);
            joint_prefetch(child->cells[child_axis]);
        }
    }
    if (!batch) {
        for (unsigned int index = 0; index < child_count; index++) {
            struct child *child = &children[index];

            worker->path[depth] = child->move;
            if (search(worker, &child->state, depth + 1, child->move, child->parity, child_axis)) {
                return 1;
            }
        }
        worker->path[depth] = MOVE_NONE;
        return 0;
    }

    worker->nodes += child_count;
    if (child_count && depth + 1 > worker->max_depth) {
        worker->max_depth = depth + 1;
    }
    /* child->cost and child->axis track the largest bound read so far, as bounded_heuristic would. */
    for (unsigned int index = 0; index < child_count; index++) {
        struct child *child = &children[index];
        unsigned int bound = joint_axis_bound(child->cells[child_axis], remaining_parity(child->parity));

        if (bound > child_budget) {
            continue;
        }
        child->cost = (unsigned char)bound;
        child->axis = (unsigned char)child_axis;
        child->t_rank = lrj_axis_t_rank(second_axis, child->state.t);
        __builtin_prefetch(&lrj.class_of[child->t_rank]);
        child->cells[third_axis] = lrj_axis_t_rank(third_axis, child->state.t);
        __builtin_prefetch(&lrj.class_of[child->cells[third_axis]]);
        survivors[survivor_count++] = (unsigned char)index;
    }
    for (unsigned int index = 0; index < survivor_count; index++) {
        struct child *child = &children[survivors[index]];

        child->cells[second_axis] = lrj_axis_cell_from_t_rank(second_axis, child->t_rank, child->state.x);
        joint_prefetch(child->cells[second_axis]);
    }
    /* The second view prunes about half of the children left, so the third is read only for the rest. */
    unsigned int kept = 0;

    for (unsigned int index = 0; index < survivor_count; index++) {
        struct child *child = &children[survivors[index]];
        unsigned int bound = joint_axis_bound(child->cells[second_axis], remaining_parity(child->parity));

        if (bound > child_budget) {
            continue;
        }
        if (bound > child->cost) {
            child->cost = (unsigned char)bound;
            child->axis = (unsigned char)second_axis;
        }
        child->cells[third_axis] =
            lrj_axis_cell_from_t_rank(third_axis, (uint32_t)child->cells[third_axis], child->state.x);
        joint_prefetch(child->cells[third_axis]);
        survivors[kept++] = survivors[index];
    }
    for (unsigned int index = 0; index < kept; index++) {
        struct child *child = &children[survivors[index]];
        unsigned int bound = joint_axis_bound(child->cells[third_axis], remaining_parity(child->parity));
        unsigned int child_cost = child->cost;

        if (bound > child_budget) {
            continue;
        }
        if (bound > child_cost) {
            child_cost = bound;
            child->axis = (unsigned char)third_axis;
        }
        child_cost = child_cost ? child_cost : parity_floor(child->parity);
        if (child_cost > child_budget) {
            continue;
        }
        if (atomic_load_explicit(&stop_search, memory_order_relaxed)) {
            return 1;
        }
        worker->path[depth] = child->move;
        if (search_node(worker, &child->state, depth + 1, child->move, child->parity, (unsigned char)child_cost, child->axis)) {
            return 1;
        }
    }
    worker->path[depth] = MOVE_NONE;
    return 0;
}

static void init_root_tasks(void)
{
    for (unsigned int first = 0; first < legal_move_count[MOVE_NONE]; first++) {
        unsigned char first_index = legal_move_index[MOVE_NONE][first];
        move_type first_move = moves_555[first_index];

        for (unsigned int second = 0; second < legal_move_count[first_move]; second++) {
            root_tasks[root_task_count].first = first_index;
            root_tasks[root_task_count].second = legal_move_index[first_move][second];
            root_task_count++;
        }
    }
}

struct pool_worker {
    uint64_t nodes;
    unsigned int max_depth;
};

static void *search_pool_worker(void *argument)
{
    struct pool_worker *pool_worker = argument;

    while (!atomic_load_explicit(&stop_search, memory_order_relaxed)) {
        unsigned int task = atomic_fetch_add_explicit(&next_root_task, 1, memory_order_relaxed);
        struct worker worker;
        struct centers after_first;
        struct centers after_second;
        unsigned int first_index;
        unsigned int second_index;
        unsigned int axis;
        move_type first;
        unsigned char parity;

        if (task >= root_task_count) {
            break;
        }
        first_index = root_tasks[task].first;
        second_index = root_tasks[task].second;
        first = moves_555[first_index];
        memset(&worker, 0, sizeof(worker));
        worker.threshold = root_threshold;

        /* The depth-1 node is shared by many tasks; only its pruning check is repeated here. */
        parity = move_parity(first);
        apply_move(&root_state, &after_first, first_index);
        if (move_is_center_noop(&root_state, &after_first, 0, parity)) {
            continue;
        }
        if (bounded_heuristic(&after_first, parity, root_threshold - 1, 0, &axis) == UINT8_MAX) {
            continue;
        }
        {
            unsigned char parity_before_second = parity;

            parity ^= move_parity(moves_555[second_index]);
            if (root_threshold == 2 && !parity_is_goal(parity)) {
                continue;
            }
            apply_move(&after_first, &after_second, second_index);
            if (move_is_center_noop(&after_first, &after_second, parity_before_second, parity)) {
                continue;
            }
        }
        worker.path[0] = first;
        worker.path[1] = moves_555[second_index];
        search(&worker, &after_second, 2, worker.path[1], parity, axis);
        pool_worker->nodes += worker.nodes;
        if (worker.max_depth > pool_worker->max_depth) {
            pool_worker->max_depth = worker.max_depth;
        }
    }
    return NULL;
}

static uint64_t search_threshold(unsigned int threshold, unsigned int *max_depth)
{
    pthread_t threads[MAX_SEARCH_THREADS];
    struct pool_worker workers[MAX_SEARCH_THREADS];
    uint64_t nodes = 0;

    atomic_store(&next_root_task, 0);
    root_threshold = threshold;
    root_horizon = threshold > ball_depth ? threshold - ball_depth : 0;
    *max_depth = 0;

    /* Thresholds below two, or a horizon below two, have no two-move prefix to hand the pool. */
    if (threshold < 2 || (ball_enabled && root_horizon < 2)) {
        struct worker worker;

        memset(&worker, 0, sizeof(worker));
        worker.threshold = threshold;
        search(&worker, &root_state, 0, MOVE_NONE, 0, 0);
        *max_depth = worker.max_depth;
        return worker.nodes;
    }
    for (unsigned int index = 0; index < search_threads; index++) {
        memset(&workers[index], 0, sizeof(workers[index]));
        if (pthread_create(&threads[index], NULL, search_pool_worker, &workers[index]) != 0) {
            fprintf(stderr, "ERROR: could not create search thread\n");
            exit(1);
        }
    }
    for (unsigned int index = 0; index < search_threads; index++) {
        pthread_join(threads[index], NULL);
        nodes += workers[index].nodes;
        if (workers[index].max_depth > *max_depth) {
            *max_depth = workers[index].max_depth;
        }
    }
    return nodes;
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *t_filename = NULL;
    const char *x_filename = NULL;
    const char *joint_filename = NULL;
    const char *ball_filename = NULL;
    unsigned int joint_options = 0;
    unsigned int min_threshold = 0;
    unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
    int print_ranks = 0;
    int print_legal_moves = 0;
    char cube[CUBE_ARRAY_SIZE];
    uint64_t t_rank;
    uint64_t x_rank;
    unsigned char initial_cost;

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--t-center-cost") && index + 1 < argc) {
            t_filename = argv[++index];
        } else if (!strcmp(argv[index], "--x-center-cost") && index + 1 < argc) {
            x_filename = argv[++index];
        } else if (!strcmp(argv[index], "--lr-joint-cost") && index + 1 < argc) {
            joint_filename = argv[++index];
            joint_options++;
        } else if (!strcmp(argv[index], "--lr-joint-parity-cost") && index + 1 < argc) {
            joint_filename = argv[++index];
            joint_parity_aware = 1;
            joint_options++;
        } else if (!strcmp(argv[index], "--goal-ball") && index + 1 < argc) {
            ball_filename = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--solution-count") && index + 1 < argc) {
            solution_limit = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--threads") && index + 1 < argc) {
            search_threads = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--orbit0-need-odd-w")) {
            parity_requirement = PARITY_ODD;
        } else if (!strcmp(argv[index], "--orbit0-need-even-w")) {
            parity_requirement = PARITY_EVEN;
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
    if (!kociemba || min_threshold > max_threshold || max_threshold > MAX_THRESHOLD ||
            !search_threads || search_threads > MAX_SEARCH_THREADS || !t_filename != !x_filename ||
            (!t_filename && !joint_filename) || joint_options > 1) {
        usage(argv[0]);
        return 2;
    }

    init_binom();
    init_rank_offsets();
    ida_init_move_tables(
        moves_555, MOVE_COUNT_555, move_is_allowed,
        legal_move_count, legal_move_index, inverse_move
    );
    /* Moves are applied with lr_joint_555.h's mask tables, so it is initialized for every table choice. */
    lrj_init(0);
    init_root_tasks();
    ida_init_cube(cube, CUBE_SIZE, kociemba);
    memcpy(start_cube, cube, CUBE_ARRAY_SIZE);
    print_centers_cube("starting cube", start_cube);
    {
        unsigned char t_symbols[GROUP_SIZE];
        unsigned char x_symbols[GROUP_SIZE];

        if (!state_from_cube(cube, t_squares, t_symbols) || !state_from_cube(cube, x_squares, x_symbols)) {
            fprintf(stderr, "ERROR: each center coordinate must be eight F, eight L, and eight U\n");
            return 1;
        }
        centers_from_cube(cube, &root_state);
        t_rank = multiset_rank_flu(t_symbols);
        x_rank = multiset_rank_flu(x_symbols);
    }
    if (t_rank != fast_rank_flu(root_state.t) || x_rank != fast_rank_flu(root_state.x)) {
        fprintf(stderr, "ERROR: fast rank disagrees with multiset rank\n");
        return 1;
    }

    if (t_filename) {
        struct mapped_cost_file mapped = ida_map_cost_file(t_filename, GROUP_UNIVERSE);
        t_fd = mapped.fd;
        t_costs = mapped.costs;
        mapped = ida_map_cost_file(x_filename, GROUP_UNIVERSE);
        x_fd = mapped.fd;
        x_costs = mapped.costs;
    }
    if (joint_filename) {
        struct mapped_cost_file mapped;

        joint_bytes = joint_parity_aware ? lrj_parity_packed_bytes() : lrj_packed_bytes();
        mapped = ida_map_cost_file_random(joint_filename, joint_bytes);
        joint_fd = mapped.fd;
        joint_cells = mapped.costs;
        joint_enabled = 1;
    }
    if (ball_filename) {
        struct gb_header header;
        struct mapped_cost_file mapped;
        FILE *file = fopen(ball_filename, "rb");

        if (!file || fread(&header, sizeof(header), 1, file) != 1 || memcmp(header.magic, GB_MAGIC, sizeof(header.magic)) ||
                header.version != GB_VERSION || header.slots_log2 < GB_MIN_SLOTS_LOG2 ||
                header.slots_log2 > GB_MAX_SLOTS_LOG2 || header.max_depth < 1 || header.max_depth > GB_MAX_DEPTH) {
            fprintf(stderr, "ERROR: %s is not a goal ball file\n", ball_filename);
            return 1;
        }
        fclose(file);
        gb_init();
        ball_depth = header.max_depth;
        ball_slots_log2 = header.slots_log2;
        ball_bytes = (uint64_t)GB_HEADER_BYTES + (UINT64_C(8) << ball_slots_log2);
        mapped = ida_map_cost_file_random(ball_filename, ball_bytes);
        ball_fd = mapped.fd;
        ball_file = mapped.costs;
        ball_slots = (const uint64_t *)(ball_file + GB_HEADER_BYTES);
        ball_enabled = 1;
        LOG("goal ball depth %u, %" PRIu64 " states\n", ball_depth, header.states);
    }
    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_555[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
        printf("SUCCESSORS NONE");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_555[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
        for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
            move_type previous = moves_555[move_index];

            printf("SUCCESSORS %s", move2str[previous]);
            for (unsigned int index = 0; index < legal_move_count[previous]; index++) {
                printf(" %s", move2str[moves_555[legal_move_index[previous][index]]]);
            }
            printf("\n");
        }
    }
    initial_cost = heuristic(&root_state, 0);
    if (print_ranks) {
        printf(
            "T_RANK %" PRIu64 " T_COST %u X_RANK %" PRIu64 " X_COST %u COST %u\n",
            t_rank, table_cost(t_costs, t_rank),
            x_rank, table_cost(x_costs, x_rank),
            initial_cost
        );
        if (joint_enabled) {
            for (unsigned int axis = 0; axis < 3; axis++) {
                uint64_t cell = lrj_axis_cell_from_masks(axis, root_state.t, root_state.x);

                if (joint_parity_aware) {
                    unsigned int entry = lrj_parity_get(joint_cells, cell);

                    printf(
                        "JOINT_%s CELL %" PRIu64 " VALUE %u FLAGS %u\n",
                        joint_axis_name[axis], cell, entry & 15, entry >> 4
                    );
                } else {
                    printf(
                        "JOINT_%s CELL %" PRIu64 " VALUE %u\n",
                        joint_axis_name[axis], cell, lrj_nibble_get(joint_cells, cell)
                    );
                }
            }
        }
        if (ball_enabled) {
            unsigned int nibbles = ball_nibbles(&root_state);

            printf("BALL EVEN %d ODD %d\n", gb_distance(nibbles, 0) == GB_UNSEEN ? -1 : (int)gb_distance(nibbles, 0),
                   gb_distance(nibbles, 1) == GB_UNSEEN ? -1 : (int)gb_distance(nibbles, 1));
        }
    }
    if (initial_cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial state is absent from a ranked cost table\n");
        if (t_costs) {
            ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
            ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
        }
        return 1;
    }
    if (min_threshold < initial_cost) {
        min_threshold = initial_cost;
    }
    LOG("%u root tasks across %u threads\n", root_task_count, search_threads);
    for (unsigned int threshold = min_threshold; threshold <= max_threshold; threshold++) {
        struct timeval start;
        struct timeval end;
        unsigned int before = solution_count;
        double seconds;
        uint64_t nodes;
        uint64_t nodes_per_sec;
        unsigned int max_depth;

        gettimeofday(&start, NULL);
        nodes = search_threshold(threshold, &max_depth);
        gettimeofday(&end, NULL);
        seconds = (end.tv_sec - start.tv_sec) + (end.tv_usec - start.tv_usec) / 1000000.0;
        nodes_per_sec = seconds > 0.0 ? (uint64_t)(nodes / seconds) : 0;
        LOG(
            "IDA threshold %u, explored %" PRIu64 " nodes, took %.3fs, %" PRIu64 " nodes-per-sec, max depth %u\n",
            threshold,
            nodes,
            seconds,
            nodes_per_sec,
            max_depth
        );
        if (solution_count != before) {
            break;
        }
    }

    if (t_costs) {
        ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
        ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
    }
    if (joint_enabled) {
        ida_unmap_cost_file(joint_fd, (unsigned char *)joint_cells, joint_bytes);
    }
    if (ball_enabled) {
        ida_unmap_cost_file(ball_fd, (unsigned char *)ball_file, ball_bytes);
    }
    if (!solution_count) {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
        return 1;
    }
    return 0;
}
