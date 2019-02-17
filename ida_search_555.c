
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


unsigned int LFRB_t_centers_555[NUM_LFRB_T_CENTERS_555] = {
    33, 37, 39, 43,
    58, 62, 64, 68,
    83, 87, 89, 93,
    108, 112, 114, 118
};

unsigned int LFRB_x_centers_555[NUM_LFRB_T_CENTERS_555] = {
    32, 34, 42, 44,
    57, 59, 67, 69,
    82, 84, 92, 94,
    107, 109, 117, 119
};


// ===========================================================================
// step 10
// ===========================================================================
struct ida_heuristic_result
ida_heuristic_UD_centers_555(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **UD_centers_cost_555,
    char *pt_UD_t_centers_cost_only,
    char *pt_UD_x_centers_cost_only,
    cpu_mode_type cpu_mode)
{
    unsigned int cost_to_goal = 0;
    unsigned long long UD_t_centers_state = 0;
    unsigned long long UD_x_centers_state = 0;
    unsigned long UD_t_centers_cost = 0;
    unsigned long UD_x_centers_cost = 0;
    unsigned long long UD_centers_state = 0;
    struct ida_heuristic_result result;

    // t-centers
    for (int i = 0; i < NUM_T_CENTERS_555; i++) {
        if (cube[t_centers_555[i]] == '1') {
            UD_t_centers_state |= 0x1;
        }
        UD_t_centers_state <<= 1;
    }
    UD_t_centers_state >>= 1;
    UD_t_centers_cost = hex_to_int(pt_UD_t_centers_cost_only[UD_t_centers_state]);

    // x-centers
    for (int i = 0; i < NUM_X_CENTERS_555; i++) {
        if (cube[x_centers_555[i]] == '1') {
            UD_x_centers_state |= 0x1;
        }
        UD_x_centers_state <<= 1;
    }
    UD_x_centers_state >>= 1;
    UD_x_centers_cost = hex_to_int(pt_UD_x_centers_cost_only[UD_x_centers_state]);

    // centers
    for (int i = 0; i < NUM_CENTERS_555; i++) {
        if (cube[centers_555[i]] == '1') {
            UD_centers_state |= 0x1;
        }
        UD_centers_state <<= 1;
    }

    UD_centers_state >>= 1;
    cost_to_goal = max(UD_t_centers_cost, UD_x_centers_cost);
    sprintf(result.lt_state, "%014llx", UD_centers_state);

    /*
    LOG("UD_t_centers_state %llu, UD_t_centers_cost %d\n", UD_t_centers_state, UD_t_centers_cost);
    LOG("UD_x_centers_state %llu, UD_x_centers_cost %d\n", UD_x_centers_state, UD_x_centers_cost);
    LOG("UD_centers_state %llu, cost_to_goal %d\n", UD_centers_state, cost_to_goal);
     */

    if (cost_to_goal > 0) {
        // The step10 table we loaded is 5-deep
        int MAX_DEPTH = 5;

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(UD_centers_cost_555, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {

            if (cpu_mode == CPU_FAST) {
                // time ./ida_search --kociemba ......UUU..xUx..xxx............xUx..Uxx..UxU............UxU..xxx..xxU............xxx..xUx..xUx............xxx..Uxx..xUx............Uxx..Uxx..xUx...... --type 5x5x5-UD-centers-stage

                // x1.0 takes 20s (baseline, admissible)
                // x1.2 takes 1.5s
                cost_to_goal = max((int) cost_to_goal * 1.2, MAX_DEPTH+1);
            } else {
                cost_to_goal = max((int) cost_to_goal, MAX_DEPTH+1);
            }
        }
    }

    //if (debug) {
    //    LOG("ida_heuristic t-centers state %d or 0x%x, cost %d\n", UD_t_centers_state, UD_t_centers_state, UD_t_centers_cost);
    //    LOG("ida_heuristic x-centers state %d or 0x%x, cost %d\n", UD_x_centers_state, UD_x_centers_state, UD_x_centers_cost);
    //    LOG("ida_heuristic t-centers %d, x-centers %d, cost_to_goal %d\n", UD_t_centers_cost, UD_x_centers_cost, cost_to_goal);
    //}

    result.cost_to_goal = cost_to_goal;
    return result;
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



// ===========================================================================
// step 20
// ===========================================================================
struct ida_heuristic_result
ida_heuristic_LR_centers_555(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **LR_centers_cost_555,
    char *pt_LR_t_centers_cost_only,
    char *pt_LR_x_centers_cost_only)
{
    unsigned int cost_to_goal = 0;
    unsigned long long LR_t_centers_state = 0;
    unsigned long long LR_x_centers_state = 0;
    unsigned long LR_t_centers_cost = 0;
    unsigned long LR_x_centers_cost = 0;
    unsigned long long LR_centers_state = 0;
    struct ida_heuristic_result result;

    // t-centers
    for (int i = 0; i < NUM_LFRB_T_CENTERS_555; i++) {
        if (cube[LFRB_t_centers_555[i]] == '1') {
            LR_t_centers_state |= 0x1;
        }
        LR_t_centers_state <<= 1;
    }
    LR_t_centers_state >>= 1;
    LR_t_centers_cost = hex_to_int(pt_LR_t_centers_cost_only[LR_t_centers_state]);

    // x-centers
    for (int i = 0; i < NUM_LFRB_X_CENTERS_555; i++) {
        if (cube[LFRB_x_centers_555[i]] == '1') {
            LR_x_centers_state |= 0x1;
        }
        LR_x_centers_state <<= 1;
    }
    LR_x_centers_state >>= 1;
    LR_x_centers_cost = hex_to_int(pt_LR_x_centers_cost_only[LR_x_centers_state]);

    // centers
    for (int i = 0; i < NUM_LFRB_CENTERS_555; i++) {
        if (cube[LFRB_centers_555[i]] == '1') {
            LR_centers_state |= 0x1;
        }
        LR_centers_state <<= 1;
    }

    LR_centers_state >>= 1;
    sprintf(result.lt_state, "%09llx", LR_centers_state);
    cost_to_goal = max(LR_t_centers_cost, LR_x_centers_cost);

    if (cost_to_goal > 0) {

        // 7-deep takes 2100ms and uses 540M
        // 6-deep takes 230ms and uses 62M
        int MAX_DEPTH = 5;

        // time ./ida_search --kociemba ......xxx..xxx..xxx............LFF..LLL..FFL............FLL..FFL..LFL............xxx..xxx..xxx............FFF..LLL..LLL............LLF..FFF..FFF...... --type 5x5x5-LR-centers-stage

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(LR_centers_cost_555, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {
            cost_to_goal = max(cost_to_goal, MAX_DEPTH+1);
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

unsigned int
get_edges_paired_count(char *cube)
{
    unsigned int count = 0;

    // There are 12 edges to check

    // UB
    if (cube[2] != '-' && cube[2] == cube[3] && cube[104] == cube[103] && cube[4] == cube[3] && cube[102] == cube[103]) {
        count++;
    }

    // UL
    if (cube[6] != '-' && cube[6] == cube[11] && cube[27] == cube[28] && cube[16] == cube[11] && cube[29] == cube[28]) {
        count++;
    }

    // UR
    if (cube[10] != '-' && cube[10] == cube[15] && cube[79] == cube[78] && cube[20] == cube[15] && cube[77] == cube[78]) {
        count++;
    }

    // UF
    if (cube[22] != '-' && cube[22] == cube[23] && cube[52] == cube[53] && cube[24] == cube[23] && cube[54] == cube[53]) {
        count++;
    }

    // LB
    if (cube[31] != '-' && cube[31] == cube[36] && cube[110] == cube[115] && cube[41] == cube[36] && cube[120] == cube[115]) {
        count++;
    }

    // LF
    if (cube[35] != '-' && cube[35] == cube[40] && cube[56] == cube[61] && cube[45] == cube[40] && cube[66] == cube[61]) {
        count++;
    }

    // RF
    if (cube[60] != '-' && cube[60] == cube[65] && cube[81] == cube[86] && cube[70] == cube[65] && cube[91] == cube[86]) {
        count++;
    }

    // RB
    if (cube[85] != '-' && cube[85] == cube[90] && cube[106] == cube[111] && cube[95] == cube[90] && cube[116] == cube[111]) {
        count++;
    }

    // DF
    if (cube[72] != '-' && cube[72] == cube[73] && cube[127] == cube[128] && cube[74] == cube[73] && cube[129] == cube[128]) {
        count++;
    }

    // DL
    if (cube[131] != '-' && cube[131] == cube[136] && cube[49] == cube[48] && cube[141] == cube[136] && cube[47] == cube[48]) {
        count++;
    }

    // DR
    if (cube[135] != '-' && cube[135] == cube[140] && cube[97] == cube[98] && cube[145] == cube[140] && cube[99] == cube[98]) {
        count++;
    }

    // DB
    if (cube[147] != '-' && cube[147] == cube[148] && cube[124] == cube[123] && cube[149] == cube[148] && cube[122] == cube[123]) {
        count++;
    }

    return count;
}


unsigned int
get_wings_paired_count(char *cube)
{
    unsigned int count = 0;

    // There are 24 wings to check

    // UB
    if (cube[2] != '-' && cube[2] == cube[3] && cube[104] == cube[103]) {
        count++;
    }

    if (cube[4] != '-' && cube[4] == cube[3] && cube[102] == cube[103]) {
        count++;
    }

    // UL
    if (cube[6] != '-' && cube[6] == cube[11] && cube[27] == cube[28]) {
        count++;
    }

    if (cube[16] != '-' && cube[16] == cube[11] && cube[29] == cube[28]) {
        count++;
    }

    // UR
    if (cube[10] != '-' && cube[10] == cube[15] && cube[79] == cube[78]) {
        count++;
    }

    if (cube[20] != '-' && cube[20] == cube[15] && cube[77] == cube[78]) {
        count++;
    }

    // UF
    if (cube[22] != '-' && cube[22] == cube[23] && cube[52] == cube[53]) {
        count++;
    }

    if (cube[24] != '-' && cube[24] == cube[23] && cube[54] == cube[53]) {
        count++;
    }

    // LB
    if (cube[31] != '-' && cube[31] == cube[36] && cube[110] == cube[115]) {
        count++;
    }

    if (cube[41] != '-' && cube[41] == cube[36] && cube[120] == cube[115]) {
        count++;
    }

    // LF
    if (cube[35] != '-' && cube[35] == cube[40] && cube[56] == cube[61]) {
        count++;
    }

    if (cube[45] != '-' && cube[45] == cube[40] && cube[66] == cube[61]) {
        count++;
    }

    // RF
    if (cube[60] != '-' && cube[60] == cube[65] && cube[81] == cube[86]) {
        count++;
    }

    if (cube[70] != '-' && cube[70] == cube[65] && cube[91] == cube[86]) {
        count++;
    }

    // RB
    if (cube[85] != '-' && cube[85] == cube[90] && cube[106] == cube[111]) {
        count++;
    }

    if (cube[95] != '-' && cube[95] == cube[90] && cube[116] == cube[111]) {
        count++;
    }

    // DF
    if (cube[72] != '-' && cube[72] == cube[73] && cube[127] == cube[128]) {
        count++;
    }

    if (cube[74] != '-' && cube[74] == cube[73] && cube[129] == cube[128]) {
        count++;
    }

    // DL
    if (cube[131] != '-' && cube[131] == cube[136] && cube[49] == cube[48]) {
        count++;
    }

    if (cube[141] != '-' && cube[141] == cube[136] && cube[47] == cube[48]) {
        count++;
    }

    // DR
    if (cube[135] != '-' && cube[135] == cube[140] && cube[97] == cube[98]) {
        count++;
    }

    if (cube[145] != '-' && cube[145] == cube[140] && cube[99] == cube[98]) {
        count++;
    }

    // DB
    if (cube[147] != '-' && cube[147] == cube[148] && cube[124] == cube[123]) {
        count++;
    }

    if (cube[149] != '-' && cube[149] == cube[148] && cube[122] == cube[123]) {
        count++;
    }

    return count;
}


unsigned int
get_outer_wings_paired_count(char *cube)
{
    unsigned int count = 0;

    // There are 12 wings to check

    // UB
    if (cube[2] == cube[4] && cube[102] == cube[104])
        count++;

    // UL
    if (cube[6] == cube[16] && cube[27] == cube[29])
        count++;

    // UR
    if (cube[10] == cube[20] && cube[77] == cube[79])
        count++;

    // UF
    if (cube[22] == cube[24] && cube[52] == cube[54])
        count++;

    // LB
    if (cube[31] == cube[41] && cube[110] == cube[120])
        count++;

    // LF
    if (cube[35] == cube[45] && cube[56] == cube[66])
        count++;

    // RF
    if (cube[60] == cube[70] && cube[81] == cube[91])
        count++;

    // RB
    if (cube[85] == cube[95] && cube[106] == cube[116])
        count++;

    // DF
    if (cube[72] == cube[74] && cube[127] == cube[129])
        count++;

    // DL
    if (cube[131] == cube[141] && cube[47] == cube[49])
        count++;

    // DR
    if (cube[135] == cube[145] && cube[97] == cube[99])
        count++;

    // DB
    if (cube[147] == cube[149] && cube[122] == cube[124])
        count++;

    return count;
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

        /*
        //unsigned int wings_paired_count = 0;
        //wings_paired_count = get_wings_paired_count(cube);
        unsigned int outer_wings_paired_count = 0;
        outer_wings_paired_count = get_outer_wings_paired_count(cube);
        LOG("CENTERS SOLVED!! %d outer wings paired\n", outer_wings_paired_count);

        if (outer_wings_paired_count >= 4) {
            return 1;
        } else {
            return 0;
        }
         */

    } else {
        return 0;
    }
}
