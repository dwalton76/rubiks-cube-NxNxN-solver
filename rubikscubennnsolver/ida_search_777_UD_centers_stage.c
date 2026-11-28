#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
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
/*
 * Pair tables top out at depth 15. The sampled matrix is indexed by the six
 * costs in ranked_tables order: LOMO, LORO, LOOX, MORO, MOOX, ROOX.
 * index = ((((c0 * 16 + c1) * 16 + c2) * 16 + c3) * 16 + c4) * 16 + c5.
 */
#define PHASE56_COST_MAX 15
#define PHASE56_MATRIX_SIDE (PHASE56_COST_MAX + 1)
#define PHASE56_MATRIX_SIZE UINT64_C(16777216)
#define DEFAULT_MAX_IDA_THRESHOLD 30
#define MAX_IDA_THRESHOLD 99
#define MAX_THREADS 64
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
 * UD stickers and eight FB stickers and is ranked as C(16, 8).
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

static const char *pair_even_filename[TABLE_COUNT];
static const char *pair_odd_filename[TABLE_COUNT];
static unsigned char *pair_even_costs[TABLE_COUNT];
static unsigned char *pair_odd_costs[TABLE_COUNT];
static int pair_even_fd[TABLE_COUNT];
static int pair_odd_fd[TABLE_COUNT];

static move_type inverse_move[MOVE_MAX];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_777];
static move_type solution[MAX_IDA_THRESHOLD + 1];
static float cost_to_goal_multiplier;
static unsigned char orbit0_requirement;
static int obliques_only;
static const char *pair_cost_matrix_filename;
static unsigned char *pair_cost_matrix;
static int pair_cost_matrix_fd = -1;

struct heuristic_result {
    uint64_t orbit_rank[ORBIT_COUNT];
    uint64_t table_rank[TABLE_COUNT];
    unsigned char table_cost[TABLE_COUNT];
    unsigned char cost;
};

/* Bit p of mask[orbit] is set when orbit_squares[orbit][p] holds a U or D sticker. */
struct node {
    uint16_t mask[ORBIT_COUNT];
};

struct child {
    struct node node;
    uint32_t table_rank[TABLE_COUNT];
    unsigned char table_cost[TABLE_COUNT];
    move_type move;
    unsigned char parity;
    unsigned char cost;
};

#define MASK_INVALID UINT16_MAX
static uint16_t mask_rank[1 << GROUP_SIZE];
static uint16_t orbit_move_chunk[MOVE_MAX][ORBIT_COUNT][2][256];

static void usage(const char *program)
{
    printf(
        "usage: %s {--kociemba STATE | --kociemba-file FILE} "
        "(all six --*-cost FILE flags | --obliques-only and the three oblique-oblique FILE flags) "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] "
        "[--multiplier F] [--pair-cost-matrix FILE] [--print-ida-summary] "
        "[--orbit0-need-odd-w|--orbit0-need-even-w] "
        "[--apply-move MOVE] [--print-ranks] [--print-legal-moves]\n",
        program
    );
    printf(
        "  --kociemba-file FILE  one root per line: INDEX,ORBIT0,ORBIT1,294-STICKER-STATE;\n"
        "                        requirement is 0 any, 1 odd, 2 even; orbit 1 is ignored\n"
        "  --obliques-only  stage UD left/middle/right obliques; do not load outer-x tables\n"
        "  --multiplier F   scale max(pair tables) by F; not admissible, default unused\n"
        "  --pair-cost-matrix FILE\n"
        "                   16^6 uint8 of (LOMO,LORO,LOOX,MORO,MOOX,ROOX) -> remaining;\n"
        "                   used instead of the multiplier when that flag is omitted\n"
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

static unsigned char decode_product_cost(const unsigned char *costs, uint64_t rank)
{
    unsigned char encoded;

    if (!costs || rank >= PRODUCT_UNIVERSE) {
        return UINT8_MAX;
    }
    encoded = costs[rank];
    return encoded ? (unsigned char)(encoded - 1) : UINT8_MAX;
}

static unsigned char pair_orbit0_cost(const uint32_t table_rank[TABLE_COUNT], unsigned char parity)
{
    unsigned char current_odd = parity & 1;
    unsigned char best = 0;
    int need_odd = -1;
    int loaded = 0;

    if (orbit0_requirement == PARITY_ODD) {
        need_odd = !current_odd;
    } else if (orbit0_requirement == PARITY_EVEN) {
        need_odd = current_odd;
    }
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        unsigned char even_cost;
        unsigned char odd_cost;
        unsigned char cost;

        if (!pair_even_costs[index]) {
            continue;
        }
        loaded = 1;
        even_cost = decode_product_cost(pair_even_costs[index], table_rank[index]);
        odd_cost = decode_product_cost(pair_odd_costs[index], table_rank[index]);
        if (need_odd < 0) {
            if (even_cost == UINT8_MAX) {
                cost = odd_cost;
            } else if (odd_cost == UINT8_MAX) {
                cost = even_cost;
            } else {
                cost = even_cost < odd_cost ? even_cost : odd_cost;
            }
        } else {
            cost = need_odd ? odd_cost : even_cost;
        }
        if (cost == UINT8_MAX) {
            return UINT8_MAX;
        }
        if (cost > best) {
            best = cost;
        }
    }
    return loaded ? best : 0;
}

