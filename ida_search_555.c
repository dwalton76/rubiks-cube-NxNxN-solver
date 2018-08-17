
#include <stdlib.h>
#include <stdio.h>
#include "ida_search_core.h"
#include "ida_search_555.h"

unsigned int centers_555[NUM_CENTERS_555] = {
    7, 8, 9, 12, 13, 14, 17, 18, 19,
    32, 33, 34, 37, 38, 39, 42, 43, 44,
    57, 58, 59, 62, 63, 64, 67, 68, 69,
    82, 83, 84, 87, 88, 89, 92, 93, 94,
    107, 108, 109, 112, 113, 114, 117, 118, 119,
    132, 133, 134, 137, 138, 139, 142, 143, 144
};

unsigned int t_centers_555[NUM_T_CENTERS_555] = {
    8, 12, 14, 18,
    33, 37, 39, 43,
    58, 62, 64, 68,
    83, 87, 89, 93,
    108, 112, 114, 118,
    133, 137, 139, 143
};

unsigned int x_centers_555[NUM_T_CENTERS_555] = {
    7, 9, 17, 19,
    32, 34, 42, 44,
    57, 59, 67, 69,
    82, 84, 92, 94,
    107, 109, 117, 119,
    132, 134, 142, 144
};

unsigned long
get_555_centers(char *cube)
{
    unsigned long centers = 0;
    int cube_index;

    for (int i = 0; i < NUM_CENTERS_555; i++) {
        cube_index = centers_555[i];

        if (cube[cube_index] == '1') {
            centers |= 0x1;
        }
        centers <<= 1;
    }
    centers >>= 1;

    return centers;
}

unsigned long
ida_heuristic_UD_centers_555(
    char *cube,
    struct key_value_pair **UD_centers_cost_555,
    char *pt_t_centers_cost_only,
    char *pt_x_centers_cost_only,
    int debug)
{
    unsigned long cost_to_goal = 0;
    unsigned long UD_t_centers_state = 0;
    unsigned long UD_x_centers_state = 0;
    unsigned long UD_t_centers_cost = 0;
    unsigned long UD_x_centers_cost = 0;
    int cube_index;

    for (int i = 0; i < NUM_T_CENTERS_555; i++) {
        if (cube[t_centers_555[i]] == '1') {
            UD_t_centers_state |= 0x1;
        }
        UD_t_centers_state <<= 1;
    }

    for (int i = 0; i < NUM_X_CENTERS_555; i++) {
        if (cube[x_centers_555[i]] == '1') {
            UD_x_centers_state |= 0x1;
        }
        UD_x_centers_state <<= 1;
    }

    UD_t_centers_state >>= 1;
    UD_x_centers_state >>= 1;

    UD_t_centers_cost = hex_to_int(pt_t_centers_cost_only[UD_t_centers_state]);
    UD_x_centers_cost = hex_to_int(pt_x_centers_cost_only[UD_x_centers_state]);
    cost_to_goal = max(UD_t_centers_cost, UD_x_centers_cost);

    // The step10 table we loaded is 5-deep so if a state is not in that
    // table we know it has a cost of at least 6...thus MAX_DEPTH of 6 here.
    int MAX_DEPTH = 6;

    if (cost_to_goal < MAX_DEPTH && cost_to_goal > 0) {
        unsigned long lt_state = get_555_centers(cube);
        char lt_state_str[24];
        sprintf(lt_state_str, "%014lx", lt_state);

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(UD_centers_cost_555, lt_state_str);

        if (hash_entry) {
            //LOG("init cost_to_goal %d, hash_entry %s cost %d\n", cost_to_goal, lt_state_str, hash_entry->value);
            cost_to_goal = max(cost_to_goal, hash_entry->value);
        } else {
            // TODO fix hard code, 5 as in 5-deep because we built the table 4-deep
            //LOG("init cost_to_goal %d, no hash_entry for %s\n", cost_to_goal, lt_state_str);
            cost_to_goal = max(cost_to_goal, MAX_DEPTH);
        }
    }

    if (debug) {
        LOG("ida_heuristic t-centers state %d or 0x%x, cost %d\n", UD_t_centers_state, UD_t_centers_state, UD_t_centers_cost);
        LOG("ida_heuristic x-centers state %d or 0x%x, cost %d\n", UD_x_centers_state, UD_x_centers_state, UD_x_centers_cost);
        LOG("ida_heuristic t-centers %d, x-centers %d, cost_to_goal %d\n", UD_t_centers_cost, UD_x_centers_cost, cost_to_goal);
    }

    return cost_to_goal;
}

int
ida_search_complete_UD_centers_555 (char *cube)
{
    if (cube[7] == '1' &&
        cube[8] == '1' &&
        cube[9] == '1' &&
        cube[12] == '1' &&
        cube[13] == '1' &&
        cube[14] == '1' &&
        cube[17] == '1' &&
        cube[18] == '1' &&
        cube[19] == '1' &&

        cube[132] == '1' &&
        cube[133] == '1' &&
        cube[134] == '1' &&
        cube[137] == '1' &&
        cube[138] == '1' &&
        cube[139] == '1' &&
        cube[142] == '1' &&
        cube[143] == '1' &&
        cube[144] == '1') {
        LOG("UD_CENTERS_STAGE_555 solved\n");
        return 1;
    } else {
        return 0;
    }
}
