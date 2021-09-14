
#include <ctype.h>
#include <limits.h>
#include <locale.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <time.h>

#include "ida_search_core.h"

unsigned long long ida_count = 0;
unsigned long long ida_count_total = 0;
unsigned char legal_move_count = 0;
unsigned char threshold = 0;
unsigned char *pt0 = NULL;
unsigned char *pt1 = NULL;
unsigned char *pt2 = NULL;
unsigned char *pt3 = NULL;
unsigned char *pt4 = NULL;
unsigned char *pt_perfect_hash01 = NULL;
unsigned char *pt_perfect_hash02 = NULL;
unsigned int pt1_state_max = 0;
unsigned int pt2_state_max = 0;
unsigned char call_pt_simple = 0;

#define MAX_IDA_THRESHOLD 20
unsigned char pt_max = 0;
unsigned char COST_LENGTH = 1;
unsigned char STATE_LENGTH = 4;
unsigned char ROW_LENGTH = 0;
unsigned char orbit0_wide_quarter_turns = 0;
unsigned char orbit1_wide_quarter_turns = 0;
unsigned int solution_count = 0;
unsigned int min_solution_count = 1;
float cost_to_goal_multiplier = 0.0;
move_type legal_moves[MOVE_MAX];
move_type move_matrix[MOVE_MAX][MOVE_MAX];
struct key_value_pair *ida_explored = NULL;

// Supported IDA searches
typedef enum {
    GENERIC,
    LR_CENTERS_STAGE_555,
    CENTERS_STAGE_555,

} lookup_table_type;

struct cost_to_goal_result {
    unsigned char cost_to_goal;
    unsigned char pt0_cost;
    unsigned char pt1_cost;
    unsigned char pt2_cost;
    unsigned char pt3_cost;
    unsigned char pt4_cost;
    unsigned char perfect_hash01_cost;
    unsigned char perfect_hash02_cost;
};

unsigned int lr_centers_stage_555[9][9] = {
    /*
    The following is a 2D array that estimates the number of moves to stage LR centers based on the t-center cost
    and x-center. This was created by staging the LR centers for 10k cubes and then crunching some stats (see
    utils/build-555-LR-centers-stage-stats.py)

    The columns are the x-center costs
     0  1  2  3  4  5  6  7  8
     */
    {0, 1, 2, 3, 4, 5, 6, 7, 8},    // t-center cost 0
    {1, 1, 2, 3, 4, 5, 6, 7, 8},    // t-center cost 1
    {2, 2, 2, 3, 4, 5, 7, 7, 8},    // t-center cost 2
    {3, 3, 3, 3, 4, 5, 6, 7, 8},    // t-center cost 3
    {4, 4, 4, 4, 4, 5, 7, 8, 8},    // t-center cost 4
    {5, 5, 5, 5, 5, 5, 7, 8, 8},    // t-center cost 5
    {6, 6, 6, 6, 7, 7, 8, 9, 10},   // t-center cost 6
    {7, 7, 7, 8, 8, 9, 9, 10, 10},  // t-center cost 7
    {8, 8, 8, 8, 8, 9, 10, 10, 8},  // t-center cost 8
};

unsigned int t_centers_stage_555[9][9] = {
    {0, 1, 2, 3, 4, 5, 6, 7, 8},    // LR t-centers cost 0
    {1, 1, 2, 3, 4, 5, 6, 7, 8},    // LR t-centers cost 1
    {2, 2, 2, 3, 4, 5, 6, 8, 8},    // LR t-centers cost 2
    {3, 3, 3, 3, 4, 5, 6, 7, 8},    // LR t-centers cost 3
    {4, 4, 4, 4, 4, 5, 6, 8, 8},    // LR t-centers cost 4
    {5, 5, 5, 5, 5, 6, 7, 8, 9},    // LR t-centers cost 5
    {6, 6, 6, 6, 6, 7, 8, 9, 9},    // LR t-centers cost 6
    {7, 7, 7, 7, 7, 8, 9, 9, 10},   // LR t-centers cost 7
    {8, 8, 8, 8, 8, 9, 9, 10, 10},  // LR t-centers cost 8
};

unsigned int x_centers_stage_555[9][9] = {
    {0, 1, 2, 3, 4, 5, 6, 7, 8},    // LR x-centers cost 0
    {1, 1, 2, 3, 4, 5, 6, 7, 8},    // LR x-centers cost 1
    {2, 2, 2, 3, 4, 5, 6, 7, 8},    // LR x-centers cost 2
    {3, 3, 3, 3, 4, 5, 6, 7, 8},    // LR x-centers cost 3
    {4, 4, 4, 4, 4, 5, 7, 7, 8},    // LR x-centers cost 4
    {5, 5, 5, 5, 5, 6, 7, 8, 9},    // LR x-centers cost 5
    {6, 6, 6, 6, 7, 7, 8, 9, 9},    // LR x-centers cost 6
    {7, 7, 7, 7, 7, 8, 9, 9, 8},    // LR x-centers cost 7
    {8, 8, 8, 8, 8, 8, 10, 10, 8},  // LR x-centers cost 8
};

