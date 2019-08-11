
#include <ctype.h>
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


int
moves_cancel_out (move_type move, move_type prev_move)
{
    switch (move) {
    case U:        return (prev_move == U_PRIME);
    case U_PRIME:  return (prev_move == U);
    case U2:       return (prev_move == U2);
    case L:        return (prev_move == L_PRIME);
    case L_PRIME:  return (prev_move == L);
    case L2:       return (prev_move == L2);
    case F:        return (prev_move == F_PRIME);
    case F_PRIME:  return (prev_move == F);
    case F2:       return (prev_move == F2);
    case R:        return (prev_move == R_PRIME);
    case R_PRIME:  return (prev_move == R);
    case R2:       return (prev_move == R2);
    case B:        return (prev_move == B_PRIME);
    case B_PRIME:  return (prev_move == B);
    case B2:       return (prev_move == B2);
    case D:        return (prev_move == D_PRIME);
    case D_PRIME:  return (prev_move == D);
    case D2:       return (prev_move == D2);
    case Uw:       return (prev_move == Uw_PRIME);
    case Uw_PRIME: return (prev_move == Uw);
    case Uw2:      return (prev_move == Uw2);
    case Lw:       return (prev_move == Lw_PRIME);
    case Lw_PRIME: return (prev_move == Lw);
    case Lw2:      return (prev_move == Lw2);
    case Fw:       return (prev_move == Fw_PRIME);
    case Fw_PRIME: return (prev_move == Fw);
    case Fw2:      return (prev_move == Fw2);
    case Rw:       return (prev_move == Rw_PRIME);
    case Rw_PRIME: return (prev_move == Rw);
    case Rw2:      return (prev_move == Rw2);
    case Bw:       return (prev_move == Bw_PRIME);
    case Bw_PRIME: return (prev_move == Bw);
    case Bw2:      return (prev_move == Bw2);
    case Dw:       return (prev_move == Dw_PRIME);
    case Dw_PRIME: return (prev_move == Dw);
    case Dw2:      return (prev_move == Dw2);
    default:
        printf("ERROR: moves_cancel_out add support for %d\n", move);
        exit(1);
    }

    return 0;
}

int
steps_on_same_face_and_layer(move_type move, move_type prev_move)
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

    default:
        printf("ERROR: steps_on_same_face_and_layer add support for %d\n", move);
        exit(1);
    }

    return 0;
}

struct ida_search_result {
    unsigned int f_cost;
    unsigned int found_solution;
};

unsigned int
read_state(
    FILE *fh,
    unsigned int location)
{
    unsigned int swapped_result = 0;
    unsigned int result = 0;
    size_t read_count;

    fseek(fh, location, SEEK_SET);
    read_count = fread(&swapped_result, 4, 1, fh);

    result = (swapped_result & 0xFF) << 24;
    result |= (swapped_result & 0xFF00) << 8;
    result |= (swapped_result & 0xFF0000)  >> 8;
    result |= (swapped_result & 0xFF000000) >> 24;

    return result;
}

