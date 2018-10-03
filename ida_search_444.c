
#include <stdlib.h>
#include <stdio.h>
#include "xxhash.h"
#include "ida_search_core.h"
#include "ida_search_444.h"

unsigned int centers_444[NUM_CENTERS_444] = {
    6, 7, 10, 11,
    22, 23, 26, 27,
    38, 39, 42, 43,
    54, 55, 58, 59,
    70, 71, 74, 75,
    86, 87, 90, 91
};


struct wings_for_edges_recolor_pattern_444*
init_wings_for_edges_recolor_pattern_444()
{
    struct wings_for_edges_recolor_pattern_444 *result = NULL;
    struct wings_for_edges_recolor_pattern_444 *curr= NULL;
    result = malloc(sizeof(struct wings_for_edges_recolor_pattern_444) * NUM_EDGES_444);
    curr = result;

    /*
wings_for_edges_recolor_pattern_444 = (
    ('0', 2, 67),  # upper
    ('1', 3, 66),
    ('2', 5, 18),
    ('3', 8, 51),
    ('4', 9, 19),
    ('5', 12, 50),
    ('6', 14, 34),
    ('7', 15, 35),

    ('8', 21, 72), # left
    ('9', 24, 37),
    ('a', 25, 76),
    ('b', 28, 41),

    ('c', 53, 40), # right
    ('d', 56, 69),
    ('e', 57, 44),
    ('f', 60, 73),

    ('g', 82, 46), # down
    ('h', 83, 47),
    ('i', 85, 31),
    ('j', 88, 62),
    ('k', 89, 30),
    ('l', 92, 63),
    ('m', 94, 79),
    ('n', 95, 78)
)
    */

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
struct ida_heuristic_result
ida_heuristic_centers_444 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **centers_cost_444,
    char *UD_centers_cost_only_444,
    char *LR_centers_cost_only_444,
    char *FB_centers_cost_only_444)
{
    unsigned int cost_to_goal = 0;
    unsigned long UD_centers_state = 0;
    unsigned long LR_centers_state = 0;
    unsigned long FB_centers_state = 0;
    unsigned long UD_centers_cost = 0;
    unsigned long LR_centers_cost = 0;
    unsigned long FB_centers_cost = 0;
    struct ida_heuristic_result result;
    memset(&result, 0, sizeof(struct ida_heuristic_result));

    for (unsigned int i = 0; i < NUM_CENTERS_444; i++) {

        if (cube[centers_444[i]] == 'U') {
            UD_centers_state |= 0x1;
        } else if (cube[centers_444[i]] == 'L') {
            LR_centers_state |= 0x1;
        } else if (cube[centers_444[i]] == 'F') {
            FB_centers_state |= 0x1;
        }

        result.lt_state[i] = cube[centers_444[i]];
        UD_centers_state <<= 1;
        LR_centers_state <<= 1;
        FB_centers_state <<= 1;
    }
    UD_centers_state >>= 1;
    LR_centers_state >>= 1;
    FB_centers_state >>= 1;
    UD_centers_cost = hex_to_int(UD_centers_cost_only_444[UD_centers_state]);
    LR_centers_cost = hex_to_int(LR_centers_cost_only_444[LR_centers_state]);
    FB_centers_cost = hex_to_int(FB_centers_cost_only_444[FB_centers_state]);

    cost_to_goal = max(UD_centers_cost, LR_centers_cost);
    cost_to_goal = max(cost_to_goal, FB_centers_cost);

    // The step10 table we loaded is 5-deep so if a state is not in that
    // table we know it has a cost of at least 6...thus MAX_DEPTH of 6 here.
    int MAX_DEPTH = 6;

    if (cost_to_goal < MAX_DEPTH && cost_to_goal > 0) {
        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(centers_cost_444, result.lt_state);

        if (hash_entry) {
            cost_to_goal = max(cost_to_goal, hash_entry->value);
        } else {
            cost_to_goal = max(cost_to_goal, MAX_DEPTH);
        }
    }

    // LOG("lt_state %s, cost_to_goal %d\n", result.lt_state, cost_to_goal);
    result.cost_to_goal = cost_to_goal;
    return result;
}

