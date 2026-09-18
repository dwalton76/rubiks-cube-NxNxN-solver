#include <inttypes.h>
#include <limits.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ida_search_core.h"

#define CUBE_ARRAY_SIZE 151
#define BINARY_GROUPS 4
#define GROUP_SIZE 8
#define BINARY_UNIVERSE 70
#define WING_UNIVERSE 1680
#define CENTERS_UNIVERSE UINT64_C(24010000)
#define COMBO_UNIVERSE UINT64_C(576240000)
#define DEFAULT_MAX_THRESHOLD 20
#define MAX_THRESHOLD 40
#define ROOT_ID_SIZE 128

static const unsigned int center_squares[BINARY_GROUPS][GROUP_SIZE] = {
    {33, 37, 39, 43, 83, 87, 89, 93},
    {32, 34, 42, 44, 82, 84, 92, 94},
    {58, 62, 64, 68, 108, 112, 114, 118},
    {57, 59, 67, 69, 107, 109, 117, 119},
};
static const unsigned int wing_squares[2][GROUP_SIZE] = {
    {2, 24, 35, 41, 85, 91, 127, 149},
    {4, 22, 31, 45, 81, 95, 129, 147},
};
static const unsigned int wing_partners[2][GROUP_SIZE] = {
    {104, 54, 56, 120, 106, 70, 72, 122},
    {102, 52, 110, 66, 60, 116, 74, 124},
};
static const unsigned int midge_squares[GROUP_SIZE] = {
    3, 23, 36, 40, 86, 90, 128, 148,
};
static const unsigned int midge_partners[GROUP_SIZE] = {
    103, 53, 115, 61, 65, 111, 73, 123,
};

struct coordinate {
    uint8_t centers[BINARY_GROUPS];
    uint8_t high_fb[2];
    uint16_t high_wing;
    uint8_t low_fb[2];
    uint16_t low_wing;
    uint16_t midge;
};

struct root {
    char id[ROOT_ID_SIZE];
    struct coordinate coordinate;
    unsigned char initial_cost;
};

static unsigned char *centers_costs;
static unsigned char *high_costs;
static unsigned char *low_costs;
static int centers_fd = -1;
static int high_fd = -1;
static int low_fd = -1;
static uint8_t binary_transition[BINARY_GROUPS + 1][BINARY_UNIVERSE][MOVE_COUNT_555];
static uint16_t wing_transition[3][WING_UNIVERSE][MOVE_COUNT_555];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX];
static move_type inverse_move[MOVE_MAX];
static move_type path[MAX_THRESHOLD + 1];
static unsigned int solution_limit = 1;
static unsigned int solutions_found;
static int find_extra;

static void usage(const char *program)
{
    printf(
        "usage: %s --roots-file FILE --centers-cost FILE "
        "--high-combo-cost FILE --low-combo-cost FILE "
        "[--min-ida-threshold N] [--max-ida-threshold N] "
        "[--solution-count N] [--find-extra] [--print-ranks] "
        "[--print-legal-moves]\n",
        program
    );
    printf(
        "roots file: ID,CENTERS_RANK,HIGH_RANK,LOW_RANK,MIDGE_RANK "
        "(one root per line; # comments allowed)\n"
    );
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
        case U:
        case U_PRIME:
        case D:
        case D_PRIME:
            return 0;
        default:
            return 1;
    }
}

static uint8_t binary_rank(uint8_t mask)
{
    uint64_t rank = 0;
    unsigned int remaining = 4;

    if (__builtin_popcount((unsigned int)mask) != 4) {
        return UINT8_MAX;
    }
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        unsigned int after = GROUP_SIZE - position - 1;

        if (mask & (1U << position)) {
            remaining--;
        } else if (remaining) {
            rank += binom[after][remaining - 1];
        }
    }
    return remaining ? UINT8_MAX : (uint8_t)rank;
}

