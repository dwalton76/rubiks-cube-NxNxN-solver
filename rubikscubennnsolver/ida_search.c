
#include <ctype.h>
#include <locale.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <time.h>

#include "ida_search_666.h"
#include "ida_search_777.h"
#include "ida_search_core.h"
#include "uthash.h"

// scratchpads that we do not want to allocate over and over again
char *sp_cube_state;
unsigned long array_size;
unsigned long long ida_count;
unsigned long long ida_count_total;
unsigned long long seek_calls = 0;
unsigned char centers_only = 0;
unsigned char legal_move_count = 0;
move_type legal_moves[MOVE_MAX];
move_type move_matrix[MOVE_MAX][MOVE_MAX];
#define MAX_IDA_THRESHOLD 20

// Supported IDA searches
typedef enum {
    NONE,

    // 6x6x6
    LR_OBLIQUE_EDGES_STAGE_666,

    // 7x7x7
    LR_OBLIQUE_EDGES_STAGE_777,
    UD_OBLIQUE_EDGES_STAGE_777,

} lookup_table_type;

struct key_value_pair *ida_explored = NULL;

void str_replace_for_binary(char *str, char *ones) {
    int i = 0;
    int j;
    int is_a_one = 0;

    /* Run till end of string */
    while (str[i] != '\0') {
        if (str[i] == '.') {
            // pass
        } else if (str[i] != '0') {
            j = 0;
            is_a_one = 0;

            while (ones[j] != 0) {
                /* If occurrence of character is found */
                if (str[i] == ones[j]) {
                    is_a_one = 1;
                    break;
                }
                j++;
            }

            if (is_a_one) {
                str[i] = '1';
            } else {
                str[i] = '0';
            }
        }

        i++;
    }
}

void init_cube(char *cube, int size, lookup_table_type type, char *kociemba) {
    int squares_per_side = size * size;
    int square_count = squares_per_side * 6;
    int U_start = 1;
    int L_start = U_start + squares_per_side;
    int F_start = L_start + squares_per_side;
    int R_start = F_start + squares_per_side;
    int B_start = R_start + squares_per_side;
    int D_start = B_start + squares_per_side;
    char cube_copy[array_size];

    // kociemba_string is in URFDLB order
    int U_start_kociemba = 0;
    int R_start_kociemba = U_start_kociemba + squares_per_side;
    int F_start_kociemba = R_start_kociemba + squares_per_side;
    int D_start_kociemba = F_start_kociemba + squares_per_side;
    int L_start_kociemba = D_start_kociemba + squares_per_side;
    int B_start_kociemba = L_start_kociemba + squares_per_side;

    char ones_UL[3] = {'U', 'L', 0};
    char ones_UF[3] = {'U', 'F', 0};
    char ones_UR[3] = {'U', 'R', 0};
    char ones_UB[3] = {'U', 'B', 0};
    char ones_UD[3] = {'U', 'D', 0};
    char ones_LF[3] = {'L', 'F', 0};
    char ones_LR[3] = {'L', 'R', 0};
    char ones_LB[3] = {'L', 'B', 0};
    char ones_LD[3] = {'L', 'D', 0};
    char ones_FR[3] = {'F', 'R', 0};
    char ones_FB[3] = {'F', 'B', 0};
    char ones_FD[3] = {'F', 'D', 0};
    char ones_RB[3] = {'R', 'B', 0};
    char ones_RD[3] = {'R', 'D', 0};
    char ones_BD[3] = {'B', 'D', 0};
    char ones_ULF[4] = {'U', 'L', 'F', 0};

    char U[2] = {'U', 0};
    char L[2] = {'L', 0};
    char F[2] = {'F', 0};
    char R[2] = {'R', 0};
    char B[2] = {'B', 0};
    char D[2] = {'D', 0};

    memset(cube, 0, sizeof(char) * (square_count + 2));
    cube[0] = 'x';  // placeholder
    memcpy(&cube[U_start], &kociemba[U_start_kociemba], squares_per_side);
    memcpy(&cube[L_start], &kociemba[L_start_kociemba], squares_per_side);
    memcpy(&cube[F_start], &kociemba[F_start_kociemba], squares_per_side);
    memcpy(&cube[R_start], &kociemba[R_start_kociemba], squares_per_side);
    memcpy(&cube[B_start], &kociemba[B_start_kociemba], squares_per_side);
    memcpy(&cube[D_start], &kociemba[D_start_kociemba], squares_per_side);
    // LOG("cube:\n%s\n\n", cube);

    switch (type) {
        case LR_OBLIQUE_EDGES_STAGE_666:
            // Convert to 1s and 0s
            str_replace_for_binary(cube, ones_LR);
            print_cube(cube, size);
            break;

        case LR_OBLIQUE_EDGES_STAGE_777:
            // Convert to 1s and 0s
            str_replace_for_binary(cube, ones_LR);
            print_cube(cube, size);
            break;

        case UD_OBLIQUE_EDGES_STAGE_777:
            // Convert to 1s and 0s
            str_replace_for_binary(cube, ones_UD);
            print_cube(cube, size);
            break;

        default:
            printf("ERROR: init_cube() does not yet support this --type\n");
            exit(1);
    }
}

