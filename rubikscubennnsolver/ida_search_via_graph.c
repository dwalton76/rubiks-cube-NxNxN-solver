
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


unsigned long long ida_count = 0;
unsigned long long ida_count_total = 0;
struct key_value_pair *ida_explored = NULL;
unsigned char legal_move_count = 0;
unsigned char threshold = 0;
unsigned char find_multiple_solutions = 0;
unsigned char *pt0 = NULL;
unsigned char *pt1 = NULL;
unsigned char *pt2 = NULL;
unsigned char *pt3 = NULL;
unsigned char *pt4 = NULL;
unsigned char *pt_perfect_hash01 = NULL;
unsigned char *pt_perfect_hash02 = NULL;
unsigned int pt1_state_max = 0;
unsigned int pt2_state_max = 0;

unsigned char pt_max = 0;
unsigned char COST_LENGTH = 1;
unsigned char STATE_LENGTH = 4;
unsigned char ROW_LENGTH = 0;
unsigned char orbit0_wide_quarter_turns = 0;
unsigned char orbit1_wide_quarter_turns = 0;
float cost_to_goal_multiplier = 0.0;
move_type legal_moves[MOVE_MAX];
move_type move_matrix[MOVE_MAX][MOVE_MAX];
move_type same_face_and_layer_matrix[MOVE_MAX][MOVE_MAX];

struct ida_search_result {
    unsigned int f_cost;
    unsigned int found_solution;
    move_type solution[MOVE_MAX];
};

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


