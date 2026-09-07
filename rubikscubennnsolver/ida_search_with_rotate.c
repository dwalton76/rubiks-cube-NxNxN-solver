#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <locale.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>

#include "ida_search_core.h"

#define CUBE_SIZE_555 5
#define CUBE_ARRAY_SIZE_555 151
#define COMPACT_CENTER_COUNT 24
#define RANK_SYMBOL_COUNT 3
#define RANK_UNIVERSE_555 UINT64_C(9465511770)
#define DEFAULT_MAX_IDA_THRESHOLD 20
#define MAX_IDA_THRESHOLD 99
#define MAX_THREADS 64
#define MAX_SPLIT_TASKS (MOVE_COUNT_555 * MOVE_COUNT_555)
#define NO_TASK UINT_MAX
// Off by default: measured hit rates are near zero because canonical move ordering already
// removes the common duplicates, and probing costs more than the few pruned subtrees save
#define DEFAULT_TT_BITS 0
#define MAX_TT_BITS 34
#define DEFAULT_PERIMETER_MAX_STATES UINT64_C(20000000)
#define PERIMETER_NOT_FOUND UINT32_MAX

static const unsigned int x_center_squares[COMPACT_CENTER_COUNT] = {
    7, 9, 17, 19, 32, 34, 42, 44, 57, 59, 67, 69,
    82, 84, 92, 94, 107, 109, 117, 119, 132, 134, 142, 144,
};

static const unsigned int t_center_squares[COMPACT_CENTER_COUNT] = {
    8, 12, 14, 18, 33, 37, 39, 43, 58, 62, 64, 68,
    83, 87, 89, 93, 108, 112, 114, 118, 133, 137, 139, 143,
};

static uint64_t binom[COMPACT_CENTER_COUNT + 1][COMPACT_CENTER_COUNT + 1];
static uint64_t rank_increment[9][9][9][RANK_SYMBOL_COUNT];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_555];
static unsigned char compact_move_source[MOVE_MAX][2][COMPACT_CENTER_COUNT];

// Restricting the last ply to wide moves is sound -- an outer move only permutes its own
// face's centers, so it can neither reach nor leave the staged goal -- but it saves nothing.
// The cost check ends the recursion long before depth reaches threshold - 1, so that ply is
// essentially never searched. Measured: identical node counts with and without it.
static move_type inverse_555[MOVE_MAX];
static unsigned char staged_symbol_by_color[UINT8_MAX + 1];
static unsigned char *x_costs = NULL;
static unsigned char *t_costs = NULL;
static move_type best_solution[MAX_IDA_THRESHOLD + 1];

// Two-move prefixes are numbered in serial DFS order. By default the first solution any
// worker finds wins and every other worker gives up: each threshold only yields solutions
// of one length, so finishing the lower numbered prefixes just picks a different solution
// of that same length. --serial-order instead abandons a subtree only once a lower numbered
// prefix has a solution, which makes the reported solution match a serial search.
static int stop_on_first_solution = 1;
static atomic_uint next_task;
static atomic_uint best_task = NO_TASK;
static pthread_mutex_t best_solution_lock = PTHREAD_MUTEX_INITIALIZER;
static struct {
    unsigned char first_index;
    unsigned char second_index;
} split_tasks[MAX_SPLIT_TASKS];
static unsigned int split_task_count;

// True once a solution this worker can no longer improve on has been recorded.
static int solution_supersedes(unsigned int task_id)
{
    unsigned int best = atomic_load_explicit(&best_task, memory_order_relaxed);

    return stop_on_first_solution ? best != NO_TASK : best < task_id;
}

// Records "this state with this previous move was searched to N remaining moves and failed".
// That verdict never expires, so entries stay useful across thresholds.
static _Atomic uint64_t *transposition_table = NULL;
static uint64_t transposition_mask = 0;
static uint64_t transposition_hits = 0;

/*
 * A solved-side perimeter entry.  X and T together identify the complete
 * projected center state.  Parent and move reconstruct the shortest path from
 * solved to this state; following inverse moves returns a meeting state to
 * solved.
 */
struct perimeter_entry {
    uint64_t x_rank;
    uint64_t t_rank;
    uint32_t parent;
    unsigned char move;
    unsigned char depth;
};

static struct perimeter_entry *perimeter_entries = NULL;
static uint32_t *perimeter_slots = NULL;
static uint64_t perimeter_slot_mask = 0;
static uint32_t perimeter_count = 0;
static unsigned char perimeter_depth = 0;
static uint64_t perimeter_hits = 0;

struct ranked_cost_file {
    int fd;
    unsigned char *costs;
};

struct heuristic_result {
    unsigned char cost;
    uint64_t x_rank;
    uint64_t t_rank;
};

struct compact_center_state {
    unsigned char x[COMPACT_CENTER_COUNT];
    unsigned char t[COMPACT_CENTER_COUNT];
};

struct worker {
    const struct compact_center_state *root_state;
    unsigned char threshold;
    unsigned int task_id;
    unsigned char aborted;
    uint64_t ida_count;
    uint64_t tt_hits;
    uint64_t perimeter_hits;
    move_type solution[MAX_IDA_THRESHOLD + 1];
};

struct child {
    move_type move;
    uint64_t x_rank;
    uint64_t t_rank;
    unsigned char cost;
    unsigned char x_encoded;
};

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE --x-cost FILE --t-cost FILE "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] [--tt-bits N] "
        "[--perimeter-depth N] [--perimeter-max-states N] "
        "[--serial-order] [--print-ranks]\n",
        program
    );
}

static void init_binom(void)
{
    for (unsigned int n = 0; n <= COMPACT_CENTER_COUNT; n++) {
        binom[n][0] = 1;
        binom[n][n] = 1;
        for (unsigned int k = 1; k < n; k++) {
            binom[n][k] = binom[n - 1][k - 1] + binom[n - 1][k];
        }
    }
}

static void init_staged_symbols(void)
{
    staged_symbol_by_color[(unsigned char)'F'] = 0;
    staged_symbol_by_color[(unsigned char)'L'] = 1;
    staged_symbol_by_color[(unsigned char)'U'] = 2;
}

// A staged center only cares which pair of opposite faces it belongs to
static char staged_color(char color)
{
    switch (color) {
        case 'F':
        case 'B':
            return 'F';
        case 'L':
        case 'R':
            return 'L';
        case 'U':
        case 'D':
            return 'U';
        default:
            return color;
    }
}