void ida_prune_table_preload(struct key_value_pair **hashtable, char *filename) {
    FILE *fh_read = NULL;
    int BUFFER_SIZE = 128;
    char buffer[BUFFER_SIZE];
    char token_buffer[BUFFER_SIZE];
    char moves[BUFFER_SIZE];
    char *token_ptr = NULL;
    char state[BUFFER_SIZE];
    int cost = 0;
    struct key_value_pair *pt_entry = NULL;

    fh_read = fopen(filename, "r");
    if (fh_read == NULL) {
        printf("ERROR: ida_prune_table_preload could not open %s\n", filename);
        exit(1);
    }

    LOG("ida_prune_table_preload %s: start\n", filename);

    // 4x4x4
    if (strmatch(filename, "lookup-tables/lookup-table-4x4x4-step30-reduce333.txt")) {
        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // DDDDLLLLBBBBRRRRFFFFUUUU10362745a8b9ecfdhgkiljnm:R2 Bw2 D' F2 D Bw2
            // 0..47 are the state
            // 48 is the :
            // 49 is the move count
            buffer[48] = '\0';
            cost = atoi(&buffer[49]);
            hash_add(hashtable, buffer, cost);
        }

    } else {
        printf("ERROR: ida_prune_table_preload add support for %s\n", filename);
        exit(1);
    }

    fclose(fh_read);
    LOG("ida_prune_table_preload %s: end\n", filename);
}

char *ida_cost_only_preload(char *filename, unsigned long size) {
    FILE *fh_read = NULL;
    char *ptr = malloc(sizeof(char) * size);
    memset(ptr, 0, sizeof(char) * size);
    LOG("ida_cost_only_preload: begin %s, %d entries, ptr 0x%x\n", filename, size, ptr);

    fh_read = fopen(filename, "r");
    if (fh_read == NULL) {
        printf("ERROR: ida_cost_only_preload could not open %s\n", filename);
        exit(1);
    }

    if (fread(ptr, size, 1, fh_read)) {
        fclose(fh_read);
        LOG("ida_cost_only_preload: end   %s, ptr 0x%x\n", filename, ptr);
        return ptr;
    } else {
        printf("ERROR: ida_cost_only_preload read failed %s\n", filename);
        exit(1);
    }
}

struct ida_heuristic_result ida_heuristic(char *cube, lookup_table_type type, unsigned int max_cost_to_goal) {
    switch (type) {
        // 6x6x6
        case LR_OBLIQUE_EDGES_STAGE_666:
            return ida_heuristic_LR_oblique_edges_stage_666(cube);

        // 7x7x7
        case LR_OBLIQUE_EDGES_STAGE_777:
            return ida_heuristic_LR_oblique_edges_stage_777(cube);

        case UD_OBLIQUE_EDGES_STAGE_777:
            return ida_heuristic_UD_oblique_edges_stage_777(cube);

        default:
            printf("ERROR: ida_heuristic() does not yet support this --type\n");
            exit(1);
    }
}