static uint8_t binary_unrank(uint64_t rank)
{
    uint8_t mask = 0;
    unsigned int remaining = 4;

    if (rank >= BINARY_UNIVERSE) {
        return UINT8_MAX;
    }
    for (unsigned int position = 0; position < GROUP_SIZE && remaining; position++) {
        unsigned int after = GROUP_SIZE - position - 1;
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

static unsigned int factorial(unsigned int value)
{
    unsigned int result = 1;

    while (value > 1) {
        result *= value--;
    }
    return result;
}

static unsigned int multiset_count(const unsigned int counts[5])
{
    unsigned int total = 0;
    unsigned int result;

    for (unsigned int symbol = 0; symbol < 5; symbol++) {
        total += counts[symbol];
    }
    result = factorial(total);
    for (unsigned int symbol = 0; symbol < 5; symbol++) {
        result /= factorial(counts[symbol]);
    }
    return result;
}

static uint16_t wing_rank(const uint8_t state[GROUP_SIZE])
{
    unsigned int counts[5] = {1, 1, 1, 1, 4};
    unsigned int rank = 0;

    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        unsigned int actual = state[position];

        if (actual >= 5 || !counts[actual]) {
            return UINT16_MAX;
        }
        for (unsigned int symbol = 0; symbol < actual; symbol++) {
            if (counts[symbol]) {
                counts[symbol]--;
                rank += multiset_count(counts);
                counts[symbol]++;
            }
        }
        counts[actual]--;
    }
    return (uint16_t)rank;
}

static int wing_unrank(uint64_t rank, uint8_t state[GROUP_SIZE])
{
    unsigned int counts[5] = {1, 1, 1, 1, 4};

    if (rank >= WING_UNIVERSE) {
        return 0;
    }
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        int selected = 0;

        for (unsigned int symbol = 0; symbol < 5; symbol++) {
            unsigned int block;

            if (!counts[symbol]) {
                continue;
            }
            counts[symbol]--;
            block = multiset_count(counts);
            if (rank < block) {
                state[position] = (uint8_t)symbol;
                selected = 1;
                break;
            }
            rank -= block;
            counts[symbol]++;
        }
        if (!selected) {
            return 0;
        }
    }
    return 1;
}

static uint8_t permute_mask(uint8_t mask, const uint8_t permutation[GROUP_SIZE])
{
    uint8_t result = 0;

    while (mask) {
        unsigned int source = (unsigned int)__builtin_ctz((unsigned int)mask);
        result |= (uint8_t)(1U << permutation[source]);
        mask &= (uint8_t)(mask - 1);
    }
    return result;
}

static void init_center_transitions(unsigned int group)
{
    char marker[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];
    int square_to_position[CUBE_ARRAY_SIZE];

    for (unsigned int square = 0; square < CUBE_ARRAY_SIZE; square++) {
        marker[square] = (char)square;
        square_to_position[square] = -1;
    }
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        square_to_position[center_squares[group][position]] = (int)position;
    }
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        uint8_t permutation[GROUP_SIZE] = {0};
        char moved[CUBE_ARRAY_SIZE];

        if (!move_is_allowed(moves_555[move_index])) {
            continue;
        }
        memcpy(moved, marker, sizeof(moved));
        rotate_555_centers(moved, scratch, CUBE_ARRAY_SIZE, moves_555[move_index]);
        for (unsigned int destination = 0; destination < GROUP_SIZE; destination++) {
            unsigned int source_square = (unsigned char)moved[center_squares[group][destination]];
            int source = source_square < CUBE_ARRAY_SIZE ? square_to_position[source_square] : -1;

            if (source < 0) {
                fprintf(stderr, "ERROR: center group %u is not closed under %s\n",
                        group, move2str[moves_555[move_index]]);
                exit(1);
            }
            permutation[source] = (uint8_t)destination;
        }
        for (unsigned int rank = 0; rank < BINARY_UNIVERSE; rank++) {
            binary_transition[group][rank][move_index] =
                binary_rank(permute_mask(binary_unrank(rank), permutation));
        }
    }
}

static void init_edge_permutation(
    const unsigned int squares[GROUP_SIZE],
    const unsigned int partners[GROUP_SIZE],
    uint8_t permutation[MOVE_COUNT_555][GROUP_SIZE],
    const char *name)
{
    char marker[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];

    memset(marker, 0, sizeof(marker));
    marker[0] = 'x';
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
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
        for (unsigned int destination = 0; destination < GROUP_SIZE; destination++) {
            unsigned int source = (unsigned char)moved[squares[destination]];

            if (!source || source > GROUP_SIZE) {
                fprintf(stderr, "ERROR: %s is not closed under %s\n",
                        name, move2str[moves_555[move_index]]);
                exit(1);
            }
            permutation[move_index][source - 1] = (uint8_t)destination;
        }
    }
}