static void init_mask_rank(void)
{
    for (unsigned int mask = 0; mask < (1u << GROUP_SIZE); mask++) {
        unsigned int u_remaining = GROUP_U_COUNT;
        unsigned int rank = 0;

        if (__builtin_popcount(mask) != GROUP_U_COUNT) {
            mask_rank[mask] = MASK_INVALID;
            continue;
        }
        for (unsigned int position = 0; position < GROUP_SIZE && u_remaining; position++) {
            if (mask & (1u << position)) {
                u_remaining--;
            } else {
                rank += (unsigned int)binom[GROUP_SIZE - position - 1][u_remaining - 1];
            }
        }
        mask_rank[mask] = (uint16_t)rank;
    }
}

/* Each legal move permutes the 16 squares of every orbit among themselves. */
static void init_orbit_moves(void)
{
    for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
        move_type move = moves_777[legal_move_index[MOVE_NONE][index]];
        char cube[CUBE_ARRAY_SIZE];
        char rotate_tmp[CUBE_ARRAY_SIZE];
        unsigned char source[ORBIT_COUNT][GROUP_SIZE];

        memset(cube, 0, sizeof(cube));
        for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
            for (unsigned int position = 0; position < GROUP_SIZE; position++) {
                cube[orbit_squares[orbit][position]] = (char)(1 + orbit * GROUP_SIZE + position);
            }
        }
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
            for (unsigned int position = 0; position < GROUP_SIZE; position++) {
                int value = cube[orbit_squares[orbit][position]] - 1;

                if (value < 0 || (unsigned int)value / GROUP_SIZE != orbit) {
                    fprintf(stderr, "ERROR: %s moves a square out of its orbit\n", move2str[move]);
                    exit(1);
                }
                source[orbit][position] = (unsigned char)(value % GROUP_SIZE);
            }
            for (unsigned int chunk = 0; chunk < 2; chunk++) {
                for (unsigned int byte = 0; byte < 256; byte++) {
                    uint16_t bits = 0;

                    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
                        unsigned int from = source[orbit][position];

                        if (from / 8 == chunk && (byte & (1u << (from % 8)))) {
                            bits |= (uint16_t)(1u << position);
                        }
                    }
                    orbit_move_chunk[move][orbit][chunk][byte] = bits;
                }
            }
        }
    }
}

static struct node node_from_cube(const char *cube)
{
    struct node node;

    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        node.mask[orbit] = 0;
        for (unsigned int position = 0; position < GROUP_SIZE; position++) {
            char sticker = cube[orbit_squares[orbit][position]];

            if (sticker == 'U' || sticker == 'D') {
                node.mask[orbit] |= (uint16_t)(1u << position);
            }
        }
    }
    return node;
}

static int node_is_valid(const struct node *node)
{
    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        if (!(obliques_only && orbit == ORBIT_OUTER_X) && mask_rank[node->mask[orbit]] == MASK_INVALID) {
            return 0;
        }
    }
    return 1;
}

static inline struct node node_apply_move(const struct node *node, move_type move)
{
    struct node next;

    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        const uint16_t (*chunk)[256] = orbit_move_chunk[move][orbit];

        next.mask[orbit] = chunk[0][node->mask[orbit] & 0xFF] | chunk[1][node->mask[orbit] >> 8];
    }
    return next;
}

/*
 * Costs come in three passes so a node's table bytes can all be in flight at
 * once: rank and prefetch the pair tables, read them, then prefetch and read
 * the orbit0 even/odd tables and the matrix for the children that survive.
 */
