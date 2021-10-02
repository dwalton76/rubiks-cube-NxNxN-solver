#include "ida_search_777.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "ida_search_core.h"

// ============================================================================
// step20 - stage LR oblique edges
// ============================================================================
unsigned int oblique_edges_777[NUM_OBLIQUE_EDGES_777] = {
    10,  11,  12,  16,  20,  23,  27,  30,  34,  38,  39,  40,   // Upper
    59,  60,  61,  65,  69,  72,  76,  79,  83,  87,  88,  89,   // Left
    108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  // Front
    157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187,  // Right
    206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  // Back
    255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  // Down
};

unsigned int left_oblique_edges_777[NUM_LEFT_OBLIQUE_EDGES_777] = {
    10,  30,  20,  40,   // Upper
    59,  79,  69,  89,   // Left
    108, 128, 118, 138,  // Front
    157, 177, 167, 187,  // Right
    206, 226, 216, 236,  // Back
    255, 275, 265, 285,  // Down
};

unsigned int middle_oblique_edges_777[NUM_MIDDLE_OBLIQUE_EDGES_777] = {
    11,  23,  27,  39,   // Upper
    60,  72,  76,  88,   // Left
    109, 121, 125, 137,  // Front
    158, 170, 174, 186,  // Right
    207, 219, 223, 235,  // Back
    256, 268, 272, 284,  // Down
};

unsigned int right_oblique_edges_777[NUM_RIGHT_OBLIQUE_EDGES_777] = {
    12,  16,  34,  38,   // Upper
    61,  65,  83,  87,   // Left
    110, 114, 132, 136,  // Front
    159, 163, 181, 185,  // Right
    208, 212, 230, 234,  // Back
    257, 261, 279, 283,  // Down
};

unsigned char get_unpaired_obliques_count_777(char *cube) {
    unsigned char left_paired_obliques = 0;
    unsigned char left_unpaired_obliques = 8;
    unsigned char right_paired_obliques = 0;
    unsigned char right_unpaired_obliques = 8;

    unsigned int left_cube_index = 0;
    unsigned int middle_cube_index = 0;
    unsigned int right_cube_index = 0;

    for (unsigned char i = 0; i < NUM_LEFT_OBLIQUE_EDGES_777; i++) {
        middle_cube_index = middle_oblique_edges_777[i];

        if (cube[middle_cube_index] == '1') {
            left_cube_index = left_oblique_edges_777[i];
            right_cube_index = right_oblique_edges_777[i];

            if (cube[left_cube_index] == '1') {
                left_paired_obliques += 1;
            }

            if (cube[right_cube_index] == '1') {
                right_paired_obliques += 1;
            }
        }
    }

    left_unpaired_obliques -= left_paired_obliques;
    right_unpaired_obliques -= right_paired_obliques;
    return (left_unpaired_obliques + right_unpaired_obliques);
}

struct ida_heuristic_result ida_heuristic_LR_oblique_edges_stage_777(char *cube) {
    struct ida_heuristic_result result;
    result.unpaired_count = get_unpaired_obliques_count_777(cube);

    // Get the state of the oblique edges
    /*
    unsigned long long state = 0;

    for (int i = 0; i < NUM_OBLIQUE_EDGES_777; i++) {
        if (cube[oblique_edges_777[i]] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }

    // state takes 18 chars in hex
    state >>= 1;
    sprintf(result.lt_state, "%018llx", state);
    */

    // inadmissable heuristic but fast...kudos to xyzzy for this formula
    /*
    if (unpaired_count > 8) {
        result.cost_to_goal = 4 + (unpaired_count >> 1);
    } else {
        result.cost_to_goal = unpaired_count;
    }
    */

    // The xyzzy heuristic was used to solve a few hundred cubes and build the following
    // switch statement that maps unpaired_count to a move count. The results of this are
    // not a huge difference from the xyzzy heuristic but it does speed up the search a good
    // bit for some problematic cubes.
    switch (result.unpaired_count) {
        case 0:
            result.cost_to_goal = 0;
            break;
        case 1:
        case 2:
            result.cost_to_goal = 1;
            break;
        case 9:
        case 10:
        case 11:
            result.cost_to_goal = result.unpaired_count;
            break;
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
        case 8:
            result.cost_to_goal = result.unpaired_count + 1;
            break;
        case 12:
            result.cost_to_goal = 11;
            break;
        case 13:
        case 14:
        case 15:
        case 16:
            result.cost_to_goal = 12;
            break;
        default:
            printf("invalid case %d\n", result.unpaired_count);
            exit(1);
            break;
    }

    return result;
}

