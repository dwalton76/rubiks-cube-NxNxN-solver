
#include <stdlib.h>
#include <stdio.h>
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
