#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "ida_search_444.h"
#include "ida_search_core.h"
#include "xxhash.h"

unsigned int centers_444[NUM_CENTERS_444] = {6,  7,  10, 11, 22, 23, 26, 27, 38, 39, 42, 43,
                                             54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91};

unsigned int centers_edges_cost_444[10][13] = {
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12},   // centers cost 0
    {1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12},   // centers cost 1
    {2, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 12},   // centers cost 2
    {3, 3, 3, 3, 4, 5, 6, 7, 8, 9, 12, 13, 12},   // centers cost 3
    {4, 4, 4, 4, 4, 5, 6, 7, 8, 9, 12, 13, 14},   // centers cost 4
    {5, 5, 5, 5, 5, 5, 6, 7, 8, 9, 12, 13, 14},   // centers cost 5
    {6, 6, 6, 6, 6, 6, 6, 7, 8, 9, 12, 13, 12},   // centers cost 6
    {7, 7, 7, 7, 7, 7, 7, 7, 8, 9, 12, 13, 12},   // centers cost 7
    {8, 8, 8, 8, 8, 8, 8, 8, 8, 11, 12, 13, 12},  // centers cost 8
    {9, 9, 9, 9, 9, 9, 9, 9, 13, 9, 10, 13, 12},  // centers cost 9
};

struct wings_for_edges_recolor_pattern_444 *init_wings_for_edges_recolor_pattern_444() {
    struct wings_for_edges_recolor_pattern_444 *result = NULL;
    struct wings_for_edges_recolor_pattern_444 *curr = NULL;
    result = malloc(sizeof(struct wings_for_edges_recolor_pattern_444) * NUM_EDGES_444);
    curr = result;

    curr->edge_index[0] = '0';
    curr->square_index = 2;
    curr->partner_index = 67;
    curr++;

    curr->edge_index[0] = '1';
    curr->square_index = 3;
    curr->partner_index = 66;
    curr++;

    curr->edge_index[0] = '2';
    curr->square_index = 5;
    curr->partner_index = 18;
    curr++;

    curr->edge_index[0] = '4';
    curr->square_index = 9;
    curr->partner_index = 19;
    curr++;

    curr->edge_index[0] = '3';
    curr->square_index = 8;
    curr->partner_index = 51;
    curr++;

    curr->edge_index[0] = '5';
    curr->square_index = 12;
    curr->partner_index = 50;
    curr++;

    curr->edge_index[0] = '6';
    curr->square_index = 14;
    curr->partner_index = 34;
    curr++;

    curr->edge_index[0] = '7';
    curr->square_index = 15;
    curr->partner_index = 35;
    curr++;

    curr->edge_index[0] = '8';
    curr->square_index = 21;
    curr->partner_index = 72;
    curr++;

    curr->edge_index[0] = 'a';
    curr->square_index = 25;
    curr->partner_index = 76;
    curr++;

    curr->edge_index[0] = '9';
    curr->square_index = 24;
    curr->partner_index = 37;
    curr++;

    curr->edge_index[0] = 'b';
    curr->square_index = 28;
    curr->partner_index = 41;
    curr++;

    curr->edge_index[0] = 'c';
    curr->square_index = 53;
    curr->partner_index = 40;
    curr++;

    curr->edge_index[0] = 'e';
    curr->square_index = 57;
    curr->partner_index = 44;
    curr++;

    curr->edge_index[0] = 'd';
    curr->square_index = 56;
    curr->partner_index = 69;
    curr++;

    curr->edge_index[0] = 'f';
    curr->square_index = 60;
    curr->partner_index = 73;
    curr++;

    curr->edge_index[0] = 'g';
    curr->square_index = 82;
    curr->partner_index = 46;
    curr++;

    curr->edge_index[0] = 'h';
    curr->square_index = 83;
    curr->partner_index = 47;
    curr++;

    curr->edge_index[0] = 'i';
    curr->square_index = 85;
    curr->partner_index = 31;
    curr++;

    curr->edge_index[0] = 'k';
    curr->square_index = 89;
    curr->partner_index = 30;
    curr++;

    curr->edge_index[0] = 'j';
    curr->square_index = 88;
    curr->partner_index = 62;
    curr++;

    curr->edge_index[0] = 'l';
    curr->square_index = 92;
    curr->partner_index = 63;
    curr++;

