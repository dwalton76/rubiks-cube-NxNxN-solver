
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "xxhash.h"
#include "ida_search_core.h"
#include "ida_search_777.h"



// ============================================================================
// step20 - stage UD oblique edges
// ============================================================================
unsigned int oblique_edges_777[NUM_OBLIQUE_EDGES_777] = {
    10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40, // Upper
    59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89, // Left
    108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138, // Front
    157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187, // Right
    206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236, // Back
    255, 256, 257, 261, 265, 268, 272, 275, 279, 283, 284, 285, // Down
};


unsigned int left_oblique_edges_777[NUM_LEFT_OBLIQUE_EDGES_777] = {
    10, 30, 20, 40, // Upper
    59, 79, 69, 89, // Left
    108, 128, 118, 138, // Front
    157, 177, 167, 187, // Right
    206, 226, 216, 236, // Back
    255, 275, 265, 285, // Down
};


unsigned int middle_oblique_edges_777[NUM_MIDDLE_OBLIQUE_EDGES_777] = {
    11, 23, 27, 39, // Upper
    60, 72, 76, 88, // Left
    109, 121, 125, 137, // Front
    158, 170, 174, 186, // Right
    207, 219, 223, 235, // Back
    256, 268, 272, 284, // Down
};


unsigned int right_oblique_edges_777[NUM_RIGHT_OBLIQUE_EDGES_777] = {
    12, 16, 34, 38, // Upper
    61, 65, 83, 87, // Left
    110, 114, 132, 136, // Front
    159, 163, 181, 185, // Right
    208, 212, 230, 234, // Back
    257, 261, 279, 283, // Down
};


unsigned int
get_unpaired_obliques_count_777 (char *cube)
{
    int left_paired_obliques = 0;
    int left_unpaired_obliques = 8;
    int right_paired_obliques = 0;
    int right_unpaired_obliques = 8;

    int left_cube_index = 0;
    int middle_cube_index = 0;
    int right_cube_index = 0;

    for (int i = 0; i < NUM_LEFT_OBLIQUE_EDGES_777; i++) {
        left_cube_index = left_oblique_edges_777[i];
        middle_cube_index = middle_oblique_edges_777[i];
        right_cube_index = right_oblique_edges_777[i];

        if (cube[left_cube_index] == '1' && cube[middle_cube_index] == '1') {
            left_paired_obliques += 1;
        }

        if (cube[right_cube_index] == '1' && cube[middle_cube_index] == '1') {
            right_paired_obliques += 1;
        }
    }

    left_unpaired_obliques -= left_paired_obliques;
    right_unpaired_obliques -= right_paired_obliques;
    return (left_unpaired_obliques + right_unpaired_obliques);
}