unsigned char hash_cost_to_cost(unsigned char perfect_hash_cost) {
    switch (perfect_hash_cost) {
        case '0':
            return 0;
        case '1':
            return 1;
        case '2':
            return 2;
        case '3':
            return 3;
        case '4':
            return 4;
        case '5':
            return 5;
        case '6':
            return 6;
        case '7':
            return 7;
        case '8':
            return 8;
        case '9':
            return 9;
        case 'a':
            return 10;
        case 'b':
            return 11;
        case 'c':
            return 12;
        case 'd':
            return 13;
        case 'e':
            return 14;
        case 'f':
            return 15;
        default:
            printf("ERROR: invalid perfect_hash01_cost %d\n", perfect_hash_cost);
            exit(1);
    };
}

// A structure to represent a stack
struct StackNode {
    unsigned char cost_to_here;
    unsigned char cost_to_goal;
    move_type moves_to_here[MAX_IDA_THRESHOLD];
    move_type prev_move;
    unsigned int pt0_state;
    unsigned int pt1_state;
    unsigned int pt2_state;
    unsigned int pt3_state;
    unsigned int pt4_state;
    struct StackNode *next;
};

void push(struct StackNode **root, unsigned char cost_to_here, unsigned char cost_to_goal, move_type *moves_to_here,
          move_type prev_move, unsigned int pt0_state, unsigned int pt1_state, unsigned int pt2_state,
          unsigned int pt3_state, unsigned int pt4_state) {
    struct StackNode *node = (struct StackNode *)malloc(sizeof(struct StackNode));
    node->cost_to_here = cost_to_here;
    node->cost_to_goal = cost_to_goal;
    memcpy(node->moves_to_here, moves_to_here, sizeof(move_type) * MAX_IDA_THRESHOLD);
    node->prev_move = prev_move;
    node->pt0_state = pt0_state;
    node->pt1_state = pt1_state;
    node->pt2_state = pt2_state;
    node->pt3_state = pt3_state;
    node->pt4_state = pt4_state;
    node->next = *root;
    *root = node;
}

struct StackNode *pop(struct StackNode **root) {
    struct StackNode *temp = *root;
    *root = (*root)->next;
    return temp;
}

unsigned char pt_states_to_cost_simple(lookup_table_type type, unsigned int prev_pt0_state, unsigned int prev_pt1_state,
                                       unsigned int prev_pt2_state, unsigned int prev_pt3_state,
                                       unsigned int prev_pt4_state, unsigned char pt0_cost, unsigned char pt1_cost,
                                       unsigned char pt2_cost, unsigned char pt3_cost, unsigned char pt4_cost,
                                       unsigned char init_cost_to_goal) {
    unsigned char cost_to_goal = init_cost_to_goal;

    if (type == LR_CENTERS_STAGE_555) {
        cost_to_goal = lr_centers_stage_555[pt0_cost][pt1_cost];
    } else if (type == CENTERS_STAGE_555) {
        unsigned char lr_t_centers_cost = pt0_cost;
        unsigned char lr_x_centers_cost = pt1_cost;
        unsigned char ud_t_centers_cost = pt2_cost;
        unsigned char ud_x_centers_cost = pt3_cost;

        if (lr_centers_stage_555[lr_t_centers_cost][lr_x_centers_cost] > cost_to_goal) {
            cost_to_goal = lr_centers_stage_555[lr_t_centers_cost][lr_x_centers_cost];
        }

        if (lr_centers_stage_555[ud_t_centers_cost][ud_x_centers_cost] > cost_to_goal) {
            cost_to_goal = lr_centers_stage_555[ud_t_centers_cost][ud_x_centers_cost];
        }

        if (lr_centers_stage_555[lr_t_centers_cost][ud_x_centers_cost] > cost_to_goal) {
            cost_to_goal = lr_centers_stage_555[lr_t_centers_cost][ud_x_centers_cost];
        }

        if (lr_centers_stage_555[ud_t_centers_cost][lr_x_centers_cost] > cost_to_goal) {
            cost_to_goal = lr_centers_stage_555[ud_t_centers_cost][lr_x_centers_cost];
        }

        if (t_centers_stage_555[lr_t_centers_cost][ud_t_centers_cost] > cost_to_goal) {
            cost_to_goal = t_centers_stage_555[lr_t_centers_cost][ud_t_centers_cost];
        }

        if (x_centers_stage_555[lr_x_centers_cost][ud_x_centers_cost] > cost_to_goal) {
            cost_to_goal = x_centers_stage_555[lr_x_centers_cost][ud_x_centers_cost];
        }
    }

    if (pt_perfect_hash01) {
        unsigned int perfect_hash01_index = (prev_pt0_state * pt1_state_max) + prev_pt1_state;
        unsigned char perfect_hash01_cost = hash_cost_to_cost(pt_perfect_hash01[perfect_hash01_index]);

        // LOG("prev_pt0_state %d, prev_pt1_state %d, perfect_hash01_index %d, perfect_hash01_cost %d, cost_to_goal %d\n",
        //     prev_pt0_state, prev_pt1_state, perfect_hash01_index, perfect_hash01_cost, cost_to_goal);

        // dwalton
        if (perfect_hash01_cost > cost_to_goal) {
            cost_to_goal = perfect_hash01_cost;
        }

        if (pt_perfect_hash02) {
            unsigned int perfect_hash02_index = (prev_pt0_state * pt2_state_max) + prev_pt2_state;
            unsigned char perfect_hash02_cost = hash_cost_to_cost(pt_perfect_hash02[perfect_hash02_index]);

            if (perfect_hash02_cost > cost_to_goal) {
                cost_to_goal = perfect_hash02_cost;
            }
        }
    }

    if (cost_to_goal_multiplier) {
        cost_to_goal = (unsigned char)round(cost_to_goal * cost_to_goal_multiplier);
    }

    return cost_to_goal;
}