unsigned char ida_search_complete_LR_oblique_edges_stage_777(char *cube) {
    unsigned int left_cube_index = 0;
    unsigned int middle_cube_index = 0;
    unsigned int right_cube_index = 0;

    for (unsigned char i = 0; i < NUM_LEFT_OBLIQUE_EDGES_777; i++) {
        middle_cube_index = middle_oblique_edges_777[i];

        if (cube[middle_cube_index] == '1') {
            left_cube_index = left_oblique_edges_777[i];
            right_cube_index = right_oblique_edges_777[i];

            if (cube[left_cube_index] != '1' || cube[right_cube_index] != '1') {
                return 0;
            }
        }
    }

    return 1;
}

// ============================================================================
// step30 - stage UD oblique edges
// ============================================================================
unsigned int UFBD_oblique_edges_777[NUM_OBLIQUE_EDGES_777] = {
    10,  11,  12,  16,  20,  23,  27,  30,  34,  38,  39,  40,   // Upper
    108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138,  // Front
    206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236,  // Back
    255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285,  // Down
};

unsigned int UFBD_left_oblique_edges_777[NUM_LEFT_OBLIQUE_EDGES_777] = {
    10,  30,  20,  40,   // Upper
    108, 128, 118, 138,  // Front
    206, 226, 216, 236,  // Back
    255, 275, 265, 285,  // Down
};

unsigned int UFBD_middle_oblique_edges_777[NUM_MIDDLE_OBLIQUE_EDGES_777] = {
    11,  23,  27,  39,   // Upper
    109, 121, 125, 137,  // Front
    207, 219, 223, 235,  // Back
    256, 268, 272, 284,  // Down
};

unsigned int UFBD_right_oblique_edges_777[NUM_RIGHT_OBLIQUE_EDGES_777] = {
    12,  16,  34,  38,   // Upper
    110, 114, 132, 136,  // Front
    208, 212, 230, 234,  // Back
    257, 261, 279, 283,  // Down
};

unsigned char get_UFBD_unpaired_obliques_count_777(char *cube) {
    unsigned char unpaired_count = 16;

    for (unsigned char i = 0; i < UFBD_NUM_LEFT_OBLIQUE_EDGES_777; i++) {
        if (cube[UFBD_middle_oblique_edges_777[i]] == '1') {
            if (cube[UFBD_left_oblique_edges_777[i]] == '1') {
                unpaired_count--;
            }

            if (cube[UFBD_right_oblique_edges_777[i]] == '1') {
                unpaired_count--;
            }
        }
    }

    return unpaired_count;
}

struct ida_heuristic_result ida_heuristic_UD_oblique_edges_stage_777(char *cube) {
    struct ida_heuristic_result result;
    result.unpaired_count = get_UFBD_unpaired_obliques_count_777(cube);

    // Get the state of the oblique edges
    /*
    unsigned long long state = 0;

    for (int i = 0; i < UFBD_NUM_OBLIQUE_EDGES_777; i++) {
        if (cube[UFBD_oblique_edges_777[i]] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }

    // state takes 12 chars in hex
    state >>= 1;
    sprintf(result.lt_state, "%012llx", state);
    */

    // inadmissable heuristic but fast...kudos to xyzzy for this formula
    /*
    if (unpaired_count > 8) {
        result.cost_to_goal = 4 + (unpaired_count >> 1);
    } else {
        result.cost_to_goal = unpaired_count;
    }
    */

    // The xyzzy heuristic was used to solve a few hundred cubes and build the following
    // switch statement that maps unpaired_count to a move count. The results of this are
    // not a huge difference from the xyzzy heuristic but it does speed up the search a good
    // bit for some problematic cubes.
    switch (result.unpaired_count) {
        case 0:
            result.cost_to_goal = 0;
            break;
        case 1:
        case 2:
            result.cost_to_goal = 1;
            break;
        case 3:
            result.cost_to_goal = result.unpaired_count;
            break;
        case 4:
        case 5:
        case 6:
        case 7:
            result.cost_to_goal = result.unpaired_count + 1;
            break;
        case 8:
        case 9:
            result.cost_to_goal = 10;
            break;
        case 10:
        case 11:
            result.cost_to_goal = 11;
            break;
        case 12:
        case 13:
        case 14:
        case 15:
        case 16:
            result.cost_to_goal = 12;
            break;
        default:
            printf("invalid case %d\n", result.unpaired_count);
            exit(1);
            break;
    }

    return result;
}

unsigned char ida_search_complete_UD_oblique_edges_stage_777(char *cube) {
    unsigned int left_cube_index = 0;
    unsigned int middle_cube_index = 0;
    unsigned int right_cube_index = 0;

    for (int i = 0; i < UFBD_NUM_LEFT_OBLIQUE_EDGES_777; i++) {
        middle_cube_index = UFBD_middle_oblique_edges_777[i];

        if (cube[middle_cube_index] == '1') {
            left_cube_index = UFBD_left_oblique_edges_777[i];
            right_cube_index = UFBD_right_oblique_edges_777[i];

            if (cube[left_cube_index] != '1' || cube[right_cube_index] != '1') {
                return 0;
            }
        }
    }

    return 1;
}
