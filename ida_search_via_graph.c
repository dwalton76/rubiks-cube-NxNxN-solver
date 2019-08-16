
#include <ctype.h>
#include <locale.h>
#include <math.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <sys/resource.h>
#include <sys/time.h>
#include "uthash.h"
#include "ida_search_core.h"
#include "rotate_xxx.h"


unsigned long ida_count = 0;
unsigned long ida_count_total = 0;
struct key_value_pair *ida_explored = NULL;
unsigned char legal_move_count = 0;
unsigned char threshold = 0;
char *pt0 = NULL;
char *pt1 = NULL;
char *pt2 = NULL;
char *pt3 = NULL;
char *pt4 = NULL;
struct key_value_pair *main_table = NULL;
unsigned char pt_count = 0;
unsigned char main_table_max_depth = 0;
unsigned char main_table_state_length = 0;
unsigned char COST_LENGTH = 1;
unsigned char STATE_LENGTH = 4;
unsigned char ROW_LENGTH = 0;
move_type legal_moves[MOVE_MAX];
move_type move_matrix[MOVE_MAX][MOVE_MAX];
move_type same_face_and_layer_matrix[MOVE_MAX][MOVE_MAX];


void
print_moves (move_type *moves, int max_i)
{
    int i = 0;
    printf("SOLUTION: ");

    while (moves[i] != MOVE_NONE) {
        printf("%s ", move2str[moves[i]]);
        i++;

        if (i >= max_i) {
            break;
        }
    }
    printf("\n");
}


unsigned char
steps_on_same_face_and_layer (move_type move, move_type prev_move)
{
    switch (move) {
    case U:
    case U_PRIME:
    case U2:
        switch (prev_move) {
        case U:
        case U_PRIME:
        case U2:
            return 1;
        default:
            return 0;
        }
        break;

    case L:
    case L_PRIME:
    case L2:
        switch (prev_move) {
        case L:
        case L_PRIME:
        case L2:
            return 1;
        default:
            return 0;
        }
        break;

    case F:
    case F_PRIME:
    case F2:
        switch (prev_move) {
        case F:
        case F_PRIME:
        case F2:
            return 1;
        default:
            return 0;
        }
        break;

    case R:
    case R_PRIME:
    case R2:
        switch (prev_move) {
        case R:
        case R_PRIME:
        case R2:
            return 1;
        default:
            return 0;
        }
        break;

    case B:
    case B_PRIME:
    case B2:
        switch (prev_move) {
        case B:
        case B_PRIME:
        case B2:
            return 1;
        default:
            return 0;
        }
        break;

    case D:
    case D_PRIME:
    case D2:
        switch (prev_move) {
        case D:
        case D_PRIME:
        case D2:
            return 1;
        default:
            return 0;
        }
        break;

    // 2-layer turns
    case Uw:
    case Uw_PRIME:
    case Uw2:
        switch (prev_move) {
        case Uw:
        case Uw_PRIME:
        case Uw2:
            return 1;
        default:
            return 0;
        }
        break;

    case Lw:
    case Lw_PRIME:
    case Lw2:
        switch (prev_move) {
        case Lw:
        case Lw_PRIME:
        case Lw2:
            return 1;
        default:
            return 0;
        }
        break;

    case Fw:
    case Fw_PRIME:
    case Fw2:
        switch (prev_move) {
        case Fw:
        case Fw_PRIME:
        case Fw2:
            return 1;
        default:
            return 0;
        }
        break;

    case Rw:
    case Rw_PRIME:
    case Rw2:
        switch (prev_move) {
        case Rw:
        case Rw_PRIME:
        case Rw2:
            return 1;
        default:
            return 0;
        }
        break;

    case Bw:
    case Bw_PRIME:
    case Bw2:
        switch (prev_move) {
        case Bw:
        case Bw_PRIME:
        case Bw2:
            return 1;
        default:
            return 0;
        }
        break;

    case Dw:
    case Dw_PRIME:
    case Dw2:
        switch (prev_move) {
        case Dw:
        case Dw_PRIME:
        case Dw2:
            return 1;
        default:
            return 0;
        }
        break;

    case threeUw:
    case threeUw_PRIME:
    case threeUw2:
        switch (prev_move) {
        case threeUw:
        case threeUw_PRIME:
        case threeUw2:
            return 1;
        default:
            return 0;
        }
        break;

    case threeLw:
    case threeLw_PRIME:
    case threeLw2:
        switch (prev_move) {
        case threeLw:
        case threeLw_PRIME:
        case threeLw2:
            return 1;
        default:
            return 0;
        }
        break;

    case threeFw:
    case threeFw_PRIME:
    case threeFw2:
        switch (prev_move) {
        case threeFw:
        case threeFw_PRIME:
        case threeFw2:
            return 1;
        default:
            return 0;
        }
        break;

    case threeRw:
    case threeRw_PRIME:
    case threeRw2:
        switch (prev_move) {
        case threeRw:
        case threeRw_PRIME:
        case threeRw2:
            return 1;
        default:
            return 0;
        }
        break;

    case threeBw:
    case threeBw_PRIME:
    case threeBw2:
        switch (prev_move) {
        case threeBw:
        case threeBw_PRIME:
        case threeBw2:
            return 1;
        default:
            return 0;
        }
        break;

    case threeDw:
    case threeDw_PRIME:
    case threeDw2:
        switch (prev_move) {
        case threeDw:
        case threeDw_PRIME:
        case threeDw2:
            return 1;
        default:
            return 0;
        }
        break;

    case X:
    case X_PRIME:
    case Y:
    case Y_PRIME:
    case Z:
    case Z_PRIME:
        return 0;

    default:
        printf("ERROR: steps_on_same_face_and_layer add support for %d (%s)\n", move, move2str[move]);
        exit(1);
    }

    return 0;
}