static uint64_t multiset_perms(const unsigned int counts[RANK_SYMBOL_COUNT], unsigned int slots)
{
    uint64_t result = 1;
    unsigned int remaining = slots;

    for (unsigned int symbol = 0; symbol < RANK_SYMBOL_COUNT; symbol++) {
        result *= binom[remaining][counts[symbol]];
        remaining -= counts[symbol];
    }
    return result;
}

static void init_rank_increment(void)
{
    for (unsigned int f_count = 0; f_count <= 8; f_count++) {
        for (unsigned int l_count = 0; l_count <= 8; l_count++) {
            for (unsigned int u_count = 0; u_count <= 8; u_count++) {
                unsigned int counts[RANK_SYMBOL_COUNT] = {f_count, l_count, u_count};
                unsigned int slots = f_count + l_count + u_count;

                if (!slots) {
                    continue;
                }

                for (unsigned int selected = 0; selected < RANK_SYMBOL_COUNT; selected++) {
                    uint64_t increment = 0;

                    for (unsigned int symbol = 0; symbol < selected; symbol++) {
                        if (!counts[symbol]) {
                            continue;
                        }
                        counts[symbol]--;
                        increment += multiset_perms(counts, slots - 1);
                        counts[symbol]++;
                    }
                    rank_increment[f_count][l_count][u_count][selected] = increment;
                }
            }
        }
    }
}

static void init_move_tables(void)
{
    inverse_555[U] = U_PRIME;
    inverse_555[U_PRIME] = U;
    inverse_555[U2] = U2;
    inverse_555[Uw] = Uw_PRIME;
    inverse_555[Uw_PRIME] = Uw;
    inverse_555[Uw2] = Uw2;
    inverse_555[L] = L_PRIME;
    inverse_555[L_PRIME] = L;
    inverse_555[L2] = L2;
    inverse_555[Lw] = Lw_PRIME;
    inverse_555[Lw_PRIME] = Lw;
    inverse_555[Lw2] = Lw2;
    inverse_555[F] = F_PRIME;
    inverse_555[F_PRIME] = F;
    inverse_555[F2] = F2;
    inverse_555[Fw] = Fw_PRIME;
    inverse_555[Fw_PRIME] = Fw;
    inverse_555[Fw2] = Fw2;
    inverse_555[R] = R_PRIME;
    inverse_555[R_PRIME] = R;
    inverse_555[R2] = R2;
    inverse_555[Rw] = Rw_PRIME;
    inverse_555[Rw_PRIME] = Rw;
    inverse_555[Rw2] = Rw2;
    inverse_555[B] = B_PRIME;
    inverse_555[B_PRIME] = B;
    inverse_555[B2] = B2;
    inverse_555[Bw] = Bw_PRIME;
    inverse_555[Bw_PRIME] = Bw;
    inverse_555[Bw2] = Bw2;
    inverse_555[D] = D_PRIME;
    inverse_555[D_PRIME] = D;
    inverse_555[D2] = D2;
    inverse_555[Dw] = Dw_PRIME;
    inverse_555[Dw_PRIME] = Dw;
    inverse_555[Dw2] = Dw2;

    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        legal_move_index[MOVE_NONE][legal_move_count[MOVE_NONE]++] = (unsigned char)move_index;
    }

    // Only the centers matter here, so moves that reach the same center state in a
    // different order are pruned the same way ida_search_via_graph does for a
    // centers_only search.
    for (unsigned int previous_index = 0; previous_index < MOVE_COUNT_555; previous_index++) {
        move_type previous_move = moves_555[previous_index];

        for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
            move_type move = moves_555[move_index];

            if (steps_on_same_face_and_layer(previous_move, move) ||
                !outer_layer_moves_in_order(previous_move, move) ||
                !steps_on_same_face_in_order(previous_move, move) ||
                !steps_on_opposite_faces_in_order(previous_move, move)) {
                continue;
            }
            legal_move_index[previous_move][legal_move_count[previous_move]++] = (unsigned char)move_index;
        }
    }
}

static void init_compact_move_tables(void)
{
    char cube[CUBE_ARRAY_SIZE_555];
    char rotate_tmp[CUBE_ARRAY_SIZE_555];

    for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
        move_type move = moves_555[move_index];

        memset(cube, 0, sizeof(cube));
        for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
            cube[x_center_squares[position]] = (char)(position + 1);
            cube[t_center_squares[position]] = (char)(position + 1);
        }
        rotate_555_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE_555, move);

        for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
            unsigned char x_source = (unsigned char)cube[x_center_squares[position]];
            unsigned char t_source = (unsigned char)cube[t_center_squares[position]];

            if (!x_source || x_source > COMPACT_CENTER_COUNT ||
                !t_source || t_source > COMPACT_CENTER_COUNT) {
                fprintf(stderr, "ERROR: move %u crosses a 5x5x5 center orbit\n", move);
                exit(1);
            }
            compact_move_source[move][0][position] = x_source - 1;
            compact_move_source[move][1][position] = t_source - 1;
        }
    }
}

static uint64_t multiset_rank_cube(const char *cube, const unsigned int squares[COMPACT_CENTER_COUNT])
{
    unsigned int counts[RANK_SYMBOL_COUNT] = {8, 8, 8};
    uint64_t rank = 0;

    for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
        unsigned int selected = staged_symbol_by_color[(unsigned char)cube[squares[position]]];
        rank += rank_increment[counts[0]][counts[1]][counts[2]][selected];
        counts[selected]--;
    }
    return rank;
}

static void compact_state_from_cube(struct compact_center_state *state, const char *cube)
{
    for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
        state->x[position] =
            staged_symbol_by_color[(unsigned char)cube[x_center_squares[position]]];
        state->t[position] =
            staged_symbol_by_color[(unsigned char)cube[t_center_squares[position]]];
    }
}

static uint64_t multiset_rank_compact(const unsigned char centers[COMPACT_CENTER_COUNT])
{
    unsigned int counts[RANK_SYMBOL_COUNT] = {8, 8, 8};
    uint64_t rank = 0;

    for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
        unsigned int selected = centers[position];

        rank += rank_increment[counts[0]][counts[1]][counts[2]][selected];
        counts[selected]--;
    }
    return rank;
}

static uint64_t multiset_rank_after_move(
    const unsigned char centers[COMPACT_CENTER_COUNT],
    const unsigned char source[COMPACT_CENTER_COUNT]
)
{
    unsigned int counts[RANK_SYMBOL_COUNT] = {8, 8, 8};
    uint64_t rank = 0;

    for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
        unsigned int selected = centers[source[position]];

        rank += rank_increment[counts[0]][counts[1]][counts[2]][selected];
        counts[selected]--;
    }
    return rank;
}

