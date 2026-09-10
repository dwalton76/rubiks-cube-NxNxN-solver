
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

unsigned char get_unpaired_obliques_count_666(char *cube) {
    unsigned char paired_obliques = 0;

    // Oblique squares only ever hold '.', '0' or '1' and '1' is the only one of those with its low bit
    // set, so anding the pair together and masking that bit counts a paired oblique without branching.
    // This runs once per node of the IDA search so the mispredicts it avoids are worth the obscurity.
    for (int i = 0; i < NUM_LEFT_OBLIQUE_EDGES_666; i++) {
        paired_obliques += cube[left_oblique_edges_666[i]] & cube[right_oblique_edges_666[i]] & 1;
    }

    return 8 - paired_obliques;
}

// ============================================================================
// step20
// ============================================================================
struct ida_heuristic_result ida_heuristic_oblique_edges_stage_666(char *cube) {
    struct ida_heuristic_result result;
    result.unpaired_count = get_unpaired_obliques_count_666(cube);

    // The math works out that it just basically takes about 1 move per unpaired oblique edge
    // so save some cycles and just use the unpaired_count as the heuristic.
    result.cost_to_goal = result.unpaired_count;

    return result;
}

unsigned char ida_search_complete_oblique_edges_stage_666(char *cube) {
    for (unsigned char i = 0; i < NUM_LEFT_OBLIQUE_EDGES_666; i++) {
        if (cube[left_oblique_edges_666[i]] != cube[right_oblique_edges_666[i]]) {
            return 0;
        }
    }

    return 1;
}