static void init_edge_transitions(void)
{
    uint8_t permutations[3][MOVE_COUNT_555][GROUP_SIZE] = {{{0}}};

    init_edge_permutation(wing_squares[0], wing_partners[0], permutations[0], "high wing group");
    init_edge_permutation(wing_squares[1], wing_partners[1], permutations[1], "low wing group");
    init_edge_permutation(midge_squares, midge_partners, permutations[2], "midge group");
    for (unsigned int orbit = 0; orbit < 3; orbit++) {
        for (unsigned int rank = 0; rank < WING_UNIVERSE; rank++) {
            uint8_t state[GROUP_SIZE];

            wing_unrank(rank, state);
            for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
                uint8_t child[GROUP_SIZE];

                if (!move_is_allowed(moves_555[move_index])) {
                    continue;
                }
                for (unsigned int source = 0; source < GROUP_SIZE; source++) {
                    child[permutations[orbit][move_index][source]] = state[source];
                }
                wing_transition[orbit][rank][move_index] = wing_rank(child);
            }
        }
    }
    for (unsigned int rank = 0; rank < BINARY_UNIVERSE; rank++) {
        uint8_t mask = binary_unrank(rank);

        for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
            if (move_is_allowed(moves_555[move_index])) {
                binary_transition[BINARY_GROUPS][rank][move_index] =
                    binary_rank(permute_mask(mask, permutations[2][move_index]));
            }
        }
    }
}

static uint64_t centers_rank(const struct coordinate *coordinate)
{
    uint64_t rank = 0;

    for (unsigned int group = 0; group < BINARY_GROUPS; group++) {
        rank = rank * BINARY_UNIVERSE + coordinate->centers[group];
    }
    return rank;
}

static uint64_t combo_rank(const uint8_t fb[2], uint16_t wing, uint8_t midge)
{
    return (((uint64_t)fb[0] * BINARY_UNIVERSE + fb[1]) * WING_UNIVERSE + wing) *
            BINARY_UNIVERSE + midge;
}

static int centers_unrank(uint64_t rank, struct coordinate *coordinate)
{
    if (rank >= CENTERS_UNIVERSE) {
        return 0;
    }
    for (int group = BINARY_GROUPS - 1; group >= 0; group--) {
        coordinate->centers[group] = (uint8_t)(rank % BINARY_UNIVERSE);
        rank /= BINARY_UNIVERSE;
    }
    return 1;
}

static int combo_unrank(uint64_t rank, uint8_t fb[2], uint16_t *wing, uint8_t *midge)
{
    if (rank >= COMBO_UNIVERSE) {
        return 0;
    }
    *midge = (uint8_t)(rank % BINARY_UNIVERSE);
    rank /= BINARY_UNIVERSE;
    *wing = (uint16_t)(rank % WING_UNIVERSE);
    rank /= WING_UNIVERSE;
    fb[1] = (uint8_t)(rank % BINARY_UNIVERSE);
    fb[0] = (uint8_t)(rank / BINARY_UNIVERSE);
    return 1;
}

static unsigned char table_cost(const unsigned char *costs, uint64_t rank)
{
    return decode_cost_byte(costs[rank]);
}

static unsigned char heuristic(const struct coordinate *coordinate)
{
    uint8_t midge_state[GROUP_SIZE];
    uint8_t midge_mask = 0;
    uint8_t midge_rank;
    unsigned char center = table_cost(centers_costs, centers_rank(coordinate));

    wing_unrank(coordinate->midge, midge_state);
    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        if (midge_state[position] != 4) {
            midge_mask |= (uint8_t)(1U << position);
        }
    }
    midge_rank = binary_rank(midge_mask);
    unsigned char high = table_cost(
        high_costs,
        combo_rank(coordinate->high_fb, coordinate->high_wing, midge_rank)
    );
    unsigned char low = table_cost(
        low_costs,
        combo_rank(coordinate->low_fb, coordinate->low_wing, midge_rank)
    );
    unsigned char result = center;

    if (center == UINT8_MAX || high == UINT8_MAX || low == UINT8_MAX) {
        return UINT8_MAX;
    }
    if (high > result) {
        result = high;
    }
    if (low > result) {
        result = low;
    }
    return result;
}