int
ida_search_complete_centers_444 (char *cube)
{
    if (cube[6] == 'U' && cube[7] == 'U' && cube[10] == 'U' && cube[11] == 'U' &&
        cube[86] == 'U' && cube[87] == 'U' && cube[90] == 'U' && cube[91] == 'U') {

        // UUUULLLLFFFFLLLLFFFFUUUU
        if (cube[22] == 'L' && cube[23] == 'L' && cube[26] == 'L' && cube[27] == 'L' &&
            cube[54] == 'L' && cube[55] == 'L' && cube[58] == 'L' && cube[59] == 'L' &&

            cube[38] == 'F' && cube[39] == 'F' && cube[42] == 'F' && cube[43] == 'F' &&
            cube[70] == 'F' && cube[71] == 'F' && cube[74] == 'F' && cube[75] == 'F') {
            return 1;

        // UUUUFFFFLLLLFFFFLLLLUUUU
        } else if (
            cube[22] == 'F' && cube[23] == 'F' && cube[26] == 'F' && cube[27] == 'F' &&
            cube[54] == 'F' && cube[55] == 'F' && cube[58] == 'F' && cube[59] == 'F' &&

            cube[38] == 'L' && cube[39] == 'L' && cube[42] == 'L' && cube[43] == 'L' &&
            cube[70] == 'L' && cube[71] == 'L' && cube[74] == 'L' && cube[75] == 'L') {
            return 1;
        }

    } else if (
        cube[6] == 'F' && cube[7] == 'F' && cube[10] == 'F' && cube[11] == 'F' &&
        cube[86] == 'F' && cube[87] == 'F' && cube[90] == 'F' && cube[91] == 'F') {

        // FFFFLLLLUUUULLLLUUUUFFFF
        if (cube[22] == 'L' && cube[23] == 'L' && cube[26] == 'L' && cube[27] == 'L' &&
            cube[54] == 'L' && cube[55] == 'L' && cube[58] == 'L' && cube[59] == 'L' &&

            cube[38] == 'U' && cube[39] == 'U' && cube[42] == 'U' && cube[43] == 'U' &&
            cube[70] == 'U' && cube[71] == 'U' && cube[74] == 'U' && cube[75] == 'U') {
            return 1;

        // FFFFUUUULLLLUUUULLLLFFFF
        } else if (
            cube[22] == 'U' && cube[23] == 'U' && cube[26] == 'U' && cube[27] == 'U' &&
            cube[54] == 'U' && cube[55] == 'U' && cube[58] == 'U' && cube[59] == 'U' &&

            cube[38] == 'L' && cube[39] == 'L' && cube[42] == 'L' && cube[43] == 'L' &&
            cube[70] == 'L' && cube[71] == 'L' && cube[74] == 'L' && cube[75] == 'L') {
            return 1;
        }

    } else if (
        cube[6] == 'L' && cube[7] == 'L' && cube[10] == 'L' && cube[11] == 'L' &&
        cube[86] == 'L' && cube[87] == 'L' && cube[90] == 'L' && cube[91] == 'L') {

        // LLLLFFFFUUUUFFFFUUUULLLL
        if (cube[22] == 'F' && cube[23] == 'F' && cube[26] == 'F' && cube[27] == 'F' &&
            cube[54] == 'F' && cube[55] == 'F' && cube[58] == 'F' && cube[59] == 'F' &&

            cube[38] == 'U' && cube[39] == 'U' && cube[42] == 'U' && cube[43] == 'U' &&
            cube[70] == 'U' && cube[71] == 'U' && cube[74] == 'U' && cube[75] == 'U') {
            return 1;

        // LLLLUUUUFFFFUUUUFFFFLLLL
        } else if (
            cube[22] == 'U' && cube[23] == 'U' && cube[26] == 'U' && cube[27] == 'U' &&
            cube[54] == 'U' && cube[55] == 'U' && cube[58] == 'U' && cube[59] == 'U' &&

            cube[38] == 'F' && cube[39] == 'F' && cube[42] == 'F' && cube[43] == 'F' &&
            cube[70] == 'F' && cube[71] == 'F' && cube[74] == 'F' && cube[75] == 'F') {
            return 1;
        }
    }

    return 0;
}

