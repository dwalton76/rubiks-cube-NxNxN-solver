#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ida_search_core.h"

#define CUBE_ARRAY_SIZE 151
#define ORBIT_COUNT 3
#define ORBIT_SIZE 12
#define SELECTED_COUNT 4
#define ORBIT_UNIVERSE UINT64_C(495)
#define RANK_UNIVERSE UINT64_C(121287375)
#define MAX_THRESHOLD 7
#define ROOT_ID_SIZE 32

static const unsigned int orbit_squares[ORBIT_COUNT][ORBIT_SIZE] = {
    {2, 10, 24, 16, 35, 41, 85, 91, 127, 135, 149, 141},
    {3, 11, 15, 23, 36, 40, 86, 90, 128, 136, 140, 148},
    {4, 20, 22, 6, 31, 45, 81, 95, 129, 145, 147, 131},
};
static const unsigned int orbit_partners[ORBIT_COUNT][ORBIT_SIZE] = {
    {104, 79, 54, 29, 56, 120, 106, 70, 72, 97, 122, 47},
    {103, 28, 78, 53, 115, 61, 65, 111, 73, 48, 98, 123},
    {102, 77, 52, 27, 110, 66, 60, 116, 74, 99, 124, 49},
};

struct root {
    char id[ROOT_ID_SIZE];
    uint16_t masks[ORBIT_COUNT];
    unsigned char initial_cost;
};

static unsigned char *costs;
static int costs_fd = -1;
static uint16_t move_bits[ORBIT_COUNT][MOVE_COUNT_555][ORBIT_SIZE];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
static move_type path[MAX_THRESHOLD + 1];

static void usage(const char *program)
{
    printf(
        "usage: %s --roots-file FILE --cost-table FILE "
        "[--max-ida-threshold 0..7] [--print-ranks] [--print-legal-moves]\n",
        program
    );
    printf("roots file: ID,RANK (one root per line; # comments allowed)\n");
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
        case L:
        case L_PRIME:
        case R:
        case R_PRIME:
            return 0;
        default:
            return 1;
    }
}

static uint64_t combination_rank(uint16_t mask)
{
    uint64_t rank = 0;
    unsigned int remaining = SELECTED_COUNT;

    if (__builtin_popcount((unsigned int)mask) != SELECTED_COUNT) {
        return UINT64_MAX;
    }
    for (unsigned int position = 0; position < ORBIT_SIZE; position++) {
        unsigned int after = ORBIT_SIZE - position - 1;

        if (mask & (1U << position)) {
            remaining--;
        } else if (remaining) {
            rank += binom[after][remaining - 1];
        }
    }
    return remaining ? UINT64_MAX : rank;
}

static uint16_t combination_unrank(uint64_t rank)
{
    uint16_t mask = 0;
    unsigned int remaining = SELECTED_COUNT;

    if (rank >= ORBIT_UNIVERSE) {
        return UINT16_MAX;
    }
    for (unsigned int position = 0; position < ORBIT_SIZE && remaining; position++) {
        unsigned int after = ORBIT_SIZE - position - 1;
        uint64_t selected_prefix = binom[after][remaining - 1];

        if (rank < selected_prefix) {
            mask |= (uint16_t)(1U << position);
            remaining--;
        } else {
            rank -= selected_prefix;
        }
    }
    return remaining ? UINT16_MAX : mask;
}

static uint64_t grouped_rank(const uint16_t masks[ORBIT_COUNT])
{
    uint64_t rank = 0;

    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        uint64_t component = combination_rank(masks[orbit]);

        if (component >= ORBIT_UNIVERSE) {
            return UINT64_MAX;
        }
        rank = (rank * ORBIT_UNIVERSE) + component;
    }
    return rank;
}

static int grouped_unrank(uint64_t rank, uint16_t masks[ORBIT_COUNT])
{
    if (rank >= RANK_UNIVERSE) {
        return 0;
    }
    for (int orbit = ORBIT_COUNT - 1; orbit >= 0; orbit--) {
        masks[orbit] = combination_unrank(rank % ORBIT_UNIVERSE);
        rank /= ORBIT_UNIVERSE;
    }
    return 1;
}

static unsigned char table_cost(const uint16_t masks[ORBIT_COUNT])
{
    uint64_t rank = grouped_rank(masks);
    unsigned char encoded;

    if (rank >= RANK_UNIVERSE) {
        return UINT8_MAX;
    }
    encoded = costs[rank];
    return encoded ? decode_cost_byte(encoded) : UINT8_MAX;
}

static uint16_t apply_move(uint16_t mask, const uint16_t bits[ORBIT_SIZE])
{
    uint16_t result = 0;

    while (mask) {
        unsigned int source = (unsigned int)__builtin_ctz((unsigned int)mask);
        result |= bits[source];
        mask &= (uint16_t)(mask - 1);
    }
    return result;
}