unsigned int read_state(unsigned char *pt, unsigned int location) {
    unsigned int result = 0;
    memcpy(&result, &pt[location], sizeof(unsigned int));
    return result;
}

unsigned char read_cost(unsigned char *pt, unsigned int location) { return pt[location]; }

struct cost_to_goal_result pt_states_to_cost(lookup_table_type type, unsigned int prev_pt0_state,
                                             unsigned int prev_pt1_state, unsigned int prev_pt2_state,
                                             unsigned int prev_pt3_state, unsigned int prev_pt4_state) {
    struct cost_to_goal_result result;

    switch (pt_max) {
        case 1:
            result.pt0_cost = read_cost(pt0, prev_pt0_state * ROW_LENGTH);
            result.pt1_cost = read_cost(pt1, prev_pt1_state * ROW_LENGTH);
            result.pt2_cost = 0;
            result.pt3_cost = 0;
            result.pt4_cost = 0;
            result.cost_to_goal = result.pt0_cost;

            if (type == LR_CENTERS_STAGE_555) {
                result.cost_to_goal = lr_centers_stage_555[result.pt0_cost][result.pt1_cost];
            } else {
                if (result.pt1_cost > result.cost_to_goal) {
                    result.cost_to_goal = result.pt1_cost;
                }
            }
            break;

        case 2:
            result.pt0_cost = read_cost(pt0, prev_pt0_state * ROW_LENGTH);
            result.pt1_cost = read_cost(pt1, prev_pt1_state * ROW_LENGTH);
            result.pt2_cost = read_cost(pt2, prev_pt2_state * ROW_LENGTH);
            result.pt3_cost = 0;
            result.pt4_cost = 0;
            result.cost_to_goal = result.pt0_cost;

            if (result.pt1_cost > result.cost_to_goal) {
                result.cost_to_goal = result.pt1_cost;
            }

            if (result.pt2_cost > result.cost_to_goal) {
                result.cost_to_goal = result.pt2_cost;
            }
            break;

        case 3:
            result.pt0_cost = read_cost(pt0, prev_pt0_state * ROW_LENGTH);
            result.pt1_cost = read_cost(pt1, prev_pt1_state * ROW_LENGTH);
            result.pt2_cost = read_cost(pt2, prev_pt2_state * ROW_LENGTH);
            result.pt3_cost = read_cost(pt3, prev_pt3_state * ROW_LENGTH);
            result.pt4_cost = 0;
            result.cost_to_goal = result.pt0_cost;

            if (type == CENTERS_STAGE_555) {
                unsigned char lr_t_centers_cost = result.pt0_cost;
                unsigned char lr_x_centers_cost = result.pt1_cost;
                unsigned char ud_t_centers_cost = result.pt2_cost;
                unsigned char ud_x_centers_cost = result.pt3_cost;

                if (lr_centers_stage_555[lr_t_centers_cost][lr_x_centers_cost] > result.cost_to_goal) {
                    result.cost_to_goal = lr_centers_stage_555[lr_t_centers_cost][lr_x_centers_cost];
                }

                if (lr_centers_stage_555[ud_t_centers_cost][ud_x_centers_cost] > result.cost_to_goal) {
                    result.cost_to_goal = lr_centers_stage_555[ud_t_centers_cost][ud_x_centers_cost];
                }

                if (lr_centers_stage_555[lr_t_centers_cost][ud_x_centers_cost] > result.cost_to_goal) {
                    result.cost_to_goal = lr_centers_stage_555[lr_t_centers_cost][ud_x_centers_cost];
                }

                if (lr_centers_stage_555[ud_t_centers_cost][lr_x_centers_cost] > result.cost_to_goal) {
                    result.cost_to_goal = lr_centers_stage_555[ud_t_centers_cost][lr_x_centers_cost];
                }

                if (t_centers_stage_555[lr_t_centers_cost][ud_t_centers_cost] > result.cost_to_goal) {
                    result.cost_to_goal = t_centers_stage_555[lr_t_centers_cost][ud_t_centers_cost];
                }

                if (x_centers_stage_555[lr_x_centers_cost][ud_x_centers_cost] > result.cost_to_goal) {
                    result.cost_to_goal = x_centers_stage_555[lr_x_centers_cost][ud_x_centers_cost];
                }

            } else {
                if (result.pt1_cost > result.cost_to_goal) {
                    result.cost_to_goal = result.pt1_cost;
                }

                if (result.pt2_cost > result.cost_to_goal) {
                    result.cost_to_goal = result.pt2_cost;
                }

                if (result.pt3_cost > result.cost_to_goal) {
                    result.cost_to_goal = result.pt3_cost;
                }
            }
            break;

        case 4:
            result.pt0_cost = read_cost(pt0, prev_pt0_state * ROW_LENGTH);
            result.pt1_cost = read_cost(pt1, prev_pt1_state * ROW_LENGTH);
            result.pt2_cost = read_cost(pt2, prev_pt2_state * ROW_LENGTH);
            result.pt3_cost = read_cost(pt3, prev_pt3_state * ROW_LENGTH);
            result.pt4_cost = read_cost(pt4, prev_pt4_state * ROW_LENGTH);
            result.cost_to_goal = result.pt0_cost;

            if (result.pt1_cost > result.cost_to_goal) {
                result.cost_to_goal = result.pt1_cost;
            }

            if (result.pt2_cost > result.cost_to_goal) {
                result.cost_to_goal = result.pt2_cost;
            }

            if (result.pt3_cost > result.cost_to_goal) {
                result.cost_to_goal = result.pt3_cost;
            }

            if (result.pt4_cost > result.cost_to_goal) {
                result.cost_to_goal = result.pt4_cost;
            }
            break;

        default:
            printf("ERROR: invalid pt_max %d\n", pt_max);
            exit(1);
    }

    if (pt_perfect_hash01) {
        unsigned int perfect_hash01_index = (prev_pt0_state * pt1_state_max) + prev_pt1_state;
        unsigned char perfect_hash01_cost = hash_cost_to_cost(pt_perfect_hash01[perfect_hash01_index]);

        if (perfect_hash01_cost > result.cost_to_goal) {
            result.cost_to_goal = perfect_hash01_cost;
        }

        result.perfect_hash01_cost = perfect_hash01_cost;
    } else {
        result.perfect_hash01_cost = 0;
    }

    if (pt_perfect_hash02) {
        unsigned int perfect_hash02_index = (prev_pt0_state * pt2_state_max) + prev_pt2_state;
        unsigned char perfect_hash02_cost = hash_cost_to_cost(pt_perfect_hash02[perfect_hash02_index]);

        if (perfect_hash02_cost > result.cost_to_goal) {
            result.cost_to_goal = perfect_hash02_cost;
        }

        result.perfect_hash02_cost = perfect_hash02_cost;
    } else {
        result.perfect_hash02_cost = 0;
    }

    if (cost_to_goal_multiplier) {
        result.cost_to_goal = (unsigned char)round(result.cost_to_goal * cost_to_goal_multiplier);
    }

    return result;
}