struct ida_heuristic_result
ida_heuristic_reduce_333_444 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **reduce_333_444,
    char *reduce_333_edges_only,
    char *reduce_333_centers_only,
    struct wings_for_edges_recolor_pattern_444 *wings_for_recolor)
{
    unsigned long cost_to_goal = 0;
    unsigned long edges_state_bucket = 0;
    unsigned long centers_state_bucket = 0;
    unsigned int edges_cost = 0;
    unsigned int centers_cost = 0;
    char lt_state[NUM_EDGES_AND_CENTERS_444+2];
    char edges_state[NUM_EDGES_444+1];
    char centers_state[NUM_CENTERS_444+1];
    char i_wing_str[3];
    char j_wing_str[3];
    struct wings_for_edges_recolor_pattern_444 *i_wings_for_recolor = wings_for_recolor;
    struct wings_for_edges_recolor_pattern_444 *j_wings_for_recolor = wings_for_recolor;
    struct ida_heuristic_result result;
    memset(&result, 0, sizeof(struct ida_heuristic_result));

    //memset(centers_state, '\0', NUM_CENTERS_444+1);
    centers_state[NUM_EDGES_444] = '\0';
    memset(edges_state, '\0', NUM_EDGES_444+1);

    // dwalton this loop within a loop is expensive, find a better way to do this
    // Record the two edge_indexes for each of the 12 edges
    for (int i = 0; i < NUM_EDGES_444; i++) {
        j_wings_for_recolor = wings_for_recolor;
        i_wing_str[0] = cube[i_wings_for_recolor->square_index];
        i_wing_str[1] = cube[i_wings_for_recolor->partner_index];
        i_wing_str[2] = '\0';

        if (edges_state[i] != '\0') {
            i_wings_for_recolor++;
            continue;
        }

        if (strmatch(i_wing_str, "BU") ||
            strmatch(i_wing_str, "LU") ||
            strmatch(i_wing_str, "RU") ||
            strmatch(i_wing_str, "FU") ||
            strmatch(i_wing_str, "BL") ||
            strmatch(i_wing_str, "FL") ||
            strmatch(i_wing_str, "BR") ||
            strmatch(i_wing_str, "FR") ||
            strmatch(i_wing_str, "BD") ||
            strmatch(i_wing_str, "LD") ||
            strmatch(i_wing_str, "RD") ||
            strmatch(i_wing_str, "FD"))  {

            i_wing_str[2] = i_wing_str[0];
            i_wing_str[0] = i_wing_str[1];
            i_wing_str[1] = i_wing_str[2];
            i_wing_str[2] = '\0';
        }

        for (int j = 0; j < NUM_EDGES_444; j++) {

            if (i == j || edges_state[j] != '\0') {
                j_wings_for_recolor++;
                continue;
            }

            j_wing_str[0] = cube[j_wings_for_recolor->square_index];
            j_wing_str[1] = cube[j_wings_for_recolor->partner_index];
            j_wing_str[2] = '\0';

            if (strmatch(j_wing_str, "BU") ||
                strmatch(j_wing_str, "LU") ||
                strmatch(j_wing_str, "RU") ||
                strmatch(j_wing_str, "FU") ||
                strmatch(j_wing_str, "BL") ||
                strmatch(j_wing_str, "FL") ||
                strmatch(j_wing_str, "BR") ||
                strmatch(j_wing_str, "FR") ||
                strmatch(j_wing_str, "BD") ||
                strmatch(j_wing_str, "LD") ||
                strmatch(j_wing_str, "RD") ||
                strmatch(j_wing_str, "FD"))  {

                j_wing_str[2] = j_wing_str[0];
                j_wing_str[0] = j_wing_str[1];
                j_wing_str[1] = j_wing_str[2];
                j_wing_str[2] = '\0';
            }

            if (strmatch(i_wing_str, j_wing_str)) {
                edges_state[i] = j_wings_for_recolor->edge_index[0];
                edges_state[j] = i_wings_for_recolor->edge_index[0];
                //LOG("i %d, j %d, wing_str %s, i->edge_index %s, j->edge_index %s\n", i, j, i_wing_str, i_wings_for_recolor->edge_index, j_wings_for_recolor->edge_index);
                break;
            }
            j_wings_for_recolor++;
        }

        i_wings_for_recolor++;
    }
    edges_state_bucket = XXH32(edges_state, NUM_EDGES_444, 0) % BUCKETSIZE_EDGES_444;
    edges_cost = hex_to_int(reduce_333_edges_only[edges_state_bucket]);

