
#ifndef _IDA_SEARCH_CORE_H
#define _IDA_SEARCH_CORE_H

#include <stddef.h>
#include <stdint.h>

typedef enum {
    MOVE_NONE,

    U,
    U_PRIME,
    U2,
    Uw,
    Uw_PRIME,
    Uw2,
    threeUw,
    threeUw_PRIME,
    threeUw2,

    L,
    L_PRIME,
    L2,
    Lw,
    Lw_PRIME,
    Lw2,
    threeLw,
    threeLw_PRIME,
    threeLw2,

    F,
    F_PRIME,
    F2,
    Fw,
    Fw_PRIME,
    Fw2,
    threeFw,
    threeFw_PRIME,
    threeFw2,

    R,
    R_PRIME,
    R2,
    Rw,
    Rw_PRIME,
    Rw2,
    threeRw,
    threeRw_PRIME,
    threeRw2,

    B,
    B_PRIME,
    B2,
    Bw,
    Bw_PRIME,
    Bw2,
    threeBw,
    threeBw_PRIME,
    threeBw2,

    D,
    D_PRIME,
    D2,
    Dw,
    Dw_PRIME,
    Dw2,
    threeDw,
    threeDw_PRIME,
    threeDw2,

    X,
    X_PRIME,
    Y,
    Y_PRIME,
    Z,
    Z_PRIME,
    MOVE_MAX
} move_type;

#define MAX_MOVE_STR_SIZE 5

static const char move2str[MOVE_MAX][MAX_MOVE_STR_SIZE] = {
    "N/A", "U",  "U'", "U2", "Uw",  "Uw'", "Uw2", "3Uw",  "3Uw'", "3Uw2",

    "L",   "L'", "L2", "Lw", "Lw'", "Lw2", "3Lw", "3Lw'", "3Lw2",

    "F",   "F'", "F2", "Fw", "Fw'", "Fw2", "3Fw", "3Fw'", "3Fw2",

    "R",   "R'", "R2", "Rw", "Rw'", "Rw2", "3Rw", "3Rw'", "3Rw2",

    "B",   "B'", "B2", "Bw", "Bw'", "Bw2", "3Bw", "3Bw'", "3Bw2",

    "D",   "D'", "D2", "Dw", "Dw'", "Dw2", "3Dw", "3Dw'", "3Dw2",

    "X",   "X'", "Y",  "Y'", "Z",   "Z'",
};

#define MOVE_COUNT_444 36
static const move_type moves_444[MOVE_COUNT_444] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2, L, L_PRIME, L2, Lw, Lw_PRIME, Lw2, F, F_PRIME, F2, Fw, Fw_PRIME, Fw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2, B, B_PRIME, B2, Bw, Bw_PRIME, Bw2, D, D_PRIME, D2, Dw, Dw_PRIME, Dw2};

#define MOVE_COUNT_555 36
static const move_type moves_555[MOVE_COUNT_555] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2, L, L_PRIME, L2, Lw, Lw_PRIME, Lw2, F, F_PRIME, F2, Fw, Fw_PRIME, Fw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2, B, B_PRIME, B2, Bw, Bw_PRIME, Bw2, D, D_PRIME, D2, Dw, Dw_PRIME, Dw2};

#define MOVE_COUNT_666 54
static const move_type moves_666[MOVE_COUNT_666] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2, threeUw, threeUw_PRIME, threeUw2,
    L, L_PRIME, L2, Lw, Lw_PRIME, Lw2, threeLw, threeLw_PRIME, threeLw2,
    F, F_PRIME, F2, Fw, Fw_PRIME, Fw2, threeFw, threeFw_PRIME, threeFw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2, threeRw, threeRw_PRIME, threeRw2,
    B, B_PRIME, B2, Bw, Bw_PRIME, Bw2, threeBw, threeBw_PRIME, threeBw2,
    D, D_PRIME, D2, Dw, Dw_PRIME, Dw2, threeDw, threeDw_PRIME, threeDw2};

#define MOVE_COUNT_777 54
static const move_type moves_777[MOVE_COUNT_777] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2, threeUw, threeUw_PRIME, threeUw2,
    L, L_PRIME, L2, Lw, Lw_PRIME, Lw2, threeLw, threeLw_PRIME, threeLw2,
    F, F_PRIME, F2, Fw, Fw_PRIME, Fw2, threeFw, threeFw_PRIME, threeFw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2, threeRw, threeRw_PRIME, threeRw2,
    B, B_PRIME, B2, Bw, Bw_PRIME, Bw2, threeBw, threeBw_PRIME, threeBw2,
    D, D_PRIME, D2, Dw, Dw_PRIME, Dw2, threeDw, threeDw_PRIME, threeDw2};