static void compact_apply_move(
    struct compact_center_state *result,
    const struct compact_center_state *state,
    move_type move
)
{
    const unsigned char *x_source = compact_move_source[move][0];
    const unsigned char *t_source = compact_move_source[move][1];

    for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
        result->x[position] = state->x[x_source[position]];
        result->t[position] = state->t[t_source[position]];
    }
}

static void unrank_compact(unsigned char centers[COMPACT_CENTER_COUNT], uint64_t rank)
{
    unsigned int counts[RANK_SYMBOL_COUNT] = {8, 8, 8};

    for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
        unsigned int slots_after = COMPACT_CENTER_COUNT - position - 1;

        for (unsigned int symbol = 0; symbol < RANK_SYMBOL_COUNT; symbol++) {
            uint64_t block_size;

            if (!counts[symbol]) {
                continue;
            }
            counts[symbol]--;
            block_size = multiset_perms(counts, slots_after);
            if (rank < block_size) {
                centers[position] = (unsigned char)symbol;
                break;
            }
            rank -= block_size;
            counts[symbol]++;
        }
    }
}

static void compact_state_from_ranks(
    struct compact_center_state *state,
    uint64_t x_rank,
    uint64_t t_rank
)
{
    unrank_compact(state->x, x_rank);
    unrank_compact(state->t, t_rank);
}

static struct heuristic_result heuristic(const char *cube)
{
    struct heuristic_result result;
    unsigned char x_encoded;
    unsigned char t_encoded;

    result.x_rank = multiset_rank_cube(cube, x_center_squares);
    result.t_rank = multiset_rank_cube(cube, t_center_squares);
    x_encoded = x_costs[result.x_rank];
    t_encoded = t_costs[result.t_rank];

    if (!x_encoded || !t_encoded) {
        result.cost = UINT8_MAX;
    } else {
        unsigned char x_cost = x_encoded - 1;
        unsigned char t_cost = t_encoded - 1;
        result.cost = x_cost > t_cost ? x_cost : t_cost;
    }
    return result;
}

static struct ranked_cost_file map_ranked_cost_file(const char *filename)
{
    struct ranked_cost_file result;
    struct stat file_stat;

