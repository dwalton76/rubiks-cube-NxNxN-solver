
#ifndef _ROTATE_XXX_H
#define _ROTATE_XXX_H

typedef enum {
    MOVE_NONE,

    U, U_PRIME, U2, 
    L, L_PRIME, L2, 
    F, F_PRIME, F2, 
    R, R_PRIME, R2, 
    B, B_PRIME, B2, 
    D, D_PRIME, D2, 

    Uw, Uw_PRIME, Uw2,
    Lw, Lw_PRIME, Lw2,
    Fw, Fw_PRIME, Fw2,
    Rw, Rw_PRIME, Rw2,
    Bw, Bw_PRIME, Bw2,
    Dw, Dw_PRIME, Dw2,

    X, X_PRIME,
    Y, Y_PRIME,
    Z, Z_PRIME,
    MOVE_MAX
} move_type;

#define MAX_MOVE_STR_SIZE 5

static const char move2str[MOVE_MAX][MAX_MOVE_STR_SIZE] = { 
    "N/A",
    "U", "U'", "U2",
    "L", "L'", "L2",
    "F", "F'", "F2",
    "R", "R'", "R2",
    "B", "B'", "B2",
    "D", "D'", "D2",
    "Uw", "Uw'", "Uw2",
    "Lw", "Lw'", "Lw2",
    "Fw", "Fw'", "Fw2",
    "Rw", "Rw'", "Rw2",
    "Bw", "Bw'", "Bw2",
    "Dw", "Dw'", "Dw2"
};


#define MOVE_COUNT_555 36
static const move_type moves_555[MOVE_COUNT_555] = { 
    U, U_PRIME, U2, 
    L, L_PRIME, L2, 
    F, F_PRIME, F2, 
    R, R_PRIME, R2, 
    B, B_PRIME, B2, 
    D, D_PRIME, D2, 
    Uw, Uw_PRIME, Uw2,
    Lw, Lw_PRIME, Lw2,
    Fw, Fw_PRIME, Fw2,
    Rw, Rw_PRIME, Rw2,
    Bw, Bw_PRIME, Bw2,
    Dw, Dw_PRIME, Dw2 
};


int strmatch (char *str1, char *str2);
void rotate_555(char *cube, char *cube_tmp, int array_size, move_type move);

#endif /* _ROTATE_XXX_H */