static int exact_goal(const struct coordinate *coordinate)
{
    uint8_t high[GROUP_SIZE];
    uint8_t low[GROUP_SIZE];
    uint8_t midge[GROUP_SIZE];

    wing_unrank(coordinate->high_wing, high);
    wing_unrank(coordinate->low_wing, low);
    wing_unrank(coordinate->midge, midge);

    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
        int parked = position >= 2 && position <= 5;

        if ((midge[position] != 4) != parked ||
                (high[position] != 4) != parked ||
                (low[position] != 4) != parked) {
            return 0;
        }
    }
    return high[2] == midge[3] &&
           high[3] == midge[2] &&
           high[4] == midge[5] &&
           high[5] == midge[4] &&
           low[2] == midge[2] &&
           low[3] == midge[3] &&
           low[4] == midge[4] &&
           low[5] == midge[5];
}

static struct coordinate apply_move(const struct coordinate *coordinate, unsigned int move_index)
{
    struct coordinate child;

    for (unsigned int group = 0; group < BINARY_GROUPS; group++) {
        child.centers[group] = binary_transition[group][coordinate->centers[group]][move_index];
    }
    child.high_fb[0] = binary_transition[2][coordinate->high_fb[0]][move_index];
    child.high_fb[1] = binary_transition[3][coordinate->high_fb[1]][move_index];
    child.high_wing = wing_transition[0][coordinate->high_wing][move_index];
    child.low_fb[0] = binary_transition[2][coordinate->low_fb[0]][move_index];
    child.low_fb[1] = binary_transition[3][coordinate->low_fb[1]][move_index];
    child.low_wing = wing_transition[1][coordinate->low_wing][move_index];
    child.midge = wing_transition[2][coordinate->midge][move_index];
    return child;
}

static int emit_solution(const struct root *root, unsigned int depth)
{
    printf("SOLUTION ROOT %s (%u steps):", root->id, depth);
    for (unsigned int index = 0; index < depth; index++) {
        printf(" %s", move2str[path[index]]);
    }
    printf("\n");
    solutions_found++;
    if (!find_extra) {
        return 1;
    }
    return solution_limit && solutions_found >= solution_limit;
}