    result.fd = open(filename, O_RDONLY);
    if (result.fd < 0) {
        fprintf(stderr, "ERROR: could not open %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if (fstat(result.fd, &file_stat) != 0) {
        fprintf(stderr, "ERROR: could not stat %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if ((uint64_t)file_stat.st_size != RANK_UNIVERSE_555) {
        fprintf(
            stderr,
            "ERROR: %s is %" PRIu64 " bytes, expected %" PRIu64 "\n",
            filename,
            (uint64_t)file_stat.st_size,
            RANK_UNIVERSE_555
        );
        exit(1);
    }

    int mmap_flags = MAP_SHARED;
#ifdef MAP_POPULATE
    /* Sparse unit-test files must not be fully faulted in. */
    if ((uint64_t)file_stat.st_blocks * 512 >= RANK_UNIVERSE_555) {
        mmap_flags |= MAP_POPULATE;
    }
#endif
    result.costs = mmap(NULL, (size_t)RANK_UNIVERSE_555, PROT_READ, mmap_flags, result.fd, 0);
    if (result.costs == MAP_FAILED) {
        fprintf(stderr, "ERROR: could not mmap %s: %s\n", filename, strerror(errno));
        exit(1);
    }
#ifdef MADV_HUGEPAGE
    madvise(result.costs, (size_t)RANK_UNIVERSE_555, MADV_HUGEPAGE);
#endif
    return result;
}

static void unmap_ranked_cost_file(struct ranked_cost_file *file)
{
    if (file->costs && file->costs != MAP_FAILED) {
        munmap(file->costs, (size_t)RANK_UNIVERSE_555);
    }
    if (file->fd >= 0) {
        close(file->fd);
    }
}

static void init_cube_from_kociemba(char cube[CUBE_ARRAY_SIZE_555], const char *kociemba)
{
    const unsigned int face_size = CUBE_SIZE_555 * CUBE_SIZE_555;
    const unsigned int U = 0;
    const unsigned int R = face_size;
    const unsigned int F = face_size * 2;
    const unsigned int D = face_size * 3;
    const unsigned int L = face_size * 4;
    const unsigned int B = face_size * 5;

    if (strlen(kociemba) != face_size * 6) {
        fprintf(stderr, "ERROR: --kociemba must contain 150 stickers for a 5x5x5 cube\n");
        exit(1);
    }

    cube[0] = 'x';
    memcpy(&cube[1], &kociemba[U], face_size);
    memcpy(&cube[1 + face_size], &kociemba[L], face_size);
    memcpy(&cube[1 + (face_size * 2)], &kociemba[F], face_size);
    memcpy(&cube[1 + (face_size * 3)], &kociemba[R], face_size);
    memcpy(&cube[1 + (face_size * 4)], &kociemba[B], face_size);
    memcpy(&cube[1 + (face_size * 5)], &kociemba[D], face_size);

    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE_555; square++) {
        cube[square] = staged_color(cube[square]);
    }
}

// Returns UINT8_MAX when the state is absent from a table, else the admissible cost
static unsigned char cost_from_ranks(uint64_t x_rank, uint64_t t_rank)
{
    unsigned char x_encoded = x_costs[x_rank];
    unsigned char t_encoded = t_costs[t_rank];

    if (!x_encoded || !t_encoded) {
        return UINT8_MAX;
    }
    return (x_encoded > t_encoded ? x_encoded : t_encoded) - 1;
}

static uint64_t center_state_hash(uint64_t x_rank, uint64_t t_rank)
{
    uint64_t key = x_rank * UINT64_C(0x9E3779B97F4A7C15);

    key ^= t_rank + UINT64_C(0x165667B19E3779F9) + (key << 6) + (key >> 2);
    key ^= key >> 30;
    key *= UINT64_C(0xBF58476D1CE4E5B9);
    key ^= key >> 27;
    key *= UINT64_C(0x94D049BB133111EB);
    key ^= key >> 31;
    return key;
}

static uint32_t perimeter_lookup(uint64_t x_rank, uint64_t t_rank)
{
    uint64_t slot;

    if (!perimeter_slots) {
        return PERIMETER_NOT_FOUND;
    }

    slot = center_state_hash(x_rank, t_rank) & perimeter_slot_mask;
    while (perimeter_slots[slot]) {
        uint32_t index = perimeter_slots[slot] - 1;
        const struct perimeter_entry *entry = &perimeter_entries[index];

        if (entry->x_rank == x_rank && entry->t_rank == t_rank) {
            return index;
        }
        slot = (slot + 1) & perimeter_slot_mask;
    }
    return PERIMETER_NOT_FOUND;
}

static uint32_t perimeter_insert(
    uint64_t x_rank,
    uint64_t t_rank,
    uint32_t parent,
    move_type move,
    unsigned char depth,
    uint64_t max_states,
    int *inserted
)
{
    uint64_t slot = center_state_hash(x_rank, t_rank) & perimeter_slot_mask;

    while (perimeter_slots[slot]) {
        uint32_t index = perimeter_slots[slot] - 1;
        const struct perimeter_entry *entry = &perimeter_entries[index];

        if (entry->x_rank == x_rank && entry->t_rank == t_rank) {
            *inserted = 0;
            return index;
        }
        slot = (slot + 1) & perimeter_slot_mask;
    }

    if ((uint64_t)perimeter_count >= max_states || perimeter_count == UINT32_MAX - 1) {
        fprintf(
            stderr,
            "ERROR: solved-side perimeter exceeded %" PRIu64
            " states; increase --perimeter-max-states or lower --perimeter-depth\n",
            max_states
        );
        exit(1);
    }

    perimeter_entries[perimeter_count].x_rank = x_rank;
    perimeter_entries[perimeter_count].t_rank = t_rank;
    perimeter_entries[perimeter_count].parent = parent;
    perimeter_entries[perimeter_count].move = (unsigned char)move;
    perimeter_entries[perimeter_count].depth = depth;
    perimeter_slots[slot] = perimeter_count + 1;
    *inserted = 1;
    return perimeter_count++;
}

static void init_solved_center_cube(char cube[CUBE_ARRAY_SIZE_555])
{
    static const char face_symbols[6] = {'U', 'L', 'F', 'L', 'F', 'U'};
    const unsigned int face_size = CUBE_SIZE_555 * CUBE_SIZE_555;

    cube[0] = 'x';
    for (unsigned int face = 0; face < 6; face++) {
        memset(&cube[1 + face * face_size], face_symbols[face], face_size);
    }
}

static void cube_from_ranks(char cube[CUBE_ARRAY_SIZE_555], uint64_t x_rank, uint64_t t_rank)
{
    static const char symbols[RANK_SYMBOL_COUNT] = {'F', 'L', 'U'};
    struct compact_center_state state;

    init_solved_center_cube(cube);
    compact_state_from_ranks(&state, x_rank, t_rank);
    for (unsigned int position = 0; position < COMPACT_CENTER_COUNT; position++) {
        cube[x_center_squares[position]] = symbols[state.x[position]];
        cube[t_center_squares[position]] = symbols[state.t[position]];
    }
}

static void blank_edges_and_corners(char cube[CUBE_ARRAY_SIZE_555])
{
    const unsigned int face_size = CUBE_SIZE_555 * CUBE_SIZE_555;

    for (unsigned int face = 0; face < 6; face++) {
        unsigned int base = 1 + face * face_size;

        for (unsigned int row = 0; row < CUBE_SIZE_555; row++) {
            for (unsigned int col = 0; col < CUBE_SIZE_555; col++) {
                if (row == 0 || row == CUBE_SIZE_555 - 1 || col == 0 || col == CUBE_SIZE_555 - 1) {
                    cube[base + row * CUBE_SIZE_555 + col] = '.';
                }
            }
        }
    }
}

static void print_perimeter_cube(
    const char *label,
    uint64_t x_rank,
    uint64_t t_rank,
    unsigned char perimeter_moves,
    unsigned char forward_moves
)
{
    char cube[CUBE_ARRAY_SIZE_555];
    char x_rank_buf[32];
    char t_rank_buf[32];
    unsigned char x_encoded = x_costs[x_rank];
    unsigned char t_encoded = t_costs[t_rank];
    unsigned char x_cost = x_encoded ? x_encoded - 1 : UINT8_MAX;
    unsigned char t_cost = t_encoded ? t_encoded - 1 : UINT8_MAX;

    LOG(
        "\n%s (forward %u, perimeter %u, x_cost %u, t_cost %u, x_rank %s, t_rank %s)\n",
        label,
        forward_moves,
        perimeter_moves,
        x_cost,
        t_cost,
        grouped_uint64(x_rank, x_rank_buf, sizeof(x_rank_buf)),
        grouped_uint64(t_rank, t_rank_buf, sizeof(t_rank_buf))
    );
    cube_from_ranks(cube, x_rank, t_rank);
    blank_edges_and_corners(cube);
    print_cube(cube, CUBE_SIZE_555);
    fflush(stdout);
}

static void build_solved_perimeter(unsigned char depth, uint64_t max_states)
{
    char solved_cube[CUBE_ARRAY_SIZE_555];
    struct compact_center_state solved;
    struct compact_center_state parent_state;
    uint64_t slot_count = 1;
    uint32_t level_start = 0;
    uint32_t level_end;
    uint64_t solved_x_rank;
    uint64_t solved_t_rank;
    struct timeval start;
    struct timeval stop;
    int inserted;

    if (!depth) {
        return;
    }
    if (!max_states || max_states > UINT32_MAX - 1) {
        fprintf(stderr, "ERROR: --perimeter-max-states must be between 1 and %u\n", UINT32_MAX - 1);
        exit(1);
    }
    while (slot_count < max_states * 2) {
        slot_count <<= 1;
    }

    perimeter_entries = malloc((size_t)max_states * sizeof(*perimeter_entries));
    perimeter_slots = calloc((size_t)slot_count, sizeof(*perimeter_slots));
    if (!perimeter_entries || !perimeter_slots) {
        fprintf(
            stderr,
            "ERROR: could not allocate solved-side perimeter for %" PRIu64 " states\n",
            max_states
        );
        exit(1);
    }
    perimeter_slot_mask = slot_count - 1;
    perimeter_depth = depth;

    init_solved_center_cube(solved_cube);
    compact_state_from_cube(&solved, solved_cube);
    solved_x_rank = multiset_rank_compact(solved.x);
    solved_t_rank = multiset_rank_compact(solved.t);
    print_perimeter_cube("PERIMETER ROOT", solved_x_rank, solved_t_rank, 0, 0);
    perimeter_insert(
        solved_x_rank,
        solved_t_rank,
        PERIMETER_NOT_FOUND,
        MOVE_NONE,
        0,
        max_states,
        &inserted
    );
    level_end = perimeter_count;
    gettimeofday(&start, NULL);

    for (unsigned char current_depth = 0; current_depth < depth; current_depth++) {
        uint32_t next_level_end;

        for (uint32_t parent = level_start; parent < level_end; parent++) {
            const struct perimeter_entry *entry = &perimeter_entries[parent];

            compact_state_from_ranks(&parent_state, entry->x_rank, entry->t_rank);
            for (unsigned int move_index = 0; move_index < MOVE_COUNT_555; move_index++) {
                move_type move = moves_555[move_index];
                uint64_t x_rank =
                    multiset_rank_after_move(parent_state.x, compact_move_source[move][0]);
                uint64_t t_rank =
                    multiset_rank_after_move(parent_state.t, compact_move_source[move][1]);

                if (x_rank == entry->x_rank && t_rank == entry->t_rank) {
                    continue;
                }
                perimeter_insert(
                    x_rank,
                    t_rank,
                    parent,
                    move,
                    current_depth + 1,
                    max_states,
                    &inserted
                );
            }
        }

        next_level_end = perimeter_count;
        LOG(
            "perimeter depth %u: %'u new states, %'u total\n",
            current_depth + 1,
            next_level_end - level_end,
            next_level_end
        );
        level_start = level_end;
        level_end = next_level_end;
    }

    gettimeofday(&stop, NULL);
    LOG(
        "built solved-side perimeter depth %u with %'u states in %.3fs\n",
        depth,
        perimeter_count,
        ((stop.tv_sec - start.tv_sec) * 1000000 + stop.tv_usec - start.tv_usec) / 1000000.0
    );
}

static void free_solved_perimeter(void)
{
    free(perimeter_entries);
    free(perimeter_slots);
    perimeter_entries = NULL;
    perimeter_slots = NULL;
    perimeter_slot_mask = 0;
    perimeter_count = 0;
    perimeter_depth = 0;
}

static void append_perimeter_path(
    move_type solution[MAX_IDA_THRESHOLD + 1],
    unsigned char depth,
    uint32_t perimeter_index
)
{
    while (perimeter_entries[perimeter_index].depth) {
        const struct perimeter_entry *entry = &perimeter_entries[perimeter_index];

        solution[depth++] = inverse_555[entry->move];
        perimeter_index = entry->parent;
    }
    solution[depth] = MOVE_NONE;
}

/*
 * Returns 1 for an intersection that fits, -1 when perimeter completeness
 * proves the node cannot finish within the remaining threshold, and 0 when the
 * perimeter has no information because more than perimeter_depth moves remain.
 */
static int perimeter_decision(
    move_type solution[MAX_IDA_THRESHOLD + 1],
    unsigned char depth,
    unsigned char threshold,
    uint64_t x_rank,
    uint64_t t_rank,
    uint64_t *hits
)
{
    uint32_t index = perimeter_lookup(x_rank, t_rank);

    if (!perimeter_slots) {
        return 0;
    }
    if (index != PERIMETER_NOT_FOUND) {
        const struct perimeter_entry *entry = &perimeter_entries[index];

        (*hits)++;
        if ((unsigned int)depth + entry->depth <= threshold) {
            pthread_mutex_lock(&best_solution_lock);
            print_perimeter_cube("PERIMETER HIT", entry->x_rank, entry->t_rank, entry->depth, depth);
            pthread_mutex_unlock(&best_solution_lock);
            append_perimeter_path(solution, depth, index);
            return 1;
        }
    }
    return threshold - depth <= perimeter_depth ? -1 : 0;
}

static void print_ida_summary(char cube[CUBE_ARRAY_SIZE_555], const move_type *solution)
{
    char rotate_tmp[CUBE_ARRAY_SIZE_555];
    unsigned char solution_len = 0;

    while (solution[solution_len] != MOVE_NONE) {
        solution_len++;
    }

    printf("\n\n");
    printf("       PT0  PT1  CTG  TRU  IDX\n");
    printf("       ===  ===  ===  ===  ===\n");

    for (unsigned char idx = 0; idx <= solution_len; idx++) {
        uint64_t x_rank = multiset_rank_cube(cube, x_center_squares);
        uint64_t t_rank = multiset_rank_cube(cube, t_center_squares);
        unsigned char x_encoded = x_costs[x_rank];
        unsigned char t_encoded = t_costs[t_rank];
        unsigned char x_cost = x_encoded ? x_encoded - 1 : UINT8_MAX;
        unsigned char t_cost = t_encoded ? t_encoded - 1 : UINT8_MAX;
        unsigned char ctg = x_cost > t_cost ? x_cost : t_cost;

        if (idx == 0) {
            printf(" INIT  ");
        } else {
            printf("%5s  ", move2str[solution[idx - 1]]);
        }
        printf("%3d  %3d  %3d  %3d  %3d\n", x_cost, t_cost, ctg, solution_len - idx, idx);

        if (idx < solution_len) {
            rotate_555_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE_555, solution[idx]);
        }
    }
    printf("\n");
    fflush(stdout);
}

