
#include <stdlib.h>
#include <stdio.h>
#include "xxhash.h"
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

unsigned int ULRD_centers_555[NUM_ULRD_CENTERS_555] = {
    7, 8, 9, 12, 13, 14, 17, 18, 19, // Upper
    32, 33, 34, 37, 38, 39, 42, 43, 44, // Left
    82, 83, 84, 87, 88, 89, 92, 93, 94, // Right
    132, 133, 134, 137, 138, 139, 142, 143, 144  // Down
};

unsigned int UFBD_centers_555[NUM_UFBD_CENTERS_555] = {
    7, 8, 9, 12, 13, 14, 17, 18, 19, // Upper
    57, 58, 59, 62, 63, 64, 67, 68, 69, // Front
    107, 108, 109, 112, 113, 114, 117, 118, 119, // Back
    132, 133, 134, 137, 138, 139, 142, 143, 144  // Down
};

unsigned int LFRB_centers_555[NUM_LFRB_CENTERS_555] = {
    32, 33, 34, 37, 38, 39, 42, 43, 44, // Left
    57, 58, 59, 62, 63, 64, 67, 68, 69, // Front
    82, 83, 84, 87, 88, 89, 92, 93, 94, // Right
    107, 108, 109, 112, 113, 114, 117, 118, 119 // Back
};