static void init_permutations(void)
{
    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        char marker[CUBE_ARRAY_SIZE];
        char scratch[CUBE_ARRAY_SIZE];

        memset(marker, 0, sizeof(marker));
        marker[0] = 'x';
        for (unsigned int position = 0; position < ORBIT_SIZE; position++) {
            marker[orbit_squares[orbit][position]] = (char)(position + 1);
            marker[orbit_partners[orbit][position]] = (char)(position + 1);
        }
        for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
            char moved[CUBE_ARRAY_SIZE];

            if (!move_is_allowed(moves_555[move_index])) {
                continue;
            }
            memcpy(moved, marker, sizeof(moved));
            rotate_555(moved, scratch, CUBE_ARRAY_SIZE, moves_555[move_index]);
            for (unsigned int destination = 0; destination < ORBIT_SIZE; destination++) {
                unsigned int source = (unsigned char)moved[orbit_squares[orbit][destination]];

                if (!source || source > ORBIT_SIZE) {
                    fprintf(stderr, "ERROR: orbit %u is not closed under %s\n", orbit, move2str[moves_555[move_index]]);
                    exit(1);
                }
                move_bits[orbit][move_index][source - 1] = (uint16_t)(1U << destination);
            }
        }
    }
}

static int emit_solution(const struct root *root, unsigned int depth)
{
    printf("SOLUTION ROOT %s (%u steps):", root->id, depth);
    for (unsigned int index = 0; index < depth; index++) {
        printf(" %s", move2str[path[index]]);
    }
    printf("\n");
    return 1;
}

static int search(
    const struct root *root,
    const uint16_t masks[ORBIT_COUNT],
    unsigned int depth,
    unsigned int threshold,
    move_type previous)
{
    unsigned char cost = table_cost(masks);

    if (cost == UINT8_MAX || depth + cost > threshold) {
        return 0;
    }
    if (!cost) {
        return emit_solution(root, depth);
    }
    if (depth >= threshold) {
        return 0;
    }
    for (unsigned int legal = 0; legal < legal_move_count[previous]; legal++) {
        unsigned int move_index = legal_move_index[previous][legal];
        uint16_t child[ORBIT_COUNT];

        for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
            child[orbit] = apply_move(masks[orbit], move_bits[orbit][move_index]);
        }
        path[depth] = moves_555[move_index];
        if (search(root, child, depth + 1, threshold, moves_555[move_index])) {
            return 1;
        }
    }
    path[depth] = MOVE_NONE;
    return 0;
}

static void append_root(struct root **roots, size_t *count, size_t *capacity, const struct root *root)
{
    if (*count == *capacity) {
        size_t new_capacity = *capacity ? *capacity * 2 : 512;
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

static void load_roots(const char *filename, struct root **roots, size_t *root_count)
{
    FILE *file = fopen(filename, "r");
    char line[256];
    size_t capacity = 0;
    unsigned int line_number = 0;

    if (!file) {
        fprintf(stderr, "ERROR: could not open roots file %s\n", filename);
        exit(1);
    }
    while (fgets(line, sizeof(line), file)) {
        struct root root;
        uint64_t rank;
        char trailing;
        char *hash = strchr(line, '#');

        line_number++;
        if (hash) {
            *hash = '\0';
        }
        if (line[0] == '\0' || line[0] == '\n') {
            continue;
        }
        memset(&root, 0, sizeof(root));
        if (sscanf(line, "%31[^,],%" SCNu64 " %c", root.id, &rank, &trailing) != 2 ||
                !grouped_unrank(rank, root.masks)) {
            fprintf(stderr, "ERROR: roots file line %u must be ID,RANK\n", line_number);
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
    const char *cost_filename = NULL;
    unsigned int max_threshold = 2;
    int print_ranks = 0;
    int print_legal_moves = 0;
    struct root *roots = NULL;
    unsigned char *solved = NULL;
    size_t root_count = 0;
    unsigned int found = 0;

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--roots-file") && index + 1 < argc) {
            roots_filename = argv[++index];
        } else if (!strcmp(argv[index], "--cost-table") && index + 1 < argc) {
            cost_filename = argv[++index];
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
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
    if (!roots_filename || !cost_filename || max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 2;
    }

    init_binom();
    ida_init_move_tables(
        moves_555, MOVE_COUNT_555, move_is_allowed,
        legal_move_count, legal_move_index, inverse_move
    );
    init_permutations();
    {
        struct mapped_cost_file mapped = ida_map_cost_file(cost_filename, RANK_UNIVERSE);
        costs_fd = mapped.fd;
        costs = mapped.costs;
    }
    load_roots(roots_filename, &roots, &root_count);
    solved = calloc(root_count, sizeof(*solved));
    if (!root_count || !solved) {
        fprintf(stderr, "ERROR: no roots or could not allocate solved flags\n");
        return 1;
    }
    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_555[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }
    for (size_t index = 0; index < root_count; index++) {
        roots[index].initial_cost = table_cost(roots[index].masks);
        if (print_ranks) {
            printf("ROOT %s RANK %" PRIu64 " COST %u\n",
                   roots[index].id, grouped_rank(roots[index].masks), roots[index].initial_cost);
        }
    }
    for (unsigned int threshold = 0; threshold <= max_threshold; threshold++) {
        for (size_t index = 0; index < root_count; index++) {
            if (solved[index] || roots[index].initial_cost != threshold) {
                continue;
            }
            if (search(&roots[index], roots[index].masks, 0, threshold, MOVE_NONE)) {
                solved[index] = 1;
                found++;
            }
        }
    }

    ida_unmap_cost_file(costs_fd, costs, RANK_UNIVERSE);
    free(solved);
    free(roots);
    return found ? 0 : 1;
}