// The X and T ranks together identify the center state exactly, and the previous move
// decides which successors are legal, so all three belong in the key.
static uint64_t transposition_key(uint64_t x_rank, uint64_t t_rank, move_type previous_move)
{
    uint64_t key = x_rank * UINT64_C(0x9E3779B97F4A7C15);

    key ^= t_rank + UINT64_C(0x165667B19E3779F9) + (key << 6) + (key >> 2);
    key ^= (uint64_t)previous_move * UINT64_C(0xD6E8FEB86659FD93);
    key ^= key >> 29;
    key *= UINT64_C(0xBF58476D1CE4E5B9);
    key ^= key >> 32;
    return key;
}

static int ida_search(
    struct worker *worker,
    const struct compact_center_state *state,
    unsigned char depth,
    unsigned char threshold,
    move_type previous_move,
    uint64_t x_rank,
    uint64_t t_rank
)
{
    struct child children[MOVE_COUNT_555];
    unsigned int child_count = 0;
    unsigned char count = legal_move_count[previous_move];
    const unsigned char *move_indexes = legal_move_index[previous_move];
    unsigned char next_depth = depth + 1;
    unsigned char remaining = threshold - depth;
    uint64_t key = 0;
    uint64_t tag = 0;
    uint64_t slot = 0;
    uint64_t entry = 0;

    if (solution_supersedes(worker->task_id)) {
        worker->aborted = 1;
        return 0;
    }

    if (transposition_table) {
        key = transposition_key(x_rank, t_rank, previous_move);
        tag = key >> 8;
        slot = key & transposition_mask;
        entry = atomic_load_explicit(&transposition_table[slot], memory_order_relaxed);

        if ((entry >> 8) == tag && (unsigned char)entry >= remaining) {
            worker->tt_hits++;
            return 0;
        }
    }

    // Rank every child before touching the cost tables so the loads for all of them
    // are issued together instead of one cache miss at a time
    for (unsigned int i = 0; i < count; i++) {
        move_type move = moves_555[move_indexes[i]];

        children[i].move = move;
        children[i].x_rank =
            multiset_rank_after_move(state->x, compact_move_source[move][0]);
        children[i].t_rank =
            multiset_rank_after_move(state->t, compact_move_source[move][1]);
        __builtin_prefetch(&x_costs[children[i].x_rank], 0, 0);
    }

    worker->ida_count += count;

    // Children the X table already rules out never touch the T table at all
    for (unsigned int i = 0; i < count; i++) {
        unsigned char x_encoded = x_costs[children[i].x_rank];

        children[i].x_encoded = x_encoded;

        // A move that leaves both ranks alone spends a move without changing anything this
        // search can see, so any solution through it has a shorter one without it
        if (children[i].x_rank == x_rank && children[i].t_rank == t_rank) {
            children[i].x_encoded = 0;
            continue;
        }
        if (!x_encoded || next_depth + (x_encoded - 1) > threshold) {
            children[i].x_encoded = 0;
            continue;
        }
        __builtin_prefetch(&t_costs[children[i].t_rank], 0, 0);
    }

    for (unsigned int i = 0; i < count; i++) {
        unsigned char x_encoded = children[i].x_encoded;
        unsigned char t_encoded;
        unsigned char cost;

        if (!x_encoded) {
            continue;
        }
        t_encoded = t_costs[children[i].t_rank];
        if (!t_encoded) {
            continue;
        }
        cost = (x_encoded > t_encoded ? x_encoded : t_encoded) - 1;
        if (next_depth + cost > threshold) {
            continue;
        }
        worker->solution[depth] = children[i].move;
        int decision = perimeter_decision(
                worker->solution,
                next_depth,
                threshold,
                children[i].x_rank,
                children[i].t_rank,
                &worker->perimeter_hits
            );
        if (decision > 0) {
            return 1;
        }
        if (decision < 0) {
            continue;
        }
        if (cost == 0) {
            worker->solution[next_depth] = MOVE_NONE;
            return 1;
        }
        children[child_count] = children[i];
        children[child_count].cost = cost;
        child_count++;
    }

    if (next_depth >= threshold || next_depth >= MAX_IDA_THRESHOLD) {
        goto failed;
    }

    // Cheapest child first, keeping equal costs in move order so the search stays deterministic
    for (unsigned int i = 1; i < child_count; i++) {
        struct child pending = children[i];
        unsigned int j = i;

        while (j > 0 && children[j - 1].cost > pending.cost) {
            children[j] = children[j - 1];
            j--;
        }
        children[j] = pending;
    }

    for (unsigned int i = 0; i < child_count; i++) {
        struct compact_center_state child_state;

        worker->solution[depth] = children[i].move;
        compact_apply_move(&child_state, state, children[i].move);
        if (ida_search(worker, &child_state, next_depth, threshold, children[i].move, children[i].x_rank,
                       children[i].t_rank)) {
            return 1;
        }

        if (worker->aborted) {
            return 0;
        }
    }

failed:
    worker->solution[depth] = MOVE_NONE;

    // An abandoned subtree proves nothing, so it must never be recorded as a failure
    if (transposition_table && !worker->aborted && !((entry >> 8) == tag && (unsigned char)entry > remaining)) {
        atomic_store_explicit(&transposition_table[slot], (tag << 8) | remaining, memory_order_relaxed);
    }
    return 0;
}