void print_ida_summary(lookup_table_type type, unsigned int pt0_state, unsigned int pt1_state, unsigned int pt2_state,
                       unsigned int pt3_state, unsigned int pt4_state, move_type *solution,
                       unsigned char solution_len) {
    struct cost_to_goal_result ctg;
    unsigned char cost_to_goal = 0;
    unsigned char pt0_cost = 0;
    unsigned char pt1_cost = 0;
    unsigned char pt2_cost = 0;
    unsigned char pt3_cost = 0;
    unsigned char pt4_cost = 0;
    unsigned char steps_to_solved = solution_len;

    ctg = pt_states_to_cost(type, pt0_state, pt1_state, pt2_state, pt3_state, pt4_state);
    pt0_cost = ctg.pt0_cost;
    pt1_cost = ctg.pt1_cost;
    pt2_cost = ctg.pt2_cost;
    pt3_cost = ctg.pt3_cost;
    pt4_cost = ctg.pt4_cost;

    printf("\n");
    printf("       PT0  PT1  PT2  PT3  PT4  PER01  PER02  CTG  TRU  IDX\n");
    printf("       ===  ===  ===  ===  ===  =====  =====  ===  ===  ===\n");
    printf("  INIT %3d  %3d  %3d  %3d  %3d    %3d    %3d  %3d  %3d  %3d\n", pt0_cost, pt1_cost, pt2_cost, pt3_cost,
           pt4_cost, ctg.perfect_hash01_cost, ctg.perfect_hash02_cost, cost_to_goal, steps_to_solved, 0);

    for (unsigned char i = 0; i < solution_len; i++) {
        unsigned char j = 0;

        while (j < legal_move_count) {
            if (legal_moves[j] == solution[i]) {
                break;
            }
            j++;
        }
        unsigned int offset = COST_LENGTH + ((STATE_LENGTH + COST_LENGTH) * j);

        if (pt_max == 1) {
            pt1_state = read_state(pt1, (pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);

        } else if (pt_max == 2) {
            pt2_state = read_state(pt2, (pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);

        } else if (pt_max == 3) {
            pt3_state = read_state(pt3, (pt3_state * ROW_LENGTH) + offset);
            pt2_state = read_state(pt2, (pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);

        } else if (pt_max == 4) {
            pt4_state = read_state(pt4, (pt4_state * ROW_LENGTH) + offset);
            pt3_state = read_state(pt3, (pt3_state * ROW_LENGTH) + offset);
            pt2_state = read_state(pt2, (pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);

        } else {
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);
        }

        ctg = pt_states_to_cost(type, pt0_state, pt1_state, pt2_state, pt3_state, pt4_state);
        cost_to_goal = ctg.cost_to_goal;
        pt0_cost = ctg.pt0_cost;
        pt1_cost = ctg.pt1_cost;
        pt2_cost = ctg.pt2_cost;
        pt3_cost = ctg.pt3_cost;
        pt4_cost = ctg.pt4_cost;
        steps_to_solved--;
        printf("%5s  %3d  %3d  %3d  %3d  %3d  %5d  %5d  %3d  %3d  %3d\n", move2str[solution[i]], pt0_cost, pt1_cost,
               pt2_cost, pt3_cost, pt4_cost, ctg.perfect_hash01_cost, ctg.perfect_hash02_cost, cost_to_goal,
               steps_to_solved, i + 1);
    }
    printf("\n");
}

unsigned char parity_ok(move_type *moves_to_here) {
    unsigned int orbit0_wide_quarter_turn_count = 0;
    unsigned int orbit1_wide_quarter_turn_count = 0;

    if (orbit0_wide_quarter_turns) {
        orbit0_wide_quarter_turn_count = get_orbit0_wide_quarter_turn_count(moves_to_here);

        // orbit0 must have an odd number of wide quarter turns
        if (orbit0_wide_quarter_turns == 1) {
            if (orbit0_wide_quarter_turn_count % 2 == 0) {
                return 0;
            }

        // orbit0 must have an even number of wide quarter turns
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

        // orbit1 must have an odd number of wide quarter turns
        if (orbit1_wide_quarter_turns == 1) {
            if (orbit1_wide_quarter_turn_count % 2 == 0) {
                return 0;
            }

        // orbit1 must have an even number of wide quarter turns
        } else if (orbit1_wide_quarter_turns == 2) {
            if (orbit1_wide_quarter_turn_count % 2) {
                return 0;
            }

        } else {
            printf("ERROR: orbit1_wide_quarter_turns %d is not supported\n", orbit1_wide_quarter_turns);
            exit(1);
        }
    }

    return 1;
}

struct ida_search_result ida_search(lookup_table_type type, unsigned int init_pt0_state, unsigned int init_pt1_state,
                                    unsigned int init_pt2_state, unsigned int init_pt3_state,
                                    unsigned int init_pt4_state, unsigned char use_uthash) {
    struct ida_search_result search_result;
    unsigned char cost_to_goal = 0;
    unsigned char f_cost = 0;
    unsigned char offset[legal_move_count];
    unsigned char offset_i = 0;
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
    move_type move, moves_to_here[MAX_IDA_THRESHOLD];
    memset(moves_to_here, MOVE_NONE, sizeof(move_type) * MAX_IDA_THRESHOLD);
    search_result.found_solution = 0;
    char key[64];
    move_type *prev_move_move_matrix = NULL;

    struct cost_to_goal_result ctg =
        pt_states_to_cost(type, init_pt0_state, init_pt1_state, init_pt2_state, init_pt3_state, init_pt4_state);
    struct StackNode *root = NULL;
    struct StackNode *node = NULL;

    push(&root, 0, ctg.cost_to_goal, moves_to_here, MOVE_NONE, init_pt0_state, init_pt1_state, init_pt2_state,
         init_pt3_state, init_pt4_state);

    for (unsigned char i = 0; i < legal_move_count; i++) {
        offset[i] = COST_LENGTH + ((STATE_LENGTH + COST_LENGTH) * i);
    }

    while (root) {
        node = pop(&root);

        if (node->cost_to_goal == 0) {
            if (parity_ok(node->moves_to_here)) {
                // We found a solution!!
                solution_count++;
                f_cost = node->cost_to_here + node->cost_to_goal;

                if (!search_result.found_solution || f_cost < search_result.f_cost) {
                    search_result.f_cost = f_cost;
                    search_result.found_solution = 1;
                    memcpy(search_result.solution, node->moves_to_here, sizeof(move_type) * MAX_IDA_THRESHOLD);

                    LOG("IDA count %'llu, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n", ida_count,
                        search_result.f_cost, threshold, node->cost_to_here, node->cost_to_goal);
                }
                print_moves(node->moves_to_here, node->cost_to_here);

                if (solution_count >= min_solution_count) {
                    return search_result;
                }
            }

            free(node);
            continue;
        }

        // The following works, it does reduce the number of nodes we explore but it does so at the cost
        // of the memory to remember all of the nodes and the CPU to do the hash search to see if the
        // node is one that has already been explored.
        /*
        if (use_uthash) {
            // keep memory usage in check
            if (ida_count % 1000000 == 0) {
                hash_delete_all(&ida_explored);
            }

            sprintf(key, "%u-%u-%u-%u-%u-%u-%u-%u", node->pt0_state, node->pt1_state, node->pt2_state, node->pt3_state,
                    node->pt4_state,
                    orbit0_wide_quarter_turns ? get_orbit0_wide_quarter_turn_count(node->moves_to_here) : 0,
                    orbit1_wide_quarter_turns ? get_orbit1_wide_quarter_turn_count(node->moves_to_here) : 0,
                    node->cost_to_here);

            if (hash_find(&ida_explored, key)) {
                free(node);
                continue;
            }
            hash_add(&ida_explored, key, 0);
        }
        */

        memcpy(moves_to_here, node->moves_to_here, sizeof(move_type) * MAX_IDA_THRESHOLD);
        prev_move_move_matrix = move_matrix[node->prev_move];

        for (unsigned char i = 0; i < legal_move_count; i++) {
            move = prev_move_move_matrix[i];

            // This is the scenario where the move is on the same face and layer as prev_move
            if (move == MOVE_NONE) {
                continue;
            }

            offset_i = offset[i];

            switch (pt_max) {
                case 1:
                    pt0_state = read_state(pt0, (node->pt0_state * ROW_LENGTH) + offset_i);
                    pt0_cost = read_cost(pt0, (node->pt0_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt1_state = read_state(pt1, (node->pt1_state * ROW_LENGTH) + offset_i);
                    pt1_cost = read_cost(pt1, (node->pt1_state * ROW_LENGTH) + offset_i + STATE_LENGTH);
                    cost_to_goal = max(pt0_cost, pt1_cost);
                    break;

                case 3:
                    pt0_state = read_state(pt0, (node->pt0_state * ROW_LENGTH) + offset_i);
                    pt0_cost = read_cost(pt0, (node->pt0_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt1_state = read_state(pt1, (node->pt1_state * ROW_LENGTH) + offset_i);
                    pt1_cost = read_cost(pt1, (node->pt1_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt2_state = read_state(pt2, (node->pt2_state * ROW_LENGTH) + offset_i);
                    pt2_cost = read_cost(pt2, (node->pt2_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt3_state = read_state(pt3, (node->pt3_state * ROW_LENGTH) + offset_i);
                    pt3_cost = read_cost(pt3, (node->pt3_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    cost_to_goal = max(pt0_cost, pt1_cost);
                    cost_to_goal = max(cost_to_goal, pt2_cost);
                    cost_to_goal = max(cost_to_goal, pt3_cost);
                    break;

                case 2:
                    pt0_state = read_state(pt0, (node->pt0_state * ROW_LENGTH) + offset_i);
                    pt0_cost = read_cost(pt0, (node->pt0_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt1_state = read_state(pt1, (node->pt1_state * ROW_LENGTH) + offset_i);
                    pt1_cost = read_cost(pt1, (node->pt1_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt2_state = read_state(pt2, (node->pt2_state * ROW_LENGTH) + offset_i);
                    pt2_cost = read_cost(pt2, (node->pt2_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    cost_to_goal = max(pt0_cost, pt1_cost);
                    cost_to_goal = max(cost_to_goal, pt2_cost);
                    break;

                case 4:
                    pt0_state = read_state(pt0, (node->pt0_state * ROW_LENGTH) + offset_i);
                    pt0_cost = read_cost(pt0, (node->pt0_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt1_state = read_state(pt1, (node->pt1_state * ROW_LENGTH) + offset_i);
                    pt1_cost = read_cost(pt1, (node->pt1_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt2_state = read_state(pt2, (node->pt2_state * ROW_LENGTH) + offset_i);
                    pt2_cost = read_cost(pt2, (node->pt2_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt3_state = read_state(pt3, (node->pt3_state * ROW_LENGTH) + offset_i);
                    pt3_cost = read_cost(pt3, (node->pt3_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    pt4_state = read_state(pt4, (node->pt4_state * ROW_LENGTH) + offset_i);
                    pt4_cost = read_cost(pt4, (node->pt4_state * ROW_LENGTH) + offset_i + STATE_LENGTH);

                    cost_to_goal = max(pt0_cost, pt1_cost);
                    cost_to_goal = max(cost_to_goal, pt2_cost);
                    cost_to_goal = max(cost_to_goal, pt3_cost);
                    cost_to_goal = max(cost_to_goal, pt4_cost);
                    break;

                default:
                    printf("ERROR: invalid pt_max %d\n", pt_max);
                    exit(1);
            }

            if (call_pt_simple) {
                cost_to_goal = pt_states_to_cost_simple(type, pt0_state, pt1_state, pt2_state, pt3_state, pt4_state,
                                                        pt0_cost, pt1_cost, pt2_cost, pt3_cost, pt4_cost, cost_to_goal);
            }
            ida_count++;
            moves_to_here[node->cost_to_here] = move;

            if (node->cost_to_here + 1 + cost_to_goal <= threshold) {
                push(&root, node->cost_to_here + 1, cost_to_goal, moves_to_here, move, pt0_state, pt1_state, pt2_state,
                     pt3_state, pt4_state);
            }
        }
        free(node);
    }

    return search_result;
}

struct ida_search_result ida_solve(lookup_table_type type, unsigned int pt0_state, unsigned int pt1_state,
                                   unsigned int pt2_state, unsigned int pt3_state, unsigned int pt4_state,
                                   unsigned char max_ida_threshold, unsigned char use_uthash) {
    struct ida_search_result search_result;
    struct timeval stop, start, start_this_threshold;
    unsigned char min_ida_threshold = 0;
    unsigned char pt0_cost = 0;
    unsigned char pt1_cost = 0;
    unsigned char pt2_cost = 0;
    unsigned char pt3_cost = 0;
    unsigned char pt4_cost = 0;
    unsigned char cost_to_goal = 0;

    // For printing commas via %'d
    setlocale(LC_NUMERIC, "");

    struct cost_to_goal_result ctg = pt_states_to_cost(type, pt0_state, pt1_state, pt2_state, pt3_state, pt4_state);
    min_ida_threshold = ctg.cost_to_goal;
    search_result.found_solution = 0;

    if (min_ida_threshold >= max_ida_threshold) {
        // LOG("min_ida_threshold %d >= max_ida_threshold %d\n", min_ida_threshold, max_ida_threshold);
        return search_result;
    }

    LOG("pt0_state %d, pt1_state %d, pt2_state %d, pt3_state %d, pt4_state %d\n",
        pt0_state, pt1_state, pt2_state, pt3_state, pt4_state);

    gettimeofday(&start, NULL);

    for (threshold = min_ida_threshold; threshold <= max_ida_threshold; threshold++) {
        ida_count = 0;
        gettimeofday(&start_this_threshold, NULL);
        hash_delete_all(&ida_explored);

        search_result = ida_search(type, pt0_state, pt1_state, pt2_state, pt3_state, pt4_state, use_uthash);

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
            LOG("IDA found solution, explored %'llu total nodes, took %.3fs, %'d nodes-per-sec\n\n", ida_count_total,
                ms / 1000, nodes_per_sec);

            if (solution_count >= min_solution_count) {
                return search_result;
            }
        }
    }

    LOG("IDA failed with range %d->%d\n\n", min_ida_threshold, max_ida_threshold);
    return search_result;
}

char *read_file(char *filename) {
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

        // Read the entire file into memory. A 128M file take ~140ms to load.
        // LOG("%s fread begin\n", filename);
        size_t new_len = fread(buffer, sizeof(char), bufsize, fh);
        // LOG("%s fread end\n", filename);

        if (ferror(fh) != 0) {
            printf("ERROR: could not read %s\n", filename);
            exit(1);
        } else {
            buffer[new_len++] = '\0';  // Just to be safe.
        }
        // LOG("%s is %dM\n", filename, bufsize / (1024 * 1024));
    }

    fclose(fh);
    return buffer;
}

int main(int argc, char *argv[]) {
    unsigned long prune_table_0_state = 0;
    unsigned long prune_table_1_state = 0;
    unsigned long prune_table_2_state = 0;
    unsigned long prune_table_3_state = 0;
    unsigned long prune_table_4_state = 0;
    unsigned char max_ida_threshold = 30;
    unsigned char centers_only = 0;
    unsigned char use_uthash = 0;
    unsigned char find_extra = 0;
    char *prune_table_states_filename = NULL;
    lookup_table_type type = GENERIC;

    memset(legal_moves, MOVE_NONE, MOVE_MAX);
    memset(move_matrix, MOVE_NONE, MOVE_MAX * MOVE_MAX);

    for (unsigned char i = 1; i < argc; i++) {
        if (strmatch(argv[i], "-t") || strmatch(argv[i], "--type")) {
            i++;

            if (strmatch(argv[i], "5x5x5-centers-stage")) {
                type = CENTERS_STAGE_555;

            } else if (strmatch(argv[i], "5x5x5-lr-centers-stage")) {
                type = LR_CENTERS_STAGE_555;

            } else {
                printf("ERROR: %s is an invalid --type\n", argv[i]);
                exit(1);
            }

        } else if (strmatch(argv[i], "--prune-table-0-filename")) {
            i++;
            pt0 = read_file(argv[i]);
            pt_max = 0;

        } else if (strmatch(argv[i], "--prune-table-0-state")) {
            i++;
            prune_table_0_state = atoi(argv[i]);
            pt_max = 0;

        } else if (strmatch(argv[i], "--prune-table-1-filename")) {
            i++;
            pt1 = read_file(argv[i]);
            pt_max = 1;

        } else if (strmatch(argv[i], "--prune-table-1-state")) {
            i++;
            prune_table_1_state = atoi(argv[i]);
            pt_max = 1;

        } else if (strmatch(argv[i], "--prune-table-2-filename")) {
            i++;
            pt2 = read_file(argv[i]);
            pt_max = 2;

        } else if (strmatch(argv[i], "--prune-table-2-state")) {
            i++;
            prune_table_2_state = atoi(argv[i]);
            pt_max = 2;

        } else if (strmatch(argv[i], "--prune-table-3-filename")) {
            i++;
            pt3 = read_file(argv[i]);
            pt_max = 3;

        } else if (strmatch(argv[i], "--prune-table-3-state")) {
            i++;
            prune_table_3_state = atoi(argv[i]);
            pt_max = 3;

        } else if (strmatch(argv[i], "--prune-table-4-filename")) {
            i++;
            pt4 = read_file(argv[i]);
            pt_max = 4;

        } else if (strmatch(argv[i], "--prune-table-4-state")) {
            i++;
            prune_table_4_state = atoi(argv[i]);
            pt_max = 4;

        } else if (strmatch(argv[i], "--prune-table-perfect-hash01")) {
            i++;
            pt_perfect_hash01 = read_file(argv[i]);

        } else if (strmatch(argv[i], "--prune-table-perfect-hash02")) {
            i++;
            pt_perfect_hash02 = read_file(argv[i]);

        } else if (strmatch(argv[i], "--pt1-state-max")) {
            i++;
            pt1_state_max = atoi(argv[i]);

        } else if (strmatch(argv[i], "--pt2-state-max")) {
            i++;
            pt2_state_max = atoi(argv[i]);

        } else if (strmatch(argv[i], "--prune-table-states")) {
            i++;
            prune_table_states_filename = argv[i];

        } else if (strmatch(argv[i], "--multiplier")) {
            i++;
            cost_to_goal_multiplier = atof(argv[i]);

        } else if (strmatch(argv[i], "--solution-count")) {
            i++;
            min_solution_count = atoi(argv[i]);

        } else if (strmatch(argv[i], "--max-ida-threshold")) {
            i++;
            max_ida_threshold = atoi(argv[i]);

        } else if (strmatch(argv[i], "--centers-only")) {
            centers_only = 1;

            // } else if (strmatch(argv[i], "--uthash")) {
            //     use_uthash = 1;

        } else if (strmatch(argv[i], "--find-extra")) {
            find_extra = 1;

        } else if (strmatch(argv[i], "--orbit0-need-odd-w")) {
            orbit0_wide_quarter_turns = 1;

        } else if (strmatch(argv[i], "--orbit0-need-even-w")) {
            orbit0_wide_quarter_turns = 2;

        } else if (strmatch(argv[i], "--orbit1-need-odd-w")) {
            orbit1_wide_quarter_turns = 1;

        } else if (strmatch(argv[i], "--orbit1-need-even-w")) {
            orbit1_wide_quarter_turns = 2;

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
            printf("\nida_search --kociemba KOCIEMBA_STRING --type 5x5x5-UD-centers-stage\n\n");
            exit(0);

        } else {
            printf("ERROR: %s is an invalid arg\n\n", argv[i]);
            exit(1);
        }
    }

    if (type == LR_CENTERS_STAGE_555 || type == CENTERS_STAGE_555 || pt_perfect_hash01 || cost_to_goal_multiplier) {
        call_pt_simple = 1;
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

            } else if (!steps_on_same_face_in_order(i_move, j_move)) {
                move_matrix[i_move][j] = MOVE_NONE;

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

    ROW_LENGTH = COST_LENGTH + ((STATE_LENGTH + COST_LENGTH) * legal_move_count);
    struct ida_search_result search_result;
    search_result.found_solution = 0;
    search_result.f_cost = 99;

    if (prune_table_states_filename) {
        FILE *fh_read = NULL;
        char *line = NULL;
        size_t len = 0;
        ssize_t read = 0;
        unsigned int line_index = 0;
        struct ida_search_result min_search_result;
        min_search_result.found_solution = 0;
        min_search_result.f_cost = 99;

        for (unsigned char i_max_ida_threshold = 0; i_max_ida_threshold <= max_ida_threshold; i_max_ida_threshold++) {
            LOG("loop %d/%d\n", i_max_ida_threshold, max_ida_threshold);

            fh_read = fopen(prune_table_states_filename, "r");
            while ((read = getline(&line, &len, fh_read)) != -1) {
                // printf("%s", line);
                unsigned char token_index = 0;
                char *pt;
                pt = strtok(line, ",");

                while (pt != NULL) {
                    unsigned int token_value = atoi(pt);
                    pt = strtok(NULL, ",");

                    if (token_index == 0) {
                        prune_table_0_state = token_value;
                    } else if (token_index == 1) {
                        prune_table_1_state = token_value;
                    } else if (token_index == 2) {
                        prune_table_2_state = token_value;
                    } else if (token_index == 3) {
                        prune_table_3_state = token_value;
                    } else if (token_index == 4) {
                        prune_table_4_state = token_value;
                    }
                    token_index++;
                }

                search_result = ida_solve(type, prune_table_0_state, prune_table_1_state, prune_table_2_state,
                                          prune_table_3_state, prune_table_4_state, i_max_ida_threshold, use_uthash);

                if (search_result.found_solution && search_result.f_cost < min_search_result.f_cost) {
                    min_search_result = search_result;
                    // max_ida_threshold = search_result.f_cost;
                }

                line_index++;
            }
            fclose(fh_read);

            search_result = min_search_result;

            if (search_result.found_solution) {
                if (find_extra) {
                    if (solution_count >= min_solution_count) {
                        break;
                    }
                } else {
                    break;
                }
            }
        }

        if (line) {
            free(line);
        }

    } else {
        search_result = ida_solve(type, prune_table_0_state, prune_table_1_state, prune_table_2_state,
                                  prune_table_3_state, prune_table_4_state, max_ida_threshold, use_uthash);

        if (search_result.found_solution) {
            print_ida_summary(type, prune_table_0_state, prune_table_1_state, prune_table_2_state, prune_table_3_state,
                              prune_table_4_state, search_result.solution, search_result.f_cost);
        }
    }

    if (!search_result.found_solution) {
        exit(1);
    }
}