unsigned char dwalton[9][9][9][9] = {{{{2, 0, 7, 6, 4, 5, 7, 0, 0},
   {6, 1, 5, 3, 4, 6, 6, 11, 0},
   {5, 4, 2, 3, 4, 5, 6, 8, 0},
   {4, 3, 3, 3, 4, 5, 6, 7, 0},
   {5, 4, 4, 4, 4, 5, 7, 7, 0},
   {5, 5, 5, 5, 5, 5, 7, 8, 0},
   {6, 6, 6, 6, 7, 7, 7, 8, 0},
   {7, 7, 7, 7, 8, 9, 9, 10, 0},
   {9, 8, 13, 9, 10, 10, 13, 0, 0}},
  {{7, 9, 0, 0, 0, 9, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 7, 0, 0, 0, 0},
   {6, 8, 0, 0, 9, 0, 0, 0, 0},
   {0, 9, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 9, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{8, 0, 6, 0, 0, 0, 10, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {8, 0, 0, 0, 9, 0, 0, 0, 0},
   {6, 0, 8, 0, 10, 0, 0, 0, 0},
   {7, 7, 7, 0, 0, 8, 11, 0, 0},
   {9, 0, 12, 0, 0, 14, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{7, 0, 0, 6, 0, 0, 0, 0, 0},
   {0, 0, 7, 8, 6, 0, 9, 0, 0},
   {0, 0, 13, 8, 8, 7, 11, 0, 0},
   {7, 0, 0, 5, 5, 7, 8, 9, 0},
   {7, 0, 8, 7, 7, 8, 10, 10, 0},
   {10, 0, 14, 0, 9, 9, 9, 14, 0},
   {0, 0, 0, 0, 0, 13, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{4, 0, 0, 0, 4, 5, 7, 0, 0},
   {0, 7, 0, 5, 5, 5, 6, 0, 0},
   {12, 0, 4, 6, 4, 5, 6, 12, 0},
   {14, 0, 5, 5, 5, 5, 7, 7, 0},
   {8, 9, 7, 6, 6, 6, 7, 8, 0},
   {9, 11, 8, 9, 7, 8, 8, 8, 0},
   {0, 0, 12, 12, 9, 9, 8, 11, 0},
   {0, 0, 0, 0, 0, 11, 13, 14, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{5, 0, 0, 0, 5, 5, 6, 0, 0},
   {14, 5, 0, 5, 5, 5, 7, 12, 0},
   {13, 0, 6, 5, 5, 6, 7, 7, 0},
   {0, 11, 8, 5, 6, 6, 7, 9, 0},
   {0, 9, 8, 7, 7, 7, 8, 8, 0},
   {11, 16, 9, 9, 9, 8, 9, 10, 0},
   {0, 15, 10, 11, 9, 10, 10, 10, 0},
   {0, 0, 9, 0, 14, 14, 12, 16, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{6, 0, 0, 0, 10, 6, 6, 0, 0},
   {0, 6, 0, 13, 0, 7, 7, 13, 0},
   {0, 0, 7, 7, 8, 7, 9, 9, 0},
   {0, 0, 7, 6, 6, 7, 8, 10, 0},
   {15, 0, 7, 8, 8, 8, 9, 10, 0},
   {0, 0, 0, 11, 9, 9, 9, 11, 0},
   {0, 11, 12, 0, 12, 11, 11, 12, 0},
   {0, 0, 0, 0, 0, 15, 15, 15, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{11, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 15, 0, 0, 0, 12, 11, 0},
   {0, 0, 0, 15, 7, 10, 9, 14, 0},
   {0, 0, 0, 0, 13, 10, 8, 11, 0},
   {0, 0, 0, 0, 15, 9, 9, 16, 0},
   {0, 0, 0, 0, 0, 15, 16, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}}},
 {{{6, 0, 0, 16, 8, 0, 0, 0, 0},
   {6, 8, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 10, 11, 0, 0, 0, 0, 0},
   {0, 0, 8, 0, 8, 0, 0, 0, 0},
   {0, 0, 0, 0, 13, 13, 0, 0, 0},
   {0, 0, 11, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{1, 0, 0, 11, 6, 5, 7, 0, 0},
   {7, 1, 0, 3, 4, 5, 7, 10, 0},
   {6, 6, 2, 3, 4, 5, 7, 9, 0},
   {5, 5, 3, 3, 4, 5, 6, 8, 0},
   {6, 6, 4, 4, 4, 5, 6, 8, 0},
   {7, 7, 5, 5, 5, 5, 6, 8, 0},
   {7, 6, 6, 6, 7, 7, 7, 8, 0},
   {8, 8, 7, 7, 8, 8, 8, 8, 0},
   {0, 0, 11, 13, 9, 10, 12, 14, 0}},
  {{5, 8, 10, 0, 0, 0, 0, 0, 0},
   {0, 0, 5, 0, 0, 0, 13, 0, 0},
   {0, 0, 5, 8, 11, 7, 0, 0, 0},
   {0, 0, 6, 7, 7, 6, 7, 0, 0},
   {0, 5, 8, 0, 6, 6, 9, 10, 0},
   {0, 6, 6, 0, 6, 8, 7, 16, 0},
   {0, 0, 0, 8, 8, 8, 8, 13, 0},
   {0, 0, 0, 0, 15, 8, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{3, 0, 9, 0, 5, 5, 13, 0, 0},
   {0, 3, 0, 3, 5, 5, 6, 9, 0},
   {0, 0, 5, 5, 4, 5, 6, 7, 0},
   {11, 5, 7, 3, 4, 5, 6, 8, 0},
   {0, 6, 6, 5, 4, 5, 6, 8, 0},
   {0, 5, 5, 6, 5, 5, 7, 8, 0},
   {0, 7, 6, 7, 7, 7, 7, 9, 0},
   {11, 10, 8, 10, 9, 9, 9, 9, 0},
   {0, 10, 0, 0, 0, 0, 0, 0, 0}},
  {{4, 0, 0, 6, 5, 5, 7, 0, 0},
   {0, 4, 0, 5, 4, 5, 8, 0, 0},
   {0, 7, 4, 5, 4, 5, 7, 0, 0},
   {7, 7, 5, 4, 4, 5, 6, 8, 0},
   {6, 6, 6, 6, 4, 5, 7, 8, 11},
   {15, 7, 5, 5, 6, 6, 7, 8, 0},
   {0, 8, 7, 6, 6, 7, 7, 8, 0},
   {0, 8, 7, 11, 9, 8, 10, 13, 0},
   {0, 0, 0, 8, 0, 0, 0, 0, 0}},
  {{6, 0, 0, 0, 5, 5, 7, 0, 0},
   {0, 5, 0, 5, 5, 6, 7, 0, 0},
   {11, 11, 5, 5, 5, 6, 7, 7, 0},
   {10, 5, 6, 5, 5, 5, 7, 9, 0},
   {0, 6, 7, 5, 5, 5, 7, 9, 0},
   {0, 7, 5, 7, 6, 7, 8, 8, 0},
   {0, 10, 10, 12, 8, 8, 9, 9, 0},
   {0, 0, 11, 13, 15, 9, 9, 11, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{6, 0, 0, 14, 7, 7, 7, 0, 0},
   {0, 7, 0, 6, 6, 6, 6, 0, 0},
   {0, 15, 6, 6, 7, 7, 7, 10, 0},
   {0, 11, 8, 6, 6, 7, 8, 9, 0},
   {0, 15, 7, 7, 7, 7, 8, 9, 0},
   {0, 14, 10, 7, 8, 8, 8, 10, 0},
   {0, 12, 11, 11, 11, 9, 10, 11, 0},
   {0, 0, 0, 0, 13, 11, 10, 12, 0},
   {0, 0, 0, 0, 16, 15, 16, 0, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 16, 0, 0, 10, 11, 10, 0, 0},
   {0, 0, 7, 0, 13, 11, 11, 12, 0},
   {0, 0, 0, 7, 8, 9, 8, 12, 0},
   {0, 0, 0, 8, 9, 9, 9, 8, 0},
   {0, 0, 0, 11, 9, 12, 9, 10, 0},
   {0, 0, 0, 0, 12, 13, 9, 11, 0},
   {0, 0, 0, 0, 0, 0, 15, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}}},
 {{{5, 0, 0, 12, 14, 7, 0, 0, 0},
   {0, 6, 0, 0, 0, 0, 0, 0, 0},
   {5, 6, 7, 7, 8, 9, 0, 0, 0},
   {7, 8, 6, 7, 7, 8, 12, 0, 0},
   {0, 6, 6, 7, 8, 9, 10, 0, 0},
   {13, 6, 7, 9, 8, 8, 11, 0, 0},
   {0, 9, 7, 7, 10, 14, 16, 0, 0},
   {0, 0, 0, 13, 10, 15, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{4, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 6, 0, 0, 12, 6, 12, 0, 0},
   {6, 4, 0, 7, 5, 8, 8, 10, 0},
   {0, 13, 7, 6, 6, 6, 6, 14, 0},
   {0, 12, 6, 6, 5, 6, 6, 7, 0},
   {0, 0, 7, 7, 5, 6, 7, 8, 0},
   {0, 0, 6, 8, 7, 7, 8, 11, 0},
   {0, 0, 8, 0, 8, 11, 10, 14, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{2, 0, 7, 8, 4, 7, 7, 0, 0},
   {7, 2, 5, 5, 4, 5, 6, 10, 0},
   {8, 7, 2, 3, 4, 5, 6, 8, 0},
   {7, 3, 3, 3, 4, 5, 6, 8, 0},
   {7, 4, 4, 4, 4, 5, 6, 8, 0},
   {7, 5, 5, 5, 5, 5, 6, 8, 0},
   {6, 6, 6, 6, 6, 7, 7, 8, 0},
   {9, 7, 7, 7, 7, 8, 8, 9, 0},
   {0, 12, 8, 11, 10, 12, 9, 11, 0}},
  {{3, 0, 0, 7, 6, 5, 8, 0, 0},
   {0, 3, 8, 5, 5, 5, 6, 0, 0},
   {12, 9, 3, 3, 4, 5, 6, 8, 0},
   {6, 5, 5, 3, 4, 5, 6, 8, 0},
   {7, 6, 4, 4, 4, 5, 6, 8, 0},
   {8, 5, 5, 5, 5, 5, 6, 8, 0},
   {6, 6, 6, 6, 7, 7, 7, 8, 9},
   {9, 8, 7, 7, 8, 8, 8, 8, 0},
   {0, 10, 9, 8, 0, 14, 9, 0, 0}},
  {{4, 0, 9, 10, 4, 5, 6, 0, 0},
   {0, 4, 6, 4, 4, 5, 6, 9, 0},
   {0, 5, 4, 4, 4, 5, 6, 9, 0},
   {6, 5, 5, 4, 4, 5, 6, 8, 0},
   {8, 6, 5, 4, 4, 5, 6, 8, 0},
   {11, 6, 5, 5, 5, 5, 7, 8, 11},
   {7, 6, 6, 6, 7, 7, 7, 8, 14},
   {11, 8, 8, 9, 9, 9, 9, 9, 0},
   {0, 11, 8, 10, 13, 12, 11, 13, 0}},
  {{5, 0, 0, 8, 5, 6, 6, 11, 0},
   {0, 5, 8, 5, 5, 6, 6, 0, 0},
   {12, 6, 5, 5, 5, 5, 6, 8, 0},
   {0, 6, 5, 5, 5, 5, 7, 8, 0},
   {13, 7, 6, 6, 5, 5, 7, 8, 14},
   {11, 8, 5, 6, 5, 5, 7, 8, 11},
   {10, 8, 7, 7, 7, 7, 8, 9, 0},
   {15, 0, 9, 9, 9, 9, 10, 10, 14},
   {0, 0, 0, 0, 13, 15, 11, 12, 0}},
  {{6, 0, 0, 7, 6, 7, 7, 12, 0},
   {0, 6, 0, 6, 6, 7, 7, 11, 0},
   {0, 7, 6, 6, 6, 7, 7, 9, 0},
   {0, 6, 7, 6, 7, 7, 7, 8, 0},
   {13, 8, 8, 7, 7, 7, 7, 9, 0},
   {11, 10, 7, 8, 7, 7, 7, 9, 11},
   {0, 10, 8, 8, 9, 8, 8, 9, 9},
   {0, 10, 8, 11, 11, 10, 10, 9, 0},
   {0, 0, 0, 0, 0, 14, 13, 16, 0}},
  {{8, 0, 0, 0, 11, 9, 10, 16, 0},
   {0, 8, 0, 7, 8, 7, 11, 0, 0},
   {0, 0, 8, 8, 8, 9, 8, 7, 0},
   {0, 0, 9, 8, 7, 8, 8, 9, 0},
   {0, 0, 12, 8, 8, 8, 9, 9, 0},
   {0, 0, 7, 9, 9, 9, 9, 10, 14},
   {0, 0, 10, 10, 11, 9, 10, 9, 0},
   {0, 0, 11, 12, 10, 10, 10, 12, 0},
   {0, 0, 0, 0, 15, 0, 11, 12, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 11, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 9, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 10, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}}},
 {{{4, 6, 6, 7, 8, 9, 0, 0, 0},
   {0, 5, 0, 0, 0, 0, 0, 0, 0},
   {0, 10, 7, 6, 7, 12, 0, 0, 0},
   {4, 5, 5, 8, 7, 8, 8, 0, 0},
   {8, 5, 5, 7, 8, 9, 8, 0, 0},
   {11, 6, 6, 7, 8, 9, 8, 16, 0},
   {9, 8, 7, 7, 9, 11, 11, 14, 0},
   {7, 9, 8, 7, 11, 10, 15, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{3, 6, 0, 10, 15, 8, 0, 0, 0},
   {0, 5, 9, 5, 7, 6, 8, 13, 0},
   {7, 7, 3, 5, 6, 6, 6, 0, 0},
   {5, 3, 4, 3, 6, 6, 7, 7, 0},
   {10, 5, 4, 5, 6, 6, 8, 11, 0},
   {5, 5, 5, 5, 6, 7, 8, 11, 0},
   {6, 8, 6, 6, 6, 7, 9, 10, 0},
   {7, 7, 7, 7, 9, 8, 11, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}},
  {{3, 0, 6, 0, 5, 8, 0, 0, 0},
   {11, 3, 6, 6, 5, 6, 8, 0, 0},
   {6, 10, 3, 5, 5, 5, 6, 7, 0},
   {6, 4, 3, 3, 4, 5, 7, 7, 0},
   {4, 4, 4, 4, 4, 5, 7, 8, 0},
   {5, 5, 5, 5, 5, 5, 7, 8, 0},
   {6, 6, 6, 6, 6, 6, 7, 8, 10},
   {7, 7, 7, 7, 7, 8, 8, 9, 0},
   {12, 0, 8, 8, 12, 10, 11, 0, 0}},
  {{3, 0, 8, 7, 5, 5, 7, 0, 0},
   {10, 3, 7, 3, 4, 5, 6, 7, 0},
   {7, 6, 3, 3, 4, 5, 6, 7, 0},
   {8, 3, 3, 3, 4, 5, 6, 7, 0},
   {8, 6, 4, 4, 4, 5, 6, 8, 0},
   {8, 5, 5, 5, 5, 5, 6, 8, 0},
   {6, 6, 6, 6, 6, 7, 7, 8, 12},
   {10, 7, 7, 7, 7, 8, 9, 9, 0},
   {12, 0, 8, 8, 9, 10, 10, 14, 0}},
  {{4, 0, 13, 5, 5, 6, 6, 10, 0},
   {11, 4, 7, 4, 4, 5, 6, 9, 0},
   {7, 6, 4, 4, 4, 5, 7, 8, 10},
   {9, 6, 4, 4, 4, 5, 6, 8, 0},
   {8, 6, 4, 4, 4, 5, 7, 8, 9},
   {9, 6, 5, 5, 5, 5, 7, 8, 10},
   {8, 6, 6, 6, 7, 7, 7, 8, 8},
   {7, 7, 7, 8, 8, 8, 9, 9, 10},
   {12, 9, 8, 9, 8, 9, 12, 14, 0}},
  {{5, 0, 14, 8, 5, 6, 7, 13, 0},
   {0, 5, 7, 5, 5, 5, 7, 10, 0},
   {10, 6, 5, 5, 5, 5, 7, 8, 0},
   {9, 6, 5, 5, 5, 5, 7, 8, 8},
   {11, 7, 6, 6, 5, 5, 7, 8, 8},
   {8, 8, 5, 6, 5, 5, 7, 8, 8},
   {10, 8, 6, 7, 7, 7, 8, 9, 9},
   {11, 9, 8, 9, 9, 9, 9, 9, 10},
   {16, 0, 10, 11, 12, 10, 11, 9, 0}},
  {{6, 0, 15, 8, 7, 8, 8, 12, 0},
   {0, 6, 9, 6, 6, 7, 7, 9, 0},
   {0, 6, 6, 6, 7, 7, 7, 9, 0},
   {8, 7, 7, 6, 6, 7, 7, 9, 12},
   {12, 9, 8, 7, 6, 7, 7, 9, 12},
   {10, 8, 8, 8, 7, 7, 7, 9, 10},
   {12, 9, 7, 8, 8, 8, 8, 9, 11},
   {13, 11, 9, 9, 9, 10, 10, 10, 11},
   {0, 0, 14, 11, 13, 12, 10, 9, 0}},
  {{7, 0, 0, 13, 7, 9, 8, 14, 0},
   {0, 8, 9, 7, 7, 10, 9, 12, 0},
   {0, 0, 8, 7, 8, 8, 9, 9, 0},
   {0, 9, 8, 7, 8, 8, 9, 8, 0},
   {0, 14, 9, 8, 8, 8, 9, 9, 11},
   {0, 0, 10, 10, 9, 9, 9, 9, 0},
   {0, 10, 9, 11, 10, 9, 9, 9, 12},
   {0, 0, 11, 9, 10, 10, 11, 11, 10},
   {0, 0, 0, 0, 0, 14, 11, 12, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 9, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 13, 9, 16, 0},
   {0, 0, 0, 0, 0, 10, 9, 12, 0},
   {0, 0, 0, 0, 0, 9, 12, 11, 0},
   {0, 0, 0, 0, 0, 12, 12, 12, 0},
   {0, 0, 0, 0, 0, 0, 15, 13, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}}},
 {{{5, 7, 7, 8, 9, 0, 0, 0, 0},
   {7, 6, 0, 10, 8, 0, 0, 0, 0},
   {8, 0, 7, 6, 8, 12, 10, 0, 0},
   {6, 12, 4, 8, 8, 13, 9, 0, 0},
   {5, 6, 4, 8, 9, 10, 10, 12, 0},
   {6, 6, 5, 8, 9, 10, 11, 0, 0},
   {6, 6, 6, 7, 8, 11, 12, 12, 0},
   {8, 7, 9, 8, 9, 11, 13, 0, 0},
   {0, 13, 0, 13, 0, 14, 0, 0, 0}},
  {{4, 0, 7, 9, 8, 13, 0, 0, 0},
   {0, 6, 5, 6, 6, 7, 11, 0, 0},
   {7, 0, 4, 6, 5, 7, 7, 0, 0},
   {6, 5, 4, 6, 6, 7, 8, 15, 0},
   {6, 4, 4, 4, 7, 7, 8, 10, 0},
   {6, 5, 5, 5, 6, 8, 8, 13, 0},
   {6, 8, 6, 6, 6, 7, 9, 11, 0},
   {8, 8, 7, 7, 8, 8, 9, 11, 0},
   {8, 0, 0, 0, 11, 0, 13, 0, 0}},
  {{4, 0, 7, 8, 6, 8, 8, 12, 0},
   {0, 4, 7, 6, 6, 7, 10, 0, 0},
   {6, 6, 4, 4, 5, 6, 8, 10, 0},
   {5, 4, 4, 4, 4, 6, 8, 10, 0},
   {4, 4, 4, 4, 4, 7, 8, 10, 0},
   {5, 5, 5, 5, 5, 6, 8, 9, 0},
   {6, 6, 6, 6, 6, 7, 8, 9, 16},
   {8, 7, 7, 7, 7, 8, 8, 9, 11},
   {9, 8, 11, 10, 15, 9, 10, 16, 0}},
  {{4, 8, 0, 7, 5, 7, 9, 0, 0},
   {7, 4, 10, 5, 6, 6, 8, 0, 0},
   {8, 7, 4, 4, 4, 6, 7, 9, 0},
   {7, 5, 4, 4, 4, 6, 7, 8, 0},
   {9, 4, 4, 4, 4, 6, 7, 8, 0},
   {7, 5, 5, 5, 5, 6, 7, 8, 12},
   {6, 6, 6, 6, 6, 7, 8, 8, 0},
   {8, 7, 7, 7, 8, 8, 9, 9, 0},
   {9, 15, 11, 9, 10, 10, 10, 0, 0}},
  {{4, 8, 10, 7, 6, 6, 8, 9, 0},
   {0, 4, 6, 4, 4, 5, 7, 9, 0},
   {8, 5, 4, 4, 4, 5, 6, 8, 0},
   {8, 6, 4, 4, 4, 5, 6, 8, 0},
   {9, 7, 4, 4, 4, 5, 6, 8, 10},
   {9, 6, 5, 5, 5, 5, 7, 8, 9},
   {8, 6, 6, 6, 6, 7, 7, 8, 10},
   {8, 7, 7, 7, 8, 8, 9, 9, 9},
   {14, 11, 9, 8, 8, 9, 11, 11, 0}},
  {{5, 0, 8, 9, 6, 7, 8, 13, 0},
   {10, 5, 7, 5, 5, 5, 7, 7, 0},
   {7, 6, 5, 5, 5, 5, 7, 9, 0},
   {9, 6, 5, 5, 5, 5, 7, 8, 0},
   {11, 7, 7, 6, 5, 5, 7, 8, 8},
   {10, 8, 5, 6, 6, 5, 7, 8, 9},
   {10, 8, 7, 7, 7, 7, 8, 9, 10},
   {10, 8, 8, 8, 8, 9, 9, 10, 10},
   {0, 9, 9, 9, 10, 10, 10, 11, 0}},
  {{6, 0, 0, 9, 7, 8, 8, 11, 15},
   {0, 6, 9, 6, 7, 7, 7, 8, 0},
   {0, 7, 6, 6, 6, 7, 7, 9, 0},
   {8, 7, 7, 6, 7, 7, 7, 9, 8},
   {11, 9, 8, 7, 7, 7, 7, 9, 12},
   {11, 9, 8, 8, 7, 7, 7, 9, 11},
   {9, 10, 8, 9, 8, 8, 8, 9, 11},
   {12, 9, 8, 9, 9, 9, 10, 10, 9},
   {14, 11, 11, 10, 12, 10, 11, 11, 0}},
  {{8, 0, 0, 14, 8, 10, 10, 9, 0},
   {0, 8, 14, 8, 8, 9, 8, 9, 0},
   {0, 8, 8, 8, 8, 9, 9, 9, 0},
   {0, 9, 8, 8, 8, 8, 9, 9, 0},
   {0, 15, 8, 8, 8, 8, 9, 9, 11},
   {0, 10, 10, 9, 9, 8, 9, 9, 11},
   {15, 9, 9, 10, 9, 9, 9, 10, 12},
   {0, 0, 11, 11, 10, 10, 10, 10, 12},
   {0, 0, 0, 0, 12, 12, 12, 12, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 14, 15, 0, 0},
   {0, 0, 0, 0, 8, 10, 10, 14, 0},
   {0, 0, 0, 0, 11, 11, 9, 11, 0},
   {0, 0, 0, 0, 10, 8, 10, 10, 0},
   {0, 0, 0, 0, 16, 11, 11, 11, 14},
   {0, 0, 0, 0, 0, 0, 12, 13, 0},
   {0, 0, 0, 0, 0, 0, 14, 0, 0}}},
 {{{5, 8, 8, 9, 11, 13, 0, 0, 0},
   {0, 6, 16, 13, 0, 0, 0, 0, 0},
   {0, 0, 7, 7, 9, 0, 0, 0, 0},
   {0, 5, 5, 7, 8, 9, 10, 0, 0},
   {0, 5, 5, 6, 9, 10, 11, 11, 0},
   {5, 5, 6, 8, 9, 9, 9, 0, 0},
   {7, 6, 7, 8, 9, 10, 11, 0, 0},
   {8, 9, 9, 8, 10, 11, 12, 13, 0},
   {0, 10, 12, 0, 12, 0, 0, 0, 0}},
  {{5, 0, 0, 6, 11, 8, 0, 0, 0},
   {0, 6, 7, 5, 6, 7, 0, 0, 0},
   {9, 0, 5, 5, 7, 9, 10, 0, 0},
   {6, 5, 5, 5, 6, 8, 8, 11, 0},
   {5, 5, 5, 5, 7, 8, 9, 9, 0},
   {5, 5, 5, 5, 7, 7, 9, 10, 0},
   {7, 7, 6, 6, 7, 7, 9, 8, 0},
   {9, 7, 7, 8, 8, 9, 9, 0, 0},
   {0, 0, 8, 8, 10, 10, 16, 0, 0}},
  {{5, 0, 0, 11, 9, 7, 13, 0, 0},
   {0, 5, 10, 5, 5, 6, 10, 0, 0},
   {7, 9, 5, 5, 5, 5, 6, 8, 0},
   {6, 5, 5, 5, 5, 5, 8, 9, 0},
   {5, 5, 5, 5, 5, 5, 8, 9, 0},
   {6, 5, 5, 5, 5, 7, 8, 10, 13},
   {6, 6, 6, 6, 6, 7, 8, 9, 0},
   {9, 8, 8, 7, 8, 8, 9, 9, 12},
   {14, 16, 9, 9, 11, 8, 8, 11, 0}},
  {{5, 0, 0, 8, 9, 8, 12, 0, 0},
   {0, 5, 8, 6, 6, 9, 9, 13, 0},
   {9, 6, 5, 5, 5, 5, 8, 10, 0},
   {8, 5, 5, 5, 5, 6, 8, 9, 0},
   {7, 5, 5, 5, 5, 6, 8, 9, 0},
   {8, 5, 5, 5, 5, 6, 8, 9, 0},
   {7, 6, 6, 6, 6, 7, 8, 9, 0},
   {8, 7, 7, 7, 8, 8, 9, 10, 0},
   {0, 9, 8, 8, 8, 9, 10, 11, 0}},
  {{5, 0, 9, 12, 6, 8, 12, 0, 0},
   {12, 5, 7, 5, 6, 7, 8, 0, 0},
   {9, 5, 5, 5, 5, 5, 8, 8, 0},
   {8, 6, 5, 5, 5, 5, 7, 9, 0},
   {9, 5, 5, 5, 5, 6, 7, 9, 9},
   {8, 7, 5, 5, 5, 6, 8, 9, 10},
   {9, 6, 6, 6, 6, 7, 8, 9, 10},
   {8, 8, 8, 8, 8, 8, 9, 10, 9},
   {12, 15, 8, 8, 9, 11, 11, 11, 0}},
  {{5, 12, 10, 8, 8, 8, 9, 11, 0},
   {14, 5, 7, 5, 6, 7, 8, 8, 0},
   {9, 6, 5, 5, 5, 5, 7, 8, 13},
   {9, 7, 5, 5, 5, 5, 7, 8, 0},
   {10, 7, 6, 6, 5, 5, 7, 9, 12},
   {11, 8, 7, 6, 6, 5, 7, 9, 10},
   {10, 8, 7, 7, 7, 7, 8, 9, 11},
   {11, 8, 8, 8, 8, 9, 9, 10, 11},
   {0, 8, 9, 9, 10, 11, 11, 11, 0}},
  {{7, 0, 11, 10, 8, 9, 10, 13, 0},
   {13, 6, 10, 7, 7, 8, 8, 10, 0},
   {15, 7, 6, 6, 7, 7, 7, 9, 0},
   {11, 8, 7, 6, 7, 7, 7, 9, 13},
   {9, 9, 7, 7, 7, 7, 7, 9, 10},
   {12, 9, 8, 8, 8, 7, 8, 9, 11},
   {10, 10, 8, 9, 9, 9, 9, 10, 11},
   {11, 10, 9, 9, 10, 10, 10, 10, 12},
   {12, 15, 11, 11, 11, 11, 11, 12, 15}},
  {{8, 0, 0, 9, 8, 9, 10, 12, 0},
   {0, 8, 12, 8, 8, 9, 9, 10, 0},
   {0, 12, 8, 8, 8, 8, 9, 9, 0},
   {0, 7, 8, 8, 8, 9, 9, 9, 14},
   {16, 11, 8, 8, 8, 8, 9, 9, 11},
   {14, 11, 8, 9, 9, 9, 9, 10, 10},
   {0, 11, 10, 10, 10, 10, 10, 10, 10},
   {0, 10, 10, 11, 11, 11, 11, 11, 11},
   {0, 0, 16, 0, 15, 12, 11, 11, 16}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 15, 0, 0, 0},
   {0, 0, 0, 0, 15, 12, 12, 0, 0},
   {0, 0, 11, 10, 10, 9, 10, 14, 0},
   {0, 0, 0, 0, 12, 10, 11, 10, 0},
   {0, 0, 0, 14, 9, 10, 11, 11, 0},
   {0, 0, 14, 10, 9, 10, 11, 11, 15},
   {0, 0, 0, 0, 0, 13, 11, 11, 0},
   {0, 0, 0, 0, 0, 0, 0, 12, 14}}},
 {{{6, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 6, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 6, 7, 9, 16, 0, 0, 0},
   {8, 6, 6, 7, 9, 9, 11, 0, 0},
   {6, 6, 6, 6, 8, 11, 12, 15, 0},
   {7, 7, 6, 7, 9, 10, 11, 13, 0},
   {6, 6, 6, 8, 9, 10, 11, 0, 0},
   {8, 7, 8, 8, 9, 11, 11, 13, 0},
   {9, 13, 9, 11, 14, 15, 14, 0, 0}},
  {{6, 0, 0, 0, 0, 0, 0, 0, 0},
   {10, 6, 10, 7, 9, 10, 10, 0, 0},
   {8, 0, 6, 6, 7, 9, 14, 0, 0},
   {7, 6, 6, 6, 6, 8, 10, 0, 0},
   {7, 8, 6, 6, 6, 8, 9, 10, 0},
   {7, 6, 6, 6, 6, 8, 9, 12, 0},
   {6, 6, 6, 7, 7, 9, 10, 10, 0},
   {9, 7, 7, 7, 8, 9, 10, 12, 0},
   {10, 13, 9, 10, 8, 10, 12, 0, 0}},
  {{6, 0, 0, 0, 7, 9, 0, 0, 0},
   {0, 6, 9, 6, 7, 12, 8, 0, 0},
   {8, 7, 6, 6, 6, 7, 8, 14, 0},
   {7, 6, 6, 6, 6, 6, 7, 10, 0},
   {7, 6, 6, 6, 6, 7, 8, 9, 0},
   {7, 6, 6, 6, 6, 7, 8, 10, 0},
   {7, 6, 6, 6, 7, 8, 9, 10, 14},
   {8, 7, 8, 7, 8, 9, 10, 10, 0},
   {10, 13, 9, 11, 13, 9, 9, 11, 0}},
  {{6, 0, 0, 0, 11, 0, 14, 0, 0},
   {0, 6, 0, 6, 8, 9, 12, 9, 0},
   {11, 7, 6, 6, 6, 7, 9, 14, 0},
   {8, 7, 6, 6, 6, 7, 8, 10, 0},
   {7, 6, 6, 6, 6, 7, 9, 10, 0},
   {7, 6, 6, 6, 6, 7, 9, 10, 0},
   {8, 7, 6, 6, 7, 8, 9, 10, 0},
   {8, 8, 7, 8, 8, 9, 10, 11, 0},
   {0, 11, 8, 10, 8, 9, 10, 10, 0}},
  {{7, 0, 0, 14, 10, 11, 9, 0, 0},
   {0, 7, 13, 6, 7, 8, 10, 0, 0},
   {8, 8, 6, 7, 7, 7, 8, 9, 0},
   {9, 6, 6, 6, 7, 7, 8, 10, 0},
   {9, 6, 6, 6, 6, 7, 8, 10, 0},
   {8, 7, 6, 6, 6, 7, 9, 10, 11},
   {9, 7, 7, 7, 7, 8, 9, 10, 12},
   {10, 8, 8, 8, 8, 9, 10, 11, 11},
   {13, 8, 8, 8, 9, 10, 11, 11, 11}},
  {{7, 0, 13, 15, 8, 10, 11, 0, 0},
   {0, 7, 6, 7, 7, 8, 10, 10, 0},
   {10, 7, 7, 7, 7, 8, 8, 9, 15},
   {10, 7, 6, 7, 7, 7, 8, 9, 15},
   {9, 7, 7, 7, 7, 7, 8, 9, 12},
   {10, 8, 7, 7, 7, 7, 9, 10, 11},
   {10, 9, 8, 8, 8, 8, 9, 10, 11},
   {11, 9, 9, 9, 9, 9, 10, 11, 10},
   {10, 9, 9, 10, 10, 11, 11, 11, 0}},
  {{7, 16, 0, 10, 8, 10, 11, 13, 0},
   {0, 7, 8, 7, 8, 9, 10, 10, 0},
   {11, 8, 7, 7, 7, 8, 8, 9, 0},
   {11, 9, 7, 7, 7, 8, 8, 9, 10},
   {11, 9, 8, 8, 7, 8, 8, 9, 11},
   {12, 9, 8, 8, 8, 8, 9, 10, 11},
   {11, 10, 9, 9, 9, 9, 9, 10, 11},
   {10, 10, 10, 10, 10, 10, 11, 11, 11},
   {0, 12, 10, 10, 10, 11, 12, 12, 13}},
  {{8, 0, 0, 0, 9, 10, 11, 13, 0},
   {0, 8, 0, 8, 8, 9, 11, 7, 0},
   {0, 0, 8, 8, 8, 9, 9, 10, 0},
   {0, 10, 8, 8, 8, 9, 9, 10, 11},
   {0, 10, 9, 9, 8, 9, 9, 10, 11},
   {16, 11, 9, 9, 9, 9, 10, 10, 11},
   {15, 11, 10, 10, 10, 10, 10, 11, 11},
   {0, 11, 10, 11, 11, 11, 11, 11, 12},
   {0, 15, 14, 14, 12, 12, 12, 12, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 12, 0, 0},
   {0, 0, 0, 0, 15, 0, 11, 16, 0},
   {0, 0, 0, 12, 8, 9, 12, 12, 0},
   {0, 0, 0, 12, 10, 10, 10, 12, 0},
   {0, 0, 8, 0, 9, 10, 10, 11, 0},
   {0, 0, 0, 11, 11, 11, 11, 11, 16},
   {0, 0, 15, 13, 15, 11, 12, 11, 15},
   {0, 0, 0, 0, 0, 0, 15, 14, 0}}},
 {{{8, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 8, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 9, 8, 11, 0, 0, 0, 0},
   {0, 7, 7, 8, 7, 11, 14, 16, 0},
   {8, 0, 7, 8, 8, 9, 13, 16, 0},
   {7, 7, 7, 8, 9, 11, 12, 0, 0},
   {8, 9, 8, 8, 11, 11, 12, 0, 0},
   {7, 7, 8, 9, 10, 11, 11, 14, 0},
   {0, 12, 11, 16, 14, 12, 16, 0, 0}},
  {{7, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 8, 0, 8, 14, 0, 0, 0, 0},
   {0, 0, 7, 7, 9, 9, 12, 0, 0},
   {9, 7, 7, 7, 8, 8, 11, 0, 0},
   {8, 10, 7, 8, 8, 8, 10, 15, 0},
   {8, 7, 7, 7, 8, 8, 10, 14, 0},
   {9, 7, 7, 8, 8, 9, 10, 9, 0},
   {8, 7, 7, 8, 9, 10, 10, 11, 0},
   {9, 0, 12, 8, 13, 11, 15, 0, 0}},
  {{7, 0, 0, 0, 0, 0, 0, 0, 0},
   {12, 7, 0, 7, 13, 12, 14, 0, 0},
   {11, 0, 7, 7, 7, 7, 9, 12, 0},
   {8, 7, 7, 7, 7, 8, 8, 8, 0},
   {8, 8, 7, 7, 7, 8, 8, 10, 0},
   {8, 8, 7, 7, 8, 8, 9, 10, 0},
   {8, 7, 7, 7, 8, 9, 9, 10, 16},
   {8, 7, 7, 8, 8, 9, 10, 11, 13},
   {12, 16, 8, 10, 11, 10, 12, 16, 0}},
  {{8, 0, 0, 0, 0, 11, 0, 0, 0},
   {16, 7, 0, 8, 16, 0, 12, 0, 0},
   {15, 0, 7, 7, 7, 8, 11, 11, 0},
   {8, 7, 7, 7, 8, 8, 10, 11, 0},
   {7, 8, 7, 7, 7, 8, 9, 11, 0},
   {8, 8, 7, 7, 8, 8, 9, 10, 13},
   {8, 7, 8, 8, 8, 9, 10, 11, 0},
   {9, 8, 8, 8, 8, 10, 10, 11, 0},
   {9, 8, 9, 8, 11, 11, 11, 15, 0}},
  {{8, 0, 0, 0, 0, 13, 0, 0, 0},
   {0, 8, 0, 7, 12, 11, 11, 0, 0},
   {0, 0, 7, 8, 8, 10, 9, 13, 0},
   {11, 7, 8, 7, 8, 9, 10, 12, 0},
   {9, 8, 7, 8, 8, 8, 9, 10, 0},
   {10, 8, 8, 8, 8, 8, 10, 10, 0},
   {10, 8, 8, 8, 8, 9, 10, 11, 12},
   {10, 8, 9, 9, 9, 10, 11, 11, 0},
   {15, 13, 9, 10, 9, 11, 12, 12, 0}},
  {{8, 0, 0, 0, 13, 13, 14, 0, 0},
   {0, 8, 13, 8, 10, 9, 9, 14, 0},
   {0, 9, 8, 8, 8, 8, 10, 11, 0},
   {10, 8, 8, 8, 8, 9, 9, 11, 0},
   {11, 9, 8, 8, 8, 9, 9, 10, 11},
   {12, 9, 8, 8, 9, 9, 10, 10, 10},
   {11, 10, 9, 9, 9, 10, 10, 11, 12},
   {11, 9, 9, 9, 10, 10, 11, 11, 12},
   {9, 11, 10, 11, 11, 10, 12, 11, 12}},
  {{9, 0, 0, 0, 12, 13, 12, 0, 0},
   {0, 8, 11, 9, 9, 8, 11, 0, 0},
   {0, 11, 8, 9, 9, 9, 10, 11, 0},
   {13, 9, 8, 8, 9, 9, 10, 10, 16},
   {11, 9, 8, 8, 9, 9, 10, 10, 9},
   {12, 9, 9, 9, 9, 9, 10, 11, 12},
   {12, 11, 10, 10, 10, 10, 11, 11, 12},
   {13, 10, 10, 11, 10, 11, 11, 12, 12},
   {0, 15, 10, 11, 11, 12, 12, 12, 16}},
  {{9, 0, 0, 0, 11, 10, 15, 0, 0},
   {0, 9, 0, 7, 10, 12, 11, 16, 0},
   {0, 0, 8, 9, 9, 9, 10, 10, 16},
   {0, 10, 9, 9, 9, 9, 10, 11, 0},
   {0, 15, 9, 9, 9, 9, 10, 10, 10},
   {13, 11, 9, 11, 10, 10, 10, 11, 10},
   {0, 10, 10, 10, 11, 11, 11, 11, 13},
   {0, 9, 11, 11, 11, 12, 12, 12, 12},
   {0, 0, 13, 13, 12, 11, 13, 12, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 12, 0, 0, 0, 0, 14, 0},
   {0, 0, 0, 0, 12, 10, 0, 16, 0},
   {0, 0, 0, 0, 10, 11, 12, 11, 0},
   {0, 0, 0, 0, 13, 13, 11, 13, 0},
   {0, 0, 0, 14, 11, 12, 11, 12, 0},
   {0, 0, 0, 0, 13, 12, 12, 12, 0},
   {0, 0, 0, 0, 0, 0, 12, 0, 0}}},
 {{{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 15, 8, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 12, 0, 0, 0},
   {0, 10, 0, 0, 0, 0, 14, 0, 0},
   {0, 0, 0, 12, 11, 11, 0, 0, 0},
   {0, 0, 9, 13, 14, 13, 0, 0, 0},
   {0, 0, 0, 0, 15, 0, 0, 0, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 9, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 8, 0, 0, 0, 15, 0},
   {0, 0, 0, 10, 10, 0, 0, 0, 0},
   {0, 0, 0, 14, 11, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 11, 14, 0, 0},
   {0, 8, 16, 10, 10, 12, 13, 0, 0},
   {0, 8, 0, 12, 13, 11, 16, 0, 0},
   {0, 0, 0, 0, 0, 0, 12, 0, 0}},
  {{8, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 8, 0, 13, 0, 0, 0, 0, 0},
   {0, 0, 8, 0, 10, 11, 0, 0, 0},
   {0, 0, 9, 8, 8, 10, 0, 0, 0},
   {0, 15, 9, 9, 8, 8, 11, 12, 0},
   {11, 0, 14, 9, 8, 11, 11, 15, 0},
   {0, 0, 8, 8, 9, 9, 10, 13, 0},
   {0, 0, 8, 8, 9, 10, 11, 15, 0},
   {0, 0, 0, 0, 13, 13, 13, 0, 0}},
  {{9, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 9, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 12, 0, 0, 14, 0, 0, 0},
   {0, 0, 8, 8, 10, 9, 0, 0, 0},
   {0, 0, 12, 10, 8, 8, 9, 14, 0},
   {0, 8, 8, 8, 9, 9, 10, 0, 0},
   {0, 8, 8, 10, 10, 10, 12, 11, 0},
   {0, 12, 10, 9, 10, 11, 11, 11, 0},
   {0, 0, 0, 0, 16, 0, 0, 0, 0}},
  {{9, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 10, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 8, 16, 0, 0, 0, 13, 0},
   {0, 0, 0, 10, 9, 10, 16, 0, 0},
   {0, 0, 11, 8, 8, 9, 11, 13, 0},
   {0, 0, 10, 8, 10, 10, 11, 10, 0},
   {11, 10, 9, 8, 9, 10, 11, 11, 0},
   {16, 9, 10, 11, 11, 10, 11, 13, 0},
   {0, 0, 15, 0, 11, 14, 13, 0, 0}},
  {{9, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 8, 0, 15, 0, 0, 0, 0, 0},
   {0, 0, 9, 0, 14, 0, 14, 0, 0},
   {0, 15, 12, 10, 11, 10, 13, 14, 0},
   {0, 0, 12, 10, 10, 10, 10, 11, 0},
   {0, 13, 11, 10, 10, 10, 11, 12, 0},
   {0, 12, 11, 9, 10, 11, 11, 12, 14},
   {9, 8, 10, 11, 11, 11, 12, 13, 0},
   {0, 0, 0, 12, 13, 11, 13, 13, 0}},
  {{9, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 12, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 9, 13, 15, 13, 10, 0, 0},
   {0, 0, 9, 10, 10, 10, 11, 10, 0},
   {0, 0, 11, 11, 10, 10, 11, 10, 0},
   {0, 11, 8, 9, 11, 10, 11, 12, 0},
   {0, 11, 10, 11, 12, 11, 11, 12, 0},
   {10, 14, 10, 12, 11, 12, 12, 12, 0},
   {0, 0, 16, 0, 14, 12, 12, 12, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 8, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 11, 12, 15, 16, 0, 12, 0},
   {0, 0, 10, 9, 16, 12, 10, 14, 0},
   {0, 0, 11, 10, 10, 10, 11, 10, 0},
   {0, 0, 11, 11, 9, 11, 11, 11, 0},
   {0, 0, 9, 10, 11, 11, 12, 12, 0},
   {0, 0, 13, 12, 12, 12, 13, 12, 0},
   {0, 0, 0, 16, 0, 13, 12, 13, 0}},
  {{0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0},
   {0, 0, 0, 0, 0, 10, 15, 0, 0},
   {0, 0, 0, 0, 0, 0, 16, 16, 0},
   {0, 0, 0, 0, 0, 16, 15, 16, 0},
   {0, 0, 0, 0, 0, 0, 0, 0, 0}}}};

unsigned char
hash_cost_to_cost(unsigned char perfect_hash_cost)
{
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

struct cost_to_goal_result
get_cost_to_goal (
    unsigned int prev_pt0_state,
    unsigned int prev_pt1_state,
    unsigned int prev_pt2_state,
    unsigned int prev_pt3_state,
    unsigned int prev_pt4_state)
{
    struct cost_to_goal_result result;
    memset(&result, 0, sizeof(struct cost_to_goal_result));

    if (pt_perfect_hash01) {
        unsigned char perfect_hash01_cost = 0;
        unsigned int perfect_hash01_index = 0;

        perfect_hash01_index = (prev_pt0_state * pt1_state_max) + prev_pt1_state;
        perfect_hash01_cost = hash_cost_to_cost(pt_perfect_hash01[perfect_hash01_index]);

        if (perfect_hash01_cost > result.cost_to_goal) {
            result.cost_to_goal = perfect_hash01_cost;
        }

        result.perfect_hash01_cost = perfect_hash01_cost;
    }

    if (pt_perfect_hash02) {
        unsigned char perfect_hash02_cost = 0;
        unsigned int perfect_hash02_index = 0;

        perfect_hash02_index = (prev_pt0_state * pt2_state_max) + prev_pt2_state;
        perfect_hash02_cost = hash_cost_to_cost(pt_perfect_hash02[perfect_hash02_index]);

        if (perfect_hash02_cost > result.cost_to_goal) {
            result.cost_to_goal = perfect_hash02_cost;
        }

        result.perfect_hash02_cost = perfect_hash02_cost;
    }

    switch (pt_max) {
    case 4:
        result.pt4_cost = pt4[prev_pt4_state * ROW_LENGTH];
        result.pt3_cost = pt3[prev_pt3_state * ROW_LENGTH];
        result.pt2_cost = pt2[prev_pt2_state * ROW_LENGTH];
        result.pt1_cost = pt1[prev_pt1_state * ROW_LENGTH];
        result.pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        result.cost_to_goal = (result.pt4_cost > result.cost_to_goal) ? result.pt4_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt3_cost > result.cost_to_goal) ? result.pt3_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt2_cost > result.cost_to_goal) ? result.pt2_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt1_cost > result.cost_to_goal) ? result.pt1_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt0_cost > result.cost_to_goal) ? result.pt0_cost : result.cost_to_goal;
        break;

    case 3:
        result.pt3_cost = pt3[prev_pt3_state * ROW_LENGTH];
        result.pt2_cost = pt2[prev_pt2_state * ROW_LENGTH];
        result.pt1_cost = pt1[prev_pt1_state * ROW_LENGTH];
        result.pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        result.cost_to_goal = (result.pt3_cost > result.cost_to_goal) ? result.pt3_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt2_cost > result.cost_to_goal) ? result.pt2_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt1_cost > result.cost_to_goal) ? result.pt1_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt0_cost > result.cost_to_goal) ? result.pt0_cost : result.cost_to_goal;

        // dwalton
        unsigned char dwalton_cost = dwalton[result.pt0_cost][result.pt1_cost][result.pt2_cost][result.pt3_cost];
        result.cost_to_goal = (dwalton_cost > result.cost_to_goal) ? dwalton_cost : result.cost_to_goal;

        break;

    case 2:
        result.pt2_cost = pt2[prev_pt2_state * ROW_LENGTH];
        result.pt1_cost = pt1[prev_pt1_state * ROW_LENGTH];
        result.pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        result.cost_to_goal = (result.pt2_cost > result.cost_to_goal) ? result.pt2_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt1_cost > result.cost_to_goal) ? result.pt1_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt0_cost > result.cost_to_goal) ? result.pt0_cost : result.cost_to_goal;
        break;

    case 1:
        result.pt1_cost = pt1[prev_pt1_state * ROW_LENGTH];
        result.pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];

        result.cost_to_goal = (result.pt1_cost > result.cost_to_goal) ? result.pt1_cost : result.cost_to_goal;
        result.cost_to_goal = (result.pt0_cost > result.cost_to_goal) ? result.pt0_cost : result.cost_to_goal;
        break;

    default:
        result.pt0_cost = pt0[prev_pt0_state * ROW_LENGTH];
        result.cost_to_goal = (result.pt0_cost > result.cost_to_goal) ? result.pt0_cost : result.cost_to_goal;
        break;
    }

    if (cost_to_goal_multiplier) {
        result.cost_to_goal = (unsigned char) round(result.cost_to_goal * cost_to_goal_multiplier);
    }

    return result;
}


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


void
print_ida_summary (
    unsigned int pt0_state,
    unsigned int pt1_state,
    unsigned int pt2_state,
    unsigned int pt3_state,
    unsigned int pt4_state,
    move_type *solution,
    unsigned char solution_len)
{
    struct cost_to_goal_result ctg;
    unsigned char cost_to_goal = 0;
    unsigned char pt0_cost = 0;
    unsigned char pt1_cost = 0;
    unsigned char pt2_cost = 0;
    unsigned char pt3_cost = 0;
    unsigned char pt4_cost = 0;
    unsigned char steps_to_solved = solution_len;

    if (find_multiple_solutions) {
        return;
    }

    ctg = get_cost_to_goal(pt0_state, pt1_state, pt2_state, pt3_state, pt4_state);
    cost_to_goal = ctg.cost_to_goal;
    pt0_cost = ctg.pt0_cost;
    pt1_cost = ctg.pt1_cost;
    pt2_cost = ctg.pt2_cost;
    pt3_cost = ctg.pt3_cost;
    pt4_cost = ctg.pt4_cost;

    printf("\n");
    printf("       PT0  PT1  PT2  PT3  PT4  PER01  PER02  CTG  TRU  IDX\n");
    printf("       ===  ===  ===  ===  ===  =====  =====  ===  ===  ===\n");
    printf("  INIT %3d  %3d  %3d  %3d  %3d    %3d    %3d  %3d  %3d  %3d\n",
        pt0_cost, pt1_cost, pt2_cost, pt3_cost, pt4_cost, ctg.perfect_hash01_cost, ctg.perfect_hash02_cost, cost_to_goal, steps_to_solved, 0);

    for (unsigned char i = 0; i < solution_len; i++) {
        unsigned char j = 0;

        while (j < legal_move_count) {
            if (legal_moves[j] == solution[i]) {
                break;
            }
            j++;
        }
        unsigned int offset = 1 + (4 * j);

        switch (pt_max) {
        case 4:
            pt4_state = read_state(pt4, (pt4_state * ROW_LENGTH) + offset);
            pt3_state = read_state(pt3, (pt3_state * ROW_LENGTH) + offset);
            pt2_state = read_state(pt2, (pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);
            break;

        case 3:
            pt3_state = read_state(pt3, (pt3_state * ROW_LENGTH) + offset);
            pt2_state = read_state(pt2, (pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);
            break;

        case 2:
            pt2_state = read_state(pt2, (pt2_state * ROW_LENGTH) + offset);
            pt1_state = read_state(pt1, (pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);
            break;

        case 1:
            pt1_state = read_state(pt1, (pt1_state * ROW_LENGTH) + offset);
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);
            break;

        default:
            pt0_state = read_state(pt0, (pt0_state * ROW_LENGTH) + offset);
            break;
        }

        ctg = get_cost_to_goal(pt0_state, pt1_state, pt2_state, pt3_state, pt4_state);
        cost_to_goal = ctg.cost_to_goal;
        pt0_cost = ctg.pt0_cost;
        pt1_cost = ctg.pt1_cost;
        pt2_cost = ctg.pt2_cost;
        pt3_cost = ctg.pt3_cost;
        pt4_cost = ctg.pt4_cost;
        steps_to_solved--;
        printf("%5s  %3d  %3d  %3d  %3d  %3d  %5d  %5d  %3d  %3d  %3d\n",
            move2str[solution[i]], pt0_cost, pt1_cost, pt2_cost, pt3_cost, pt4_cost,
            ctg.perfect_hash01_cost, ctg.perfect_hash02_cost, cost_to_goal, steps_to_solved, i+1);
    }
    printf("\n");
}


unsigned char
invalid_prune(unsigned char cost_to_here, move_type *moves_to_here)
{
    // Lw2 U' Fw2 D R2 L2 Lw2 U2 L2 U' Rw2 Bw2 Rw2 U R2 D Rw2
    move_type move_seq[17];

    move_seq[0] = Lw2;
    move_seq[1] = U_PRIME;
    move_seq[2] = Fw2;
    move_seq[3] = D;
    move_seq[4] = R2;
    move_seq[5] = L2;
    move_seq[6] = Lw2;
    move_seq[7] = U2;
    move_seq[8] = L2;
    move_seq[9] = U_PRIME;
    move_seq[10] = Rw2;
    move_seq[11] = Bw2;
    move_seq[12] = Rw2;
    move_seq[13] = U;
    move_seq[14] = R2;
    move_seq[15] = D;
    move_seq[16] = Rw2;

    if (threshold == 18 && memcmp(moves_to_here, move_seq, sizeof(move_type) * cost_to_here) == 0) {
        return 1;
    }

    return 0;
}


unsigned char
parity_ok (move_type *moves_to_here)
{
    unsigned int orbit0_wide_quarter_turn_count = 0;
    unsigned int orbit1_wide_quarter_turn_count = 0;

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

    return 1;
}

struct ida_search_result
ida_search (
    unsigned char cost_to_here,
    move_type *moves_to_here,
    move_type prev_move,
    unsigned int prev_pt0_state,
    unsigned int prev_pt1_state,
    unsigned int prev_pt2_state,
    unsigned int prev_pt3_state,
    unsigned int prev_pt4_state)
{
    struct cost_to_goal_result ctg;
    unsigned char cost_to_goal = 0;
    unsigned char f_cost = 0;
    move_type move, skip_other_steps_this_face;
    skip_other_steps_this_face = MOVE_NONE;
    struct ida_search_result search_result, tmp_search_result;
    unsigned int pt0_state = 0;
    unsigned int pt1_state = 0;
    unsigned int pt2_state = 0;
    unsigned int pt3_state = 0;
    unsigned int pt4_state = 0;

    ida_count++;

    ctg = get_cost_to_goal(prev_pt0_state, prev_pt1_state, prev_pt2_state, prev_pt3_state, prev_pt4_state);
    cost_to_goal = ctg.cost_to_goal;

    f_cost = cost_to_here + cost_to_goal;
    search_result.f_cost = f_cost;
    search_result.found_solution = 0;

    if (cost_to_goal == 0 && parity_ok(moves_to_here)) {
        // We are finished!!
        LOG("IDA count %'llu, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
            ida_count, f_cost, threshold, cost_to_here, cost_to_goal);
        print_moves(moves_to_here, cost_to_here);
        search_result.found_solution = 1;
        memcpy(search_result.solution, moves_to_here, sizeof(move_type) * cost_to_here);
        return search_result;
    }

    // Abort Searching
    if (f_cost >= threshold) {
        // uncomment this to troubleshoot when the correct solution is incorrectly pruned
        /*
        if (invalid_prune(cost_to_here, moves_to_here)) {
            LOG("IDA invalid prune, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
                f_cost, threshold, cost_to_here, cost_to_goal);
            print_moves(moves_to_here, cost_to_here);
            LOG("pt0_state %07u, cost %d\n", prev_pt0_state, pt0_cost);
            LOG("pt1_state %07u, cost %d\n", prev_pt1_state, pt1_cost);
            LOG("pt2_state %07u, cost %d\n", prev_pt2_state, pt2_cost);
            exit(1);
        }
         */
        return search_result;
    }

    unsigned int offset = 0;

    for (unsigned char i = 0; i < legal_move_count; i++) {
        move = move_matrix[prev_move][i];

        // This is the scenario where the move is on the same face and layer as prev_move
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

        switch (pt_max) {
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
            if (find_multiple_solutions) {
                search_result.found_solution = 1;
            } else {
                return tmp_search_result;
            }
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


struct ida_search_result
ida_solve (
    unsigned char cost_to_here,
    unsigned int pt0_state,
    unsigned int pt1_state,
    unsigned int pt2_state,
    unsigned int pt3_state,
    unsigned int pt4_state,
    unsigned char max_ida_threshold)
{
    struct cost_to_goal_result ctg;
    move_type moves_to_here[max_ida_threshold];
    struct ida_search_result search_result;
    struct timeval stop, start, start_this_threshold;
    unsigned char pt0_cost = 0;
    unsigned char pt1_cost = 0;
    unsigned char pt2_cost = 0;
    unsigned char pt3_cost = 0;
    unsigned char pt4_cost = 0;
    unsigned char min_ida_threshold = 0;

    memset(moves_to_here, MOVE_NONE, max_ida_threshold);

    // For printing commas via %'d
    setlocale(LC_NUMERIC, "");

    ctg = get_cost_to_goal(pt0_state, pt1_state, pt2_state, pt3_state, pt4_state);
    pt0_cost = ctg.pt0_cost;
    pt1_cost = ctg.pt1_cost;
    pt2_cost = ctg.pt2_cost;
    pt3_cost = ctg.pt3_cost;
    pt4_cost = ctg.pt4_cost;
    min_ida_threshold = ctg.cost_to_goal;
    search_result.found_solution = 0;

    // LOG("min_ida_threshold %d\n", min_ida_threshold);
    if (min_ida_threshold >= max_ida_threshold) {
        return search_result;
    }

    gettimeofday(&start, NULL);

    for (threshold = min_ida_threshold; threshold <= max_ida_threshold; threshold++) {
        ida_count = 0;
        gettimeofday(&start_this_threshold, NULL);
        memset(moves_to_here, MOVE_NONE, sizeof(move_type) * max_ida_threshold);
        hash_delete_all(&ida_explored);

        search_result = ida_search(
            cost_to_here,
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

        LOG("IDA threshold %d, explored %'llu nodes, took %.3fs, %'d nodes-per-sec\n", threshold, ida_count,  ms / 1000, nodes_per_sec);

        if (search_result.found_solution) {
            float ms = ((stop.tv_sec - start.tv_sec) * 1000) + ((stop.tv_usec - start.tv_usec) / 1000);
            float nodes_per_ms = ida_count_total / ms;
            unsigned int nodes_per_sec = nodes_per_ms * 1000;
            LOG("IDA found solution, explored %'llu total nodes, took %.3fs, %'d nodes-per-sec\n",
                ida_count_total, ms / 1000, nodes_per_sec);
            return search_result;
        }
    }

    LOG("IDA failed with range %d->%d\n\n", min_ida_threshold, max_ida_threshold);
    return search_result;
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
        LOG("%s is %dM\n", filename, bufsize / (1024 * 1024));
    }

    fclose(fh);
    return buffer;
}


int
main (int argc, char *argv[])
{
    unsigned long prune_table_0_state = 0;
    unsigned long prune_table_1_state = 0;
    unsigned long prune_table_2_state = 0;
    unsigned long prune_table_3_state = 0;
    unsigned long prune_table_4_state = 0;
    unsigned char max_ida_threshold = 30;
    char *prune_table_states_filename = NULL;

    memset(legal_moves, MOVE_NONE, MOVE_MAX);
    memset(move_matrix, MOVE_NONE, MOVE_MAX * MOVE_MAX);
    memset(same_face_and_layer_matrix, 0, MOVE_MAX * MOVE_MAX);

    for (unsigned char i = 1; i < argc; i++) {
        if (strmatch(argv[i], "--prune-table-0-filename")) {
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

        } else if (strmatch(argv[i], "--multiple-solutions")) {
            find_multiple_solutions = 1;

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
    // printf("legal_move_count %d, ROW_LENGTH %d\n", legal_move_count, ROW_LENGTH);
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
            LOG("loop %d\n", i_max_ida_threshold);

            fh_read = fopen(prune_table_states_filename, "r");
            while ((read = getline(&line, &len, fh_read)) != -1) {
                // printf("%s", line);
                unsigned char token_index = 0;
                char *pt;
                pt = strtok (line, ",");

                while (pt != NULL) {
                    unsigned int token_value = atoi(pt);
                    pt = strtok (NULL, ",");

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

                search_result = ida_solve(
                    0,
                    prune_table_0_state,
                    prune_table_1_state,
                    prune_table_2_state,
                    prune_table_3_state,
                    prune_table_4_state,
                    i_max_ida_threshold);

                if (search_result.found_solution && search_result.f_cost < min_search_result.f_cost) {
                    min_search_result = search_result;
                    max_ida_threshold = search_result.f_cost;
                    break;
                }

                line_index++;
            }
            fclose(fh_read);

            search_result = min_search_result;

            if (search_result.found_solution) {
                break;
            }
        }

        if (line) {
            free(line);
        }

    } else {
        search_result = ida_solve(
            0,
            prune_table_0_state,
            prune_table_1_state,
            prune_table_2_state,
            prune_table_3_state,
            prune_table_4_state,
            max_ida_threshold);

        if (search_result.found_solution) {
            print_ida_summary(
                prune_table_0_state,
                prune_table_1_state,
                prune_table_2_state,
                prune_table_3_state,
                prune_table_4_state,
                search_result.solution,
                search_result.f_cost);
        }
    }

    if (!search_result.found_solution) {
        exit(1);
    }
}
