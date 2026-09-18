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
static uint32_t *rank_cache;
static uint32_t *t_transitions;
static uint32_t *x_transitions;
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
static move_type path[MAX_THRESHOLD + 1];
static unsigned int solution_limit = 1;
static unsigned int solution_count;
static int t_centers_only;

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE --t-center-cost FILE "
        "(--x-center-cost FILE | --t-centers-only) "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--solution-count N] "
        "[--print-ranks] [--print-legal-moves]\n",
        program
    );
}

/* buildercore.multiset_rank order for eight lower symbols followed by sixteen higher symbols. */
static uint64_t combination_rank(uint32_t selected)
{
    uint64_t rank = 0;
    unsigned int remaining = SELECTED_COUNT;
    uint32_t cached;

    if (__builtin_popcount(selected) != SELECTED_COUNT) {
        return UINT64_MAX;
    }
    cached = rank_cache[selected];
    if (cached) {
        return cached - 1;
    }
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        unsigned int after = GROUP_SIZE - position - 1;

        if (selected & (UINT32_C(1) << position)) {
            remaining--;
        } else if (remaining) {
            rank += binom[after][remaining - 1];
        }
    }
    if (remaining) {
        return UINT64_MAX;
    }
    rank_cache[selected] = (uint32_t)rank + 1;
    return rank;
}

static uint32_t combination_unrank(uint64_t rank)
{
    uint32_t mask = 0;
    unsigned int remaining = SELECTED_COUNT;

    if (rank >= GROUP_UNIVERSE) {
        return UINT32_MAX;
    }
    for (unsigned int position = 0; position < GROUP_SIZE && remaining; position++) {
        unsigned int after = GROUP_SIZE - position - 1;
        uint64_t selected_prefix = binom[after][remaining - 1];

        if (rank < selected_prefix) {
            mask |= UINT32_C(1) << position;
            remaining--;
        } else {
            rank -= selected_prefix;
        }
    }
    return remaining ? UINT32_MAX : mask;
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

static uint32_t *build_transitions(const uint32_t chunks[MOVE_COUNT_555][3][256])
{
    size_t entry_count = (size_t)GROUP_UNIVERSE * MOVE_COUNT_555;
    uint32_t *transitions = malloc(entry_count * sizeof(*transitions));

    if (!transitions) {
        fprintf(stderr, "ERROR: could not allocate ranked move transitions\n");
        exit(1);
    }
    for (uint32_t rank = 0; rank < GROUP_UNIVERSE; rank++) {
        uint32_t mask = combination_unrank(rank);

        for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
            transitions[(size_t)rank * MOVE_COUNT_555 + move_index] =
                (uint32_t)combination_rank(apply_move(mask, chunks[move_index]));
        }
    }
    return transitions;
}

static int emit_solution(unsigned int depth)
{
    printf("SOLUTION (%u steps):", depth);
    for (unsigned int index = 0; index < depth; index++) {
        printf(" %s", move2str[path[index]]);
    }
    printf("\n");
    solution_count++;
    return solution_limit && solution_count >= solution_limit;
}

static int search(
    uint32_t t_rank,
    uint32_t x_rank,
    unsigned int depth,
    unsigned int threshold,
    move_type previous)
{
    unsigned char cost = heuristic(t_rank, x_rank);

    if (cost == UINT8_MAX || depth + cost > threshold) {
        return 0;
    }
    if (!cost) {
        return depth == threshold ? emit_solution(depth) : 0;
    }
    if (depth >= threshold) {
        return 0;
    }

    for (unsigned int legal = 0; legal < legal_move_count[previous]; legal++) {
        unsigned int move_index = legal_move_index[previous][legal];

        path[depth] = moves_555[move_index];
        if (search(
                t_transitions[(size_t)t_rank * MOVE_COUNT_555 + move_index],
                t_centers_only ? 0 : x_transitions[(size_t)x_rank * MOVE_COUNT_555 + move_index],
                depth + 1,
                threshold,
                path[depth])) {
            return 1;
        }
    }
    path[depth] = MOVE_NONE;
    return 0;
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
    rank_cache = calloc(UINT32_C(1) << GROUP_SIZE, sizeof(*rank_cache));
    if (!rank_cache) {
        fprintf(stderr, "ERROR: could not allocate combination-rank cache\n");
        return 1;
    }
    ida_init_cube(cube, CUBE_SIZE, kociemba);
    t_mask = mask_from_cube(cube, t_squares);
    x_mask = t_centers_only ? 0 : mask_from_cube(cube, x_squares);
    if (t_mask == UINT32_MAX || (!t_centers_only && x_mask == UINT32_MAX)) {
        fprintf(
            stderr,
            "ERROR: %s center coordinate must contain eight L/R stickers\n",
            t_centers_only ? "the t" : "each"
        );
        free(rank_cache);
        return 1;
    }
    t_rank = (uint32_t)combination_rank(t_mask);
    x_rank = t_centers_only ? 0 : (uint32_t)combination_rank(x_mask);

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

    t_transitions = build_transitions(t_move_chunks);
    if (!t_centers_only) {
        x_transitions = build_transitions(x_move_chunks);
    }
    free(rank_cache);
    rank_cache = NULL;

    unsigned char initial_cost = heuristic(t_rank, x_rank);
    if (initial_cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial state is absent from a ranked cost table\n");
        ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
        if (!t_centers_only) {
            ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
        }
        free(t_transitions);
        free(x_transitions);
        return 1;
    }
    if (min_threshold < initial_cost) {
        min_threshold = initial_cost;
    }
    for (unsigned int threshold = min_threshold; threshold <= max_threshold; threshold++) {
        unsigned int before = solution_count;

        search(t_rank, x_rank, 0, threshold, MOVE_NONE);
        if (solution_count != before) {
            break; /* solution-count zero means all solutions at this first solved threshold */
        }
    }

    ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
    if (!t_centers_only) {
        ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
    }
    free(t_transitions);
    free(x_transitions);
    if (!solution_count) {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
        return 1;
    }
    return 0;
}