unsigned char ida_search_complete(char *cube, lookup_table_type type, unsigned int orbit0_wide_quarter_turns,
                                  unsigned int orbit1_wide_quarter_turns,
                                  move_type *moves_to_here) {
    struct key_value_pair *pt_entry = NULL;
    unsigned int orbit0_wide_quarter_turn_count = 0;
    unsigned int orbit1_wide_quarter_turn_count = 0;
    int result = 0;

    if (orbit0_wide_quarter_turns) {
        orbit0_wide_quarter_turn_count = get_orbit0_wide_quarter_turn_count(moves_to_here);

        // orbit0 must have an odd number of wide quarter
        if (orbit0_wide_quarter_turns == 1) {
            if (orbit0_wide_quarter_turn_count % 2 == 0) {
                return 0;
            }

            // orbit0 must have an even number of wide quarter
        } else if (orbit0_wide_quarter_turns == 2) {
            if (orbit0_wide_quarter_turn_count % 2) {
                return 0;
            }

        } else {
            printf("ERROR: orbit0_wide_quarter_turns %d is not supported\n", orbit0_wide_quarter_turns);
            exit(1);
        }
    }

    if (orbit1_wide_quarter_turns) {
        orbit1_wide_quarter_turn_count = get_orbit1_wide_quarter_turn_count(moves_to_here);

        // orbit1 must have an odd number of wide quarter
        if (orbit1_wide_quarter_turns == 1) {
            if (orbit1_wide_quarter_turn_count % 2 == 0) {
                return 0;
            }

            // orbit1 must have an even number of wide quarter
        } else if (orbit1_wide_quarter_turns == 2) {
            if (orbit1_wide_quarter_turn_count % 2) {
                return 0;
            }

        } else {
            printf("ERROR: orbit1_wide_quarter_turns %d is not supported\n", orbit1_wide_quarter_turns);
            exit(1);
        }
    }

    switch (type) {
        // 6x6x6
        case LR_OBLIQUE_EDGES_STAGE_666:
            return ida_search_complete_LR_oblique_edges_stage_666(cube);

        // 7x7x7
        case LR_OBLIQUE_EDGES_STAGE_777:
            return ida_search_complete_LR_oblique_edges_stage_777(cube);

        case UD_OBLIQUE_EDGES_STAGE_777:
            return ida_search_complete_UD_oblique_edges_stage_777(cube);

        default:
            printf("ERROR: ida_search_complete() does not yet support type %d\n", type);
            exit(1);
    }

    return 0;
}