struct ida_search_result
ida_search (move_type *legal_moves,
            unsigned char legal_move_count,
            unsigned char cost_to_here,
            move_type *moves_to_here,
            unsigned char threshold,
            move_type prev_move,
            FILE *pt0_fh,
            unsigned int prev_pt0_state,
            FILE *pt1_fh,
            unsigned int prev_pt1_state,
            unsigned int ROW_LENGTH)
{
    unsigned char cost_to_goal = 0;
    unsigned char f_cost = 0;
    move_type move, skip_other_steps_this_face;
    struct ida_heuristic_result heuristic_result;
    struct key_value_pair *prev_heuristic_result = NULL;
    char cost_to_here_str[3];
    skip_other_steps_this_face = MOVE_NONE;
    struct ida_search_result search_result, tmp_search_result;
    size_t read_count;
    unsigned int pt0_state;
    unsigned int pt1_state;
    unsigned char pt0_cost = 0;
    unsigned char pt1_cost = 0;
    unsigned char max_cost_to_goal = threshold - cost_to_here;

    ida_count++;

    fseek(pt0_fh, prev_pt0_state * ROW_LENGTH, SEEK_SET);
    read_count = fread(&pt0_cost, 1, 1, pt0_fh);
    fseek(pt1_fh, prev_pt1_state * ROW_LENGTH, SEEK_SET);
    read_count = fread(&pt1_cost, 1, 1, pt1_fh);

    if (pt0_cost > pt1_cost) {
        cost_to_goal = pt0_cost;
    } else {
        cost_to_goal = pt1_cost;
    }

    // LOG("prev_pt0_state %lu, pt0_cost %lu, prev_pt1_state %lu, pt1_cost %lu\n", prev_pt0_state, pt0_cost, prev_pt1_state, pt1_cost);

    f_cost = cost_to_here + cost_to_goal;
    search_result.f_cost = f_cost;
    search_result.found_solution = 0;

    // Abort Searching
    if (f_cost >= threshold) {
        return search_result;
    }

    if (cost_to_goal == 0) {
        // We are finished!!
        LOG("IDA count %d, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
            ida_count, f_cost, threshold, cost_to_here, cost_to_goal);
        print_moves(moves_to_here, cost_to_here);
        search_result.found_solution = 1;
        return search_result;
    }

    // dwalton here now
    //memset(&heuristic_result, 0, sizeof(struct ida_heuristic_result));
    memset(&heuristic_result.lt_state, '\0', 64);
    memcpy(&heuristic_result.lt_state[0], &prev_pt0_state, 4);
    memcpy(&heuristic_result.lt_state[4], &prev_pt1_state, 4);
    //heuristic_result.lt_state[8] = cost_to_here;
    //heuristic_result.lt_state[8] = f_cost;

    prev_heuristic_result = hash_find(&ida_explored, heuristic_result.lt_state);

    if (prev_heuristic_result) {
        if (prev_heuristic_result->value <= cost_to_here) {
            return search_result;
        } else {
            hash_delete(&ida_explored, prev_heuristic_result);
        }
    }

    hash_add(&ida_explored, heuristic_result.lt_state, cost_to_here);

    for (int i = 0; i < legal_move_count; i++) {
        move = legal_moves[i];

        if (steps_on_same_face_and_layer(move, prev_move)) {
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
            if (steps_on_same_face_and_layer(move, skip_other_steps_this_face)) {
                continue;
            } else {
                skip_other_steps_this_face = MOVE_NONE;
            }
        }

        pt0_state = read_state(pt0_fh, (prev_pt0_state * ROW_LENGTH) + 1 + (4 * i));
        pt1_state = read_state(pt1_fh, (prev_pt1_state * ROW_LENGTH) + 1 + (4 * i));
        moves_to_here[cost_to_here] = move;

        tmp_search_result = ida_search(
            legal_moves,
            legal_move_count,
            cost_to_here + 1,
            moves_to_here,
            threshold,
            move,
            pt0_fh,
            pt0_state,
            pt1_fh,
            pt1_state,
            ROW_LENGTH
        );

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
    move_type *legal_moves,
    unsigned char legal_move_count,
    FILE *pt0_fh,
    unsigned int pt0_state,
    FILE *pt1_fh,
    unsigned int pt1_state)
{
    unsigned char MAX_SEARCH_DEPTH = 30;
    unsigned char min_ida_threshold = 0;
    move_type moves_to_here[MAX_SEARCH_DEPTH];
    struct ida_search_result search_result;
    size_t read_count;

    unsigned char COST_LENGTH = 1;
    unsigned char STATE_LENGTH = 4;
    unsigned char ROW_LENGTH = COST_LENGTH + (STATE_LENGTH * legal_move_count);
    unsigned char pt0_cost = 0;
    unsigned char pt1_cost = 0;
    
    memset(moves_to_here, MOVE_NONE, MAX_SEARCH_DEPTH);
    fseek(pt0_fh, pt0_state * ROW_LENGTH, SEEK_SET);
    read_count = fread(&pt0_cost, 1, 1, pt0_fh);
    fseek(pt1_fh, pt1_state * ROW_LENGTH, SEEK_SET);
    read_count = fread(&pt1_cost, 1, 1, pt1_fh);

    if (pt0_cost > pt1_cost) {
        min_ida_threshold = pt0_cost;
    } else {
        min_ida_threshold = pt1_cost;
    }

    LOG("min_ida_threshold %d\n", min_ida_threshold);

    for (unsigned char threshold = min_ida_threshold; threshold <= MAX_SEARCH_DEPTH; threshold++) {
        ida_count = 0;
        memset(moves_to_here, MOVE_NONE, sizeof(move_type) * MAX_SEARCH_DEPTH);
        hash_delete_all(&ida_explored);

        search_result = ida_search(
            legal_moves,
            legal_move_count,
            0,
            moves_to_here,
            threshold,
            MOVE_NONE,
            pt0_fh,
            pt0_state,
            pt1_fh,
            pt1_state,
            ROW_LENGTH
        );

        if (search_result.found_solution) {
            ida_count_total += ida_count;
            LOG("IDA threshold %d, explored %d branches (%d total), found solution\n", threshold, ida_count, ida_count_total);
            return 1;
        } else {
            ida_count_total += ida_count;
            LOG("IDA threshold %d, explored %d branches\n", threshold, ida_count);
        }
    }

    LOG("IDA failed with range %d->%d\n", min_ida_threshold, MAX_SEARCH_DEPTH);
    return 0;
}


int
main (int argc, char *argv[])
{
    unsigned char legal_move_count = 0;
    unsigned long prune_table_0_state = 0;
    unsigned long prune_table_1_state = 0;
    FILE *prune_table_0_fh = NULL;
    FILE *prune_table_1_fh = NULL;
    move_type legal_moves[MOVE_MAX];

    memset(legal_moves, MOVE_NONE, MOVE_MAX);

    for (unsigned char i = 1; i < argc; i++) {
        if (strmatch(argv[i], "--prune-table-0-filename")) {
            i++;
            prune_table_0_fh = fopen(argv[i], "rb");

        } else if (strmatch(argv[i], "--prune-table-0-state")) {
            i++;
            prune_table_0_state = atoi(argv[i]);

        } else if (strmatch(argv[i], "--prune-table-1-filename")) {
            i++;
            prune_table_1_fh = fopen(argv[i], "rb");

        } else if (strmatch(argv[i], "--prune-table-1-state")) {
            i++;
            prune_table_1_state = atoi(argv[i]);

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

    ida_solve(legal_moves, legal_move_count, prune_table_0_fh, prune_table_0_state, prune_table_1_fh, prune_table_1_state);

    if (prune_table_0_fh) {
        fclose(prune_table_0_fh);
        prune_table_0_fh = NULL;
    }

    if (prune_table_1_fh) {
        fclose(prune_table_1_fh);
        prune_table_1_fh = NULL;
    }

    // Print the maximum resident set size used (in MB).
    struct rusage r_usage;
    getrusage(RUSAGE_SELF, &r_usage);
    printf("Memory usage: %lu MB\n", (unsigned long) r_usage.ru_maxrss / (1024 * 1024));
}
