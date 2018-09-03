
#ifndef _ROTATE_XXX_H
#define _ROTATE_XXX_H

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
    "3Dw", "3Dw'", "3Dw2"
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

#endif /* _ROTATE_XXX_H */