struct ida_search_result ida_search(unsigned int cost_to_here, move_type *moves_to_here, unsigned int threshold,
                                    move_type prev_move, char *cube, unsigned int cube_size, lookup_table_type type,
                                    unsigned int orbit0_wide_quarter_turns, unsigned int orbit1_wide_quarter_turns) {
    unsigned int cost_to_goal = 0;
    unsigned int f_cost = 0;
    move_type move;
    struct ida_heuristic_result heuristic_result;
    char cube_tmp[array_size];
    char cost_to_here_str[4];
    struct ida_search_result search_result, tmp_search_result;

    ida_count++;
    unsigned int max_cost_to_goal = threshold - cost_to_here;
    heuristic_result = ida_heuristic(cube, type, max_cost_to_goal);
    cost_to_goal = heuristic_result.cost_to_goal;
    f_cost = cost_to_here + cost_to_goal;
    search_result.f_cost = f_cost;
    search_result.found_solution = 0;
    move_type *prev_move_move_matrix = NULL;
    size_t array_size_char = sizeof(char) * array_size;

    if (cost_to_goal == 0 && ida_search_complete(cube, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns,
                                                 moves_to_here)) {
        // We are finished!!
        LOG("IDA count %'llu, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n", ida_count, f_cost,
            threshold, cost_to_here, cost_to_goal);
        print_moves(moves_to_here, cost_to_here);

        if (!search_result.found_solution || f_cost < search_result.f_cost) {
            search_result.f_cost = f_cost;
            search_result.found_solution = 1;
            memcpy(search_result.solution, moves_to_here, sizeof(move_type) * MAX_IDA_THRESHOLD);
        }

        // print the solved cube
        print_cube(cube, cube_size);
        return search_result;
    }

    // Stop searching down this branch
    if (f_cost > threshold) {
        // uncomment this to troubleshoot when the correct solution is incorrectly pruned
        /*
        if (invalid_prune(cost_to_here, moves_to_here, threshold)) {
            LOG("IDA invalid prune HERE 00, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
                f_cost, threshold, cost_to_here, cost_to_goal);
            print_moves(moves_to_here, cost_to_here);
            exit(1);
        }
         */
        return search_result;
    }

    sprintf(cost_to_here_str, "%d", cost_to_here);
    strcat(heuristic_result.lt_state, cost_to_here_str);

    if (hash_find(&ida_explored, heuristic_result.lt_state)) {
        return search_result;
    }

    hash_add(&ida_explored, heuristic_result.lt_state, 0);
    prev_move_move_matrix = move_matrix[prev_move];

    for (unsigned char i = 0; i < legal_move_count; i++) {
        move = prev_move_move_matrix[i];

        // This is the scenario where the move is on the same face and layer as prev_move
        if (move == MOVE_NONE) {
            continue;
        }

        char cube_copy[array_size];
        memcpy(cube_copy, cube, array_size_char);

        if (cube_size == 6) {
            rotate_666(cube_copy, cube_tmp, array_size, move);
        } else if (cube_size == 7) {
            rotate_777(cube_copy, cube_tmp, array_size, move);
        } else {
            printf("ERROR: ida_search() does not have rotate_xxx() for this cube size\n");
            exit(1);
        }

        // if the cube state did not change, continue
        if (memcmp(cube, cube_copy, array_size_char) == 0) {
            continue;
        }
        moves_to_here[cost_to_here] = move;

        tmp_search_result = ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size, type,
                                       orbit0_wide_quarter_turns, orbit1_wide_quarter_turns);

        if (tmp_search_result.found_solution) {
            return tmp_search_result;
        } else {
            moves_to_here[cost_to_here] = MOVE_NONE;
        }
    }

    return search_result;
}

void print_ida_summary(lookup_table_type type, char *cube, struct ida_search_result search_result) {
    unsigned int solution_len = search_result.f_cost;
    char cube_tmp[array_size];
    char cube_copy[array_size];
    size_t array_size_char = sizeof(char) * array_size;
    unsigned int cost_to_goal = 0;
    struct ida_heuristic_result heuristic;

    memcpy(cube_copy, cube, array_size_char);

    if (type == LR_OBLIQUE_EDGES_STAGE_666) {
        heuristic = ida_heuristic_LR_oblique_edges_stage_666(cube);
    } else if (type == LR_OBLIQUE_EDGES_STAGE_777) {
        heuristic = ida_heuristic_LR_oblique_edges_stage_777(cube);
    } else if (type == UD_OBLIQUE_EDGES_STAGE_777) {
        heuristic = ida_heuristic_UD_oblique_edges_stage_777(cube);
    }

    printf("\n\n");
    printf("       UNPAIRED\n");
    printf("          COUNT  CTG  TRU  IDX\n");
    printf("       ========  ===  ===  ===\n");
    printf(" INIT  %8d  %3d  %3d  %3d\n", heuristic.unpaired_count, heuristic.cost_to_goal, search_result.f_cost,
           0);

    for (unsigned char i = 0; i < solution_len; i++) {
        if (type == LR_OBLIQUE_EDGES_STAGE_666) {
            rotate_666(cube, cube_tmp, array_size, search_result.solution[i]);
            heuristic = ida_heuristic_LR_oblique_edges_stage_666(cube);
        } else if (type == LR_OBLIQUE_EDGES_STAGE_777) {
            rotate_777(cube, cube_tmp, array_size, search_result.solution[i]);
            heuristic = ida_heuristic_LR_oblique_edges_stage_777(cube);
        } else if (type == UD_OBLIQUE_EDGES_STAGE_777) {
            rotate_777(cube, cube_tmp, array_size, search_result.solution[i]);
            heuristic = ida_heuristic_UD_oblique_edges_stage_777(cube);
        } else {
            printf("ERROR: print_ida_summary %d is an invalid --type\n", type);
            exit(1);
        }

        printf("%5s  %8d  %3d  %3d  %3d\n", move2str[search_result.solution[i]], heuristic.unpaired_count,
               heuristic.cost_to_goal, search_result.f_cost - i - 1, i + 1);
    }
    printf("\n");
}