// Enumerate legal two-move prefixes in serial DFS order. A one-move solution is
// returned immediately so later prefixes never hide an earlier serial result.
static int build_split_tasks(
    const struct compact_center_state *root,
    unsigned char threshold,
    uint64_t *nodes,
    move_type one_move_solution[MAX_IDA_THRESHOLD + 1]
)
{
    unsigned char first_count = legal_move_count[MOVE_NONE];

    split_task_count = 0;
    one_move_solution[0] = MOVE_NONE;

    for (unsigned int first_index = 0; first_index < first_count; first_index++) {
        move_type first = moves_555[legal_move_index[MOVE_NONE][first_index]];
        struct compact_center_state state;
        uint64_t x_rank;
        uint64_t t_rank;
        unsigned char cost;
        unsigned char second_count;

        compact_apply_move(&state, root, first);
        (*nodes)++;

        x_rank = multiset_rank_compact(state.x);
        t_rank = multiset_rank_compact(state.t);
        cost = cost_from_ranks(x_rank, t_rank);
        if (cost == UINT8_MAX || 1 + cost > threshold) {
            continue;
        }
        one_move_solution[0] = first;
        int decision = perimeter_decision(
            one_move_solution,
            1,
            threshold,
            x_rank,
            t_rank,
            &perimeter_hits
        );
        if (decision > 0) {
            return 1;
        }
        if (decision < 0) {
            continue;
        }
        if (cost == 0) {
            one_move_solution[0] = first;
            one_move_solution[1] = MOVE_NONE;
            return 1;
        }
        if (threshold < 2) {
            continue;
        }

        second_count = legal_move_count[first];
        for (unsigned int second_index = 0; second_index < second_count; second_index++) {
            if (split_task_count >= MAX_SPLIT_TASKS) {
                fprintf(stderr, "ERROR: two-move task list overflowed\n");
                exit(1);
            }
            split_tasks[split_task_count].first_index = (unsigned char)first_index;
            split_tasks[split_task_count].second_index = (unsigned char)second_index;
            split_task_count++;
        }
    }
    return 0;
}

