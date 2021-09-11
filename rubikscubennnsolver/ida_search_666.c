
#include "ida_search_666.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "ida_search_core.h"

unsigned int oblique_edges_666[NUM_OBLIQUE_EDGES_666] = {9,   10,  14,  17,  20,  23,  27,  28,  45,  46,  50,  53,
                                                         56,  59,  63,  64,  81,  82,  86,  89,  92,  95,  99,  100,
                                                         117, 118, 122, 125, 128, 131, 135, 136, 153, 154, 158, 161,
                                                         164, 167, 171, 172, 189, 190, 194, 197, 200, 203, 207, 208};

unsigned int left_oblique_edges_666[NUM_LEFT_OBLIQUE_EDGES_666] = {
    9,   20,  17,  28,   // Upper
    45,  56,  53,  64,   // Left
    81,  92,  89,  100,  // Front
    117, 128, 125, 136,  // Right
    153, 164, 161, 172,  // Back
    189, 200, 197, 208,  // Down
};

unsigned int right_oblique_edges_666[NUM_RIGHT_OBLIQUE_EDGES_666] = {
    10,  14,  23,  27,   // Upper
    46,  50,  59,  63,   // Left
    82,  86,  95,  99,   // Front
    118, 122, 131, 135,  // Right
    154, 158, 167, 171,  // Back
    190, 194, 203, 207,  // Down
};

unsigned int get_unpaired_obliques_count_666(char *cube) {
    unsigned int unpaired_obliques = 8;
    unsigned int left_cube_index = 0;
    unsigned int right_cube_index = 0;

    for (int i = 0; i < NUM_LEFT_OBLIQUE_EDGES_666; i++) {
        left_cube_index = left_oblique_edges_666[i];
        right_cube_index = right_oblique_edges_666[i];

        if (cube[left_cube_index] == '1' && cube[right_cube_index] == '1') {
            unpaired_obliques -= 1;
        }
    }

    return unpaired_obliques;
}

// ============================================================================
// step20
// ============================================================================
struct ida_heuristic_result ida_heuristic_LR_oblique_edges_stage_666(char *cube) {
    int unpaired_count = get_unpaired_obliques_count_666(cube);
    struct ida_heuristic_result result;
    unsigned long long state = 0;

    result.unpaired_count = unpaired_count;

    // Get the state of the oblique edges
    for (int i = 0; i < NUM_OBLIQUE_EDGES_666; i++) {
        if (cube[oblique_edges_666[i]] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }

    // 000000033fff is 12 chars
    state >>= 1;
    sprintf(result.lt_state, "%012llx", state);

    // The most oblique edges we can pair in single move is 4 so take the number that are unpaired and divide by 4.
    //
    // time ./ida_search --kociemba
    // ........xL...L..x..L..x...xx................Lx...L..L..x..L...xL................xL...x..x..x..x...xL................Lx...L..x..x..x...xx................xx...x..x..L..L...xL................xx...L..x..x..x...xx........
    // --type 6x6x6-LR-oblique-edges-stage
    //
    // 1.5 took 44s, 9 moves
    // 1.3 took 14s, 9 moves
    // 1.2 took 5.7s, 9 moves
    // 1.1 took 4s, 9 moves
    // 1 took 3s, 9 moves
    // 0.9 took 4s, 9 moves
    //
    // result.cost_to_goal = (int)ceil((double)unpaired_count / 1.2);

    // The math works out that it just basically takes about 1 mpve per unpaired oblique edge
    // so save some cycles and just use the unpaired_count as the heuristic.
    result.cost_to_goal = unpaired_count;

    return result;
}

unsigned char ida_search_complete_LR_oblique_edges_stage_666(char *cube) {
    unsigned int left_cube_index = 0;
    unsigned int right_cube_index = 0;

    for (int i = 0; i < NUM_LEFT_OBLIQUE_EDGES_666; i++) {
        left_cube_index = left_oblique_edges_666[i];
        right_cube_index = right_oblique_edges_666[i];

        if ((cube[left_cube_index] == '1' && cube[right_cube_index] == '0') ||
            (cube[left_cube_index] == '0' && cube[right_cube_index] == '1')) {
            return 0;
        }
    }

    return 1;
}