    curr->edge_index[0] = 'm';
    curr->square_index = 94;
    curr->partner_index = 79;
    curr++;

    curr->edge_index[0] = 'n';
    curr->square_index = 95;
    curr->partner_index = 78;
    curr++;

    return result;
}

// ===========================================================================
// step 10
// ===========================================================================
void edges_state_444(char *cube, struct wings_for_edges_recolor_pattern_444 *wings_for_recolor, char *edges_state) {
    struct wings_for_edges_recolor_pattern_444 *i_wings_for_recolor = wings_for_recolor;
    struct wings_for_edges_recolor_pattern_444 *j_wings_for_recolor = wings_for_recolor;
    unsigned int flip_wing_str = 0;
    char i_wing_str[2];
    char j_wing_str[2];
    char tmp_char;
    memset(edges_state, '\0', NUM_EDGES_444 + 1);

    // Record the two edge_indexes for each of the 12 edges
    for (int i = 0; i < NUM_EDGES_444; i++) {
        // If we already populated this one move on
        if (edges_state[i] != '\0') {
            i_wings_for_recolor++;
            continue;
        }

        // j_wings_for_recolor = wings_for_recolor;
        i_wing_str[0] = cube[i_wings_for_recolor->square_index];
        i_wing_str[1] = cube[i_wings_for_recolor->partner_index];
        flip_wing_str = 0;

        // Flip BU around to UB, etc.  We do this so the two use the same wing_str.
        // U, D, L, and F should always be the first charcter.
        if (i_wing_str[1] == 'U' || i_wing_str[1] == 'D') {
            if (i_wing_str[0] == 'B' || i_wing_str[0] == 'L' || i_wing_str[0] == 'R' || i_wing_str[0] == 'F') {
                flip_wing_str = 1;
            }
        } else if (i_wing_str[1] == 'L' || i_wing_str[1] == 'R') {
            if (i_wing_str[0] == 'B' || i_wing_str[0] == 'F') {
                flip_wing_str = 1;
            }
        }

        if (flip_wing_str) {
            tmp_char = i_wing_str[0];
            i_wing_str[0] = i_wing_str[1];
            i_wing_str[1] = tmp_char;
        }

        j_wings_for_recolor = i_wings_for_recolor;
        j_wings_for_recolor++;

        for (int j = i + 1; j < NUM_EDGES_444; j++) {
            // If we already populated this one move on
            if (i == j || edges_state[j] != '\0') {
                j_wings_for_recolor++;
                continue;
            }

            j_wing_str[0] = cube[j_wings_for_recolor->square_index];
            j_wing_str[1] = cube[j_wings_for_recolor->partner_index];
            flip_wing_str = 0;

            // Flip BU around to UB, etc.  We do this so the two use the same wing_str.
            // U, D, L, and F should always be the first charcter.
            if (j_wing_str[1] == 'U' || j_wing_str[1] == 'D') {
                if (j_wing_str[0] == 'B' || j_wing_str[0] == 'L' || j_wing_str[0] == 'R' || j_wing_str[0] == 'F') {
                    flip_wing_str = 1;
                }
            } else if (j_wing_str[1] == 'L' || j_wing_str[1] == 'R') {
                if (j_wing_str[0] == 'B' || j_wing_str[0] == 'F') {
                    flip_wing_str = 1;
                }
            }

            if (flip_wing_str) {
                tmp_char = j_wing_str[0];
                j_wing_str[0] = j_wing_str[1];
                j_wing_str[1] = tmp_char;
            }

            if (i_wing_str[0] == j_wing_str[0] && i_wing_str[1] == j_wing_str[1]) {
                edges_state[i] = j_wings_for_recolor->edge_index[0];
                edges_state[j] = i_wings_for_recolor->edge_index[0];
                // LOG("i %d, j %d, wing_str %s, i->edge_index %s, j->edge_index %s\n", i, j, i_wing_str,
                // i_wings_for_recolor->edge_index, j_wings_for_recolor->edge_index);
                break;
            }
            j_wings_for_recolor++;
        }

        i_wings_for_recolor++;
    }
}

void centers_state_444(char *cube, char *centers_state) {
    centers_state[NUM_CENTERS_444] = '\0';

    for (int i = 0; i < NUM_CENTERS_444; i++) {
        centers_state[i] = cube[centers_444[i]];
    }
}

