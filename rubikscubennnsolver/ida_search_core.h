
#ifndef _IDA_SEARCH_CORE_H
#define _IDA_SEARCH_CORE_H

#include "uthash.h"

typedef enum {
    CPU_NONE,
    CPU_FAST,
    CPU_NORMAL,
    CPU_SLOW,
} cpu_mode_type;


typedef enum {
    MOVE_NONE,

    U, U_PRIME, U2,
    Uw, Uw_PRIME, Uw2,
    threeUw, threeUw_PRIME, threeUw2,

    L, L_PRIME, L2,
    Lw, Lw_PRIME, Lw2,
    threeLw, threeLw_PRIME, threeLw2,

    F, F_PRIME, F2,
    Fw, Fw_PRIME, Fw2,
    threeFw, threeFw_PRIME, threeFw2,

    R, R_PRIME, R2,
    Rw, Rw_PRIME, Rw2,
    threeRw, threeRw_PRIME, threeRw2,

    B, B_PRIME, B2,
    Bw, Bw_PRIME, Bw2,
    threeBw, threeBw_PRIME, threeBw2,

    D, D_PRIME, D2,
    Dw, Dw_PRIME, Dw2,
    threeDw, threeDw_PRIME, threeDw2,

    X, X_PRIME,
    Y, Y_PRIME,
    Z, Z_PRIME,
    MOVE_MAX
} move_type;

#define MAX_MOVE_STR_SIZE 5

static const char move2str[MOVE_MAX][MAX_MOVE_STR_SIZE] = {
    "N/A",
    "U", "U'", "U2",
    "Uw", "Uw'", "Uw2",
    "3Uw", "3Uw'", "3Uw2",

    "L", "L'", "L2",
    "Lw", "Lw'", "Lw2",
    "3Lw", "3Lw'", "3Lw2",

    "F", "F'", "F2",
    "Fw", "Fw'", "Fw2",
    "3Fw", "3Fw'", "3Fw2",

    "R", "R'", "R2",
    "Rw", "Rw'", "Rw2",
    "3Rw", "3Rw'", "3Rw2",

    "B", "B'", "B2",
    "Bw", "Bw'", "Bw2",
    "3Bw", "3Bw'", "3Bw2",

    "D", "D'", "D2",
    "Dw", "Dw'", "Dw2",
    "3Dw", "3Dw'", "3Dw2",

    "X", "X'",
    "Y", "Y'",
    "Z", "Z'",
};

#define MOVE_COUNT_444 36
static const move_type moves_444[MOVE_COUNT_444] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2,
    L, L_PRIME, L2, Lw, Lw_PRIME, Lw2,
    F, F_PRIME, F2, Fw, Fw_PRIME, Fw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2,
    B, B_PRIME, B2, Bw, Bw_PRIME, Bw2,
    D, D_PRIME, D2, Dw, Dw_PRIME, Dw2
};


#define MOVE_COUNT_555 36
static const move_type moves_555[MOVE_COUNT_555] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2,
    L, L_PRIME, L2, Lw, Lw_PRIME, Lw2,
    F, F_PRIME, F2, Fw, Fw_PRIME, Fw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2,
    B, B_PRIME, B2, Bw, Bw_PRIME, Bw2,
    D, D_PRIME, D2, Dw, Dw_PRIME, Dw2
};


#define MOVE_COUNT_666 54
static const move_type moves_666[MOVE_COUNT_666] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2, threeUw, threeUw_PRIME, threeUw2,
    L, L_PRIME, L2, Lw, Lw_PRIME, Lw2, threeLw, threeLw_PRIME, threeLw2,
    F, F_PRIME, F2, Fw, Fw_PRIME, Fw2, threeFw, threeFw_PRIME, threeFw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2, threeRw, threeRw_PRIME, threeRw2,
    B, B_PRIME, B2, Bw, Bw_PRIME, Bw2, threeBw, threeBw_PRIME, threeBw2,
    D, D_PRIME, D2, Dw, Dw_PRIME, Dw2, threeDw, threeDw_PRIME, threeDw2
};

#define MOVE_COUNT_777 54
static const move_type moves_777[MOVE_COUNT_777] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2, threeUw, threeUw_PRIME, threeUw2,
    L, L_PRIME, L2, Lw, Lw_PRIME, Lw2, threeLw, threeLw_PRIME, threeLw2,
    F, F_PRIME, F2, Fw, Fw_PRIME, Fw2, threeFw, threeFw_PRIME, threeFw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2, threeRw, threeRw_PRIME, threeRw2,
    B, B_PRIME, B2, Bw, Bw_PRIME, Bw2, threeBw, threeBw_PRIME, threeBw2,
    D, D_PRIME, D2, Dw, Dw_PRIME, Dw2, threeDw, threeDw_PRIME, threeDw2
};

void rotate_222(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_333(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_444(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_555(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_666(char *cube, char *cube_tmp, int array_size, move_type move);
void rotate_777(char *cube, char *cube_tmp, int array_size, move_type move);

void LOG(const char *fmt, ...);
unsigned long hex_to_int(char value);
unsigned long max (unsigned long a, unsigned long b);

struct ida_heuristic_result {
    char lt_state[64];
    unsigned int cost_to_goal;
};


// uthash references
// http://troydhanson.github.io/uthash/index.html
// https://cfsa-pmw.warwick.ac.uk/SDF/SDF_C/blob/3cf5bf49856ef9ee4080cf6722cf9058a1e28b01/src/uthash/tests/example.c
//
struct key_value_pair {
    unsigned char state[64]; /* we'll use this field as the key */
    unsigned int value;
    UT_hash_handle hh; /* makes this structure hashable */
};


void hash_add (struct key_value_pair **hashtable, char *state_key, unsigned long value);
struct key_value_pair *hash_find (struct key_value_pair **hashtable, char *state_key);
void hash_delete (struct key_value_pair **hashtable, struct key_value_pair *s);
void hash_delete_all(struct key_value_pair **hashtable);
unsigned long hash_count (struct key_value_pair **hashtable);
void hash_print_all (struct key_value_pair **hashtable);
void print_cube (char *cube, int size);
int strmatch (char *str1, char *str2);

void print_moves (move_type *moves, int max_i);

unsigned int wide_turn_count(move_type *moves);
unsigned int get_orbit0_wide_half_turn_count (move_type *moves);
unsigned int get_orbit0_wide_quarter_turn_count (move_type *moves);
unsigned int get_orbit1_wide_quarter_turn_count (move_type *moves);
unsigned int get_outer_layer_quarter_turn_count(move_type *moves);
int moves_cancel_out (move_type move, move_type prev_move);
int steps_on_same_face_and_layer (move_type move, move_type prev_move);

#endif /* _IDA_SEARCH_CORE_H */