// ===========================================================================
// step 10
// ===========================================================================
struct ida_heuristic_result
ida_heuristic_LR_centers_555(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **LR_centers_cost_555,
    char *pt_LR_t_centers_cost_only,
    char *pt_LR_x_centers_cost_only,
    cpu_mode_type cpu_mode)
{
    unsigned int cost_to_goal = 0;
    unsigned long long LR_t_centers_state = 0;
    unsigned long long LR_x_centers_state = 0;
    unsigned long LR_t_centers_cost = 0;
    unsigned long LR_x_centers_cost = 0;
    unsigned long long LR_centers_state = 0;
    struct ida_heuristic_result result;

    // t-centers
    for (int i = 0; i < NUM_T_CENTERS_555; i++) {
        if (cube[t_centers_555[i]] == '1') {
            LR_t_centers_state |= 0x1;
        }
        LR_t_centers_state <<= 1;
    }
    LR_t_centers_state >>= 1;
    LR_t_centers_cost = hex_to_int(pt_LR_t_centers_cost_only[LR_t_centers_state]);

    // x-centers
    for (int i = 0; i < NUM_X_CENTERS_555; i++) {
        if (cube[x_centers_555[i]] == '1') {
            LR_x_centers_state |= 0x1;
        }
        LR_x_centers_state <<= 1;
    }
    LR_x_centers_state >>= 1;
    LR_x_centers_cost = hex_to_int(pt_LR_x_centers_cost_only[LR_x_centers_state]);

    // centers
    for (int i = 0; i < NUM_CENTERS_555; i++) {
        if (cube[centers_555[i]] == '1') {
            LR_centers_state |= 0x1;
        }
        LR_centers_state <<= 1;
    }

    LR_centers_state >>= 1;
    cost_to_goal = max(LR_t_centers_cost, LR_x_centers_cost);
    sprintf(result.lt_state, "%014llx", LR_centers_state);

    /*
    LOG("LR_t_centers_state %llu, LR_t_centers_cost %d\n", LR_t_centers_state, LR_t_centers_cost);
    LOG("LR_x_centers_state %llu, LR_x_centers_cost %d\n", LR_x_centers_state, LR_x_centers_cost);
    LOG("LR_centers_state %llu, cost_to_goal %d\n", LR_centers_state, cost_to_goal);
     */

    if (cost_to_goal > 0) {
        // The step10 table we loaded is 5-deep
        int MAX_DEPTH = 5;

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(LR_centers_cost_555, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {

            if (cpu_mode == CPU_FAST) {
                cost_to_goal = max((int) cost_to_goal * 1.2, MAX_DEPTH+1);
            } else {
                cost_to_goal = max((int) cost_to_goal, MAX_DEPTH+1);
            }
        }
    }

    //if (debug) {
    //    LOG("ida_heuristic t-centers state %d or 0x%x, cost %d\n", LR_t_centers_state, LR_t_centers_state, LR_t_centers_cost);
    //    LOG("ida_heuristic x-centers state %d or 0x%x, cost %d\n", LR_x_centers_state, LR_x_centers_state, LR_x_centers_cost);
    //    LOG("ida_heuristic t-centers %d, x-centers %d, cost_to_goal %d\n", LR_t_centers_cost, LR_x_centers_cost, cost_to_goal);
    //}

    result.cost_to_goal = cost_to_goal;
    return result;
}

int
ida_search_complete_LR_centers_555 (char *cube)
{
    if (cube[32] == '1' &&
        cube[33] == '1' &&
        cube[34] == '1' &&
        cube[37] == '1' &&
        cube[38] == '1' &&
        cube[39] == '1' &&
        cube[42] == '1' &&
        cube[43] == '1' &&
        cube[44] == '1' &&

        cube[82] == '1' &&
        cube[83] == '1' &&
        cube[84] == '1' &&
        cube[87] == '1' &&
        cube[88] == '1' &&
        cube[89] == '1' &&
        cube[92] == '1' &&
        cube[93] == '1' &&
        cube[94] == '1') {
        LOG("LR_CENTERS_STAGE_555 solved\n");
        return 1;
    } else {
        return 0;
    }
}


// ===========================================================================
// step 30
// ===========================================================================
struct ida_heuristic_result
ida_heuristic_ULFRBD_centers_555 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **ULFRBD_centers_cost_555,
    char *UL_centers_cost_only_555,
    char *UF_centers_cost_only_555,
    char *LF_centers_cost_only_555)
{
    unsigned int cost_to_goal = 0;
    unsigned long long UL_centers_state = 0;
    unsigned long UL_centers_cost = 0;
    unsigned long UL_centers_bucket = 0;

    unsigned long long UF_centers_state = 0;
    unsigned long UF_centers_cost = 0;
    unsigned long UF_centers_bucket = 0;

    unsigned long long LF_centers_state = 0;
    unsigned long LF_centers_cost = 0;
    unsigned long LF_centers_bucket = 0;

    unsigned long long centers_state = 0;
    struct ida_heuristic_result result;
    char UL_centers_state_str[24];
    char UF_centers_state_str[24];
    char LF_centers_state_str[24];
    unsigned long BUCKETS = 24010031;
    unsigned int STATE_LENGTH = 9;
    unsigned int HASH_SEED = 0;

    // UL centers
    for (int i = 0; i < NUM_ULRD_CENTERS_555; i++) {
        if (cube[ULRD_centers_555[i]] == '1') {
            UL_centers_state |= 0x1;
        }
        UL_centers_state <<= 1;
    }
    UL_centers_state >>= 1;
    sprintf(UL_centers_state_str , "%09llx", UL_centers_state);
    UL_centers_bucket = XXH32(UL_centers_state_str, STATE_LENGTH, HASH_SEED) % BUCKETS;
    UL_centers_cost = hex_to_int(UL_centers_cost_only_555[UL_centers_bucket]);

    if (UL_centers_cost >= max_cost_to_goal) {
        result.cost_to_goal = UL_centers_cost;
        return result;
    }

    // UF centers
    for (int i = 0; i < NUM_UFBD_CENTERS_555; i++) {
        if (cube[UFBD_centers_555[i]] == '1') {
            UF_centers_state |= 0x1;
        }
        UF_centers_state <<= 1;
    }
    UF_centers_state >>= 1;
    sprintf(UF_centers_state_str , "%09llx", UF_centers_state);
    UF_centers_bucket = XXH32(UF_centers_state_str, STATE_LENGTH, HASH_SEED) % BUCKETS;
    UF_centers_cost = hex_to_int(UF_centers_cost_only_555[UF_centers_bucket]);

    if (UF_centers_cost >= max_cost_to_goal) {
        result.cost_to_goal = UF_centers_cost;
        return result;
    }

    // LF centers
    for (int i = 0; i < NUM_LFRB_CENTERS_555; i++) {
        if (cube[LFRB_centers_555[i]] == '1') {
            LF_centers_state |= 0x1;
        }
        LF_centers_state <<= 1;
    }
    LF_centers_state >>= 1;
    sprintf(LF_centers_state_str , "%09llx", LF_centers_state);
    LF_centers_bucket = XXH32(LF_centers_state_str, STATE_LENGTH, HASH_SEED) % BUCKETS;
    LF_centers_cost = hex_to_int(LF_centers_cost_only_555[LF_centers_bucket]);

    if (LF_centers_cost >= max_cost_to_goal) {
        result.cost_to_goal = LF_centers_cost;
        return result;
    }

    // centers
    for (int i = 0; i < NUM_CENTERS_555; i++) {
        if (cube[centers_555[i]] == '1') {
            centers_state |= 0x1;
        }
        centers_state <<= 1;
    }

    centers_state >>= 1;

    // 3ffffff8000000 is 14 chars
    sprintf(result.lt_state, "%014llx", centers_state);
    cost_to_goal = max(UL_centers_cost, UF_centers_cost);
    cost_to_goal = max(cost_to_goal, LF_centers_cost);

    /*
    LOG("sizeof(unsigned long) %d\n", sizeof(unsigned long));
    LOG("sizeof(unsigned long long) %d\n", sizeof(unsigned long long));
    LOG("UL_centers_state %llu, UL_centers_state_str %s, UL_centers_bucket %d, UL_centers_cost %d\n",
        UL_centers_state, UL_centers_state_str, UL_centers_bucket, UL_centers_cost);
    LOG("UF_centers_state %llu, UF_centers_state_str %s, UF_centers_bucket %d, UF_centers_cost %d\n",
        UF_centers_state, UF_centers_state_str, UF_centers_bucket, UF_centers_cost);
    LOG("LF_centers_state %llu, LF_centers_state_str %s, LF_centers_bucket %d, LF_centers_cost %d\n",
        LF_centers_state, LF_centers_state_str, LF_centers_bucket, LF_centers_cost);
    LOG("centers_state %llu, lt_state %s, cost_to_goal %d\n", centers_state, result.lt_state, cost_to_goal);
    */

    if (cost_to_goal > 0) {
        // The step30 table we loaded is 6-deep
        int MAX_DEPTH = 5;
        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(ULFRBD_centers_cost_555, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {
            cost_to_goal = max(cost_to_goal, MAX_DEPTH+1);
        }
    }

    //if (debug) {
    //    LOG("ida_heuristic t-centers state %d or 0x%x, cost %d\n", t_centers_state, t_centers_state, t_centers_cost);
    //    LOG("ida_heuristic x-centers state %d or 0x%x, cost %d\n", x_centers_state, x_centers_state, x_centers_cost);
    //    LOG("ida_heuristic t-centers %d, x-centers %d, cost_to_goal %d\n", t_centers_cost, x_centers_cost, cost_to_goal);
    //}

    result.cost_to_goal = cost_to_goal;
    return result;
}


int
ida_search_complete_ULFRBD_centers_555 (char *cube)
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

        cube[32] == '1' &&
        cube[33] == '1' &&
        cube[34] == '1' &&
        cube[37] == '1' &&
        cube[38] == '1' &&
        cube[39] == '1' &&
        cube[42] == '1' &&
        cube[43] == '1' &&
        cube[44] == '1' &&

        cube[57] == '1' &&
        cube[58] == '1' &&
        cube[59] == '1' &&
        cube[62] == '1' &&
        cube[63] == '1' &&
        cube[64] == '1' &&
        cube[67] == '1' &&
        cube[68] == '1' &&
        cube[69] == '1') {

        return 1;

    } else {
        return 0;
    }
}