int ida_solve(char *cube, unsigned int cube_size, lookup_table_type type, unsigned int orbit0_wide_quarter_turns,
              unsigned int orbit1_wide_quarter_turns) {
    move_type moves_to_here[MAX_IDA_THRESHOLD];
    int min_ida_threshold = 0;
    struct ida_heuristic_result heuristic_result;
    struct ida_search_result search_result;
    struct timeval stop, start, start_this_threshold;

    // For printing commas via %'d
    setlocale(LC_NUMERIC, "");

    memset(moves_to_here, MOVE_NONE, MAX_IDA_THRESHOLD);

    if (ida_search_complete(cube, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, moves_to_here)) {
        LOG("cube already solved\n");
        printf("SOLUTION:\n");
        return 1;
    }

    heuristic_result = ida_heuristic(cube, type, 99);
    min_ida_threshold = heuristic_result.cost_to_goal;
    LOG("min_ida_threshold %d\n", min_ida_threshold);
    gettimeofday(&start, NULL);

    for (int threshold = min_ida_threshold; threshold <= MAX_IDA_THRESHOLD; threshold++) {
        ida_count = 0;
        gettimeofday(&start_this_threshold, NULL);
        memset(moves_to_here, MOVE_NONE, sizeof(move_type) * MAX_IDA_THRESHOLD);
        hash_delete_all(&ida_explored);

        search_result = ida_search(0, moves_to_here, threshold, MOVE_NONE, cube, cube_size, type,
                                   orbit0_wide_quarter_turns, orbit1_wide_quarter_turns);

        gettimeofday(&stop, NULL);
        ida_count_total += ida_count;
        float ms = ((stop.tv_sec - start_this_threshold.tv_sec) * 1000) +
                   ((stop.tv_usec - start_this_threshold.tv_usec) / 1000);
        float nodes_per_ms = ida_count / ms;
        unsigned int nodes_per_sec = nodes_per_ms * 1000;

        LOG("IDA threshold %d, explored %'llu nodes, took %.3fs, %'d nodes-per-sec\n", threshold, ida_count, ms / 1000,
            nodes_per_sec);

        if (search_result.found_solution) {
            float ms = ((stop.tv_sec - start.tv_sec) * 1000) + ((stop.tv_usec - start.tv_usec) / 1000);
            float nodes_per_ms = ida_count_total / ms;
            unsigned int nodes_per_sec = nodes_per_ms * 1000;
            LOG("IDA found solution, explored %'llu total nodes, took %.3fs, %'d nodes-per-sec\n", ida_count_total,
                ms / 1000, nodes_per_sec);

            print_ida_summary(type, cube, search_result);
            return 1;
        }
    }

    LOG("IDA failed with range %d->%d\n", min_ida_threshold, MAX_IDA_THRESHOLD);
    return 0;
}

