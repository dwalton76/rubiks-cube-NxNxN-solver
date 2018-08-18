
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "ida_search_core.h"
#include "ida_search_666.h"


unsigned int oblique_edges_666[NUM_OBLIQUE_EDGES_666] = {
    9, 10, 14, 17, 20, 23, 27, 28,
    45, 46, 50, 53, 56, 59, 63, 64,
    81, 82, 86, 89, 92, 95, 99, 100,
    117, 118, 122, 125, 128, 131, 135, 136,
    153, 154, 158, 161, 164, 167, 171, 172,
    189, 190, 194, 197, 200, 203, 207, 208
};


unsigned int left_oblique_edges_666[NUM_LEFT_OBLIQUE_EDGES_666] = {
    9, 14, 17, 27,
    45, 50, 53, 63,
    81, 86, 89, 99,
    117, 122, 125, 135,
    153, 158, 161, 171,
    189, 194, 197, 207
};


unsigned int right_oblique_edges_666[NUM_RIGHT_OBLIQUE_EDGES_666] = {
    10, 20, 23, 28,
    46, 56, 59, 64,
    82, 92, 95, 100,
    118, 128, 131, 136,
    154, 164, 167, 172,
    190, 200, 203, 208
};

unsigned int LFRB_inner_x_centers_666[NUM_LFRB_INNER_X_CENTERS_666] = {
    51, 52, 57, 58,
    87, 88, 93, 94,
    123, 124, 129, 130,
    159, 160, 165, 166
};

unsigned int LFRB_inner_x_centers_and_oblique_edges_666[NUM_LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666] = {
        45, 46,
    50, 51, 52, 53,
    56, 57, 58, 59,
        63, 64,

        81, 82,
    86, 87, 88, 89,
    92, 93, 94, 95,
        99, 100,

         117, 118,
    122, 123, 124, 125,
    128, 129, 130, 131,
         135, 136,

         153, 154,
    158, 159, 160, 161,
    164, 165, 166, 167,
         171, 172
};

unsigned int
get_unpaired_obliques_count_666 (char *cube)
{
    int paired_obliques = 0;
    int unpaired_obliques = 8;
    int left_cube_index = 0;
    int right_cube_index = 0;

    for (int i = 0; i < NUM_LEFT_OBLIQUE_EDGES_666; i++) {
        left_cube_index = left_oblique_edges_666[i];
        right_cube_index = right_oblique_edges_666[i];

        if (cube[left_cube_index] == '1' && cube[right_cube_index] == '1') {
            paired_obliques += 1;
        }
    }

    unpaired_obliques -= paired_obliques;
    return unpaired_obliques;
}


// ============================================================================
// step20
// ============================================================================
unsigned long
get_UD_oblique_edges_stage_666 (char *cube)
{
    unsigned long state = 0;
    int cube_index;

    for (int i = 0; i < NUM_OBLIQUE_EDGES_666; i++) {
        cube_index = oblique_edges_666[i];

        if (cube[cube_index] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }
    state >>= 1;

    return state;
}

unsigned long
ida_heuristic_UD_oblique_edges_stage_666 (char *cube)
{
    int unpaired_count = get_unpaired_obliques_count_666(cube);

    // The most oblique edges we can pair in single move is 4 so take
    // the number that are unpaired and divide by 4.
    //
    // admissable but slow
    // return (int) ceil(unpaired_count / 4);

    // RFFRBDLBRFFFBLLBBRURFRUFLUBURRDDDRBLUDDBRLDFUDDBDLDDDLBFFUBLULLLDRBFFLRRLLLURFDBURRBFFBUBFBFBRRUBRBLFLRBRFDUFUDRFRLDBUULBFLDBRBLDRLBLLDUFFLFFRFDDFDRUFBULDDRLDLUDUDDFBRLRUURLUUBDUDUBRBUDFLBRUBDUFUFDUFFRLRLURBFLUBUDLUB
    // admissable took 6m 24s, explored 1,946,110,533 total, found 6 move solution
    // divide by 2 took 9s, found solution 6 moves
    // divide by 1.7 took 2.2s, found solution 7 moves
    // divide by 1.6 took 580ms, found solution 7 moves
    // divide by 1.5 took 580ms, found solution 7 moves
    // divide by 1.4 took 400ms, found solution 7 moves
    // divide by 1.0 took 280ms, found solution 8 moves

    // inadmissable but a million times faster
    return (int) ceil(unpaired_count / 1.6);
}

int
ida_search_complete_UD_oblique_edges_stage_666 (char *cube)
{
    if (get_unpaired_obliques_count_666(cube) == 0) {
        return 1;
    } else {
        return 0;
    }
}


// ============================================================================
// step30
// ============================================================================
unsigned long
get_LR_inner_x_centers_and_oblique_edges_stage (char *cube)
{
    unsigned long state = 0;
    int cube_index;

    for (int i = 0; i < NUM_LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666; i++) {
        cube_index = LFRB_inner_x_centers_and_oblique_edges_666[i];

        if (cube[cube_index] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }
    state >>= 1;

    return state;
}

unsigned long
ida_heuristic_LR_inner_x_centers_and_oblique_edges_stage_666 (
    char *cube,
    char *LR_inner_x_centers_cost_666
)
{
    unsigned long inner_x_centers_state = 0;
    unsigned long inner_x_centers_cost = 0;
    int cube_index;
    int unpaired_count;
    int oblique_edges_cost;

    // The most oblique edges we can pair in single move is 4 so take
    // the number that are unpaired and divide by 4.
    //
    // admissable but slow
    unpaired_count = get_unpaired_obliques_count_666(cube);
    oblique_edges_cost = (int) ceil(unpaired_count / 4);

    // Now get the state for the inner x-centers on LFRB
    for (int i = 0; i < NUM_LFRB_INNER_X_CENTERS_666; i++) {
        if (cube[LFRB_inner_x_centers_666[i]] == '1') {
            inner_x_centers_state |= 0x1;
        }
        inner_x_centers_state <<= 1;
    }
    inner_x_centers_state >>= 1;
    inner_x_centers_cost = hex_to_int(LR_inner_x_centers_cost_666[inner_x_centers_state]);

    //LOG("FOO inner_x_centers_cost %d, unpaired_count %d, oblique_edges_cost %d\n", inner_x_centers_cost, unpaired_count, oblique_edges_cost);
    return max(oblique_edges_cost, inner_x_centers_cost);
}

int
ida_search_complete_LR_inner_x_centers_and_oblique_edges_stage (char *cube)
{
    if ((
        // First check if the inner x-centers are staged
        (cube[51] == '1' &&
         cube[52] == '1' &&
         cube[57] == '1' &&
         cube[58] == '1' &&
         cube[123] == '1' &&
         cube[124] == '1' &&
         cube[129] == '1' &&
         cube[130] == '1') ||

        (cube[51] == '0' &&
         cube[52] == '0' &&
         cube[57] == '0' &&
         cube[58] == '0' &&
         cube[123] == '0' &&
         cube[124] == '0' &&
         cube[129] == '0' &&
         cube[130] == '0')) &&

        // Then check if all LR oblique edges are paired
        get_unpaired_obliques_count_666(cube) == 0) {
        return 1;
    } else {
        return 0;
    }
}