static inline void child_prefetch_pairs(struct child *child)
{
    uint32_t orbit_rank[ORBIT_COUNT];

    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        orbit_rank[orbit] = mask_rank[child->node.mask[orbit]];
    }
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        const struct ranked_table *table = &ranked_tables[index];

        if (table->costs) {
            child->table_rank[index] =
                orbit_rank[table->orbit_a] * (uint32_t)GROUP_UNIVERSE + orbit_rank[table->orbit_b];
            __builtin_prefetch(&table->costs[child->table_rank[index]]);
        }
    }
}

/* The max of the loaded pair tables, or UINT8_MAX when any of them lacks the state. */
static inline unsigned char child_pair_cost(struct child *child)
{
    unsigned char cost = 0;

    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        const struct ranked_table *table = &ranked_tables[index];
        unsigned char encoded;

        if (!table->costs) {
            child->table_cost[index] = UINT8_MAX;
            continue;
        }
        encoded = table->costs[child->table_rank[index]];
        if (!encoded) {
            return UINT8_MAX;
        }
        child->table_cost[index] = encoded - 1;
        if (child->table_cost[index] > cost) {
            cost = child->table_cost[index];
        }
    }
    return cost;
}

/* Six pair costs, each clamped to 0..15, packed in ranked_tables order. */
static uint32_t matrix_index(const unsigned char table_cost[TABLE_COUNT])
{
    uint32_t index = 0;

    for (unsigned int axis = 0; axis < TABLE_COUNT; axis++) {
        unsigned char cost = table_cost[axis] > PHASE56_COST_MAX ? PHASE56_COST_MAX : table_cost[axis];

        index = index * PHASE56_MATRIX_SIDE + cost;
    }
    return index;
}

static int use_pair_cost_matrix(void)
{
    return pair_cost_matrix && !cost_to_goal_multiplier && !obliques_only;
}

static inline void child_prefetch_rest(const struct child *child)
{
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        if (pair_even_costs[index]) {
            __builtin_prefetch(&pair_even_costs[index][child->table_rank[index]]);
            __builtin_prefetch(&pair_odd_costs[index][child->table_rank[index]]);
        }
    }
    if (use_pair_cost_matrix()) {
        __builtin_prefetch(&pair_cost_matrix[matrix_index(child->table_cost)]);
    }
}

static unsigned char scaled_cost(unsigned char cost)
{
    if (cost && cost_to_goal_multiplier) {
        return (unsigned char)roundf(cost * cost_to_goal_multiplier);
    }
    return cost;
}

/* pair_cost is child_pair_cost(child); returns the full heuristic. */
static unsigned char child_final_cost(const struct child *child, unsigned char pair_cost)
{
    unsigned char cost = pair_cost;
    unsigned char orbit_cost;

    /*
     * The matrix estimates the moves still left from the six pair costs. It is
     * not applied on top of --multiplier: that flag already inflates the
     * admissible max, and stacking both over-prunes.
     */
    if (use_pair_cost_matrix()) {
        unsigned char estimated = pair_cost_matrix[matrix_index(child->table_cost)];

        if (estimated != UINT8_MAX && estimated > cost) {
            cost = estimated;
        }
    }
    orbit_cost = pair_orbit0_cost(child->table_rank, child->parity);
    if (orbit_cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    if (orbit_cost > cost) {
        cost = orbit_cost;
    }
    cost = scaled_cost(cost);
    return cost ? cost : parity_flip_floor(child->parity);
}

static unsigned char cube_cost(const char *cube, unsigned char parity)
{
    struct child child;
    unsigned char pair_cost;

    child.node = node_from_cube(cube);
    child.parity = parity;
    if (!node_is_valid(&child.node)) {
        return UINT8_MAX;
    }
    child_prefetch_pairs(&child);
    pair_cost = child_pair_cost(&child);
    if (pair_cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    return child_final_cost(&child, pair_cost);
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
        if (pair_even_filename[index]) {
            struct mapped_cost_file even = ida_map_cost_file(pair_even_filename[index], PRODUCT_UNIVERSE);
            struct mapped_cost_file odd = ida_map_cost_file(pair_odd_filename[index], PRODUCT_UNIVERSE);

            pair_even_fd[index] = even.fd;
            pair_even_costs[index] = even.costs;
            pair_odd_fd[index] = odd.fd;
            pair_odd_costs[index] = odd.costs;
        }
    }
}

static void unmap_ranked_tables(void)
{
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        struct ranked_table *table = &ranked_tables[index];

        ida_unmap_cost_file(table->fd, table->costs, (size_t)PRODUCT_UNIVERSE);
        table->costs = NULL;
        table->fd = -1;
        if (pair_even_costs[index]) {
            ida_unmap_cost_file(pair_even_fd[index], pair_even_costs[index], (size_t)PRODUCT_UNIVERSE);
            ida_unmap_cost_file(pair_odd_fd[index], pair_odd_costs[index], (size_t)PRODUCT_UNIVERSE);
            pair_even_costs[index] = pair_odd_costs[index] = NULL;
            pair_even_fd[index] = pair_odd_fd[index] = -1;
        }
    }
    if (pair_cost_matrix) {
        ida_unmap_cost_file(pair_cost_matrix_fd, pair_cost_matrix, (size_t)PHASE56_MATRIX_SIZE);
        pair_cost_matrix = NULL;
        pair_cost_matrix_fd = -1;
    }
}