    // centers cost
    for (int i = 0; i < NUM_CENTERS_444; i++) {
        centers_state[i] = cube[centers_444[i]];
    }
    centers_state_bucket = XXH32(centers_state, NUM_CENTERS_444, 0) % BUCKETSIZE_CENTERS_444;
    centers_cost = hex_to_int(reduce_333_centers_only[centers_state_bucket]);

    cost_to_goal = max(edges_cost, centers_cost);

    // dwalton here now
    sprintf(result.lt_state, "%s%s", centers_state, edges_state);

    /*
    if (edges_cost == 0) {
        LOG("edges_state %s, edges_hash %lu, edges_bucket %d, edges_cost %d\n",
            edges_state,
            XXH32(edges_state, NUM_EDGES_444, 0),
            edges_state_bucket, edges_cost);
        print_cube(cube, 4);
        exit(0);
    }
    */

    //LOG("edges_state %s, edges_cost %d\n", edges_state, edges_cost);
    //LOG("centers_state %s, centers_cost %d\n", centers_state, centers_cost);
    //LOG("lt_state %s\n", result.lt_state);

    // The table we loaded is 6-deep so if a state is not in that
    // table we know it has a cost of at least 7...thus MAX_DEPTH of 7 here.
    int MAX_DEPTH = 7;

    if (cost_to_goal < MAX_DEPTH && cost_to_goal > 0) {
        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(reduce_333_444, result.lt_state);

        if (hash_entry) {
            cost_to_goal = max(cost_to_goal, hash_entry->value);
        } else {
            cost_to_goal = max(cost_to_goal, MAX_DEPTH);
        }
    }

    result.cost_to_goal = cost_to_goal;
    return result;
}


int
ida_search_complete_reduce_333_444 (char *cube)
{
    // Are the centers solved?
    if (cube[6] == cube[7] && cube[10] == cube[11] && cube[6] == cube[10] &&
        cube[22] == cube[23] && cube[26] == cube[27] && cube[22] == cube[26] &&
        cube[38] == cube[39] && cube[42] == cube[43] && cube[38] == cube[42] &&
        cube[54] == cube[55] && cube[58] == cube[59] && cube[54] == cube[58] &&
        cube[70] == cube[71] && cube[74] == cube[75] && cube[70] == cube[74] &&
        cube[86] == cube[87] && cube[90] == cube[91] && cube[86] == cube[90]) {

        // Are the centers valid? U and D must be on opposite sides, etc
        if ((cube[6] == 'U' && cube[22] == 'L' && cube[38] == 'F' && cube[54] == 'R' && cube[70] == 'B' && cube[86] == 'D') ||
            (cube[6] == 'U' && cube[22] == 'R' && cube[38] == 'B' && cube[54] == 'L' && cube[70] == 'F' && cube[86] == 'D') ||
            (cube[6] == 'D' && cube[22] == 'L' && cube[38] == 'B' && cube[54] == 'R' && cube[70] == 'F' && cube[86] == 'U') ||
            (cube[6] == 'D' && cube[22] == 'R' && cube[38] == 'F' && cube[54] == 'L' && cube[70] == 'B' && cube[86] == 'U')) {

            // Are all edges paired?
            if ( cube[2] == cube[3]  && cube[5]  == cube[9]  && cube[8]  == cube[12] && cube[14] == cube[15] &&
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