struct ida_heuristic_result
ida_heuristic_UD_oblique_edges_stage_777 (
    char *cube,
    unsigned int max_cost_to_goal)
{
    int unpaired_count = get_unpaired_obliques_count_777(cube);
    struct ida_heuristic_result result;
    unsigned long long state = 0;

    // Get the state of the oblique edges
    for (int i = 0; i < NUM_OBLIQUE_EDGES_777; i++) {
        if (cube[oblique_edges_777[i]] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }

    // state takes 18 chars in hex
    state >>= 1;
    sprintf(result.lt_state, "%018llx", state);

    // time ./ida_search --kociemba .........Uxx...U...x..U...x..U...x...xUx..................Uxx...U...U..x...x..x...U...xxx..................xUU...x...U..x...x..x...U...xxx..................xUx...x...x..x...x..x...x...xUx..................Uxx...x...x..x...x..x...U...xUU..................UUx...U...x..U...x..x...U...xxx......... --type 7x7x7-UD-oblique-edges-stage

    // 12 moves in 15s
    //if (unpaired_count > 6) {
    //    result.cost_to_goal = 3 + (unpaired_count >> 1);

    // inadmissable heuristic but fast...kudos to xyzzy for this formula
    // 12 moves in 1s
    if (unpaired_count > 8) {
        result.cost_to_goal = 4 + (unpaired_count >> 1);

    // 12 moves in 800ms
    //if (unpaired_count > 10) {
    //    result.cost_to_goal = 5 + (unpaired_count >> 1);

    } else {
        result.cost_to_goal = unpaired_count;
    }

    return result;
}

int
ida_search_complete_UD_oblique_edges_stage_777 (char *cube)
{
    if (get_unpaired_obliques_count_777(cube) == 0) {
        return 1;
    } else {
        return 0;
    }
}



// ============================================================================
// step30 - stage UD oblique edges
// ============================================================================
unsigned int LFRB_oblique_edges_777[LFRB_NUM_OBLIQUE_EDGES_777] = {
    59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89, // Left
    108, 109, 110, 114, 118, 121, 125, 128, 132, 136, 137, 138, // Front
    157, 158, 159, 163, 167, 170, 174, 177, 181, 185, 186, 187, // Right
    206, 207, 208, 212, 216, 219, 223, 226, 230, 234, 235, 236, // Back
};


unsigned int LFRB_left_oblique_edges_777[LFRB_NUM_LEFT_OBLIQUE_EDGES_777] = {
    59, 79, 69, 89, // Left
    108, 128, 118, 138, // Front
    157, 177, 167, 187, // Right
    206, 226, 216, 236, // Back
};


unsigned int LFRB_middle_oblique_edges_777[LFRB_NUM_MIDDLE_OBLIQUE_EDGES_777] = {
    60, 72, 76, 88, // Left
    109, 121, 125, 137, // Front
    158, 170, 174, 186, // Right
    207, 219, 223, 235, // Back
};


unsigned int LFRB_right_oblique_edges_777[LFRB_NUM_RIGHT_OBLIQUE_EDGES_777] = {
    61, 65, 83, 87, // Left
    110, 114, 132, 136, // Front
    159, 163, 181, 185, // Right
    208, 212, 230, 234, // Back
};


unsigned int
get_LFRB_unpaired_obliques_count_777 (char *cube)
{
    int left_paired_obliques = 0;
    int left_unpaired_obliques = 8;
    int right_paired_obliques = 0;
    int right_unpaired_obliques = 8;

    int left_cube_index = 0;
    int middle_cube_index = 0;
    int right_cube_index = 0;

    for (int i = 0; i < LFRB_NUM_LEFT_OBLIQUE_EDGES_777; i++) {
        left_cube_index = LFRB_left_oblique_edges_777[i];
        middle_cube_index = LFRB_middle_oblique_edges_777[i];
        right_cube_index = LFRB_right_oblique_edges_777[i];

        if (cube[left_cube_index] == '1' && cube[middle_cube_index] == '1') {
            left_paired_obliques += 1;
        }

        if (cube[right_cube_index] == '1' && cube[middle_cube_index] == '1') {
            right_paired_obliques += 1;
        }
    }

    left_unpaired_obliques -= left_paired_obliques;
    right_unpaired_obliques -= right_paired_obliques;
    return (left_unpaired_obliques + right_unpaired_obliques);
}


struct ida_heuristic_result
ida_heuristic_LR_oblique_edges_stage_777 (
    char *cube,
    unsigned int max_cost_to_goal)
{
    int unpaired_count = get_unpaired_obliques_count_777(cube);
    struct ida_heuristic_result result;
    unsigned long long state = 0;

    // Get the state of the oblique edges
    for (int i = 0; i < LFRB_NUM_OBLIQUE_EDGES_777; i++) {
        if (cube[LFRB_oblique_edges_777[i]] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }

    // state takes 18 chars in hex
    state >>= 1;
    sprintf(result.lt_state, "%012llx", state);

    // inadmissable heuristic but fast...kudos to xyzzy for this formula
    if (unpaired_count > 8) {
        result.cost_to_goal = 4 + (unpaired_count >> 1);
    } else {
        result.cost_to_goal = unpaired_count;
    }

    return result;
}

int
ida_search_complete_LR_oblique_edges_stage_777 (char *cube)
{
    if (get_LFRB_unpaired_obliques_count_777(cube) == 0) {
        return 1;
    } else {
        return 0;
    }
}



// ============================================================================
// step40 - LR centers to horizontal bars
// ============================================================================
unsigned int centers_step40_777[NUM_CENTERS_STEP40_777] = {
    58, 59, 60, 61, 62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 86, 87, 88, 89, 90, // Left
    156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188 // Right
};

unsigned int centers_step41_777[NUM_CENTERS_STEP41_777] = {
    59, 61, 65, 66, 67, 68, 69, 73, 74, 75, 79, 80, 81, 82, 83, 87, 89, // Left
    157, 159, 163, 164, 165, 166, 167, 171, 172, 173, 177, 178, 179, 180, 181, 185, 187 // Right
};

unsigned int centers_step42_777[NUM_CENTERS_STEP42_777] = {
    58, 60, 62, 66, 67, 68, 72, 73, 74, 75, 76, 80, 81, 82, 86, 88, 90, // Left
    156, 158, 160, 164, 165, 166, 170, 171, 172, 173, 174, 178, 179, 180, 184, 186, 188 // Right
};

struct ida_heuristic_result ida_heuristic_step40_777 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **step40_777,
    char *step41_777,
    char *step42_777)
{
    unsigned long long lt_state = 0;
    unsigned int cost_to_goal = 0;
    unsigned long step41_state_bucket = 0;
    unsigned long step42_state_bucket = 0;
    unsigned int step41_cost = 0;
    unsigned int step42_cost = 0;
    char step41_state[NUM_CENTERS_STEP41_777];
    char step42_state[NUM_CENTERS_STEP42_777];
    struct ida_heuristic_result result;

    // step41 cost
    for (int i = 0; i < NUM_CENTERS_STEP41_777; i++) {
        step41_state[i] = cube[centers_step41_777[i]];
    }
    step41_state_bucket = XXH32(step41_state, NUM_CENTERS_STEP41_777, 0) % BUCKETSIZE_STEP41_777;
    step41_cost = hex_to_int(step41_777[step41_state_bucket]);

    // step42 cost
    for (int i = 0; i < NUM_CENTERS_STEP42_777; i++) {
        step42_state[i] = cube[centers_step42_777[i]];
    }
    step42_state_bucket = XXH32(step42_state, NUM_CENTERS_STEP42_777, 0) % BUCKETSIZE_STEP42_777;
    step42_cost = hex_to_int(step42_777[step42_state_bucket]);

    // lt_state
    for (int i = 0; i < NUM_CENTERS_STEP40_777; i++) {
        if (cube[centers_step40_777[i]] == 'L') {
            lt_state = lt_state | 0x1;
        }
        lt_state = lt_state << 1;
    }
    lt_state = lt_state >> 1;

    // 0002001ffefff 13 chars
    sprintf(result.lt_state, "%013llx", lt_state);
    cost_to_goal = max(step41_cost, step42_cost);

    if (cost_to_goal > 0) {
        // The step40 table we loaded is 5-deep
        int MAX_DEPTH = 5;

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(step40_777, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {
            cost_to_goal = max(cost_to_goal, MAX_DEPTH+1);
        }
    }

    result.cost_to_goal = cost_to_goal;
    return result;
}

int
ida_search_complete_step40_777 (char *cube)
{
    if (cube[58] == cube[65] && cube[65] == cube[72] && cube[72] == cube[79] && cube[79] == cube[86] && // Left
        cube[59] == cube[66] && cube[66] == cube[73] && cube[73] == cube[80] && cube[80] == cube[87] &&
        cube[60] == cube[67] && cube[67] == cube[74] && cube[74] == cube[81] && cube[81] == cube[88] &&
        cube[61] == cube[68] && cube[68] == cube[75] && cube[75] == cube[82] && cube[82] == cube[89] &&
        cube[62] == cube[69] && cube[69] == cube[76] && cube[76] == cube[83] && cube[83] == cube[90] &&
        cube[156] == cube[163] && cube[163] == cube[170] && cube[170] == cube[177] && cube[177] == cube[184] && // Right
        cube[157] == cube[164] && cube[164] == cube[171] && cube[171] == cube[178] && cube[178] == cube[185] &&
        cube[158] == cube[165] && cube[165] == cube[172] && cube[172] == cube[179] && cube[179] == cube[186] &&
        cube[159] == cube[166] && cube[166] == cube[173] && cube[173] == cube[180] && cube[180] == cube[187] &&
        cube[160] == cube[167] && cube[167] == cube[174] && cube[174] == cube[181] && cube[181] == cube[188]) {
        return 1;
    } else {
        return 0;
    }
}


// ============================================================================
// step50 - UD centers to vertical bars
// ============================================================================
unsigned int centers_step50_777[NUM_CENTERS_STEP50_777] = {
    9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, // Upper
    254, 255, 256, 257, 258, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 282, 283, 284, 285, 286 // Down
};

unsigned int centers_step51_777[NUM_CENTERS_STEP51_777] = {
    10, 12, 16, 17, 18, 19, 20, 24, 25, 26, 30, 31, 32, 33, 34, 38, 40, // Upper
    255, 257, 261, 262, 263, 264, 265, 269, 270, 271, 275, 276, 277, 278, 279, 283, 285 // Down
};

unsigned int centers_step52_777[NUM_CENTERS_STEP52_777] = {
    9, 11, 13, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 37, 39, 41, // Upper
    254, 256, 258, 262, 263, 264, 268, 269, 270, 271, 272, 276, 277, 278, 282, 284, 286 // Down
};

struct ida_heuristic_result ida_heuristic_step50_777 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **step50_777,
    char *step51_777,
    char *step52_777)
{
    unsigned long long lt_state = 0;
    unsigned int cost_to_goal = 0;
    unsigned long step51_state_bucket = 0;
    unsigned long step52_state_bucket = 0;
    unsigned int step51_cost = 0;
    unsigned int step52_cost = 0;
    char step51_state[NUM_CENTERS_STEP51_777];
    char step52_state[NUM_CENTERS_STEP52_777];
    struct ida_heuristic_result result;

    // step51 cost
    for (int i = 0; i < NUM_CENTERS_STEP51_777; i++) {
        step51_state[i] = cube[centers_step51_777[i]];
    }
    step51_state_bucket = XXH32(step51_state, NUM_CENTERS_STEP51_777, 0) % BUCKETSIZE_STEP51_777;
    step51_cost = hex_to_int(step51_777[step51_state_bucket]);

    // step52 cost
    for (int i = 0; i < NUM_CENTERS_STEP52_777; i++) {
        step52_state[i] = cube[centers_step52_777[i]];
    }
    step52_state_bucket = XXH32(step52_state, NUM_CENTERS_STEP52_777, 0) % BUCKETSIZE_STEP52_777;
    step52_cost = hex_to_int(step52_777[step52_state_bucket]);

    // lt_state
    for (int i = 0; i < NUM_CENTERS_STEP50_777; i++) {
        if (cube[centers_step50_777[i]] == 'U') {
            lt_state = lt_state | 0x1;
        }
        lt_state = lt_state << 1;
    }
    lt_state = lt_state >> 1;

    // 0002001ffefff 13 chars
    sprintf(result.lt_state, "%013llx", lt_state);
    cost_to_goal = max(step51_cost, step52_cost);

    if (cost_to_goal > 0) {
        // The step50 table we loaded is 5-deep
        int MAX_DEPTH = 5;

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(step50_777, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {
            cost_to_goal = max(cost_to_goal, MAX_DEPTH+1);
        }
    }

    result.cost_to_goal = cost_to_goal;
    return result;
}

int
ida_search_complete_step50_777 (char *cube)
{
    if (cube[9] == cube[16] && cube[16] == cube[23] && cube[23] == cube[30] && cube[30] == cube[37] && // Upper
        cube[10] == cube[17] && cube[17] == cube[24] && cube[24] == cube[31] && cube[31] == cube[38] &&
        cube[11] == cube[18] && cube[18] == cube[25] && cube[25] == cube[32] && cube[32] == cube[39] &&
        cube[12] == cube[19] && cube[19] == cube[26] && cube[26] == cube[33] && cube[33] == cube[40] &&
        cube[13] == cube[20] && cube[20] == cube[27] && cube[27] == cube[34] && cube[34] == cube[41] &&
        cube[254] == cube[261] && cube[261] == cube[268] && cube[268] == cube[275] && cube[275] == cube[282] && // Down
        cube[255] == cube[262] && cube[262] == cube[269] && cube[269] == cube[276] && cube[276] == cube[283] &&
        cube[256] == cube[263] && cube[263] == cube[270] && cube[270] == cube[277] && cube[277] == cube[284] &&
        cube[257] == cube[264] && cube[264] == cube[271] && cube[271] == cube[278] && cube[278] == cube[285] &&
        cube[258] == cube[265] && cube[265] == cube[272] && cube[272] == cube[279] && cube[279] == cube[286]) {
        return 1;
    } else {
        return 0;
    }
}


// ============================================================================
// step60 - solve centers
// ============================================================================
unsigned int centers_step60_777[NUM_CENTERS_STEP60_777] = {
    9, 10, 11, 12, 13, 16, 17, 18, 19, 20, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 37, 38, 39, 40, 41, // Upper
    58, 59, 60, 61, 62, 65, 66, 67, 68, 69, 72, 73, 74, 75, 76, 79, 80, 81, 82, 83, 86, 87, 88, 89, 90, // Left
    107, 108, 109, 110, 111, 114, 115, 116, 117, 118, 121, 122, 123, 124, 125, 128, 129, 130, 131, 132, 135, 136, 137, 138, 139, // Front
    156, 157, 158, 159, 160, 163, 164, 165, 166, 167, 170, 171, 172, 173, 174, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188, // Right
    205, 206, 207, 208, 209, 212, 213, 214, 215, 216, 219, 220, 221, 222, 223, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237, // Back
    254, 255, 256, 257, 258, 261, 262, 263, 264, 265, 268, 269, 270, 271, 272, 275, 276, 277, 278, 279, 282, 283, 284, 285, 286 // Down
};

unsigned int centers_step61_777[NUM_CENTERS_STEP61_777] = {
    108, 110, 114, 115, 116, 117, 118, 122, 123, 124, 128, 129, 130, 131, 132, 136, 138, // Front
    206, 208, 212, 213, 214, 215, 216, 220, 221, 222, 226, 227, 228, 229, 230, 234, 236 // Back
};

unsigned int centers_step62_777[NUM_CENTERS_STEP62_777] = {
    107, 109, 111, 115, 116, 117, 121, 122, 123, 124, 125, 129, 130, 131, 135, 137, 139, // Front
    205, 207, 209, 213, 214, 215, 219, 220, 221, 222, 223, 227, 228, 229, 233, 235, 237 // Back
};

unsigned int centers_step63_777[NUM_CENTERS_STEP63_777] = {
    23, 24, 25, 26, 27, // Upper
    60, 67, 74, 81, 88, // Left
    115, 116, 117, 122, 123, 124, 129, 130, 131, // Front
    158, 165, 172, 179, 186, // Right
    213, 214, 215, 220, 221, 222, 227, 228, 229, // Back
    268, 269, 270, 271, 272 // Down
};

struct ida_heuristic_result ida_heuristic_step60_777 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **step60_777,
    char *step61_777,
    char *step62_777,
    char *step63_777)
{
    int cost_to_goal = 0;
    unsigned long step61_state_bucket = 0;
    unsigned long step62_state_bucket = 0;
    unsigned long step63_state_bucket = 0;
    unsigned int step61_cost = 0;
    unsigned int step62_cost = 0;
    unsigned int step63_cost = 0;
    char lt_state[NUM_CENTERS_STEP60_777+2];
    char step61_state[NUM_CENTERS_STEP61_777];
    char step62_state[NUM_CENTERS_STEP62_777];
    char step63_state_str[24];
    unsigned long long step63_state = 0;
    struct ida_heuristic_result result;

    // step61 cost
    for (int i = 0; i < NUM_CENTERS_STEP61_777; i++) {
        step61_state[i] = cube[centers_step61_777[i]];
    }
    step61_state_bucket = XXH32(step61_state, NUM_CENTERS_STEP61_777, 0) % BUCKETSIZE_STEP61_777;
    step61_cost = hex_to_int(step61_777[step61_state_bucket]);

    if (step61_cost >= max_cost_to_goal) {
        result.cost_to_goal = step61_cost;
        return result;
    }

    // step62 cost
    for (int i = 0; i < NUM_CENTERS_STEP62_777; i++) {
        step62_state[i] = cube[centers_step62_777[i]];
    }
    step62_state_bucket = XXH32(step62_state, NUM_CENTERS_STEP62_777, 0) % BUCKETSIZE_STEP62_777;
    step62_cost = hex_to_int(step62_777[step62_state_bucket]);

    if (step62_cost >= max_cost_to_goal) {
        result.cost_to_goal = step62_cost;
        return result;
    }

    // This one used hex (I should have done step61 and step62 this way) so it bitshifts
    // instead of using an array.
    //
    // step63 cost
    for (int i = 0; i < NUM_CENTERS_STEP63_777; i++) {
        if (cube[centers_step63_777[i]] == 'U' ||
            cube[centers_step63_777[i]] == 'L' ||
            cube[centers_step63_777[i]] == 'F') {
            step63_state |= 0x1;
        }
        step63_state <<= 1;
    }
    step63_state >>= 1;

    // 08408efd7b is 10 chars
    sprintf(step63_state_str, "%010llx", step63_state);
    step63_state_bucket = XXH32(step63_state_str, 10, 0) % BUCKETSIZE_STEP63_777;
    step63_cost = hex_to_int(step63_777[step63_state_bucket]);

    if (step63_cost >= max_cost_to_goal) {
        result.cost_to_goal = step63_cost;
        return result;
    }

    // we have 19 bytes of data which is 152 bits but lt_state is 150 bits
    // so we need to pad the first two bits with 0s
    lt_state[0] = '0';
    lt_state[1] = '0';

    // lt_state
    for (int i = 0; i < NUM_CENTERS_STEP60_777; i++) {
        if (cube[centers_step60_777[i]] == 'U' ||
            cube[centers_step60_777[i]] == 'L' ||
            cube[centers_step60_777[i]] == 'F') {
            lt_state[i+2] = '1';
        } else {
            lt_state[i+2] = '0';
        }
    }

    for (int i = 0; i < 38; i++) {
        int tmp = 0;

        if (lt_state[0 + (i * 4)] == '1') {
            tmp |= 0x8;
        }

        if (lt_state[1 + (i * 4)] == '1') {
            tmp |= 0x4;
        }

        if (lt_state[2 + (i * 4)] == '1') {
            tmp |= 0x2;
        }

        if (lt_state[3 + (i * 4)] == '1') {
            tmp |= 0x1;
        }
        
        switch (tmp) {
        case 0:
            result.lt_state[i] = '0';
            break;
        case 1:
            result.lt_state[i] = '1';
            break;
        case 2:
            result.lt_state[i] = '2';
            break;
        case 3:
            result.lt_state[i] = '3';
            break;
        case 4:
            result.lt_state[i] = '4';
            break;
        case 5:
            result.lt_state[i] = '5';
            break;
        case 6:
            result.lt_state[i] = '6';
            break;
        case 7:
            result.lt_state[i] = '7';
            break;
        case 8:
            result.lt_state[i] = '8';
            break;
        case 9:
            result.lt_state[i] = '9';
            break;
        case 10:
            result.lt_state[i] = 'a';
            break;
        case 11:
            result.lt_state[i] = 'b';
            break;
        case 12:
            result.lt_state[i] = 'c';
            break;
        case 13:
            result.lt_state[i] = 'd';
            break;
        case 14:
            result.lt_state[i] = 'e';
            break;
        case 15:
            result.lt_state[i] = 'f';
            break;
        }
    }

    int original_cost_to_goal = max(max(step61_cost, step62_cost), step63_cost);

    if (original_cost_to_goal > 0) {
        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(step60_777, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {
            // ./ida_search --kociemba BLFBRRULDUUDULLDUUDUDDDUUDUDDDUUDUFFDUUDUURFFFLFBLBLBBDFULLLLLRBRRRRRRDRRRRRRULLLLLLRRRRRRDULDLFDBUURUUDDRFBBFBFDFFFBFRRFBFFBLFBBBFFBBFBBBBBFULRUDLDLBUFBFUUDDUDFRUDDUDBLUDDUDBRUDDUDRBUDDUDFRFUFBLRUUURFRBLRRRRRDDLLLLLFDLLLLLFLRRRRRUULLLLLRFLUUDRLRUUULBLDFFBBBDDFFFBFLBFBBBFFDBBFFBBBFBFFBBDFRLBRD --type 7x7x7-step60
            // 99 : 16 moves in 39s
            //  5 : 16 moves in 2.5s
            //  4 : 17 moves in 4s
            //  3 : 18 moves in 2s
            //  2 : 19 moves in 3s
            //  0 : 20 moves in 40s

            // ./ida_search --kociemba xxxxxxxxUUUUDxxUUUUDxxUUUUDxxUUUUDxxUUUUDxxxxxxxxxxxxxxxxLLLLLxxLLLLLxxRRRRRxxRRRRRxxLLLLLxxxxxxxxxxxxxxxxBFBBBxxBBFFFxxFBFFFxxBBFFBxxFBFBBxxxxxxxxxxxxxxxxDDDDUxxDDDDUxxDDDDUxxDDDDUxxDDDDUxxxxxxxxxxxxxxxxRRRRRxxRRRRRxxLLLLLxxLLLLLxxRRRRRxxxxxxxxxxxxxxxxFFFFFxxFBBFBxxBBBFBxxBBBFFxxFFBFBxxxxxxxx --type 7x7x7-step60

            //  5 : 17 moves in 3m 0s
            //  4 : 17 moves in 45s
            //  3 : 18 moves in 54s
            //  2 : 18 moves in 43s
            //  1 : 18 moves in 23s
            //  0 : 19 moves in 2m
            unsigned int heuristic_stats_error = 4;
            cost_to_goal = original_cost_to_goal + heuristic_stats_error;
        
            // These stats come from back when I was using python IDA here. These are not
            // admissible but it DRASTICALLY speeds up this search. At the time that I
            // collected these stats I was not using the step63 table.
            switch (step61_cost) {
            case 0:
                switch (step62_cost) {
                case 0:
                    cost_to_goal = 1;
                    break;
                case 1:
                    cost_to_goal = 8;
                    break;
                case 2:
                    cost_to_goal = 9;
                    break;
                case 3:
                    cost_to_goal = 4;
                    break;
                case 4:
                    cost_to_goal = 6;
                    break;
                case 5:
                    cost_to_goal = 6;
                    break;
                default:
                    break;
                }
                break;
            case 1:
                switch (step62_cost) {
                case 0:
                    cost_to_goal = 9;
                    break;
                case 1:
                    cost_to_goal = 2;
                    break;
                case 2:
                    cost_to_goal = 6;
                    break;
                case 3:
                    cost_to_goal = 8;
                    break;
                case 4:
                    cost_to_goal = 5;
                    break;
                default:
                    break;
                }
                break;
            case 2:
                switch (step62_cost) {
                case 0:
                    cost_to_goal = 9;
                    break;
                case 1:
                    cost_to_goal = 8;
                    break;
                case 2:
                    cost_to_goal = 4;
                    break;
                case 3:
                    cost_to_goal = 6;
                    break;
                case 4:
                    cost_to_goal = 8;
                    break;
                case 5:
                    cost_to_goal = 6;
                    break;
                case 6:
                    cost_to_goal = 7;
                    break;
                default:
                    break;
                }
                break;
            case 3:
                switch (step62_cost) {
                case 1:
                    cost_to_goal = 11;
                    break;
                case 2:
                    cost_to_goal = 9;
                    break;
                case 3:
                    cost_to_goal = 7;
                    break;
                case 4:
                    cost_to_goal = 6;
                    break;
                case 5:
                    cost_to_goal = 8;
                    break;
                case 6:
                    cost_to_goal = 14;
                    break;
                default:
                    break;
                }
                break;
            case 4:
                switch (step62_cost) {
                case 2:
                    cost_to_goal = 11;
                    break;
                case 3:
                    cost_to_goal = 10;
                    break;
                case 4:
                    cost_to_goal = 9;
                    break;
                case 5:
                    cost_to_goal = 10;
                    break;
                case 6:
                    cost_to_goal = 13;
                    break;
                case 7:
                    cost_to_goal = 15;
                    break;
                default:
                    break;
                }
                break;
            case 5:
                switch (step62_cost) {
                case 3:
                    cost_to_goal = 12;
                    break;
                case 4:
                    cost_to_goal = 11;
                    break;
                case 5:
                    cost_to_goal = 11;
                    break;
                case 6:
                    cost_to_goal = 12;
                    break;
                case 7:
                    cost_to_goal = 15;
                    break;
                case 8:
                    cost_to_goal = 16;
                    break;
                default:
                    break;
                }
                break;
            case 6:
                switch (step62_cost) {
                case 4:
                    cost_to_goal = 13;
                    break;
                case 5:
                    cost_to_goal = 12;
                    break;
                case 6:
                    cost_to_goal = 13;
                    break;
                case 7:
                    cost_to_goal = 14;
                    break;
                case 8:
                    cost_to_goal = 15;
                    break;
                case 9:
                    cost_to_goal = 15;
                    break;
                default:
                    break;
                }
                break;
            case 7:
                switch (step62_cost) {
                case 4:
                    cost_to_goal = 15;
                    break;
                case 5:
                    cost_to_goal = 14;
                    break;
                case 6:
                    cost_to_goal = 13;
                    break;
                case 7:
                    cost_to_goal = 14;
                    break;
                case 8:
                    cost_to_goal = 15;
                    break;
                case 9:
                    cost_to_goal = 16;
                    break;
                case 10:
                    cost_to_goal = 18;
                    break;
                case 11:
                    cost_to_goal = 18;
                    break;
                default:
                    break;
                }
                break;
            case 8:
                switch (step62_cost) {
                case 5:
                    cost_to_goal = 16;
                    break;
                case 6:
                    cost_to_goal = 15;
                    break;
                case 7:
                    cost_to_goal = 15;
                    break;
                case 8:
                    cost_to_goal = 15;
                    break;
                case 9:
                    cost_to_goal = 16;
                    break;
                case 10:
                    cost_to_goal = 18;
                    break;
                case 11:
                    cost_to_goal = 16;
                    break;
                default:
                    break;
                }
                break;
            case 9:
                switch (step62_cost) {
                case 5:
                    cost_to_goal = 17;
                    break;
                case 6:
                    cost_to_goal = 16;
                    break;
                case 7:
                    cost_to_goal = 16;
                    break;
                case 8:
                    cost_to_goal = 16;
                    break;
                case 9:
                    cost_to_goal = 17;
                    break;
                case 10:
                    cost_to_goal = 17;
                    break;
                case 11:
                    cost_to_goal = 19;
                    break;
                default:
                    break;
                }
                break;
            case 10:
                switch (step62_cost) {
                case 6:
                    cost_to_goal = 17;
                    break;
                case 7:
                    cost_to_goal = 16;
                    break;
                case 8:
                    cost_to_goal = 17;
                    break;
                case 9:
                    cost_to_goal = 17;
                    break;
                case 10:
                    cost_to_goal = 19;
                    break;
                case 11:
                    cost_to_goal = 18;
                    break;
                case 12:
                    cost_to_goal = 16;
                    break;
                default:
                    break;
                }
                break;
            case 11:
                switch (step62_cost) {
                case 7:
                    cost_to_goal = 17;
                    break;
                case 8:
                    cost_to_goal = 18;
                    break;
                case 9:
                    cost_to_goal = 18;
                    break;
                case 10:
                    cost_to_goal = 18;
                    break;
                case 11:
                    cost_to_goal = 19;
                    break;
                default:
                    break;
                }
                break;
            case 12:
                switch (step62_cost) {
                case 9:
                    cost_to_goal = 19;
                    break;
                case 10:
                    cost_to_goal = 19;
                    break;
                case 11:
                    cost_to_goal = 20;
                    break;
                default:
                    break;
                }
                break;
            default:
                break;
            }
        
            cost_to_goal -= heuristic_stats_error;
        
            // If the heuristic_error is set to high and it gives us a cost_to_goal
            // that is below both the centers_cost and edges_cost then we know we
            // have subtracted too much in this scenario.  Go back to using the max
            // among centers_cost and edges_cost.
            if (cost_to_goal < original_cost_to_goal) {
                cost_to_goal = original_cost_to_goal;
            }

            // The step60 table we loaded is 6-deep
            int MAX_DEPTH = 6;
            cost_to_goal = max(cost_to_goal, MAX_DEPTH+1);
        }

    } else {
        cost_to_goal = 0;
    }

    result.cost_to_goal = cost_to_goal;
    return result;
}

int
ida_search_complete_step60_777 (char *cube)
{
    if (cube[107] == 'F' && cube[108] == 'F' && cube[109] == 'F' && cube[110] == 'F' && cube[111] == 'F' && // Front
        cube[114] == 'F' && cube[115] == 'F' && cube[116] == 'F' && cube[117] == 'F' && cube[118] == 'F' &&
        cube[121] == 'F' && cube[122] == 'F' && cube[123] == 'F' && cube[124] == 'F' && cube[125] == 'F' &&
        cube[128] == 'F' && cube[129] == 'F' && cube[130] == 'F' && cube[131] == 'F' && cube[132] == 'F' &&
        cube[135] == 'F' && cube[136] == 'F' && cube[137] == 'F' && cube[138] == 'F' && cube[139] == 'F' &&

        cube[9]  == 'U' && cube[10] == 'U' && cube[11] == 'U' && cube[12] == 'U' && cube[13] == 'U' && // Upper
        cube[16] == 'U' && cube[17] == 'U' && cube[18] == 'U' && cube[19] == 'U' && cube[20] == 'U' &&
        cube[23] == 'U' && cube[24] == 'U' && cube[25] == 'U' && cube[26] == 'U' && cube[27] == 'U' &&
        cube[30] == 'U' && cube[31] == 'U' && cube[32] == 'U' && cube[33] == 'U' && cube[34] == 'U' &&
        cube[37] == 'U' && cube[38] == 'U' && cube[39] == 'U' && cube[40] == 'U' && cube[41] == 'U' &&

        cube[58] == 'L' && cube[59] == 'L' && cube[60] == 'L' && cube[61] == 'L' && cube[62] == 'L' && // Left
        cube[65] == 'L' && cube[66] == 'L' && cube[67] == 'L' && cube[68] == 'L' && cube[69] == 'L' &&
        cube[72] == 'L' && cube[73] == 'L' && cube[74] == 'L' && cube[75] == 'L' && cube[76] == 'L' &&
        cube[79] == 'L' && cube[80] == 'L' && cube[81] == 'L' && cube[82] == 'L' && cube[83] == 'L' &&
        cube[86] == 'L' && cube[87] == 'L' && cube[88] == 'L' && cube[89] == 'L' && cube[90] == 'L') {
        return 1;
    } else {
        return 0;
    }
}


// ============================================================================
// step70 - solve centers
// ============================================================================
unsigned int centers_step70_777[NUM_CENTERS_STEP70_777] = {
    107, 108, 109, 110, 111, 114, 115, 116, 117, 118, 121, 122, 123, 124, 125, 128, 129, 130, 131, 132, 135, 136, 137, 138, 139, // Front
    205, 206, 207, 208, 209, 212, 213, 214, 215, 216, 219, 220, 221, 222, 223, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237 // Back
};

struct ida_heuristic_result ida_heuristic_step70_777 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **step70_777,
    char *step61_777,
    char *step62_777)
{
    int cost_to_goal = 0;
    unsigned long step61_state_bucket = 0;
    unsigned long step62_state_bucket = 0;
    unsigned int step61_cost = 0;
    unsigned int step62_cost = 0;
    char lt_state[NUM_CENTERS_STEP60_777+2];
    char step61_state[NUM_CENTERS_STEP61_777];
    char step62_state[NUM_CENTERS_STEP62_777];
    struct ida_heuristic_result result;
    unsigned long long centers_state = 0;

    // step61 cost
    for (int i = 0; i < NUM_CENTERS_STEP61_777; i++) {
        step61_state[i] = cube[centers_step61_777[i]];
    }
    step61_state_bucket = XXH32(step61_state, NUM_CENTERS_STEP61_777, 0) % BUCKETSIZE_STEP61_777;
    step61_cost = hex_to_int(step61_777[step61_state_bucket]);

    if (step61_cost >= max_cost_to_goal) {
        result.cost_to_goal = step61_cost;
        return result;
    }

    // step62 cost
    for (int i = 0; i < NUM_CENTERS_STEP62_777; i++) {
        step62_state[i] = cube[centers_step62_777[i]];
    }
    step62_state_bucket = XXH32(step62_state, NUM_CENTERS_STEP62_777, 0) % BUCKETSIZE_STEP62_777;
    step62_cost = hex_to_int(step62_777[step62_state_bucket]);

    if (step62_cost >= max_cost_to_goal) {
        result.cost_to_goal = step62_cost;
        return result;
    }

    // centers
    for (int i = 0; i < NUM_CENTERS_STEP70_777; i++) {
        if (cube[centers_step70_777[i]] == 'F') {
            centers_state |= 0x1;
        }
        centers_state <<= 1;
    }
    centers_state >>= 1;

    // 0002009bfefff is 13 chars
    sprintf(result.lt_state, "%013llx", centers_state);
    cost_to_goal = max(step61_cost, step62_cost);

    if (cost_to_goal > 0) {
        // The step70 table we loaded is 6-deep
        int MAX_DEPTH = 6;

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(step70_777, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {
            cost_to_goal = max(cost_to_goal, MAX_DEPTH+1);
        }
    }

    result.cost_to_goal = cost_to_goal;
    return result;
}

int
ida_search_complete_step70_777 (char *cube)
{
    if (cube[107] == 'F' && cube[108] == 'F' && cube[109] == 'F' && cube[110] == 'F' && cube[111] == 'F' && // Front
        cube[114] == 'F' && cube[115] == 'F' && cube[116] == 'F' && cube[117] == 'F' && cube[118] == 'F' &&
        cube[121] == 'F' && cube[122] == 'F' && cube[123] == 'F' && cube[124] == 'F' && cube[125] == 'F' &&
        cube[128] == 'F' && cube[129] == 'F' && cube[130] == 'F' && cube[131] == 'F' && cube[132] == 'F' &&
        cube[135] == 'F' && cube[136] == 'F' && cube[137] == 'F' && cube[138] == 'F' && cube[139] == 'F') {
        return 1;
    } else {
        return 0;
    }
}