static int match_pair_orbit_flag(const char *arg, const char *suffix, unsigned int *table_out)
{
    for (unsigned int table = 0; table < TABLE_COUNT; table++) {
        const char *flag = ranked_tables[table].flag;
        size_t length = strlen(flag);
        char expected[96];

        if (length < 5 || strcmp(flag + length - 5, "-cost") != 0) {
            continue;
        }
        if (length - 5 + strlen(suffix) >= sizeof(expected)) {
            continue;
        }
        memcpy(expected, flag, length - 5);
        memcpy(expected + (length - 5), suffix, strlen(suffix) + 1);
        if (!strcmp(arg, expected)) {
            *table_out = table;
            return 1;
        }
    }
    return 0;
}

static void init_cube(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    ida_init_cube(cube, CUBE_SIZE, kociemba);
}

static int is_outer_x_center(unsigned int square)
{
    unsigned int face_offset = (square - 1) % (CUBE_SIZE * CUBE_SIZE);

    return face_offset == 8 || face_offset == 12 || face_offset == 36 || face_offset == 40;
}

static void recolor_cube(char cube[CUBE_ARRAY_SIZE])
{
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (ida_is_edge_or_corner(square, CUBE_SIZE) || (obliques_only && is_outer_x_center(square))) {
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

struct walker {
    const struct ida_ordered_tasks *tasks;
    size_t task;
    unsigned char threshold;
    uint64_t nodes;
    move_type path[MAX_IDA_THRESHOLD + 1];
};

/*
 * Score every legal child of node. Below the root, the first goal child in
 * move order is returned alone with *goal set; otherwise the children that fit
 * under the threshold come back cheapest first. The root keeps move order and
 * its goal children, because each root move is searched on its own.
 */
static unsigned int score_children(
    struct walker *walker,
    const struct node *node,
    unsigned char depth,
    move_type previous_move,
    unsigned char parity,
    int root,
    struct child children[MOVE_COUNT_777],
    int *goal
)
{
    unsigned char next_depth = depth + 1;
    unsigned char threshold = walker->threshold;
    int last_ply = next_depth == threshold;
    unsigned char pair_cost[MOVE_COUNT_777];
    unsigned int count = 0;
    unsigned int kept = 0;

    *goal = 0;
    for (unsigned int index = 0; index < legal_move_count[previous_move]; index++) {
        move_type move = moves_777[legal_move_index[previous_move][index]];
        struct child *child = &children[count++];

        if (last_ply && !last_ply_can_be_goal(parity, move)) {
            count--;
            continue;
        }
        child->move = move;
        child->parity = parity_after_move(parity, move);
        child->node = node_apply_move(node, move);
        child_prefetch_pairs(child);
    }
    walker->nodes += count;
    for (unsigned int index = 0; index < count; index++) {
        unsigned char cost = child_pair_cost(&children[index]);

        if (cost == UINT8_MAX || next_depth + scaled_cost(cost) > threshold) {
            continue;
        }
        pair_cost[kept] = cost;
        children[kept++] = children[index];
    }
    for (unsigned int index = 0; index < kept; index++) {
        child_prefetch_rest(&children[index]);
    }
    count = kept;
    kept = 0;
    for (unsigned int index = 0; index < count; index++) {
        unsigned char cost = child_final_cost(&children[index], pair_cost[index]);

        if (cost == UINT8_MAX || next_depth + cost > threshold) {
            continue;
        }
        children[index].cost = cost;
        if (!cost && !root) {
            children[0] = children[index];
            *goal = 1;
            return 1;
        }
        children[kept++] = children[index];
    }
    if (root || next_depth >= threshold) {
        return kept;
    }
    for (unsigned int index = 1; index < kept; index++) {
        struct child pending = children[index];
        unsigned int destination = index;

        while (destination && children[destination - 1].cost > pending.cost) {
            children[destination] = children[destination - 1];
            destination--;
        }
        children[destination] = pending;
    }
    return kept;
}

static int ida_search(
    struct walker *walker,
    const struct node *node,
    unsigned char depth,
    move_type previous_move,
    unsigned char parity
)
{
    struct child children[MOVE_COUNT_777];
    unsigned char next_depth = depth + 1;
    unsigned int count;
    int goal;

    if (ida_task_abandoned(walker->tasks, walker->task)) {
        return 0;
    }
    count = score_children(walker, node, depth, previous_move, parity, 0, children, &goal);
    if (goal) {
        walker->path[depth] = children[0].move;
        walker->path[next_depth] = MOVE_NONE;
        return 1;
    }
    if (next_depth >= walker->threshold || next_depth >= MAX_IDA_THRESHOLD) {
        return 0;
    }
    for (unsigned int index = 0; index < count; index++) {
        walker->path[depth] = children[index].move;
        if (ida_search(walker, &children[index].node, next_depth, children[index].move, children[index].parity)) {
            return 1;
        }
    }
    return 0;
}

/*
 * The first few plies are walked once and every surviving node at split_depth
 * becomes a task. Tasks run cheapest first, ties in search order, and the
 * first solution found stops every task: making later tasks wait on earlier
 * ones costs up to ten times the nodes at the solving threshold.
 */
#define MAX_SPLIT_DEPTH 3
#define SPLIT_TASK_TARGET 2048
#define SPLIT_BRANCHING 24

struct split_task {
    struct node node;
    move_type prefix[MAX_SPLIT_DEPTH];
    unsigned char depth;
    unsigned char parity;
    unsigned char solved;
    unsigned char cost;
    uint32_t order;
    uint64_t nodes;
    move_type *solution;
};

static int compare_split_tasks(const void *left, const void *right)
{
    const struct split_task *a = left;
    const struct split_task *b = right;

    if (a->cost != b->cost) {
        return a->cost < b->cost ? -1 : 1;
    }
    return a->order < b->order ? -1 : a->order > b->order;
}

struct split_search {
    struct ida_ordered_tasks tasks;
    unsigned char threshold;
    unsigned char split_depth;
    struct split_task *items;
    size_t count;
    size_t capacity;
};

static void add_split_task(
    struct split_search *search,
    const move_type *prefix,
    unsigned char depth,
    const struct child *child,
    int solved
)
{
    struct split_task *task;

    if (search->count == search->capacity) {
        size_t capacity = search->capacity ? search->capacity * 2 : 1024;
        struct split_task *grown = realloc(search->items, capacity * sizeof(*grown));

        if (!grown) {
            fprintf(stderr, "ERROR: could not allocate search tasks\n");
            exit(1);
        }
        search->items = grown;
        search->capacity = capacity;
    }
    task = &search->items[search->count++];
    memcpy(task->prefix, prefix, depth * sizeof(*prefix));
    task->node = child->node;
    task->depth = depth;
    task->parity = child->parity;
    task->solved = (unsigned char)solved;
    task->cost = solved ? 0 : child->cost;
    task->order = (uint32_t)(search->count - 1);
    task->nodes = 0;
    task->solution = NULL;
}

/* Mirrors ida_search down to split_depth; returns 1 once a goal ends the walk. */
static int split_node(
    struct split_search *search,
    struct walker *walker,
    const struct node *node,
    unsigned char depth,
    move_type previous_move,
    unsigned char parity
)
{
    struct child children[MOVE_COUNT_777];
    unsigned char next_depth = depth + 1;
    unsigned int count;
    int goal;

    count = score_children(walker, node, depth, previous_move, parity, 0, children, &goal);
    if (goal) {
        walker->path[depth] = children[0].move;
        add_split_task(search, walker->path, next_depth, &children[0], 1);
        return 1;
    }
    if (next_depth >= walker->threshold || next_depth >= MAX_IDA_THRESHOLD) {
        return 0;
    }
    for (unsigned int index = 0; index < count; index++) {
        walker->path[depth] = children[index].move;
        if (next_depth == search->split_depth) {
            add_split_task(search, walker->path, next_depth, &children[index], 0);
        } else if (split_node(search, walker, &children[index].node, next_depth, children[index].move, children[index].parity)) {
            return 1;
        }
    }
    return 0;
}

static void run_split_task(struct ida_ordered_tasks *tasks, size_t index)
{
    struct split_search *search = tasks->context;
    struct split_task *task = &search->items[index];
    struct walker walker;
    int found = 1;

    walker.tasks = tasks;
    walker.task = index;
    walker.threshold = search->threshold;
    walker.nodes = 0;
    memcpy(walker.path, task->prefix, task->depth * sizeof(*task->prefix));
    walker.path[task->depth] = MOVE_NONE;
    if (!task->solved) {
        found = ida_search(&walker, &task->node, task->depth, task->prefix[task->depth - 1], task->parity);
    }
    task->nodes = walker.nodes;
    if (found) {
        task->solution = malloc(sizeof(walker.path));
        if (!task->solution) {
            fprintf(stderr, "ERROR: could not allocate a solution\n");
            exit(1);
        }
        memcpy(task->solution, walker.path, sizeof(walker.path));
        ida_stop_all_tasks(tasks);
    }
}

static int search_at_threshold(
    const char cube[CUBE_ARRAY_SIZE],
    unsigned char threshold,
    unsigned int thread_count,
    uint64_t *nodes
)
{
    struct split_search search;
    struct walker walker;
    struct node root = node_from_cube(cube);
    struct child children[MOVE_COUNT_777];
    unsigned int count;
    unsigned int estimate = legal_move_count[MOVE_NONE];
    int goal;
    int found = 0;

    memset(&search, 0, sizeof(search));
    search.threshold = threshold;
    search.split_depth = 1;
    while (estimate < SPLIT_TASK_TARGET && search.split_depth < MAX_SPLIT_DEPTH && search.split_depth + 1 < threshold) {
        estimate *= SPLIT_BRANCHING;
        search.split_depth++;
    }
    search.tasks.stop_from = SIZE_MAX;
    walker.tasks = &search.tasks;
    walker.task = 0;
    walker.threshold = threshold;
    walker.nodes = 1;

    count = score_children(&walker, &root, 0, MOVE_NONE, 0, 1, children, &goal);
    for (unsigned int index = 0; index < count; index++) {
        walker.path[0] = children[index].move;
        if (!children[index].cost) {
            add_split_task(&search, walker.path, 1, &children[index], 1);
            break;
        }
        if (threshold <= 1) {
            continue;
        }
        if (search.split_depth == 1) {
            add_split_task(&search, walker.path, 1, &children[index], 0);
        } else if (split_node(&search, &walker, &children[index].node, 1, children[index].move, children[index].parity)) {
            break;
        }
    }

    qsort(search.items, search.count, sizeof(*search.items), compare_split_tasks);
    search.tasks.task_count = search.count;
    search.tasks.run = run_split_task;
    search.tasks.context = &search;
    ida_run_ordered_tasks(&search.tasks, thread_count);

    *nodes = walker.nodes;
    for (size_t index = 0; index < search.count; index++) {
        struct split_task *task = &search.items[index];

        *nodes += task->nodes;
        if (task->solution && !found) {
            memcpy(solution, task->solution, sizeof(solution));
            found = 1;
        }
        free(task->solution);
    }
    free(search.items);
    return found;
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

/* Roots the matrix prices exactly at the winning depth were never searched
 * one ply lower. A few of those can hide a shorter path when the matrix
 * overestimated. Roots below that price were already exhausted. */
#define SHORTER_ROOT_CHECKS 8

struct search_root {
    unsigned int index;
    unsigned char orbit0_requirement;
    unsigned char initial_cost;
    char cube[CUBE_ARRAY_SIZE];
};

static int compare_search_roots(const void *left, const void *right)
{
    const struct search_root *a = left;
    const struct search_root *b = right;

    if (a->initial_cost != b->initial_cost) {
        return a->initial_cost < b->initial_cost ? -1 : 1;
    }
    if (a->index != b->index) {
        return a->index < b->index ? -1 : 1;
    }
    return 0;
}

/* 7*7*6 stickers. The scan width has to be a literal, so it matches CUBE_ARRAY_SIZE - 1. */
static struct search_root *read_search_roots(const char *filename, unsigned int *root_count)
{
    FILE *stream = fopen(filename, "r");
    char *line = NULL;
    size_t capacity = 0;
    ssize_t length;
    unsigned int allocated = 0;
    unsigned int line_number = 0;
    struct search_root *roots = NULL;

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
        if (sscanf(line, "%u,%u,%u,%294[^\r\n]", &index, &orbit0, &orbit1, kociemba) != 4 ||
            strlen(kociemba) != CUBE_ARRAY_SIZE - 1 || orbit0 > PARITY_EVEN || orbit1 > PARITY_EVEN) {
            fprintf(
                stderr,
                "ERROR: invalid --kociemba-file line %u; expected "
                "ROOT_INDEX,ORBIT0_REQUIREMENT,ORBIT1_REQUIREMENT,294-STICKER-STATE\n",
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
        roots[*root_count].initial_cost = UINT8_MAX;
        init_cube(roots[*root_count].cube, kociemba);
        recolor_cube(roots[*root_count].cube);
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

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *kociemba_filename = NULL;
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
        unsigned int orbit_table = 0;

        if (match_pair_orbit_flag(argv[index], "-even-cost", &orbit_table) && index + 1 < argc) {
            pair_even_filename[orbit_table] = argv[++index];
            continue;
        }
        if (match_pair_orbit_flag(argv[index], "-odd-cost", &orbit_table) && index + 1 < argc) {
            pair_odd_filename[orbit_table] = argv[++index];
            continue;
        }

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
        } else if (!strcmp(argv[index], "--kociemba-file") && index + 1 < argc) {
            kociemba_filename = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--threads") && index + 1 < argc) {
            thread_count = (unsigned int)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--multiplier") && index + 1 < argc) {
            cost_to_goal_multiplier = (float)atof(argv[++index]);
        } else if (!strcmp(argv[index], "--pair-cost-matrix") && index + 1 < argc) {
            pair_cost_matrix_filename = argv[++index];
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
    if ((kociemba && kociemba_filename) || (!kociemba && !kociemba_filename) ||
        !thread_count || thread_count > MAX_THREADS ||
        min_threshold > max_threshold || max_threshold > MAX_IDA_THRESHOLD) {
        usage(argv[0]);
        return 2;
    }
    if (kociemba_filename && (apply_move_string || print_ranks || print_legal_moves)) {
        fprintf(stderr, "ERROR: --apply-move, --print-ranks, and --print-legal-moves need --kociemba\n");
        return 1;
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
    {
        int loaded = 0;
        int missing = 0;

        for (unsigned int table = 0; table < TABLE_COUNT; table++) {
            int table_loaded = ranked_tables[table].filename &&
                (table_is_oblique_only(&ranked_tables[table]) || !obliques_only);
            int even_set = pair_even_filename[table] != NULL;
            int odd_set = pair_odd_filename[table] != NULL;

            if (even_set != odd_set) {
                fprintf(stderr, "ERROR: %s even and odd costs must be passed together\n", ranked_tables[table].label);
                return 1;
            }
            if (!table_loaded) {
                continue;
            }
            if (even_set) {
                loaded++;
            } else {
                missing++;
            }
        }
        if (loaded && missing) {
            fprintf(stderr, "ERROR: pass even and odd costs for every loaded UD pair table\n");
            return 1;
        }
    }

    init_binom();
    init_mask_rank();
    init_move_tables();
    init_orbit_moves();
    map_ranked_tables();
    if (pair_cost_matrix_filename) {
        struct mapped_cost_file mapped = ida_map_cost_file(pair_cost_matrix_filename, PHASE56_MATRIX_SIZE);

        pair_cost_matrix_fd = mapped.fd;
        pair_cost_matrix = mapped.costs;
    }
    struct search_root *roots = NULL;
    unsigned int root_count = 0;

    if (kociemba_filename) {
        roots = read_search_roots(kociemba_filename, &root_count);
    } else {
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

        roots = calloc(1, sizeof(*roots));
        if (!roots) {
            fprintf(stderr, "ERROR: could not allocate search roots\n");
            unmap_ranked_tables();
            return 1;
        }
        roots[0].orbit0_requirement = orbit0_requirement;
        memcpy(roots[0].cube, cube, CUBE_ARRAY_SIZE);
        root_count = 1;
    }

    for (unsigned int root_index = 0; root_index < root_count; root_index++) {
        orbit0_requirement = roots[root_index].orbit0_requirement;
        roots[root_index].initial_cost = cube_cost(roots[root_index].cube, 0);
        if (roots[root_index].initial_cost == UINT8_MAX) {
            fprintf(stderr, "ERROR: initial center state is absent from a ranked cost table\n");
            unmap_ranked_tables();
            free(roots);
            return 1;
        }
    }
    qsort(roots, root_count, sizeof(*roots), compare_search_roots);
    if (min_threshold < roots[0].initial_cost) {
        min_threshold = roots[0].initial_cost;
    }
    if (cost_to_goal_multiplier) {
        LOG("searching with cost to goal multiplier %.2f\n", cost_to_goal_multiplier);
    } else if (pair_cost_matrix) {
        LOG("searching with pair cost matrix %s\n", pair_cost_matrix_filename);
    }
    if (root_count == 1) {
        printf("START\n");
        print_cube(roots[0].cube, CUBE_SIZE);
        LOG(
            "initial cost %u, threads %u, ranked tables %s\n",
            roots[0].initial_cost,
            thread_count,
            obliques_only ? "3 (obliques only)" : "6"
        );
    } else {
        LOG(
            "loaded %u starting states from %s, min initial cost %u, threads %u, ranked tables %s\n",
            root_count,
            kociemba_filename,
            roots[0].initial_cost,
            thread_count,
            obliques_only ? "3 (obliques only)" : "6"
        );
    }

    for (unsigned char threshold = min_threshold; threshold <= max_threshold; threshold++) {
        struct timeval start;
        struct timeval end;
        struct search_root *selected = NULL;
        uint64_t threshold_nodes = 0;

        gettimeofday(&start, NULL);
        for (unsigned int root_index = 0; root_index < root_count; root_index++) {
            uint64_t root_nodes = 0;
            int found;

            if (roots[root_index].initial_cost > threshold) {
                continue;
            }
            orbit0_requirement = roots[root_index].orbit0_requirement;
            if (!roots[root_index].initial_cost) {
                solution[0] = MOVE_NONE;
                found = 1;
                root_nodes = 1;
            } else {
                found = search_at_threshold(
                    roots[root_index].cube, threshold, thread_count, &root_nodes
                );
            }
            threshold_nodes += root_nodes;
            if (found) {
                selected = &roots[root_index];
                break;
            }
        }
        if (selected && selected->initial_cost) {
            move_type best_solution[MAX_IDA_THRESHOLD + 1];
            unsigned int best_length = 0;
            unsigned int checks = 0;

            while (solution[best_length] != MOVE_NONE) {
                best_length++;
            }
            memcpy(best_solution, solution, sizeof(best_solution));
            for (unsigned int root_index = 0; root_index < root_count && checks < SHORTER_ROOT_CHECKS; root_index++) {
                uint64_t root_nodes = 0;
                unsigned int length = 0;
                int found;

                if (&roots[root_index] == selected || roots[root_index].initial_cost != threshold) {
                    continue;
                }
                checks++;
                orbit0_requirement = roots[root_index].orbit0_requirement;
                found = search_at_threshold(
                    roots[root_index].cube, (unsigned char)(best_length - 1), thread_count, &root_nodes
                );
                threshold_nodes += root_nodes;
                if (!found) {
                    continue;
                }
                while (solution[length] != MOVE_NONE) {
                    length++;
                }
                if (length < best_length) {
                    LOG(
                        "root %u solved in %u, shorter than root %u in %u\n",
                        roots[root_index].index, length, selected->index, best_length
                    );
                    best_length = length;
                    selected = &roots[root_index];
                    memcpy(best_solution, solution, sizeof(best_solution));
                }
            }
            memcpy(solution, best_solution, sizeof(solution));
        }
        gettimeofday(&end, NULL);
        {
            double seconds = elapsed_seconds(&start, &end);
            uint64_t nodes_per_sec = seconds > 0.0 ? (uint64_t)(threshold_nodes / seconds) : 0;

            LOG(
                "IDA threshold %u, explored %" PRIu64 " nodes, took %.3fs, %" PRIu64 " nodes-per-sec\n",
                threshold,
                threshold_nodes,
                seconds,
                nodes_per_sec
            );
        }
        if (selected) {
            unsigned int length = 0;

            while (solution[length] != MOVE_NONE) {
                length++;
            }
            if (kociemba_filename) {
                printf("ROOT_INDEX %u\n", selected->index);
            }
            printf("SOLUTION (%u steps):", length);
            for (unsigned int index = 0; index < length; index++) {
                printf(" %s", move2str[solution[index]]);
            }
            printf("\n");
            if (print_summary) {
                print_ida_summary(selected->cube, length);
            }
            for (unsigned int index = 0; index < length; index++) {
                rotate_777_centers(selected->cube, rotate_tmp, CUBE_ARRAY_SIZE, solution[index]);
            }
            printf("END\n");
            print_cube(selected->cube, CUBE_SIZE);
            unmap_ranked_tables();
            free(roots);
            return 0;
        }
    }

    fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
    unmap_ranked_tables();
    free(roots);
    return 1;
}
