
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include "xxhash.h"
#include "ida_search_core.h"
#include "ida_search_666.h"


unsigned int oblique_edges_666[NUM_OBLIQUE_EDGES_666] = {
    9, 10, 14, 17, 20, 23, 27, 28,
    45, 46, 50, 53, 56, 59, 63, 64,
    81, 82, 86, 89, 92, 95, 99, 100,
    117, 118, 122, 125, 128, 131, 135, 136,
    153, 154, 158, 161, 164, 167, 171, 172,
    189, 190, 194, 197, 200, 203, 207, 208
};


unsigned int left_oblique_edges_666[NUM_LEFT_OBLIQUE_EDGES_666] = {
    9, 20, 17, 28, // Upper
    45, 56, 53, 64, // Left
    81, 92, 89, 100, // Front
    117, 128, 125, 136, // Right
    153, 164, 161, 172, // Back
    189, 200, 197, 208, // Down
};


unsigned int right_oblique_edges_666[NUM_RIGHT_OBLIQUE_EDGES_666] = {
    10, 14, 23, 27, // Upper
    46, 50, 59, 63, // Left
    82, 86, 95, 99, // Front
    118, 122, 131, 135, // Right
    154, 158, 167, 171, // Back
    190, 194, 203, 207, // Down
};

unsigned int LFRB_inner_x_centers_666[NUM_LFRB_INNER_X_CENTERS_666] = {
    51, 52, 57, 58,
    87, 88, 93, 94,
    123, 124, 129, 130,
    159, 160, 165, 166
};

unsigned int LFRB_oblique_edges_666[NUM_LFRB_OBLIQUE_EDGES_666] = {
        45, 46,
    50,         53,
    56,         59,
        63, 64,

        81, 82,
    86,         89,
    92,         95,
        99, 100,

         117, 118,
    122,           125,
    128,           131,
         135, 136,

         153, 154,
    158,           161,
    164,           167,
         171, 172
};

unsigned int LR_inner_x_centers_and_oblique_edges_666[NUM_LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666] = {
        45, 46,
    50, 51, 52, 53,
    56, 57, 58, 59,
        63, 64,

         117, 118,
    122, 123, 124, 125,
    128, 129, 130, 131,
         135, 136,
};

unsigned int FB_inner_x_centers_and_oblique_edges_666[NUM_FB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666] = {
        81, 82,
    86, 87, 88, 89,
    92, 93, 94, 95,
        99, 100,

         153, 154,
    158, 159, 160, 161,
    164, 165, 166, 167,
         171, 172
};

unsigned int LFRB_inner_x_centers_and_oblique_edges_666[NUM_LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666] = {
        45, 46,
    50, 51, 52, 53,
    56, 57, 58, 59,
        63, 64,

        81, 82,
    86, 87, 88, 89,
    92, 93, 94, 95,
        99, 100,

         117, 118,
    122, 123, 124, 125,
    128, 129, 130, 131,
         135, 136,

         153, 154,
    158, 159, 160, 161,
    164, 165, 166, 167,
         171, 172
};

unsigned int
get_unpaired_obliques_count_666 (char *cube)
{
    int unpaired_obliques = 8;

    for (int i = 0; i < NUM_LEFT_OBLIQUE_EDGES_666; i++) {
        if (cube[left_oblique_edges_666[i]] == '1' && cube[right_oblique_edges_666[i]] == '1') {
            unpaired_obliques -= 1;
        }
    }

    return unpaired_obliques;
}


// ============================================================================
// step20
// ============================================================================
struct ida_heuristic_result
ida_heuristic_UD_oblique_edges_stage_666 (
    char *cube,
    unsigned int max_cost_to_goal)
{
    int unpaired_count = get_unpaired_obliques_count_666(cube);
    struct ida_heuristic_result result;
    unsigned long long state = 0;

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

    // The most oblique edges we can pair in single move is 4 so take
    // the number that are unpaired and divide by 4.
    //
    // .ULBU.F.Ux.LRx..xBRx..xFF.xx.L.BRLF..BDLF.F.UU.FBx..xRFx..UDB.Ux.B.BDFD..UUFR.R.UU.RFx..UDFx..xUR.xx.D.FUBL..DLRB.D.xx.DRx..xBRx..ULR.Ux.L.RLDF..UFBU.U.Ux.DFx..xUBU..xDU.xx.D.UDDL..LUBL.D.xx.BUx..URLU..UUR.Ux.R.LLUB.
    // divide by 4 (admissable) took 53s, 6 moves
    // divide by 2 took 8s, 7 moves
    // divide by 1.5 took 4.3s, 6 moves

    // inadmissable heuristic but fast
    result.cost_to_goal = (int) ceil((double) unpaired_count / 1.5);

    // inadmissable heuristic but fast...kudos to xyzzy for this formula
    // xyzzy 4/2 took 2s, 7 moves
    // xyzzy 6/3 took 0.8s, 7 moves
    /*
    if (unpaired_count > 4) {
        result.cost_to_goal = 2 + (unpaired_count >> 1);
    } else {
        result.cost_to_goal = unpaired_count;
    }
     */

    return result;
}