struct ida_search_result {
    unsigned int f_cost;
    unsigned int found_solution;
};


inline unsigned int
read_state (char *pt, unsigned int location)
{
    unsigned int num = 0;
    // uint32_t b0, b1, b2, b3;

    memcpy(&num, &pt[location], 4);
    /*
    b0 = (num & 0x000000ff) << 24u;
    b1 = (num & 0x0000ff00) << 8u;
    b2 = (num & 0x00ff0000) >> 8u;
    b3 = (num & 0xff000000) >> 24u;

    return b0 | b1 | b2 | b3;
     */
    return ((num & 0x000000ff) << 24u) | ((num & 0x0000ff00) << 8u) | ((num & 0x00ff0000) >> 8u) | ((num & 0xff000000) >> 24u);
}


struct ida_search_result
ida_search (unsigned char cost_to_here,
            move_type *moves_to_here,
            move_type prev_move,
            unsigned int prev_pt0_state,
            unsigned int prev_pt1_state,
            unsigned int prev_pt2_state,
            unsigned int prev_pt3_state,
            unsigned int prev_pt4_state)
{
    unsigned char cost_to_goal = 0;
    unsigned char f_cost = 0;
    move_type move, skip_other_steps_this_face;
    // struct ida_heuristic_result heuristic_result;
    // struct key_value_pair *prev_heuristic_result = NULL;
    skip_other_steps_this_face = MOVE_NONE;
    struct ida_search_result search_result, tmp_search_result;
    unsigned int pt0_state = 0;
    unsigned int pt1_state = 0;
    unsigned int pt2_state = 0;
    unsigned int pt3_state = 0;
    unsigned int pt4_state = 0;
    unsigned char pt0_cost = 0;
    unsigned char pt1_cost = 0;
    unsigned char pt2_cost = 0;
    unsigned char pt3_cost = 0;
    unsigned char pt4_cost = 0;

    ida_count++;

    switch (pt_count) {
    case 4:
        pt4_cost = pt4[prev_pt4_state * ROW_LENGTH];
        pt3_cost = pt3[prev_pt3_state * ROW_LENGTH];
        pt2_cost = pt2[prev_pt2_state * ROW_LENGTH];
        pt1_cost = pt1[prev_pt1_state * ROW_LENGTH];
        pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        cost_to_goal = pt4_cost;
        cost_to_goal = (pt3_cost > cost_to_goal) ? pt3_cost : cost_to_goal;
        cost_to_goal = (pt2_cost > cost_to_goal) ? pt2_cost : cost_to_goal;
        cost_to_goal = (pt1_cost > cost_to_goal) ? pt1_cost : cost_to_goal;
        cost_to_goal = (pt0_cost > cost_to_goal) ? pt0_cost : cost_to_goal;

        if (main_table) {
            struct key_value_pair *main_table_node = NULL;
            unsigned char STATE_SIZE = 48;
            unsigned char lt_state[STATE_SIZE];
            memset(lt_state, '\0', sizeof(char) * STATE_SIZE);
            snprintf(lt_state, STATE_SIZE, "%07u-%07u-%07u-%07u-%07u",
                prev_pt0_state,
                prev_pt1_state,
                prev_pt2_state,
                prev_pt3_state,
                prev_pt4_state);

            main_table_node = hash_find(&main_table, lt_state);

            if (main_table_node) {
                cost_to_goal = main_table_node->value;
                // LOG("lt_state %s has cost %d, cost_to_here %d\n", lt_state, main_table_node->value, cost_to_here);
            } else {
                cost_to_goal = (main_table_max_depth + 1 > cost_to_goal) ? main_table_max_depth + 1 : cost_to_goal;
            }
        }
        break;

    case 3:
        pt3_cost = pt3[prev_pt3_state * ROW_LENGTH];
        pt2_cost = pt2[prev_pt2_state * ROW_LENGTH];
        pt1_cost = pt1[prev_pt1_state * ROW_LENGTH];
        pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        cost_to_goal = pt3_cost;
        cost_to_goal = (pt2_cost > cost_to_goal) ? pt2_cost : cost_to_goal;
        cost_to_goal = (pt1_cost > cost_to_goal) ? pt1_cost : cost_to_goal;
        cost_to_goal = (pt0_cost > cost_to_goal) ? pt0_cost : cost_to_goal;

        if (main_table) {
            struct key_value_pair *main_table_node = NULL;
            unsigned char STATE_SIZE = 48;
            unsigned char lt_state[STATE_SIZE];
            memset(lt_state, '\0', sizeof(char) * STATE_SIZE);
            snprintf(lt_state, STATE_SIZE, "%07u-%07u-%07u-%07u",
                prev_pt0_state,
                prev_pt1_state,
                prev_pt2_state,
                prev_pt3_state);

            main_table_node = hash_find(&main_table, lt_state);

            if (main_table_node) {
                cost_to_goal = main_table_node->value;
                // LOG("lt_state %s has cost %d, cost_to_here %d\n", lt_state, main_table_node->value, cost_to_here);
            } else {
                cost_to_goal = (main_table_max_depth + 1 > cost_to_goal) ? main_table_max_depth + 1 : cost_to_goal;
            }
        }
        break;

    case 2:
        pt2_cost = pt2[prev_pt2_state * ROW_LENGTH];
        pt1_cost = pt1[prev_pt1_state * ROW_LENGTH];
        pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        cost_to_goal = pt2_cost;
        cost_to_goal = (pt1_cost > cost_to_goal) ? pt1_cost : cost_to_goal;
        cost_to_goal = (pt0_cost > cost_to_goal) ? pt0_cost : cost_to_goal;

        if (main_table) {
            struct key_value_pair *main_table_node = NULL;
            unsigned char STATE_SIZE = 48;
            unsigned char lt_state[STATE_SIZE];
            memset(lt_state, '\0', sizeof(char) * STATE_SIZE);
            snprintf(lt_state, STATE_SIZE, "%07u-%07u-%07u",
                prev_pt0_state,
                prev_pt1_state,
                prev_pt2_state);

            main_table_node = hash_find(&main_table, lt_state);

            if (main_table_node) {
                cost_to_goal = main_table_node->value;
                // LOG("lt_state %s has cost %d, cost_to_here %d\n", lt_state, main_table_node->value, cost_to_here);
            } else {
                cost_to_goal = (main_table_max_depth + 1 > cost_to_goal) ? main_table_max_depth + 1 : cost_to_goal;
            }
        }
        break;

    case 1:
        pt1_cost = pt1[prev_pt1_state * ROW_LENGTH];
        pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        cost_to_goal = (pt1_cost > pt0_cost) ? pt1_cost : pt0_cost;

        if (main_table) {
            struct key_value_pair *main_table_node = NULL;
            unsigned char STATE_SIZE = 48;
            unsigned char lt_state[STATE_SIZE];
            memset(lt_state, '\0', sizeof(char) * STATE_SIZE);
            snprintf(lt_state, STATE_SIZE, "%07u-%07u",
                prev_pt0_state,
                prev_pt1_state);

            main_table_node = hash_find(&main_table, lt_state);

            if (main_table_node) {
                cost_to_goal = main_table_node->value;
                // LOG("lt_state %s has cost %d, cost_to_here %d\n", lt_state, main_table_node->value, cost_to_here);
            } else {
                cost_to_goal = (main_table_max_depth + 1 > cost_to_goal) ? main_table_max_depth + 1 : cost_to_goal;
            }
        }
        break;

    default:
        pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        cost_to_goal = pt0_cost;

        if (main_table) {
            struct key_value_pair *main_table_node = NULL;
            unsigned char STATE_SIZE = 48;
            unsigned char lt_state[STATE_SIZE];
            memset(lt_state, '\0', sizeof(char) * STATE_SIZE);
            snprintf(lt_state, STATE_SIZE, "%07u", prev_pt0_state);

            main_table_node = hash_find(&main_table, lt_state);

            if (main_table_node) {
                cost_to_goal = main_table_node->value;
                // LOG("lt_state %s has cost %d, cost_to_here %d\n", lt_state, main_table_node->value, cost_to_here);
            } else {
                cost_to_goal = (main_table_max_depth + 1 > cost_to_goal) ? main_table_max_depth + 1 : cost_to_goal;
            }
        }
        break;
    }

    f_cost = cost_to_here + cost_to_goal;
    search_result.f_cost = f_cost;
    search_result.found_solution = 0;

    if (cost_to_goal == 0) {
        // We are finished!!
        LOG("IDA count %'d, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
            ida_count, f_cost, threshold, cost_to_here, cost_to_goal);
        print_moves(moves_to_here, cost_to_here);
        search_result.found_solution = 1;
        return search_result;
    }

    // Abort Searching
    if (f_cost >= threshold) {
        return search_result;
    }

    // The act of computing lt_state and looking to see if lt_state is in ida_explored
    // cuts the nodes-per-sec rate in half but it can also drastically reduce the number
    // of nodes we need to visit and result in a net win. This can chew through a LOT of
    // memory on a big search though.
    /*
    memset(lt_state, '\0', sizeof(char) * STATE_SIZE);
    snprintf(lt_state, STATE_SIZE, "%u-%u-%u-%u-%u",
        prev_pt4_state,
        prev_pt3_state,
        prev_pt2_state,
        prev_pt1_state,
        prev_pt0_state);

    prev_heuristic_result = hash_find(&ida_explored, lt_state);

    if (prev_heuristic_result) {
        if (prev_heuristic_result->value <= cost_to_here) {
            //LOG("STOP strlen lt_state %d, prev_pt0_state %lu, prev_pt1_state %lu, value %lu, cost_to_here %lu\n",
            //    strlen(lt_state), prev_pt0_state, prev_pt1_state, prev_heuristic_result->value, cost_to_here);
            return search_result;
        } else {
            //LOG("CONT strlen lt_state %d, prev_pt0_state %lu, prev_pt1_state %lu, value %lu, cost_to_here %lu\n",
            //    strlen(lt_state), prev_pt0_state, prev_pt1_state, prev_heuristic_result->value, cost_to_here);
            hash_delete(&ida_explored, prev_heuristic_result);
        }
    }

    hash_add(&ida_explored, lt_state, cost_to_here);
    */

    int offset = 0;

    for (unsigned char i = 0; i < legal_move_count; i++) {
        move = move_matrix[prev_move][i];

        // This is the scenario where the move is on the same face and layer as prev_mode
        if (move == MOVE_NONE) {
            continue;
        }


        // https://github.com/cs0x7f/TPR-4x4x4-Solver/issues/7
        /*
         * Well, it's a simple technique to reduce the number of nodes accessed.
         * For example, we start at a position S whose pruning value is no more
         * than maxl, otherwise, S will be pruned in previous searching.  After
         * a move X, we obtain position S', whose pruning value is larger than
         * maxl, which means that X makes S farther from the solved state.  In
         * this case, we won't try X2 and X'.
         * --cs0x7f
         */
        if (skip_other_steps_this_face != MOVE_NONE) {
            if (same_face_and_layer_matrix[skip_other_steps_this_face][move]) {
                continue;
            } else {
                skip_other_steps_this_face = MOVE_NONE;
            }
        }

        offset = 1 + (4 * i);

        switch (pt_count) {
        case 4:
            pt4_state = read_state(pt4, (prev_pt4_state * ROW_LENGTH) + offset);
            pt3_state = read_state(pt3, (prev_pt3_state * ROW_LENGTH) + offset);
            pt2_state = read_state(pt2, (prev_pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (prev_pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (prev_pt0_state * ROW_LENGTH) + offset);
            break;

        case 3:
            pt3_state = read_state(pt3, (prev_pt3_state * ROW_LENGTH) + offset);
            pt2_state = read_state(pt2, (prev_pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (prev_pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (prev_pt0_state * ROW_LENGTH) + offset);
            break;

        case 2:
            pt2_state = read_state(pt2, (prev_pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (prev_pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (prev_pt0_state * ROW_LENGTH) + offset);
            break;

        case 1:
            pt1_state = read_state(pt1, (prev_pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (prev_pt0_state * ROW_LENGTH) + offset);
            break;

        default:
            pt0_state = read_state(pt0, (prev_pt0_state * ROW_LENGTH) + offset);
            break;
        }

        moves_to_here[cost_to_here] = move;

        tmp_search_result = ida_search(
            cost_to_here + 1,
            moves_to_here,
            move,
            pt0_state,
            pt1_state,
            pt2_state,
            pt3_state,
            pt4_state);

        if (tmp_search_result.found_solution) {
            return tmp_search_result;
        } else {
            moves_to_here[cost_to_here] = MOVE_NONE;

            if (tmp_search_result.f_cost > threshold) {
                skip_other_steps_this_face = move;
            } else {
                skip_other_steps_this_face = MOVE_NONE;
            }
        }
    }

    return search_result;
}


int
ida_solve (
    unsigned int pt0_state,
    unsigned int pt1_state,
    unsigned int pt2_state,
    unsigned int pt3_state,
    unsigned int pt4_state)
{
    unsigned char MAX_SEARCH_DEPTH = 30;
    unsigned char min_ida_threshold = 0;
    move_type moves_to_here[MAX_SEARCH_DEPTH];
    struct ida_search_result search_result;
    struct timeval stop, start, start_this_threshold;

    unsigned char pt0_cost = 0;
    unsigned char pt1_cost = 0;
    unsigned char pt2_cost = 0;
    unsigned char pt3_cost = 0;
    unsigned char pt4_cost = 0;

    memset(moves_to_here, MOVE_NONE, MAX_SEARCH_DEPTH);

    // For printing commas via %'d
    setlocale(LC_NUMERIC, "");

    if (pt4 != NULL) {
        pt4_cost = pt4[pt4_state * ROW_LENGTH];
        pt3_cost = pt3[pt3_state * ROW_LENGTH];
        pt2_cost = pt2[pt2_state * ROW_LENGTH];
        pt1_cost = pt1[pt1_state * ROW_LENGTH];
        pt0_cost = pt0[pt0_state * ROW_LENGTH];
        min_ida_threshold = pt4_cost;
        min_ida_threshold = (pt3_cost > min_ida_threshold) ? pt3_cost : min_ida_threshold;
        min_ida_threshold = (pt2_cost > min_ida_threshold) ? pt2_cost : min_ida_threshold;
        min_ida_threshold = (pt1_cost > min_ida_threshold) ? pt1_cost : min_ida_threshold;
        min_ida_threshold = (pt0_cost > min_ida_threshold) ? pt0_cost : min_ida_threshold;

    } else if (pt3 != NULL) {
        pt3_cost = pt3[pt3_state * ROW_LENGTH];
        pt2_cost = pt2[pt2_state * ROW_LENGTH];
        pt1_cost = pt1[pt1_state * ROW_LENGTH];
        pt0_cost = pt0[pt0_state * ROW_LENGTH];
        min_ida_threshold = pt3_cost;
        min_ida_threshold = (pt2_cost > min_ida_threshold) ? pt2_cost : min_ida_threshold;
        min_ida_threshold = (pt1_cost > min_ida_threshold) ? pt1_cost : min_ida_threshold;
        min_ida_threshold = (pt0_cost > min_ida_threshold) ? pt0_cost : min_ida_threshold;

    } else if (pt2 != NULL) {
        pt2_cost = pt2[pt2_state * ROW_LENGTH];
        pt1_cost = pt1[pt1_state * ROW_LENGTH];
        pt0_cost = pt0[pt0_state * ROW_LENGTH];
        min_ida_threshold = pt2_cost;
        min_ida_threshold = (pt1_cost > min_ida_threshold) ? pt1_cost : min_ida_threshold;
        min_ida_threshold = (pt0_cost > min_ida_threshold) ? pt0_cost : min_ida_threshold;

    } else if (pt1 != NULL) {
        pt1_cost = pt1[pt1_state * ROW_LENGTH];
        pt0_cost = pt0[pt0_state * ROW_LENGTH];
        min_ida_threshold = (pt1_cost > pt0_cost) ? pt1_cost : pt0_cost;

    } else {
        pt0_cost = pt0[pt0_state * ROW_LENGTH];
        min_ida_threshold = pt0_cost;
    }

    LOG("min_ida_threshold %d\n", min_ida_threshold);
    gettimeofday(&start, NULL);

    for (threshold = min_ida_threshold; threshold <= MAX_SEARCH_DEPTH; threshold++) {
        ida_count = 0;
        gettimeofday(&start_this_threshold, NULL);
        memset(moves_to_here, MOVE_NONE, sizeof(move_type) * MAX_SEARCH_DEPTH);
        hash_delete_all(&ida_explored);

        search_result = ida_search(
            0,
            moves_to_here,
            MOVE_NONE,
            pt0_state,
            pt1_state,
            pt2_state,
            pt3_state,
            pt4_state);

        gettimeofday(&stop, NULL);
        ida_count_total += ida_count;
        float ms = ((stop.tv_sec - start_this_threshold.tv_sec) * 1000) + ((stop.tv_usec - start_this_threshold.tv_usec) / 1000);
        float nodes_per_ms = ida_count / ms;
        unsigned int nodes_per_sec = nodes_per_ms * 1000;

        LOG("IDA threshold %d, explored %'d nodes, took %.3fs, %'d nodes-per-sec\n", threshold, ida_count,  ms / 1000, nodes_per_sec);

        if (search_result.found_solution) {
            float ms = ((stop.tv_sec - start.tv_sec) * 1000) + ((stop.tv_usec - start.tv_usec) / 1000);
            float nodes_per_ms = ida_count_total / ms;
            unsigned int nodes_per_sec = nodes_per_ms * 1000;
            LOG("IDA found solution, explored %'d total nodes, took %.3fs, %'d nodes-per-sec\n",
                ida_count_total, ms / 1000, nodes_per_sec);
            return 1;
        }
    }

    LOG("IDA failed with range %d->%d\n", min_ida_threshold, MAX_SEARCH_DEPTH);
    return 0;
}


char *
read_file (char *filename)
{
    FILE *fh = fopen(filename, "rb");
    unsigned long bufsize = 0;
    char *buffer = NULL;

    // Go to the end of the file
    if (fseek(fh, 0L, SEEK_END) == 0) {

        // Get the size of the file
        bufsize = ftell(fh);
        // LOG("%s bufsize is %lu\n", filename, bufsize);

        if (bufsize == -1) {
            printf("ERROR: no bufsize for %s\n", filename);
            exit(1);
        }

        // Allocate our buffer to that size
        buffer = malloc(sizeof(char) * (bufsize + 1));

        // Go back to the start of the file
        if (fseek(fh, 0L, SEEK_SET) != 0) {
            printf("ERROR: could not seek to start of %s\n", filename);
            exit(1);
        }

        // Read the entire file into memory
        size_t new_len = fread(buffer, sizeof(char), bufsize, fh);

        if (ferror(fh) != 0) {
            printf("ERROR: could not read %s\n", filename);
            exit(1);
        } else {
            buffer[new_len++] = '\0'; // Just to be safe.
        }
    }

    fclose(fh);
    return buffer;
}


void
ida_prune_table_preload (struct key_value_pair **hashtable, char *filename)
{
    FILE *fh_read = NULL;
    int BUFFER_SIZE = 128;
    char buffer[BUFFER_SIZE];
    char token_buffer[BUFFER_SIZE];
    char moves[BUFFER_SIZE];
    char *token_ptr = NULL;
    char state[BUFFER_SIZE];
    int cost = 0;
    struct key_value_pair * pt_entry = NULL;

    fh_read = fopen(filename, "r");
    if (fh_read == NULL) {
        printf("ERROR: ida_prune_table_preload could not open %s\n", filename);
        exit(1);
    }

    if (!main_table_state_length) {
        printf("ERROR: --main-table-state-length must be defined before --main-table");
        exit(1);
    }

    LOG("ida_prune_table_preload %s: start\n", filename);
    unsigned char cost_index = main_table_state_length + 1;

    // If there are two PTs then main_table_state_length should be 15, 7 for
    // each state and 1 for the - between them.
    while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
        buffer[main_table_state_length] = '\0';
        cost = atoi(&buffer[cost_index]);
        hash_add(hashtable, buffer, cost);
    }

    fclose(fh_read);
    LOG("ida_prune_table_preload %s: end\n", filename);
}


int
main (int argc, char *argv[])
{
    unsigned long prune_table_0_state = 0;
    unsigned long prune_table_1_state = 0;
    unsigned long prune_table_2_state = 0;
    unsigned long prune_table_3_state = 0;
    unsigned long prune_table_4_state = 0;
    memset(legal_moves, MOVE_NONE, MOVE_MAX);
    memset(move_matrix, MOVE_NONE, MOVE_MAX * MOVE_MAX);
    memset(same_face_and_layer_matrix, 0, MOVE_MAX * MOVE_MAX);

    for (unsigned char i = 1; i < argc; i++) {
        if (strmatch(argv[i], "--prune-table-0-filename")) {
            i++;
            pt0 = read_file(argv[i]);
            pt_count = 0;

        } else if (strmatch(argv[i], "--prune-table-0-state")) {
            i++;
            prune_table_0_state = atoi(argv[i]);
            pt_count = 0;

        } else if (strmatch(argv[i], "--prune-table-1-filename")) {
            i++;
            pt1 = read_file(argv[i]);
            pt_count = 1;

        } else if (strmatch(argv[i], "--prune-table-1-state")) {
            i++;
            prune_table_1_state = atoi(argv[i]);
            pt_count = 1;

        } else if (strmatch(argv[i], "--prune-table-2-filename")) {
            i++;
            pt2 = read_file(argv[i]);
            pt_count = 2;

        } else if (strmatch(argv[i], "--prune-table-2-state")) {
            i++;
            prune_table_2_state = atoi(argv[i]);
            pt_count = 2;

        } else if (strmatch(argv[i], "--prune-table-3-filename")) {
            i++;
            pt3 = read_file(argv[i]);
            pt_count = 3;

        } else if (strmatch(argv[i], "--prune-table-3-state")) {
            i++;
            prune_table_3_state = atoi(argv[i]);
            pt_count = 3;

        } else if (strmatch(argv[i], "--prune-table-4-filename")) {
            i++;
            pt4 = read_file(argv[i]);
            pt_count = 4;

        } else if (strmatch(argv[i], "--prune-table-4-state")) {
            i++;
            prune_table_4_state = atoi(argv[i]);
            pt_count = 4;

        } else if (strmatch(argv[i], "--main-table")) {
            i++;
            ida_prune_table_preload(&main_table, argv[i]);

        } else if (strmatch(argv[i], "--main-table-max-depth")) {
            i++;
            main_table_max_depth = atoi(argv[i]);

        } else if (strmatch(argv[i], "--main-table-state-length")) {
            i++;
            main_table_state_length = atoi(argv[i]);

        } else if (strmatch(argv[i], "--legal-moves")) {
            i++;
            char *p = strtok(argv[i], ",");

            while (p != NULL) {

                if (strmatch(p, "U")) {
                    legal_moves[legal_move_count] = U;
                } else if (strmatch(p, "U'")) {
                    legal_moves[legal_move_count] = U_PRIME;
                } else if (strmatch(p, "U2")) {
                    legal_moves[legal_move_count] = U2;
                } else if (strmatch(p, "Uw")) {
                    legal_moves[legal_move_count] = Uw;
                } else if (strmatch(p, "Uw'")) {
                    legal_moves[legal_move_count] = Uw_PRIME;
                } else if (strmatch(p, "Uw2")) {
                    legal_moves[legal_move_count] = Uw2;
                } else if (strmatch(p, "3Uw")) {
                    legal_moves[legal_move_count] = threeUw;
                } else if (strmatch(p, "3Uw'")) {
                    legal_moves[legal_move_count] = threeUw_PRIME;
                } else if (strmatch(p, "3Uw2")) {
                    legal_moves[legal_move_count] = threeUw2;

                } else if (strmatch(p, "L")) {
                    legal_moves[legal_move_count] = L;
                } else if (strmatch(p, "L'")) {
                    legal_moves[legal_move_count] = L_PRIME;
                } else if (strmatch(p, "L2")) {
                    legal_moves[legal_move_count] = L2;
                } else if (strmatch(p, "Lw")) {
                    legal_moves[legal_move_count] = Lw;
                } else if (strmatch(p, "Lw'")) {
                    legal_moves[legal_move_count] = Lw_PRIME;
                } else if (strmatch(p, "Lw2")) {
                    legal_moves[legal_move_count] = Lw2;
                } else if (strmatch(p, "3Lw")) {
                    legal_moves[legal_move_count] = threeLw;
                } else if (strmatch(p, "3Lw'")) {
                    legal_moves[legal_move_count] = threeLw_PRIME;
                } else if (strmatch(p, "3Lw2")) {
                    legal_moves[legal_move_count] = threeLw2;

                } else if (strmatch(p, "F")) {
                    legal_moves[legal_move_count] = F;
                } else if (strmatch(p, "F'")) {
                    legal_moves[legal_move_count] = F_PRIME;
                } else if (strmatch(p, "F2")) {
                    legal_moves[legal_move_count] = F2;
                } else if (strmatch(p, "Fw")) {
                    legal_moves[legal_move_count] = Fw;
                } else if (strmatch(p, "Fw'")) {
                    legal_moves[legal_move_count] = Fw_PRIME;
                } else if (strmatch(p, "Fw2")) {
                    legal_moves[legal_move_count] = Fw2;
                } else if (strmatch(p, "3Fw")) {
                    legal_moves[legal_move_count] = threeFw;
                } else if (strmatch(p, "3Fw'")) {
                    legal_moves[legal_move_count] = threeFw_PRIME;
                } else if (strmatch(p, "3Fw2")) {
                    legal_moves[legal_move_count] = threeFw2;

                } else if (strmatch(p, "R")) {
                    legal_moves[legal_move_count] = R;
                } else if (strmatch(p, "R'")) {
                    legal_moves[legal_move_count] = R_PRIME;
                } else if (strmatch(p, "R2")) {
                    legal_moves[legal_move_count] = R2;
                } else if (strmatch(p, "Rw")) {
                    legal_moves[legal_move_count] = Rw;
                } else if (strmatch(p, "Rw'")) {
                    legal_moves[legal_move_count] = Rw_PRIME;
                } else if (strmatch(p, "Rw2")) {
                    legal_moves[legal_move_count] = Rw2;
                } else if (strmatch(p, "3Rw")) {
                    legal_moves[legal_move_count] = threeRw;
                } else if (strmatch(p, "3Rw'")) {
                    legal_moves[legal_move_count] = threeRw_PRIME;
                } else if (strmatch(p, "3Rw2")) {
                    legal_moves[legal_move_count] = threeRw2;

                } else if (strmatch(p, "B")) {
                    legal_moves[legal_move_count] = B;
                } else if (strmatch(p, "B'")) {
                    legal_moves[legal_move_count] = B_PRIME;
                } else if (strmatch(p, "B2")) {
                    legal_moves[legal_move_count] = B2;
                } else if (strmatch(p, "Bw")) {
                    legal_moves[legal_move_count] = Bw;
                } else if (strmatch(p, "Bw'")) {
                    legal_moves[legal_move_count] = Bw_PRIME;
                } else if (strmatch(p, "Bw2")) {
                    legal_moves[legal_move_count] = Bw2;
                } else if (strmatch(p, "3Bw")) {
                    legal_moves[legal_move_count] = threeBw;
                } else if (strmatch(p, "3Bw'")) {
                    legal_moves[legal_move_count] = threeBw_PRIME;
                } else if (strmatch(p, "3Bw2")) {
                    legal_moves[legal_move_count] = threeBw2;

                } else if (strmatch(p, "D")) {
                    legal_moves[legal_move_count] = D;
                } else if (strmatch(p, "D'")) {
                    legal_moves[legal_move_count] = D_PRIME;
                } else if (strmatch(p, "D2")) {
                    legal_moves[legal_move_count] = D2;
                } else if (strmatch(p, "Dw")) {
                    legal_moves[legal_move_count] = Dw;
                } else if (strmatch(p, "Dw'")) {
                    legal_moves[legal_move_count] = Dw_PRIME;
                } else if (strmatch(p, "Dw2")) {
                    legal_moves[legal_move_count] = Dw2;
                } else if (strmatch(p, "3Dw")) {
                    legal_moves[legal_move_count] = threeDw;
                } else if (strmatch(p, "3Dw'")) {
                    legal_moves[legal_move_count] = threeDw_PRIME;
                } else if (strmatch(p, "3Dw2")) {
                    legal_moves[legal_move_count] = threeDw2;
                }

                p = strtok (NULL, ",");
                legal_move_count++;
            }

        } else if (strmatch(argv[i], "-h") || strmatch(argv[i], "--help")) {
            printf("\nida_search --kociemba KOCIEMBA_STRING --type 5x5x5-UD-centers-stage\n\n");
            exit(0);

        } else {
            printf("ERROR: %s is an invalid arg\n\n", argv[i]);
            exit(1);
        }
    }

    if ((main_table || main_table_max_depth || main_table_state_length) &&
        (!main_table || !main_table_max_depth || !main_table_state_length)) {

        printf("ERROR: must specify --main-table-state-length, --main-table and --main-table-max-depth\n\n");
        exit(1);
    }

    // build the move matrix, we do this to avoid tons of
    // steps_on_same_face_and_layer() during the IDA search
    for (unsigned char i = 0; i < legal_move_count; i++) {
        move_type i_move = legal_moves[i];

        for (unsigned char j = 0; j < legal_move_count; j++) {
            move_type j_move = legal_moves[j];

            if (steps_on_same_face_and_layer(i_move, j_move)) {
                move_matrix[i_move][j] = MOVE_NONE;
            } else {
                move_matrix[i_move][j] = j_move;
            }
        }
    }

    move_type i_move = MOVE_NONE;
    for (unsigned char j = 0; j < legal_move_count; j++) {
        move_matrix[i_move][j] = legal_moves[j];
    }

    // build the same_face_and_layer_matrix, we do this to avoid tons of
    // steps_on_same_face_and_layer() during the IDA search
    for (unsigned char i = 1; i < MOVE_MAX; i++) {
        for (unsigned char j = 1; j < MOVE_MAX; j++) {
            if (steps_on_same_face_and_layer(i, j)) {
                same_face_and_layer_matrix[i][j] = 1;
            } else {
                same_face_and_layer_matrix[i][j] = 0;
            }
        }
    }

    ROW_LENGTH = COST_LENGTH + (STATE_LENGTH * legal_move_count);
    ida_solve(
        prune_table_0_state,
        prune_table_1_state,
        prune_table_2_state,
        prune_table_3_state,
        prune_table_4_state);
}
