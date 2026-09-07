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

struct root {
    char id[ROOT_ID_SIZE];
    uint16_t lr_t_mask;
    uint16_t lr_x_mask;
    uint32_t outer_mask;
    uint16_t inner_mask;
    unsigned char initial_cost;
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
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
static move_type path[MAX_THRESHOLD + 1];
static unsigned int solution_limit = 1;
static unsigned int solution_count;

static void usage(const char *program)
{
    printf(
        "usage: %s (--kociemba STATE | --roots-file FILE) "
        "--lr-center-cost FILE --eo-outer-cost FILE --eo-inner-cost FILE "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--solution-count N] "
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

static unsigned char table_cost(const unsigned char *costs, uint64_t rank, uint64_t universe)
{
    return rank < universe ? decode_cost_byte(costs[rank]) : UINT8_MAX;
}

static unsigned char heuristic(uint16_t t_mask, uint16_t x_mask, uint32_t outer_mask, uint16_t inner_mask)
{
    uint64_t centers = lr_rank(t_mask, x_mask);
    uint64_t outer = combination_rank_n(outer_mask, OUTER_SIZE, OUTER_SELECTED);
    unsigned char lr_cost = table_cost(lr_costs, centers, LR_UNIVERSE);
    unsigned char outer_cost = table_cost(outer_costs, outer, OUTER_UNIVERSE);
    unsigned char inner_cost = table_cost(inner_costs, inner_mask, INNER_UNIVERSE);
    unsigned char cost = lr_cost;

    if (lr_cost == UINT8_MAX || outer_cost == UINT8_MAX || inner_cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    if (outer_cost > cost) {
        cost = outer_cost;
    }
    if (inner_cost > cost) {
        cost = inner_cost;
    }
    return cost;
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

static int emit_solution(const struct root *root, unsigned int depth)
{
    printf("SOLUTION ROOT %s (%u steps):", root->id, depth);
    for (unsigned int index = 0; index < depth; index++) {
        printf(" %s", move2str[path[index]]);
    }
    printf("\n");
    solution_count++;
    return solution_limit && solution_count >= solution_limit;
}

static int search(
    const struct root *root,
    uint16_t t_mask,
    uint16_t x_mask,
    uint32_t outer_mask,
    uint16_t inner_mask,
    unsigned int depth,
    unsigned int threshold,
    move_type previous)
{
    unsigned char cost = heuristic(t_mask, x_mask, outer_mask, inner_mask);

    if (cost == UINT8_MAX || depth + cost > threshold) {
        return 0;
    }
    if (!cost) {
        return depth == threshold ? emit_solution(root, depth) : 0;
    }
    if (depth >= threshold) {
        return 0;
    }

    for (unsigned int legal = 0; legal < legal_move_count[previous]; legal++) {
        unsigned int move_index = legal_move_index[previous][legal];
        move_type move = moves_555[move_index];

        path[depth] = move;
        if (search(
                root,
                apply_mask16(t_mask, lr_t_move_bits[move_index], 0, LR_GROUP_SIZE),
                apply_mask16(x_mask, lr_x_move_bits[move_index], 0, LR_GROUP_SIZE),
                apply_mask32(outer_mask, outer_move_bits[move_index]),
                apply_mask16(inner_mask, inner_move_bits[move_index], inner_flip[move_index], INNER_SIZE),
                depth + 1,
                threshold,
                move)) {
            return 1;
        }
    }
    path[depth] = MOVE_NONE;
    return 0;
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
    struct root *roots = NULL;
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
            roots[index].initial_cost = heuristic(
                roots[index].lr_t_mask,
                roots[index].lr_x_mask,
                roots[index].outer_mask,
                roots[index].inner_mask
            );
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

    for (unsigned int threshold = min_threshold; threshold <= max_threshold; threshold++) {
        unsigned int before = solution_count;

        for (size_t index = 0; index < root_count; index++) {
            if (roots[index].initial_cost > threshold) {
                continue;
            }
            if (search(
                    &roots[index],
                    roots[index].lr_t_mask,
                    roots[index].lr_x_mask,
                    roots[index].outer_mask,
                    roots[index].inner_mask,
                    0,
                    threshold,
                    MOVE_NONE)) {
                break;
            }
        }
        if (solution_count != before) {
            break;
        }
    }

    ida_unmap_cost_file(lr_fd, lr_costs, LR_UNIVERSE);
    ida_unmap_cost_file(outer_fd, outer_costs, OUTER_UNIVERSE);
    ida_unmap_cost_file(inner_fd, inner_costs, INNER_UNIVERSE);
    free(roots);
    if (!solution_count) {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
        return 1;
    }
    return 0;
}