int
ida_search_complete_UD_oblique_edges_stage_666 (char *cube)
{
    if (get_unpaired_obliques_count_666(cube) == 0) {
        return 1;
    } else {
        return 0;
    }
}


// ============================================================================
// step30
// ============================================================================
struct ida_heuristic_result
ida_heuristic_LR_inner_x_centers_and_oblique_edges_stage_666 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **LR_inner_x_centers_and_oblique_edges_stage_666,
    char *LR_inner_x_centers_cost_666,
    char *LR_oblique_edges_cost_666)
{
    unsigned long long inner_x_centers_state = 0;
    unsigned long long inner_x_centers_cost = 0;
    unsigned long long oblique_edges_state = 0;
    unsigned long long oblique_edges_bucket = 0;
    unsigned long long oblique_edges_cost = 0;
    unsigned long long cost_to_goal = 0;
    char oblique_edges_str[24];
    int cube_index;
    struct ida_heuristic_result result;
    unsigned long long state = 0;

    // good test cube...this took ~3m prior to using the step31 oblique edges pruning table :(
    // Now it takes ~10s
    //
    // time ./ida_search --kociemba .RFLL.F....BB....BD....RF....F.BLUR..UDUR.L.LL.LFLxLxUULLxLBL.Lx.L.BDBD..LBRF.B.xx.UDxLLxRFLLLLLB.xL.D.BURB..RLUU.D....DR....LR....RF....R.RBBB..DDFR.D.Lx.UFxLLxRFLxxLDL.xL.L.UBFF..FDUU.F.Lx.RFxxxxLLxxxLLD.Lx.U.DDUU. --type 6x6x6-LR-inner-x-centers-oblique-edges-stage --orbit1-need-even-w

    // Get the state for the inner x-centers on LFRB
    for (int i = 0; i < NUM_LFRB_INNER_X_CENTERS_666; i++) {
        if (cube[LFRB_inner_x_centers_666[i]] == '1') {
            inner_x_centers_state |= 0x1;
        }
        inner_x_centers_state <<= 1;
    }
    inner_x_centers_state >>= 1;
    inner_x_centers_cost = hex_to_int(LR_inner_x_centers_cost_666[inner_x_centers_state]);

    // Get the state for the oblique edges on LFRB
    for (int i = 0; i < NUM_LFRB_OBLIQUE_EDGES_666; i++) {
        if (cube[LFRB_oblique_edges_666[i]] == '1') {
            oblique_edges_state |= 0x1;
        }
        oblique_edges_state <<= 1;
    }
    oblique_edges_state >>= 1;
    sprintf(oblique_edges_str, "%08llx", oblique_edges_state);
    oblique_edges_bucket = XXH32(oblique_edges_str, 8, 0) % 165636907;
    oblique_edges_cost = hex_to_int(LR_oblique_edges_cost_666[oblique_edges_bucket]);

    // get state of LFRB inner x-centers and oblique edges
    for (int i = 0; i < NUM_LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666; i++) {
        if (cube[LFRB_inner_x_centers_and_oblique_edges_666[i]] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }

    // 00019b267fff is 12 chars
    state >>= 1;
    sprintf(result.lt_state, "%012llx", state);
    cost_to_goal = max(oblique_edges_cost, inner_x_centers_cost);

    if (cost_to_goal > 0) {
        // The step30 table we loaded is 2-deep
        int MAX_DEPTH = 2;

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(LR_inner_x_centers_and_oblique_edges_stage_666, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {
            // Not admissible but much faster
            cost_to_goal = max((int) cost_to_goal * 1.2, MAX_DEPTH+1);
        }
    }

    result.cost_to_goal = cost_to_goal;
    return result;
}

int
ida_search_complete_LR_inner_x_centers_and_oblique_edges_stage (char *cube)
{
    if (( // First check if the inner x-centers are staged
        (cube[51] == '1' &&
         cube[52] == '1' &&
         cube[57] == '1' &&
         cube[58] == '1' &&
         cube[123] == '1' &&
         cube[124] == '1' &&
         cube[129] == '1' &&
         cube[130] == '1') ||

        (cube[51] == '0' &&
         cube[52] == '0' &&
         cube[57] == '0' &&
         cube[58] == '0' &&
         cube[123] == '0' &&
         cube[124] == '0' &&
         cube[129] == '0' &&
         cube[130] == '0')) &&

        // Then check if all oblique edges are paired
        get_unpaired_obliques_count_666(cube) == 0) {
        return 1;
    } else {
        return 0;
    }
}


// ============================================================================
// step60
// ============================================================================
struct ida_heuristic_result
ida_heuristic_LFRB_inner_x_centers_and_oblique_edges_solve_666(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **LFRB_inner_x_centers_and_oblique_edges_solve_666,
    char *LR_inner_x_centers_and_oblique_edges_solve_666,
    char *FB_inner_x_centers_and_oblique_edges_solve_666)
{
    unsigned long long LR_state = 0;
    unsigned long long LR_cost = 0;
    unsigned long long FB_state = 0;
    unsigned long long FB_cost = 0;
    unsigned long long cost_to_goal = 0;
    unsigned long long state = 0;
    int cube_index;
    struct ida_heuristic_result result;

    // get state of LR inner x-centers and oblique edges
    for (int i = 0; i < NUM_LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666; i++) {
        if (cube[LR_inner_x_centers_and_oblique_edges_666[i]] == '1') {
            LR_state |= 0x1;
        }
        LR_state <<= 1;
    }
    LR_state >>= 1;
    LR_cost = hex_to_int(LR_inner_x_centers_and_oblique_edges_solve_666[LR_state]);

    // get state of FB inner x-centers and oblique edges
    for (int i = 0; i < NUM_FB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666; i++) {
        if (cube[FB_inner_x_centers_and_oblique_edges_666[i]] == '1') {
            FB_state |= 0x1;
        }
        FB_state <<= 1;
    }
    FB_state >>= 1;
    FB_cost = hex_to_int(FB_inner_x_centers_and_oblique_edges_solve_666[FB_state]);

    // get state of LFRB inner x-centers and oblique edges
    for (int i = 0; i < NUM_LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666; i++) {
        if (cube[LFRB_inner_x_centers_and_oblique_edges_666[i]] == '1') {
            state |= 0x1;
        }
        state <<= 1;
    }
    state >>= 1;

    // 00019b267fff is 12 chars
    sprintf(result.lt_state, "%012llx", state);
    cost_to_goal = max(LR_cost, FB_cost);

    // dwalton
    // printf("LR_state %llu, LR_cost %llu, FB_state %llu, FB_cost %llu, state %s, cost_to_goal %llu\n", LR_state, LR_cost, FB_state, FB_cost, result.lt_state, cost_to_goal);
    // exit(0);

    if (cost_to_goal > 0) {
        // The step60 table we loaded is 3-deep
        int MAX_DEPTH = 3;

        struct key_value_pair *hash_entry = NULL;
        hash_entry = hash_find(LFRB_inner_x_centers_and_oblique_edges_solve_666, result.lt_state);

        if (hash_entry) {
            cost_to_goal = hash_entry->value;
        } else {
            // Not admissible but much faster
            cost_to_goal = max((int) cost_to_goal * 1.2, MAX_DEPTH+1);
            //cost_to_goal = max(cost_to_goal, MAX_DEPTH + 1);
        }
    }

    result.cost_to_goal = cost_to_goal;
    return result;
}


int
ida_search_complete_LFRB_inner_x_centers_and_oblique_edges_solve (char *cube)
{
    if (// First check if the inner x-centers are solved
        cube[51] == '1' &&
        cube[52] == '1' &&
        cube[57] == '1' &&
        cube[58] == '1' &&
        cube[87] == '1' &&
        cube[88] == '1' &&
        cube[93] == '1' &&
        cube[94] == '1' &&

        // Then check if all oblique edges are paired
        get_unpaired_obliques_count_666(cube) == 0) {
        return 1;
    } else {
        return 0;
    }
}
