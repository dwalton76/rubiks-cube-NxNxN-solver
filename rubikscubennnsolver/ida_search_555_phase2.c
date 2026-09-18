#include <ctype.h>
#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ida_search_core.h"

#define CUBE_SIZE 5
#define CUBE_ARRAY_SIZE 151
#define GROUP_SIZE 16
#define SELECTED_COUNT 8
#define GROUP_UNIVERSE UINT64_C(12870)
#define DEFAULT_MAX_THRESHOLD 24
#define MAX_THRESHOLD 40
#define ROOT_ID_SIZE 128
#define PARITY_UNSET 0
#define PARITY_ODD 1
#define PARITY_EVEN 2

static const unsigned int t_squares[GROUP_SIZE] = {
    8, 12, 14, 18, 58, 62, 64, 68, 108, 112, 114, 118, 133, 137, 139, 143,
};
static const unsigned int x_squares[GROUP_SIZE] = {
    7, 9, 17, 19, 57, 59, 67, 69, 107, 109, 117, 119, 132, 134, 142, 144,
};

struct root {
    char id[ROOT_ID_SIZE];
    uint16_t t_mask;
    uint16_t x_mask;
    unsigned char initial_cost;
};

static unsigned char *t_costs;
static unsigned char *x_costs;
static int t_fd = -1;
static int x_fd = -1;
static uint16_t t_move_bits[MOVE_COUNT_555][GROUP_SIZE];
static uint16_t x_move_bits[MOVE_COUNT_555][GROUP_SIZE];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
static move_type path[MAX_THRESHOLD + 1];
static unsigned int solution_limit = 1;
static unsigned int solution_count;
static unsigned char parity_requirement;

static void usage(const char *program)
{
    printf(
        "usage: %s (--kociemba STATE | --roots-file FILE) "
        "--t-center-cost FILE --x-center-cost FILE "
        "(--orbit0-need-even-w | --orbit0-need-odd-w) "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--solution-count N] "
        "[--print-ranks] [--print-legal-moves]\n",
        program
    );
    printf("roots file: ID,T_RANK,X_RANK (one root per line; # comments allowed)\n");
}

/* Exact lexicographic multiset rank, with selected F as the lower symbol. */
static uint64_t combination_rank(uint16_t selected)
{
    uint64_t rank = 0;
    unsigned int remaining = SELECTED_COUNT;

    if (__builtin_popcount((unsigned int)selected) != SELECTED_COUNT) {
        return UINT64_MAX;
    }
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        unsigned int after = GROUP_SIZE - position - 1;

        if (selected & (UINT16_C(1) << position)) {
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

    if (rank >= GROUP_UNIVERSE) {
        return UINT16_MAX;
    }
    for (unsigned int position = 0; position < GROUP_SIZE && remaining; position++) {
        unsigned int after = GROUP_SIZE - position - 1;
        uint64_t selected_prefix = binom[after][remaining - 1];

        if (rank < selected_prefix) {
            mask |= UINT16_C(1) << position;
            remaining--;
        } else {
            rank -= selected_prefix;
        }
    }
    return remaining ? UINT16_MAX : mask;
}

static uint16_t mask_from_cube(const char cube[CUBE_ARRAY_SIZE], const unsigned int squares[GROUP_SIZE])
{
    uint16_t mask = 0;

    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        char sticker = cube[squares[position]];

        if (sticker == 'F' || sticker == 'B') {
            mask |= UINT16_C(1) << position;
        }
    }
    return __builtin_popcount((unsigned int)mask) == SELECTED_COUNT ? mask : UINT16_MAX;
}

static uint16_t apply_move(uint16_t mask, const uint16_t bits[GROUP_SIZE])
{
    uint16_t result = 0;

    while (mask) {
        unsigned int source = (unsigned int)__builtin_ctz((unsigned int)mask);
        result |= bits[source];
        mask &= (uint16_t)(mask - 1);
    }
    return result;
}

static unsigned char table_cost(const unsigned char *costs, uint16_t mask)
{
    uint64_t rank = combination_rank(mask);

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
    return (parity_requirement == PARITY_ODD && parity) ||
           (parity_requirement == PARITY_EVEN && !parity);
}

static unsigned char heuristic(uint16_t t_mask, uint16_t x_mask, unsigned char parity)
{
    unsigned char t_cost = table_cost(t_costs, t_mask);
    unsigned char x_cost = table_cost(x_costs, x_mask);
    unsigned char cost;

    if (t_cost == UINT8_MAX || x_cost == UINT8_MAX) {
        return UINT8_MAX;
    }
    cost = t_cost > x_cost ? t_cost : x_cost;
    return cost ? cost : parity_floor(parity);
}

static int move_is_allowed(move_type move)
{
    switch (move) {
        case Uw:
        case Uw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Dw:
        case Dw_PRIME:
            return 0;
        default:
            return 1;
    }
}

static unsigned char move_parity(move_type move)
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