static void *search_split_tasks(void *argument)
{
    struct worker *worker = argument;

    while (1) {
        unsigned int task = atomic_fetch_add(&next_task, 1);
        unsigned char first_index;
        unsigned char second_index;
        move_type first;
        move_type second;
        struct compact_center_state first_state;
        struct compact_center_state state;
        uint64_t x_rank;
        uint64_t t_rank;
        unsigned char cost;
        int found;

        if (task >= split_task_count || solution_supersedes(task)) {
            break;
        }

        worker->task_id = task;
        worker->aborted = 0;
        first_index = split_tasks[task].first_index;
        second_index = split_tasks[task].second_index;
        first = moves_555[legal_move_index[MOVE_NONE][first_index]];
        second = moves_555[legal_move_index[first][second_index]];

        compact_apply_move(&first_state, worker->root_state, first);
        compact_apply_move(&state, &first_state, second);
        worker->solution[0] = first;
        worker->solution[1] = second;
        worker->ida_count++;

        x_rank = multiset_rank_compact(state.x);
        t_rank = multiset_rank_compact(state.t);
        cost = cost_from_ranks(x_rank, t_rank);

        if (cost == UINT8_MAX || 2 + cost > worker->threshold) {
            continue;
        }
        int decision = perimeter_decision(
            worker->solution,
            2,
            worker->threshold,
            x_rank,
            t_rank,
            &worker->perimeter_hits
        );
        if (decision > 0) {
            found = 1;
        } else if (decision < 0) {
            continue;
        } else if (cost == 0) {
            worker->solution[2] = MOVE_NONE;
            found = 1;
        } else if (2 >= worker->threshold) {
            continue;
        } else {
            found = ida_search(worker, &state, 2, worker->threshold, second, x_rank, t_rank);
        }

        if (found) {
            unsigned int best;
            int accept;

            pthread_mutex_lock(&best_solution_lock);
            best = atomic_load(&best_task);
            accept = stop_on_first_solution ? best == NO_TASK : task < best;

            if (accept) {
                memcpy(best_solution, worker->solution, sizeof(best_solution));
                atomic_store(&best_task, task);
            }
            pthread_mutex_unlock(&best_solution_lock);
            break;
        }
        if (worker->aborted) {
            break;
        }
    }
    return NULL;
}

