
#ifndef _ROTATE_XXX_H
#define _ROTATE_XXX_H

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