void rotate_555(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_555_centers(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_666(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_666_centers(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_777(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_777_centers(char *cube, char *cube_tmp, int array_size, move_type move);

void LOG(const char *fmt, ...);
const char *grouped_uint64(uint64_t value, char *buffer, size_t buffer_size);
unsigned long hex_to_int(char value);
unsigned long max(unsigned long a, unsigned long b);

struct ida_search_result {
    unsigned int f_cost;
    unsigned int found_solution;
    move_type solution[MOVE_MAX];
};

struct ida_heuristic_result {
    unsigned char cost_to_goal;
    unsigned char unpaired_count;
};
void print_cube(char *cube, int size);
int strmatch(char *str1, char *str2);

void print_moves(move_type *moves, int max_i);

unsigned char wide_turn_count(move_type *moves);
unsigned char get_orbit0_wide_half_turn_count(move_type *moves);
unsigned char get_orbit0_wide_quarter_turn_count(move_type *moves);
unsigned char get_orbit1_wide_quarter_turn_count(move_type *moves);
unsigned char get_outer_layer_quarter_turn_count(move_type *moves);
unsigned char moves_cancel_out(move_type prev_move, move_type move);
unsigned char steps_on_same_face_and_layer(move_type prev_move, move_type move);
unsigned char steps_on_same_face(move_type prev_move, move_type move);
unsigned char outer_layer_move(move_type move);
unsigned char outer_layer_moves_in_order(move_type prev_move, move_type move);
unsigned char steps_on_same_face_in_order(move_type prev_move, move_type move);
unsigned char steps_on_opposite_faces(move_type prev_move, move_type move);
unsigned char steps_on_opposite_faces_in_order(move_type prev_move, move_type move);
unsigned char invalid_prune(unsigned char cost_to_here, move_type *moves_to_here, unsigned int threshold);

#define IDA_BINOM_MAX 32
#define IDA_MOVE_INDEX_MAX MOVE_COUNT_666

extern uint64_t binom[IDA_BINOM_MAX + 1][IDA_BINOM_MAX + 1];

void init_binom(void);
move_type ida_parse_move(const char *move_string, const move_type *moves, unsigned int move_count);
void ida_init_move_tables(
    const move_type *moves,
    unsigned int move_count,
    int (*move_is_allowed)(move_type),
    unsigned char legal_move_count[MOVE_MAX],
    unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX],
    move_type inverse_move[MOVE_MAX]
);
void ida_init_cube(char *cube, unsigned int cube_size, const char *kociemba);
int ida_is_edge_or_corner(unsigned int square, unsigned int cube_size);
uint64_t ida_mixed_radix_rank(const uint64_t *ranks, unsigned int count, uint64_t radix);
uint64_t ida_combination_rank_ud(
    const char *cube,
    const unsigned int *squares,
    unsigned int group_size,
    unsigned int ud_count
);
uint64_t ida_combination_rank_pair(
    const char *cube,
    const unsigned int *squares,
    unsigned int group_size,
    unsigned int color_count,
    uint64_t universe,
    char small,
    char large
);

struct mapped_cost_file {
    int fd;
    unsigned char *costs;
    size_t size;
};

struct mapped_cost_file ida_map_cost_file(const char *filename, uint64_t expected_size);
void ida_unmap_cost_file(int fd, unsigned char *costs, size_t size);

struct symmetry_index_header {
    char magic[8];
    uint64_t raw_universe;
    uint64_t orbit_count;
    uint64_t low_word_count;
    uint64_t high_bit_count;
    uint64_t high_word_count;
    uint64_t zero_sample_count;
    uint32_t low_bits;
    uint32_t zero_sample_rate;
};

struct symmetry_index {
    int fd;
    size_t size;
    unsigned char *mapping;
    const struct symmetry_index_header *header;
    const uint64_t *low;
    const uint64_t *high;
    const uint32_t *zero_samples;
};

uint64_t symmetry_dense_rank(const struct symmetry_index *index, uint64_t raw);
void map_symmetry_index(
    struct symmetry_index *index,
    const char *filename,
    uint64_t expected_raw_universe,
    const char *kind
);
void unmap_symmetry_index(struct symmetry_index *index);

static inline unsigned char decode_cost_byte(unsigned char encoded)
{
    return encoded ? (unsigned char)(encoded - 1) : UINT8_MAX;
}

#endif /* _IDA_SEARCH_CORE_H */