int main(int argc, char *argv[]) {
    lookup_table_type type = NONE;
    unsigned int cube_size_type = 0;
    unsigned int cube_size_kociemba = 0;
    unsigned int orbit0_wide_quarter_turns = 0;
    unsigned int orbit1_wide_quarter_turns = 0;
    char kociemba[300];
    memset(kociemba, 0, sizeof(char) * 300);
    memset(legal_moves, MOVE_NONE, MOVE_MAX);
    memset(move_matrix, MOVE_NONE, MOVE_MAX * MOVE_MAX);

    for (int i = 1; i < argc; i++) {
        if (strmatch(argv[i], "-k") || strmatch(argv[i], "--kociemba")) {
            i++;
            strcpy(kociemba, argv[i]);
            cube_size_kociemba = (unsigned int)sqrt(strlen(kociemba) / 6);

        } else if (strmatch(argv[i], "-t") || strmatch(argv[i], "--type")) {
            i++;

            if (strmatch(argv[i], "6x6x6-LR-oblique-edges-stage")) {
                type = LR_OBLIQUE_EDGES_STAGE_666;
                cube_size_type = 6;

            } else if (strmatch(argv[i], "7x7x7-LR-oblique-edges-stage")) {
                type = LR_OBLIQUE_EDGES_STAGE_777;
                cube_size_type = 7;

            } else if (strmatch(argv[i], "7x7x7-UD-oblique-edges-stage")) {
                type = UD_OBLIQUE_EDGES_STAGE_777;
                cube_size_type = 7;

            } else {
                printf("ERROR: %s is an invalid --type\n", argv[i]);
                exit(1);
            }

        } else if (strmatch(argv[i], "--orbit0-need-odd-w")) {
            orbit0_wide_quarter_turns = 1;

        } else if (strmatch(argv[i], "--orbit0-need-even-w")) {
            orbit0_wide_quarter_turns = 2;

        } else if (strmatch(argv[i], "--orbit1-need-odd-w")) {
            orbit1_wide_quarter_turns = 1;

        } else if (strmatch(argv[i], "--orbit1-need-even-w")) {
            orbit1_wide_quarter_turns = 2;

        } else if (strmatch(argv[i], "--centers-only")) {
            centers_only = 1;

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

                p = strtok(NULL, ",");
                legal_move_count++;
            }

        } else if (strmatch(argv[i], "-h") || strmatch(argv[i], "--help")) {
            printf("\nida_search --kociemba KOCIEMBA_STRING --type 5x5x5-LR-centers-stage\n\n");
            exit(0);

        } else {
            printf("ERROR: %s is an invalid arg\n\n", argv[i]);
            printf("Try this and run it again\n");
            printf("$ make clean\n");
            printf("$ sudo make all\n\n");
            exit(1);
        }
    }

    if (!type) {
        printf("ERROR: --type is required\n");
        exit(1);
    }

    if (cube_size_type != cube_size_kociemba) {
        printf("ERROR: --type cube size is %d, --kociemba cube size is %d\n", cube_size_type, cube_size_kociemba);
        exit(1);
    }

    if (cube_size_kociemba < 6 || cube_size_kociemba > 7) {
        printf("ERROR: only 6x6x6 and 7x7x7 cubes are supported, yours is %dx%dx%d\n", cube_size_kociemba,
               cube_size_kociemba, cube_size_kociemba);
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

            } else if (centers_only && !outer_layer_moves_in_order(i_move, j_move)) {
                // if we are solving centers, we want to avoid doing permutations of outer layer moves as they
                // will all result in the same cube state.  For instance there is no point in doing F U B, B U F,
                // U B F, etc. We can do only one of those and that is enough.
                move_matrix[i_move][j] = MOVE_NONE;

                // this has a negative impact on some of the oblique edge pairing searches
                /*
                 * } else if (!steps_on_same_face_in_order(i_move, j_move)) {
                 *   move_matrix[i_move][j] = MOVE_NONE;
                 */

            } else if (!steps_on_opposite_faces_in_order(i_move, j_move)) {
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

    unsigned int cube_size = cube_size_kociemba;
    array_size = (cube_size * cube_size * 6) + 2;
    char cube[array_size];
    char cube_tmp[array_size];

    if (orbit1_wide_quarter_turns && cube_size != 6 && cube_size != 7) {
        printf("ERROR cannot do avoid_oll on orbit1 for %dx%dx%d cubes\n", cube_size, cube_size, cube_size);
        exit(1);
    }

    sp_cube_state = malloc(sizeof(char) * array_size);
    memset(cube_tmp, 0, sizeof(char) * array_size);
    init_cube(cube, cube_size, type, kociemba);

    // print_cube(cube, cube_size);
    ida_solve(cube, cube_size, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns);
}