static int search(
    const struct root *root,
    const struct coordinate *coordinate,
    unsigned int depth,
    unsigned int threshold,
    move_type previous)
{
    unsigned char cost = heuristic(coordinate);

    if (cost == UINT8_MAX || depth + cost > threshold) {
        return 0;
    }
    if (!cost && exact_goal(coordinate)) {
        return depth == threshold ? emit_solution(root, depth) : 0;
    }
    if (depth >= threshold) {
        return 0;
    }
    for (unsigned int legal = 0; legal < legal_move_count[previous]; legal++) {
        unsigned int move_index = legal_move_index[previous][legal];
        struct coordinate child = apply_move(coordinate, move_index);

        path[depth] = moves_555[move_index];
        if (search(root, &child, depth + 1, threshold, moves_555[move_index])) {
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
    uint64_t centers;
    uint64_t high;
    uint64_t low;
    uint64_t midge;
    char trailing;

    memset(root, 0, sizeof(*root));
    if (sscanf(
            line,
            "%127[^,],%" SCNu64 ",%" SCNu64 ",%" SCNu64 ",%" SCNu64 " %c",
            root->id, &centers, &high, &low, &midge, &trailing
        ) != 5 ||
            !centers_unrank(centers, &root->coordinate) ||
            !combo_unrank(
                high,
                root->coordinate.high_fb,
                &root->coordinate.high_wing,
                &(uint8_t){0}
            ) ||
            !combo_unrank(
                low,
                root->coordinate.low_fb,
                &root->coordinate.low_wing,
                &(uint8_t){0}
            ) ||
            midge >= WING_UNIVERSE) {
        fprintf(
            stderr,
            "ERROR: roots file line %u must be "
            "ID,CENTERS_RANK,HIGH_RANK,LOW_RANK,MIDGE_RANK with valid ranks\n",
            line_number
        );
        return 0;
    }
    root->coordinate.midge = (uint16_t)midge;
    return 1;
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
        char *content = line;

        line_number++;
        hash = strchr(line, '#');
        if (hash) {
            *hash = '\0';
        }
        while (*content == ' ' || *content == '\t') {
            content++;
        }
        if (*content == '\0' || *content == '\n' || *content == '\r') {
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
    const char *centers_filename = NULL;
    const char *high_filename = NULL;
    const char *low_filename = NULL;
    unsigned int min_threshold = 0;
    unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
    int print_ranks = 0;
    int print_legal_moves = 0;
    struct root *roots = NULL;
    size_t root_count = 0;

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--roots-file") && index + 1 < argc) {
            roots_filename = argv[++index];
        } else if (!strcmp(argv[index], "--centers-cost") && index + 1 < argc) {
            centers_filename = argv[++index];
        } else if (!strcmp(argv[index], "--high-combo-cost") && index + 1 < argc) {
            high_filename = argv[++index];
        } else if (!strcmp(argv[index], "--low-combo-cost") && index + 1 < argc) {
            low_filename = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--solution-count") && index + 1 < argc) {
            solution_limit = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--find-extra")) {
            find_extra = 1;
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
    if (!roots_filename || !centers_filename || !high_filename || !low_filename ||
            min_threshold > max_threshold || max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 2;
    }

    init_binom();
    ida_init_move_tables(
        moves_555, MOVE_COUNT_555, move_is_allowed,
        legal_move_count, legal_move_index, inverse_move
    );
    for (unsigned int group = 0; group < BINARY_GROUPS; group++) {
        init_center_transitions(group);
    }
    init_edge_transitions();
    {
        struct mapped_cost_file mapped = ida_map_cost_file(centers_filename, CENTERS_UNIVERSE);
        centers_fd = mapped.fd;
        centers_costs = mapped.costs;
        mapped = ida_map_cost_file(high_filename, COMBO_UNIVERSE);
        high_fd = mapped.fd;
        high_costs = mapped.costs;
        mapped = ida_map_cost_file(low_filename, COMBO_UNIVERSE);
        low_fd = mapped.fd;
        low_costs = mapped.costs;
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
            roots[index].initial_cost = heuristic(&roots[index].coordinate);
            if (roots[index].initial_cost == UINT8_MAX) {
                fprintf(stderr, "ERROR: root %s is absent from a ranked cost table\n", roots[index].id);
                return 1;
            }
            if (print_ranks) {
                printf(
                    "ROOT %s CENTERS_RANK %" PRIu64 " HIGH_RANK %" PRIu64
                    " LOW_RANK %" PRIu64 " COST %u\n",
                    roots[index].id,
                    centers_rank(&roots[index].coordinate),
                    combo_rank(
                        roots[index].coordinate.high_fb,
                        roots[index].coordinate.high_wing,
                        binary_rank(
                            ({ uint8_t state[GROUP_SIZE], mask = 0;
                               wing_unrank(roots[index].coordinate.midge, state);
                               for (unsigned int p = 0; p < GROUP_SIZE; p++)
                                   if (state[p] != 4) mask |= (uint8_t)(1U << p);
                               mask; })
                        )
                    ),
                    combo_rank(
                        roots[index].coordinate.low_fb,
                        roots[index].coordinate.low_wing,
                        binary_rank(
                            ({ uint8_t state[GROUP_SIZE], mask = 0;
                               wing_unrank(roots[index].coordinate.midge, state);
                               for (unsigned int p = 0; p < GROUP_SIZE; p++)
                                   if (state[p] != 4) mask |= (uint8_t)(1U << p);
                               mask; })
                        )
                    ),
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
        unsigned int before = solutions_found;
        int stop = 0;

        for (size_t index = 0; index < root_count && !stop; index++) {
            if (roots[index].initial_cost <= threshold) {
                stop = search(
                    &roots[index],
                    &roots[index].coordinate,
                    0,
                    threshold,
                    MOVE_NONE
                );
            }
        }
        if (solutions_found != before) {
            break;
        }
    }

    ida_unmap_cost_file(centers_fd, centers_costs, CENTERS_UNIVERSE);
    ida_unmap_cost_file(high_fd, high_costs, COMBO_UNIVERSE);
    ida_unmap_cost_file(low_fd, low_costs, COMBO_UNIVERSE);
    free(roots);
    if (!solutions_found) {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
        return 1;
    }
    return 0;
}