static void init_permutation(
    const unsigned int squares[GROUP_SIZE],
    uint16_t destination_bits[MOVE_COUNT_555][GROUP_SIZE])
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

        if (!move_is_allowed(moves_555[move_index])) {
            continue;
        }
        memcpy(moved, marker, sizeof(moved));
        rotate_555_centers(moved, scratch, CUBE_ARRAY_SIZE, moves_555[move_index]);
        for (unsigned int destination = 0; destination < GROUP_SIZE; destination++) {
            unsigned int source_square = (unsigned char)moved[squares[destination]];
            int source = source_square < CUBE_ARRAY_SIZE ? square_to_position[source_square] : -1;

            if (source < 0) {
                fprintf(stderr, "ERROR: center orbit is not closed under %s\n", move2str[moves_555[move_index]]);
                exit(1);
            }
            destination_bits[move_index][source] = UINT16_C(1) << destination;
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
    unsigned int depth,
    unsigned int threshold,
    move_type previous,
    unsigned char parity)
{
    unsigned char cost = heuristic(t_mask, x_mask, parity);

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
        unsigned char child_parity = parity ^ move_parity(move);

        if (depth + 1 == threshold && !parity_is_goal(child_parity)) {
            continue;
        }
        path[depth] = move;
        if (search(
                root,
                apply_move(t_mask, t_move_bits[move_index]),
                apply_move(x_mask, x_move_bits[move_index]),
                depth + 1,
                threshold,
                move,
                child_parity)) {
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
        uint64_t t_rank;
        uint64_t x_rank;
        char trailing;
        char *cursor = line;
        int fields;

        line_number++;
        while (isspace((unsigned char)*cursor)) {
            cursor++;
        }
        if (!*cursor || *cursor == '#') {
            continue;
        }
        memset(&root, 0, sizeof(root));
        fields = sscanf(
            cursor, " %127[^, \t],%" SCNu64 ",%" SCNu64 " %c",
            root.id, &t_rank, &x_rank, &trailing
        );
        if (fields != 3) {
            fields = sscanf(
                cursor, " %127s %" SCNu64 " %" SCNu64 " %c",
                root.id, &t_rank, &x_rank, &trailing
            );
        }
        if (fields != 3 || t_rank >= GROUP_UNIVERSE || x_rank >= GROUP_UNIVERSE) {
            fprintf(stderr, "ERROR: invalid roots file line %u\n", line_number);
            exit(1);
        }
        root.t_mask = combination_unrank(t_rank);
        root.x_mask = combination_unrank(x_rank);
        append_root(roots, root_count, &capacity, &root);
    }
    fclose(file);
    if (!*root_count) {
        fprintf(stderr, "ERROR: roots file contains no roots\n");
        exit(1);
    }
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *roots_filename = NULL;
    const char *t_filename = NULL;
    const char *x_filename = NULL;
    unsigned int min_threshold = 0;
    unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
    int print_ranks = 0;
    int print_legal_moves = 0;
    struct root *roots = NULL;
    size_t root_count = 0;
    size_t root_capacity = 0;

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--roots-file") && index + 1 < argc) {
            roots_filename = argv[++index];
        } else if (!strcmp(argv[index], "--t-center-cost") && index + 1 < argc) {
            t_filename = argv[++index];
        } else if (!strcmp(argv[index], "--x-center-cost") && index + 1 < argc) {
            x_filename = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--solution-count") && index + 1 < argc) {
            solution_limit = (unsigned int)strtoul(argv[++index], NULL, 10);
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
    if ((!kociemba && !roots_filename) || (kociemba && roots_filename) ||
            !t_filename || !x_filename || parity_requirement == PARITY_UNSET ||
            min_threshold > max_threshold || max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 2;
    }

    init_binom();
    ida_init_move_tables(
        moves_555, MOVE_COUNT_555, move_is_allowed,
        legal_move_count, legal_move_index, inverse_move
    );
    init_permutation(t_squares, t_move_bits);
    init_permutation(x_squares, x_move_bits);
    {
        struct mapped_cost_file mapped = ida_map_cost_file(t_filename, GROUP_UNIVERSE);
        t_fd = mapped.fd;
        t_costs = mapped.costs;
        mapped = ida_map_cost_file(x_filename, GROUP_UNIVERSE);
        x_fd = mapped.fd;
        x_costs = mapped.costs;
    }

    if (kociemba) {
        char cube[CUBE_ARRAY_SIZE];
        struct root root;

        memset(&root, 0, sizeof(root));
        strcpy(root.id, "0");
        ida_init_cube(cube, CUBE_SIZE, kociemba);
        root.t_mask = mask_from_cube(cube, t_squares);
        root.x_mask = mask_from_cube(cube, x_squares);
        if (root.t_mask == UINT16_MAX || root.x_mask == UINT16_MAX) {
            fprintf(stderr, "ERROR: each center coordinate must contain eight F/B stickers\n");
            ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
            ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
            return 1;
        }
        append_root(&roots, &root_count, &root_capacity, &root);
    } else {
        load_roots_file(roots_filename, &roots, &root_count);
    }

    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_555[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }
    for (size_t index = 0; index < root_count; index++) {
        struct root *root = &roots[index];

        root->initial_cost = heuristic(root->t_mask, root->x_mask, 0);
        if (root->initial_cost == UINT8_MAX) {
            fprintf(stderr, "ERROR: root %s is absent from a ranked cost table\n", root->id);
            free(roots);
            ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
            ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
            return 1;
        }
        if (print_ranks) {
            printf(
                "ROOT %s T_RANK %" PRIu64 " T_COST %u X_RANK %" PRIu64
                " X_COST %u COST %u\n",
                root->id, combination_rank(root->t_mask), table_cost(t_costs, root->t_mask),
                combination_rank(root->x_mask), table_cost(x_costs, root->x_mask),
                root->initial_cost
            );
        }
    }

    for (unsigned int threshold = min_threshold; threshold <= max_threshold; threshold++) {
        unsigned int before = solution_count;

        for (size_t index = 0; index < root_count; index++) {
            struct root *root = &roots[index];

            if (root->initial_cost > threshold) {
                continue;
            }
            if (search(root, root->t_mask, root->x_mask, 0, threshold, MOVE_NONE, 0)) {
                break;
            }
        }
        if (solution_count != before) {
            break;
        }
    }

    free(roots);
    ida_unmap_cost_file(t_fd, t_costs, GROUP_UNIVERSE);
    ida_unmap_cost_file(x_fd, x_costs, GROUP_UNIVERSE);
    if (!solution_count) {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
        return 1;
    }
    return 0;
}