struct ida_heuristic_result ida_heuristic_reduce_333_444(
    char *cube, unsigned int max_cost_to_goal, char *reduce_333_edges_only, char *reduce_333_centers_only,
    struct wings_for_edges_recolor_pattern_444 *wings_for_recolor) {
    unsigned long edges_state_bucket = 0;
    unsigned long centers_state_bucket = 0;
    unsigned int edges_cost = 0;
    unsigned int centers_cost = 0;
    unsigned int cost_to_goal = 0;
    char lt_state[NUM_EDGES_AND_CENTERS_444 + 2];
    char edges_state[NUM_EDGES_444 + 1];
    char centers_state[NUM_CENTERS_444 + 1];
    struct ida_heuristic_result result;
    memset(&result, 0, sizeof(struct ida_heuristic_result));

    // edges cost
    edges_state_444(cube, wings_for_recolor, edges_state);
    edges_state_bucket = XXH32(edges_state, NUM_EDGES_444, 0) % BUCKETSIZE_EDGES_444;
    edges_cost = hex_to_int(reduce_333_edges_only[edges_state_bucket]);
    // LOG("edges_state %s, edges_cost %d\n", edges_state, edges_cost);

    // centers cost
    centers_state_444(cube, centers_state);
    centers_state_bucket = XXH32(centers_state, NUM_CENTERS_444, 0) % BUCKETSIZE_CENTERS_444;
    centers_cost = hex_to_int(reduce_333_centers_only[centers_state_bucket]);
    // LOG("centers_state %s, centers_cost %d\n", centers_state, centers_cost);

    sprintf(result.lt_state, "%s%s", centers_state, edges_state);
    // LOG("lt_state %s\n", result.lt_state);

    result.cost_to_goal = max(edges_cost, centers_cost);

    if (result.cost_to_goal) {
        result.cost_to_goal = centers_edges_cost_444[centers_cost][edges_cost];
    }

    return result;
}

unsigned char ida_search_complete_reduce_333_444(char *cube) {
    // Are the centers solved?
    if (cube[6] == cube[7] && cube[10] == cube[11] && cube[6] == cube[10] && cube[22] == cube[23] &&
        cube[26] == cube[27] && cube[22] == cube[26] && cube[38] == cube[39] && cube[42] == cube[43] &&
        cube[38] == cube[42] && cube[54] == cube[55] && cube[58] == cube[59] && cube[54] == cube[58] &&
        cube[70] == cube[71] && cube[74] == cube[75] && cube[70] == cube[74] && cube[86] == cube[87] &&
        cube[90] == cube[91] && cube[86] == cube[90]) {
        // Are the centers valid? U and D must be on opposite sides, etc
        if ((cube[6] == 'U' && cube[22] == 'L' && cube[38] == 'F' && cube[54] == 'R' && cube[70] == 'B' &&
             cube[86] == 'D') ||
            (cube[6] == 'U' && cube[22] == 'R' && cube[38] == 'B' && cube[54] == 'L' && cube[70] == 'F' &&
             cube[86] == 'D') ||
            (cube[6] == 'D' && cube[22] == 'L' && cube[38] == 'B' && cube[54] == 'R' && cube[70] == 'F' &&
             cube[86] == 'U') ||
            (cube[6] == 'D' && cube[22] == 'R' && cube[38] == 'F' && cube[54] == 'L' && cube[70] == 'B' &&
             cube[86] == 'U')) {
            // Are all edges paired?
            if (cube[2] == cube[3] && cube[5] == cube[9] && cube[8] == cube[12] && cube[14] == cube[15] &&
                cube[18] == cube[19] && cube[21] == cube[25] && cube[24] == cube[28] && cube[30] == cube[31] &&
                cube[34] == cube[35] && cube[37] == cube[41] && cube[40] == cube[44] && cube[46] == cube[47] &&
                cube[50] == cube[51] && cube[53] == cube[57] && cube[56] == cube[60] && cube[62] == cube[63] &&
                cube[66] == cube[67] && cube[69] == cube[73] && cube[72] == cube[76] && cube[78] == cube[79] &&
                cube[82] == cube[83] && cube[85] == cube[89] && cube[88] == cube[92] && cube[94] == cube[95]) {
                return 1;
            }
        }
    }
    return 0;
}