static int search_threshold(
    const char cube[CUBE_ARRAY_SIZE_555],
    unsigned char threshold,
    unsigned int thread_count,
    uint64_t *nodes
)
{
    struct worker workers[MAX_THREADS];
    pthread_t threads[MAX_THREADS];
    struct compact_center_state root_state;
    uint64_t x_rank;
    uint64_t t_rank;
    unsigned char cost;
    move_type one_move_solution[MAX_IDA_THRESHOLD + 1] = {MOVE_NONE};
    unsigned int workers_to_start;

    compact_state_from_cube(&root_state, cube);
    x_rank = multiset_rank_compact(root_state.x);
    t_rank = multiset_rank_compact(root_state.t);
    cost = cost_from_ranks(x_rank, t_rank);
    *nodes = 1;
    if (cost == UINT8_MAX || cost > threshold) {
        return 0;
    }
    int decision = perimeter_decision(
        best_solution,
        0,
        threshold,
        x_rank,
        t_rank,
        &perimeter_hits
    );
    if (decision > 0) {
        return 1;
    }
    if (decision < 0) {
        return 0;
    }
    if (cost == 0) {
        best_solution[0] = MOVE_NONE;
        return 1;
    }
    if (threshold == 0) {
        return 0;
    }
    if (build_split_tasks(&root_state, threshold, nodes, one_move_solution)) {
        memcpy(best_solution, one_move_solution, sizeof(best_solution));
        return 1;
    }
    if (!split_task_count) {
        return 0;
    }

    workers_to_start = thread_count;
    if (workers_to_start > split_task_count) {
        workers_to_start = split_task_count;
    }

    atomic_store(&next_task, 0);
    atomic_store(&best_task, NO_TASK);

    for (unsigned int i = 0; i < workers_to_start; i++) {
        memset(&workers[i], 0, sizeof(workers[i]));
        workers[i].root_state = &root_state;
        workers[i].threshold = threshold;
        workers[i].task_id = NO_TASK;

        if (pthread_create(&threads[i], NULL, search_split_tasks, &workers[i]) != 0) {
            fprintf(stderr, "ERROR: could not create search thread %u\n", i);
            exit(1);
        }
    }

    for (unsigned int i = 0; i < workers_to_start; i++) {
        pthread_join(threads[i], NULL);
        *nodes += workers[i].ida_count;
        transposition_hits += workers[i].tt_hits;
        perimeter_hits += workers[i].perimeter_hits;
    }
    return atomic_load(&best_task) != NO_TASK;
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *x_cost_filename = NULL;
    const char *t_cost_filename = NULL;
    unsigned char min_threshold = UINT8_MAX;
    unsigned char max_threshold = DEFAULT_MAX_IDA_THRESHOLD;
    unsigned int thread_count = 0;
    unsigned int tt_bits = DEFAULT_TT_BITS;
    unsigned int requested_perimeter_depth = 0;
    uint64_t perimeter_max_states = DEFAULT_PERIMETER_MAX_STATES;
    int print_ranks = 0;
    char cube[CUBE_ARRAY_SIZE_555];
    struct ranked_cost_file x_file = {-1, NULL};
    struct ranked_cost_file t_file = {-1, NULL};
    struct heuristic_result initial;
    struct timeval start;
    struct timeval start_this_threshold;
    struct timeval stop;
    uint64_t ida_count_total = 0;

    for (int i = 1; i < argc; i++) {
        if (strmatch(argv[i], "--kociemba") && i + 1 < argc) {
            kociemba = argv[++i];
        } else if (strmatch(argv[i], "--x-cost") && i + 1 < argc) {
            x_cost_filename = argv[++i];
        } else if (strmatch(argv[i], "--t-cost") && i + 1 < argc) {
            t_cost_filename = argv[++i];
        } else if (strmatch(argv[i], "--min-ida-threshold") && i + 1 < argc) {
            min_threshold = (unsigned char)strtoul(argv[++i], NULL, 10);
        } else if (strmatch(argv[i], "--max-ida-threshold") && i + 1 < argc) {
            max_threshold = (unsigned char)strtoul(argv[++i], NULL, 10);
        } else if (strmatch(argv[i], "--threads") && i + 1 < argc) {
            thread_count = (unsigned int)strtoul(argv[++i], NULL, 10);
        } else if (strmatch(argv[i], "--tt-bits") && i + 1 < argc) {
            tt_bits = (unsigned int)strtoul(argv[++i], NULL, 10);
        } else if (strmatch(argv[i], "--perimeter-depth") && i + 1 < argc) {
            requested_perimeter_depth = (unsigned int)strtoul(argv[++i], NULL, 10);
        } else if (strmatch(argv[i], "--perimeter-max-states") && i + 1 < argc) {
            perimeter_max_states = strtoull(argv[++i], NULL, 10);
        } else if (strmatch(argv[i], "--serial-order")) {
            stop_on_first_solution = 0;
        } else if (strmatch(argv[i], "--first-solution")) {
            stop_on_first_solution = 1;
        } else if (strmatch(argv[i], "--print-ranks")) {
            print_ranks = 1;
        } else {
            usage(argv[0]);
            return 2;
        }
    }

    if (!kociemba || !x_cost_filename || !t_cost_filename) {
        usage(argv[0]);
        return 2;
    }

    setvbuf(stdout, NULL, _IOLBF, 0);
    setlocale(LC_NUMERIC, "");
    init_binom();
    init_staged_symbols();
    init_rank_increment();
    init_move_tables();
    init_compact_move_tables();
    init_cube_from_kociemba(cube, kociemba);
    print_cube(cube, CUBE_SIZE_555);
    x_file = map_ranked_cost_file(x_cost_filename);
    t_file = map_ranked_cost_file(t_cost_filename);
    x_costs = x_file.costs;
    t_costs = t_file.costs;
    initial = heuristic(cube);

    if (print_ranks) {
        printf(
            "X_RANK %" PRIu64 " T_RANK %" PRIu64 " COST %u\n",
            initial.x_rank,
            initial.t_rank,
            initial.cost
        );
        unmap_ranked_cost_file(&x_file);
        unmap_ranked_cost_file(&t_file);
        return initial.cost == UINT8_MAX;
    }
    if (initial.cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial center state is absent from a ranked cost table\n");
        unmap_ranked_cost_file(&x_file);
        unmap_ranked_cost_file(&t_file);
        return 1;
    }
    if (min_threshold == UINT8_MAX) {
        min_threshold = initial.cost;
    }
    if (max_threshold > MAX_IDA_THRESHOLD) {
        fprintf(stderr, "ERROR: maximum IDA threshold cannot exceed %u\n", MAX_IDA_THRESHOLD);
        unmap_ranked_cost_file(&x_file);
        unmap_ranked_cost_file(&t_file);
        return 1;
    }
    if (min_threshold > max_threshold) {
        fprintf(stderr, "ERROR: minimum IDA threshold exceeds maximum\n");
        unmap_ranked_cost_file(&x_file);
        unmap_ranked_cost_file(&t_file);
        return 1;
    }
    if (requested_perimeter_depth > MAX_IDA_THRESHOLD) {
        fprintf(stderr, "ERROR: --perimeter-depth cannot exceed %u\n", MAX_IDA_THRESHOLD);
        unmap_ranked_cost_file(&x_file);
        unmap_ranked_cost_file(&t_file);
        return 1;
    }

    if (!thread_count) {
        long online = sysconf(_SC_NPROCESSORS_ONLN);

        thread_count = online > 1 ? (unsigned int)online : 1;
    }
    if (thread_count > MAX_THREADS) {
        thread_count = MAX_THREADS;
    }
    if (tt_bits) {
        uint64_t entries;

        if (tt_bits > MAX_TT_BITS) {
            fprintf(stderr, "ERROR: --tt-bits cannot exceed %u\n", MAX_TT_BITS);
            unmap_ranked_cost_file(&x_file);
            unmap_ranked_cost_file(&t_file);
            return 1;
        }
        entries = UINT64_C(1) << tt_bits;
        transposition_table = calloc(entries, sizeof(*transposition_table));

        if (!transposition_table) {
            fprintf(stderr, "ERROR: could not allocate a %" PRIu64 " entry transposition table\n", entries);
            unmap_ranked_cost_file(&x_file);
            unmap_ranked_cost_file(&t_file);
            return 1;
        }
        transposition_mask = entries - 1;
    }

    build_solved_perimeter((unsigned char)requested_perimeter_depth, perimeter_max_states);

    if (transposition_table) {
        LOG(
            "searching with %u threads, %" PRIu64 " MB transposition table, perimeter depth %u, %s\n",
            thread_count,
            (transposition_mask + 1) * sizeof(*transposition_table) / (1024 * 1024),
            perimeter_depth,
            stop_on_first_solution ? "first solution wins" : "serial move order"
        );
    } else {
        LOG(
            "searching with %u threads, perimeter depth %u, %s\n",
            thread_count,
            perimeter_depth,
            stop_on_first_solution ? "first solution wins" : "serial move order"
        );
    }

    for (unsigned int index = 0; index <= MAX_IDA_THRESHOLD; index++) {
        best_solution[index] = MOVE_NONE;
    }
    gettimeofday(&start, NULL);

    for (unsigned char threshold = min_threshold; threshold <= max_threshold; threshold++) {
        int found_solution;
        uint64_t ida_count = 0;
        uint64_t transposition_hits_before = transposition_hits;
        uint64_t perimeter_hits_before = perimeter_hits;
        float us;
        float nodes_per_us;
        unsigned int nodes_per_sec;

        gettimeofday(&start_this_threshold, NULL);
        found_solution = search_threshold(cube, threshold, thread_count, &ida_count);
        gettimeofday(&stop, NULL);
        ida_count_total += ida_count;

        us = ((stop.tv_sec - start_this_threshold.tv_sec) * 1000000) +
             ((stop.tv_usec - start_this_threshold.tv_usec));
        nodes_per_us = ida_count / us;
        nodes_per_sec = nodes_per_us * 1000000;
        LOG(
            "IDA threshold %d, explored %'llu nodes, took %.3fs, %'llu nodes-per-sec, "
            "%'llu table hits, %'llu perimeter hits\n",
            threshold,
            (unsigned long long)ida_count,
            us / 1000000,
            (unsigned long long)nodes_per_sec,
            (unsigned long long)(transposition_hits - transposition_hits_before),
            (unsigned long long)(perimeter_hits - perimeter_hits_before)
        );

        if (found_solution) {
            us = ((stop.tv_sec - start.tv_sec) * 1000000) + ((stop.tv_usec - start.tv_usec));
            nodes_per_us = ida_count_total / us;
            nodes_per_sec = nodes_per_us * 1000000;
            LOG("IDA found solution, explored %'llu total nodes, took %.3fs, %'llu nodes-per-sec\n\n",
                (unsigned long long)ida_count_total, us / 1000000, (unsigned long long)nodes_per_sec);
            print_moves(best_solution, threshold);
            print_ida_summary(cube, best_solution);
            free_solved_perimeter();
            free(transposition_table);
            unmap_ranked_cost_file(&x_file);
            unmap_ranked_cost_file(&t_file);
            return 0;
        }
    }

    LOG("IDA failed with range %u->%u\n\n", min_threshold, max_threshold);
    free_solved_perimeter();
    free(transposition_table);
    unmap_ranked_cost_file(&x_file);
    unmap_ranked_cost_file(&t_file);
    return 1;
}
