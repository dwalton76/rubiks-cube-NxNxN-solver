
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

unsigned int
get_UD_unpaired_obliques_count_666 (char *cube)
{
    int UD_paired_obliques = 0;
    int UD_unpaired_obliques = 8;
    int left_cube_index = 0;
    int right_cube_index = 0;

    for (int i = 0; i < NUM_LEFT_OBLIQUE_EDGES_666; i++) {
        left_cube_index = left_oblique_edges_666[i];
        right_cube_index = right_oblique_edges_666[i];

        if (cube[left_cube_index] == '1' && cube[right_cube_index] == '1') {
            UD_paired_obliques += 1;
        }
    }

    UD_unpaired_obliques -= UD_paired_obliques;
    return UD_unpaired_obliques;
}

unsigned long
ida_heuristic_UD_oblique_edges_stage_666 (char *cube)
{
    int unpaired_count = get_UD_unpaired_obliques_count_666(cube);

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
    if (get_UD_unpaired_obliques_count_666(cube) == 0) {
        return 1;
    } else {
        return 0;
    }
}
