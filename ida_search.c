
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
#include "rotate_xxx.h"
#include "ida_search_core.h"
#include "ida_search_444.h"
#include "ida_search_555.h"
#include "ida_search_666.h"
#include "ida_search_777.h"


// To compile:
//  gcc -O3 -o ida_search ida_search_core.c ida_search.c rotate_xxx.c ida_search_444.c ida_search_555.c ida_search_666.c ida_search_777.c -lm
//
//  Add -ggdb to build gdb symbols

// scratchpads that we do not want to allocate over and over again
char *sp_cube_state;
unsigned long array_size;
unsigned long ida_count;
unsigned long ida_count_total;
unsigned long seek_calls = 0;

// Supported IDA searches
typedef enum {
    NONE,

    // 4x4x4
    CENTERS_STAGE_444,

    // 5x5x5
    UD_CENTERS_STAGE_555,
    LR_CENTERS_STAGE_555,
    CENTERS_SOLVE_555,

    // 6x6x6
    UD_OBLIQUE_EDGES_STAGE_666,
    LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_STAGE_666,

    // 7x7x7
    UD_OBLIQUE_EDGES_STAGE_777,
    LR_OBLIQUE_EDGES_STAGE_777,
    STEP40_777,
    STEP50_777,
    STEP60_777,

} lookup_table_type;

struct key_value_pair *ida_explored = NULL;

// 4x4x4
struct key_value_pair *centers_cost_444 = NULL;
char *UD_centers_cost_only_444 = NULL;
char *LR_centers_cost_only_444 = NULL;
char *FB_centers_cost_only_444 = NULL;


// 5x5x5
struct key_value_pair *UD_centers_555 = NULL;
char *pt_UD_t_centers_cost_only = NULL;
char *pt_UD_x_centers_cost_only = NULL;

struct key_value_pair *LR_centers_555 = NULL;
char *pt_LR_t_centers_cost_only = NULL;
char *pt_LR_x_centers_cost_only = NULL;

struct key_value_pair *ULFRBD_centers_555 = NULL;
char *UL_centers_cost_only_555 = NULL;
char *UF_centers_cost_only_555 = NULL;
char *LF_centers_cost_only_555 = NULL;


// 6x6x6
struct key_value_pair *LR_inner_x_centers_and_oblique_edges_666 = NULL;
char *LR_inner_x_centers_666 = NULL;
char *LR_oblique_edges_666 = NULL;


// 7x7x7
struct key_value_pair *step40_777 = NULL;
char *step41_777 = NULL;
char *step42_777 = NULL;

struct key_value_pair *step50_777 = NULL;
char *step51_777 = NULL;
char *step52_777 = NULL;

struct key_value_pair *step60_777 = NULL;
char *step61_777 = NULL;
char *step62_777 = NULL;
char *step63_777 = NULL;


int
strmatch (char *str1, char *str2)
{
    if (strcmp(str1, str2) == 0) {
        return 1;
    }
    return 0;
}

/* Remove leading and trailing whitespaces */
char *
strstrip (char *s)
{
    size_t size;
    char *end;

    size = strlen(s);

    if (!size)
        return s;

    // Removing trailing whitespaces
    end = s + size - 1;
    while (end >= s && isspace(*end))
        end--;
    *(end + 1) = '\0';

    // Remove leading whitespaces
    // The lookup table files do not have any leading whitespaces so commenting this out to save a few CPU cycles
    //while (*s && isspace(*s))
    //    s++;

    return s;
}


/* The file must be sorted and all lines must be the same width */
unsigned long
file_binary_search (char *filename, char *state_to_find, int statewidth, unsigned long linecount, int linewidth)
{
    FILE *fh_read = NULL;
    unsigned long first = 0;
    unsigned long midpoint = 0;
    unsigned long last = linecount - 1;
    char line[128];
    int str_cmp_result;
    char *foo;

    fh_read = fopen(filename, "r");

    if (fh_read == NULL) {
        printf("ERROR: file_binary_search could not open %s\n", filename);
        exit(1);
    }

    while (first <= last) {
        midpoint = (unsigned long) ((first + last)/2);
        fseek(fh_read, midpoint * linewidth, SEEK_SET);

        if (fread(line, statewidth, 1, fh_read)) {
            seek_calls++;

            str_cmp_result = strncmp(state_to_find, line, statewidth);

            if (str_cmp_result == 0) {

                // read the entire line, not just the state
                fseek(fh_read, midpoint * linewidth, SEEK_SET);

                if (fread(line, linewidth, 1, fh_read)) {
                    strstrip(line);
                    fclose(fh_read);
                    return 1;
                } else {
                    printf("ERROR: linewidth read failed for %s\n", filename);
                    exit(1);
                }

            } else if (str_cmp_result < 0) {
                last = midpoint - 1;

            } else {
                first = midpoint + 1;
            }
        } else {
            printf("ERROR: statewidth read failed for %s\n", filename);
            exit(1);
        }
    }

    fclose(fh_read);
    return 0;
}


/*
 * Replace all occurrences of 'old' with 'new'
 */
void
streplace (char *str, char old, char new)
{
    int i = 0;

    /* Run till end of string */
    while (str[i] != '\0') {

        /* If occurrence of character is found */
        if (str[i] == old) {
            str[i] = new;
        }

        i++;
    }
}


void
str_replace_for_binary(char *str, char *ones)
{
    int i = 0;
    int j;
    int is_a_one = 0;

    /* Run till end of string */
    while (str[i] != '\0') {

        if (str[i] != '0') {
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

void
str_replace_list_of_chars (char *str, char *old, char *new)
{
    int i = 0;
    int j;

    /* Run till end of string */
    while (str[i] != '\0') {

        j = 0;

        while (old[j] != '\0') {

            /* If occurrence of character is found */
            if (str[i] == old[j]) {
                str[i] = new[0];
                break;
            }
            j++;
        }

        i++;
    }
}


void
init_cube(char *cube, int size, lookup_table_type type, char *kociemba)
{
    int squares_per_side = size * size;
    int square_count = squares_per_side * 6;
    int U_start = 1;
    int L_start = U_start + squares_per_side;
    int F_start = L_start + squares_per_side;
    int R_start = F_start + squares_per_side;
    int B_start = R_start + squares_per_side;
    int D_start = B_start + squares_per_side;

    // kociemba_string is in URFDLB order
    int U_start_kociemba = 0;
    int R_start_kociemba = U_start_kociemba + squares_per_side;
    int F_start_kociemba = R_start_kociemba + squares_per_side;
    int D_start_kociemba = F_start_kociemba + squares_per_side;
    int L_start_kociemba = D_start_kociemba + squares_per_side;
    int B_start_kociemba = L_start_kociemba + squares_per_side;

    char ones_UD[3] = {'U', 'D', 0};
    char ones_LR[3] = {'L', 'R', 0};
    char ones_ULF[4] = {'U', 'L', 'F', 0};

    char U[2] = {'U', 0};
    char L[2] = {'L', 0};
    char F[2] = {'F', 0};
    char R[2] = {'R', 0};
    char B[2] = {'B', 0};
    char D[2] = {'D', 0};

    memset(cube, 0, sizeof(char) * (square_count + 2));
    cube[0] = 'x'; // placeholder
    memcpy(&cube[U_start], &kociemba[U_start_kociemba], squares_per_side);
    memcpy(&cube[L_start], &kociemba[L_start_kociemba], squares_per_side);
    memcpy(&cube[F_start], &kociemba[F_start_kociemba], squares_per_side);
    memcpy(&cube[R_start], &kociemba[R_start_kociemba], squares_per_side);
    memcpy(&cube[B_start], &kociemba[B_start_kociemba], squares_per_side);
    memcpy(&cube[D_start], &kociemba[D_start_kociemba], squares_per_side);
    // LOG("cube:\n%s\n\n", cube);

    switch (type)  {
    case CENTERS_STAGE_444:
        str_replace_list_of_chars(cube, D, U);
        str_replace_list_of_chars(cube, R, L);
        str_replace_list_of_chars(cube, B, F);
        print_cube(cube, size);
        break;

    case UD_CENTERS_STAGE_555:
    case UD_OBLIQUE_EDGES_STAGE_666:
    case UD_OBLIQUE_EDGES_STAGE_777:
        // Convert to 1s and 0s
        str_replace_for_binary(cube, ones_UD);
        print_cube(cube, size);
        break;

    case LR_CENTERS_STAGE_555:
    case LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_STAGE_666:
    case LR_OBLIQUE_EDGES_STAGE_777:
        // Convert to 1s and 0s
        str_replace_for_binary(cube, ones_LR);
        print_cube(cube, size);
        break;

    case CENTERS_SOLVE_555:
        // Convert to 1s and 0s
        str_replace_for_binary(cube, ones_ULF);
        print_cube(cube, size);
        break;

    case STEP40_777:
    case STEP50_777:
    case STEP60_777:
        break;

    default:
        printf("ERROR: init_cube() does not yet support this --type\n");
        exit(1);
    }
}


int
moves_cost (char *moves)
{
    int cost = 0;
    int i = 0;

    if (moves) {
        cost++;

        while (moves[i] != '\0') {

            // Moves are separated by whitespace
            if (moves[i] == ' ') {
                cost++;
            }

            i++;
        }
    }

    return cost;
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

    LOG("ida_prune_table_preload %s: start\n", filename);

    // 4x4x4
    if (strmatch(filename, "lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt")) {

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // 0..23 are the state
            // 24 is the :
            // 25 is the move count
            buffer[24] = '\0';
            cost = atoi(&buffer[25]);
            hash_add(hashtable, buffer, cost);
        }

    } else if (strmatch(filename, "lookup-table-5x5x5-step10-UD-centers-stage.txt") ||
            strmatch(filename, "lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt")) {

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // 0..13 are the state
            // 14 is the :
            // 15 is the move count
            buffer[14] = '\0';
            cost = atoi(&buffer[15]);
            hash_add(hashtable, buffer, cost);
        }

    } else if (strmatch(filename, "lookup-table-5x5x5-step20-LR-centers-stage.txt")) {

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // 0..8 are the state
            // 9 is the :
            // 10 is the move count
            buffer[9] = '\0';
            cost = atoi(&buffer[10]);
            hash_add(hashtable, buffer, cost);
        }


    } else if (strmatch(filename, "lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt")) {

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // 0..11 are the state
            // 12 is the :
            // 13 is the move count
            buffer[12] = '\0';
            cost = atoi(&buffer[13]);
            hash_add(hashtable, buffer, cost);
        }

    } else if (
        strmatch(filename, "lookup-table-7x7x7-step40.txt") ||
        strmatch(filename, "lookup-table-7x7x7-step50.txt")) {

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // 0002001ffefff:3
            // 0..12 are the state
            // 13 is the :
            // 14 is the move count
            buffer[13] = '\0';
            cost = atoi(&buffer[14]);
            hash_add(hashtable, buffer, cost);
        }

    } else if (strmatch(filename, "lookup-table-7x7x7-step60.txt")) {

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // 0842108007c000008007fe0fffffdfffbdef7b:6
            // 0..37 are the state
            // 38 is the :
            // 39 is the move count
            buffer[38] = '\0';
            cost = atoi(&buffer[39]);
            hash_add(hashtable, buffer, cost);
        }

    } else {
        printf("ERROR: ida_prune_table_preload add support for %s\n", filename);
        exit(1);
    }

    fclose(fh_read);
    LOG("ida_prune_table_preload %s: end\n", filename);
}


char *
ida_cost_only_preload (char *filename, unsigned long size)
{
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


int
ida_prune_table_cost (struct key_value_pair *hashtable, char *state_to_find)
{
    int cost = 0;
    struct key_value_pair * pt_entry = NULL;

    pt_entry = hash_find(&hashtable, state_to_find);

    if (pt_entry) {
        cost = pt_entry->value;
    }

    return cost;
}


struct ida_heuristic_result
ida_heuristic (char *cube, lookup_table_type type, unsigned int max_cost_to_goal)
{
    switch (type)  {

    // 4x4x4
    case CENTERS_STAGE_444:
        return ida_heuristic_centers_444(
            cube,
            max_cost_to_goal,
            &centers_cost_444,
            UD_centers_cost_only_444,
            LR_centers_cost_only_444,
            FB_centers_cost_only_444);

    // 5x5x5
    case UD_CENTERS_STAGE_555:
        return ida_heuristic_UD_centers_555(
            cube,
            max_cost_to_goal,
            &UD_centers_555,
            pt_UD_t_centers_cost_only,
            pt_UD_x_centers_cost_only);

    case LR_CENTERS_STAGE_555:
        return ida_heuristic_LR_centers_555(
            cube,
            max_cost_to_goal,
            &LR_centers_555,
            pt_LR_t_centers_cost_only,
            pt_LR_x_centers_cost_only);


    case CENTERS_SOLVE_555:
        return ida_heuristic_ULFRBD_centers_555(
            cube,
            max_cost_to_goal,
            &ULFRBD_centers_555,
            UL_centers_cost_only_555,
            UF_centers_cost_only_555,
            LF_centers_cost_only_555);

    // 6x6x6
    case UD_OBLIQUE_EDGES_STAGE_666:
        return ida_heuristic_UD_oblique_edges_stage_666(
            cube,
            max_cost_to_goal
        );

    case LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_STAGE_666:
        return ida_heuristic_LR_inner_x_centers_and_oblique_edges_stage_666(
            cube,
            max_cost_to_goal,
            &LR_inner_x_centers_and_oblique_edges_666,
            LR_inner_x_centers_666,
            LR_oblique_edges_666);

    // 7x7x7
    case UD_OBLIQUE_EDGES_STAGE_777:
        return ida_heuristic_UD_oblique_edges_stage_777(cube, max_cost_to_goal);

    case LR_OBLIQUE_EDGES_STAGE_777:
        return ida_heuristic_LR_oblique_edges_stage_777(cube, max_cost_to_goal);

    case STEP40_777:
        return ida_heuristic_step40_777(
            cube,
            max_cost_to_goal,
            &step40_777,
            step41_777,
            step42_777);

    case STEP50_777:
        return ida_heuristic_step50_777(
            cube,
            max_cost_to_goal,
            &step50_777,
            step51_777,
            step52_777);

    case STEP60_777:
        return ida_heuristic_step60_777(
            cube,
            max_cost_to_goal,
            &step60_777,
            step61_777,
            step62_777,
            step63_777);

    default:
        printf("ERROR: ida_heuristic() does not yet support this --type\n");
        exit(1);
    }
}


unsigned int
get_orbit0_wide_quarter_turn_count (move_type *moves)
{
    unsigned int i = 0;
    unsigned int count = 0;

    while (moves[i] != MOVE_NONE) {
        switch (moves[i]) {
        case Uw:
        case Uw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Dw:
        case Dw_PRIME:
            count += 1;
            break;

        default:
            break;
        }
        i++;
    }

    return count;
}

unsigned int
get_orbit1_wide_quarter_turn_count (move_type *moves)
{
    unsigned int i = 0;
    unsigned int count = 0;

    while (moves[i] != MOVE_NONE) {
        switch (moves[i]) {
        case threeUw:
        case threeUw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeFw:
        case threeFw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeDw:
        case threeDw_PRIME:
            count += 1;
            break;

        default:
            break;
        }
        i++;
    }

    return count;
}

int
ida_search_complete (
    char *cube,
    lookup_table_type type,
    unsigned int orbit0_wide_quarter_turns,
    unsigned int orbit1_wide_quarter_turns,
    move_type *moves_to_here)
{
    struct key_value_pair * pt_entry = NULL;
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

    switch (type)  {
    // 4x4x4
    case CENTERS_STAGE_444:
        return ida_search_complete_centers_444(cube);

    // 5x5x5
    case UD_CENTERS_STAGE_555:
        return ida_search_complete_UD_centers_555(cube);

    case LR_CENTERS_STAGE_555:
        return ida_search_complete_LR_centers_555(cube);

    case CENTERS_SOLVE_555:
        return ida_search_complete_ULFRBD_centers_555(cube);

    // 6x6x6
    case UD_OBLIQUE_EDGES_STAGE_666:
        return ida_search_complete_UD_oblique_edges_stage_666(cube);

    case LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_STAGE_666:
        return ida_search_complete_LR_inner_x_centers_and_oblique_edges_stage(cube);

    // 7x7x7
    case UD_OBLIQUE_EDGES_STAGE_777:
        return ida_search_complete_UD_oblique_edges_stage_777(cube);

    case LR_OBLIQUE_EDGES_STAGE_777:
        return ida_search_complete_LR_oblique_edges_stage_777(cube);

    case STEP40_777:
        return ida_search_complete_step40_777(cube);

    case STEP50_777:
        return ida_search_complete_step50_777(cube);

    case STEP60_777:
        return ida_search_complete_step60_777(cube);

    default:
        printf("ERROR: ida_search_complete() does not yet support type %d\n", type);
        exit(1);
    }

    return 0;
}


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
step_allowed_by_ida_search (lookup_table_type type, move_type move)
{
    switch (type)  {

    // 4x4x4
    case CENTERS_STAGE_444:
        switch (move) {
        case Lw:
        case Lw_PRIME:
        case Lw2:
        case Bw:
        case Bw_PRIME:
        case Bw2:
        case Dw:
        case Dw_PRIME:
        case Dw2:
            return 0;
        default:
            return 1;
        }

    // 5x5x5
    case UD_CENTERS_STAGE_555:
        return 1;

    case LR_CENTERS_STAGE_555:
        switch (move) {
        case U:
        case U_PRIME:
        case U2:
        case D:
        case D_PRIME:
        case D2:
        case Lw:
        case Lw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Bw:
        case Bw_PRIME:
            return 0;
        default:
            return 1;
        }

    case CENTERS_SOLVE_555:
        switch (move) {
        case Uw:
        case Uw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Dw:
        case Dw_PRIME:
            return 0;
        default:
            return 1;
        }

    // 6x6x6
    case UD_OBLIQUE_EDGES_STAGE_666:
        switch (move) {
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
            return 0;
        default:
            return 1;
        }

    case LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_STAGE_666:
        switch (move) {
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Rw:
        case Rw_PRIME:
            return 0;
        default:
            return 1;
        }

    // 7x7x7
    case UD_OBLIQUE_EDGES_STAGE_777:
        switch (move) {
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
            return 0;
        default:
            return 1;
        }

    case LR_OBLIQUE_EDGES_STAGE_777:
        switch (move) {
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case threeUw:
        case threeUw_PRIME:
        case threeDw:
        case threeDw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
            return 0;
        default:
            return 1;
        }

    /*
      # keep all centers staged
      ("3Uw", "3Uw'", "Uw", "Uw'",
       "3Lw", "3Lw'", "Lw", "Lw'",
       "3Fw", "3Fw'", "Fw", "Fw'",
       "3Rw", "3Rw'", "Rw", "Rw'",
       "3Bw", "3Bw'", "Bw", "Bw'",
       "3Dw", "3Dw'", "Dw", "Dw'"),
     */
    case STEP40_777:
        switch (move) {
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case threeUw:
        case threeUw_PRIME:
        case threeDw:
        case threeDw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Uw:
        case Uw_PRIME:
        case Dw:
        case Dw_PRIME:
            return 0;
        default:
            return 1;
        }

    /*
      # keep all centers staged
      ("3Uw", "3Uw'", "Uw", "Uw'",
       "3Lw", "3Lw'", "Lw", "Lw'",
       "3Fw", "3Fw'", "Fw", "Fw'",
       "3Rw", "3Rw'", "Rw", "Rw'",
       "3Bw", "3Bw'", "Bw", "Bw'",
       "3Dw", "3Dw'", "Dw", "Dw'",

      # keep LR in vertical stripes
      "L", "L'", "R", "R'", "3Uw2", "3Dw2", "Uw2", "Dw2"),
    */
    case STEP50_777:
        switch (move) {
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case threeUw:
        case threeUw_PRIME:
        case threeDw:
        case threeDw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Uw:
        case Uw_PRIME:
        case Dw:
        case Dw_PRIME:
        case L:
        case L_PRIME:
        case R:
        case R_PRIME:
        case threeUw2:
        case threeDw2:
        case Uw2:
        case Dw2:
            return 0;
        default:
            return 1;
        }

    /*
      # keep all centers staged
      ("3Uw", "3Uw'", "Uw", "Uw'",
       "3Lw", "3Lw'", "Lw", "Lw'",
       "3Fw", "3Fw'", "Fw", "Fw'",
       "3Rw", "3Rw'", "Rw", "Rw'",
       "3Bw", "3Bw'", "Bw", "Bw'",
       "3Dw", "3Dw'", "Dw", "Dw'",

      # keep LR in horizontal stripes
      "L", "L'", "R", "R'", "3Fw2", "3Bw2", "Fw2", "Bw2",

      # keep UD in vertical stripes
      "U", "U'", "D", "D'"),
     */
    case STEP60_777:
        switch (move) {
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case threeUw:
        case threeUw_PRIME:
        case threeDw:
        case threeDw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Uw:
        case Uw_PRIME:
        case Dw:
        case Dw_PRIME:
        case L:
        case L_PRIME:
        case R:
        case R_PRIME:
        case threeFw2:
        case threeBw2:
        case Fw2:
        case Bw2:
        case U:
        case U_PRIME:
        case D:
        case D_PRIME:
            return 0;
        default:
            return 1;
        }

    default:
        printf("ERROR: step_allowed_by_ida_search add support for this type\n");
        exit(1);
    }
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

unsigned int
ida_search (unsigned int cost_to_here,
            move_type *moves_to_here,
            unsigned int threshold,
            move_type prev_move,
            char *cube,
            unsigned int cube_size,
            lookup_table_type type,
            unsigned int orbit0_wide_quarter_turns,
            unsigned int orbit1_wide_quarter_turns)
{
    unsigned int cost_to_goal = 0;
    unsigned int f_cost = 0;
    move_type move;
    struct ida_heuristic_result result;
    char cube_tmp[array_size];
    char cost_to_here_str[3];

    ida_count++;
    unsigned int max_cost_to_goal = threshold - cost_to_here;
    result = ida_heuristic(cube, type, max_cost_to_goal);
    cost_to_goal = result.cost_to_goal;
    f_cost = cost_to_here + cost_to_goal;

    // Abort Searching
    if (f_cost >= threshold) {
        //if (debug) {
        //    LOG("IDA prune f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
        //        f_cost, threshold, cost_to_here, cost_to_goal);
        //    LOG("\n");
        //}
        return 0;
    }

    if (ida_search_complete(cube, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, moves_to_here)) {
        // We are finished!!
        LOG("IDA count %d, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
            ida_count, f_cost, threshold, cost_to_here, cost_to_goal);
        print_moves(moves_to_here, cost_to_here);
        return 1;
    }

    sprintf(cost_to_here_str, "%d", cost_to_here);
    strcat(result.lt_state, cost_to_here_str);

    if (hash_find(&ida_explored, result.lt_state)) {
        return 0;
    }

    hash_add(&ida_explored, result.lt_state, 0);

    if (cube_size == 4) {

        for (int i = 0; i < MOVE_COUNT_444; i++) {
            move = moves_444[i];

            if (steps_on_same_face_and_layer(move, prev_move)) {
                continue;
            }

            if (!step_allowed_by_ida_search(type, move)) {
                continue;
            }

            char cube_copy[array_size];
            memcpy(cube_copy, cube, sizeof(char) * array_size);
            rotate_444(cube_copy, cube_tmp, array_size, move);
            moves_to_here[cost_to_here] = move;

            if (ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size,
                           type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns)) {
                return 1;
            }
        }

    } else if (cube_size == 5) {

        for (int i = 0; i < MOVE_COUNT_555; i++) {
            move = moves_555[i];

            if (steps_on_same_face_and_layer(move, prev_move)) {
                continue;
            }

            if (!step_allowed_by_ida_search(type, move)) {
                continue;
            }

            char cube_copy[array_size];
            memcpy(cube_copy, cube, sizeof(char) * array_size);
            rotate_555(cube_copy, cube_tmp, array_size, move);
            moves_to_here[cost_to_here] = move;

            if (ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size,
                           type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns)) {
                return 1;
            }
        }

    } else if (cube_size == 6) {

        for (int i = 0; i < MOVE_COUNT_666; i++) {
            move = moves_666[i];

            if (steps_on_same_face_and_layer(move, prev_move)) {
                continue;
            }

            if (!step_allowed_by_ida_search(type, move)) {
                continue;
            }

            char cube_copy[array_size];
            memcpy(cube_copy, cube, sizeof(char) * array_size);
            rotate_666(cube_copy, cube_tmp, array_size, move);
            moves_to_here[cost_to_here] = move;

            if (ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size,
                           type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns)) {
                return 1;
            }
        }

    } else if (cube_size == 7) {

        for (int i = 0; i < MOVE_COUNT_777; i++) {
            move = moves_777[i];

            if (steps_on_same_face_and_layer(move, prev_move)) {
                continue;
            }

            if (!step_allowed_by_ida_search(type, move)) {
                continue;
            }

            char cube_copy[array_size];
            memcpy(cube_copy, cube, sizeof(char) * array_size);
            rotate_777(cube_copy, cube_tmp, array_size, move);
            moves_to_here[cost_to_here] = move;

            if (ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size,
                           type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns)) {
                return 1;
            }
        }

    } else {
        printf("ERROR: ida_search() does not have rotate_xxx() for this cube size\n");
        exit(1);
    }

    return 0;
}


void
free_prune_tables()
{
    if (pt_UD_t_centers_cost_only == NULL) {
        free(pt_UD_t_centers_cost_only);
        pt_UD_t_centers_cost_only = NULL;
    }

    if (pt_UD_x_centers_cost_only == NULL) {
        free(pt_UD_x_centers_cost_only);
        pt_UD_x_centers_cost_only = NULL;
    }

    if (pt_LR_t_centers_cost_only == NULL) {
        free(pt_LR_t_centers_cost_only);
        pt_LR_t_centers_cost_only = NULL;
    }

    if (pt_LR_x_centers_cost_only == NULL) {
        free(pt_LR_x_centers_cost_only);
        pt_LR_x_centers_cost_only = NULL;
    }

    if (UL_centers_cost_only_555 == NULL) {
        free(UL_centers_cost_only_555);
        UL_centers_cost_only_555 = NULL;
    }

    if (UF_centers_cost_only_555 == NULL) {
        free(UF_centers_cost_only_555);
        UF_centers_cost_only_555 = NULL;
    }

    if (LF_centers_cost_only_555 == NULL) {
        free(LF_centers_cost_only_555);
        LF_centers_cost_only_555 = NULL;
    }

    if (LR_inner_x_centers_666 == NULL) {
        free(LR_inner_x_centers_666);
        LR_inner_x_centers_666 = NULL;
    }

    if (LR_oblique_edges_666 == NULL) {
        free(LR_oblique_edges_666);
        LR_oblique_edges_666 = NULL;
    }


    if (ida_explored == NULL) {
        free(ida_explored);
        ida_explored = NULL;
    }


    if (UD_centers_555 == NULL) {
        free(UD_centers_555);
        UD_centers_555 = NULL;
    }

    if (ULFRBD_centers_555 == NULL) {
        free(ULFRBD_centers_555);
        ULFRBD_centers_555 = NULL;
    }

    if (LR_inner_x_centers_and_oblique_edges_666 == NULL) {
        free(LR_inner_x_centers_and_oblique_edges_666);
        LR_inner_x_centers_and_oblique_edges_666 = NULL;
    }
}


int
ida_solve (
    char *cube,
    unsigned int cube_size,
    lookup_table_type type,
    unsigned int orbit0_wide_quarter_turns,
    unsigned int orbit1_wide_quarter_turns)
{
    int MAX_SEARCH_DEPTH = 20;
    move_type moves_to_here[MAX_SEARCH_DEPTH];
    int min_ida_threshold = 0;
    struct ida_heuristic_result result;

    if (ida_search_complete(cube, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, moves_to_here)) {
        LOG("cube already solved\n");
        printf("SOLUTION:\n");
        return 1;
    }

    switch (type)  {

    // 4x4x4
    case CENTERS_STAGE_444:
        ida_prune_table_preload(&centers_cost_444, "lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt");
        UD_centers_cost_only_444 = ida_cost_only_preload("lookup-table-4x4x4-step11-UD-centers-stage.cost-only.txt", 16711681);
        LR_centers_cost_only_444 = ida_cost_only_preload("lookup-table-4x4x4-step12-LR-centers-stage.cost-only.txt", 16711681);
        FB_centers_cost_only_444 = ida_cost_only_preload("lookup-table-4x4x4-step13-FB-centers-stage.cost-only.txt", 16711681);
        break;

    // 5x5x5
    case UD_CENTERS_STAGE_555:
        ida_prune_table_preload(&UD_centers_555, "lookup-table-5x5x5-step10-UD-centers-stage.txt");
        pt_UD_t_centers_cost_only = ida_cost_only_preload("lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.cost-only.txt", 16711681);
        pt_UD_x_centers_cost_only = ida_cost_only_preload("lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.cost-only.txt", 16711681);
        break;

    case LR_CENTERS_STAGE_555:
        ida_prune_table_preload(&LR_centers_555, "lookup-table-5x5x5-step20-LR-centers-stage.txt");
        pt_LR_t_centers_cost_only = ida_cost_only_preload("lookup-table-5x5x5-step21-LR-t-centers-stage.cost-only.txt", 65281);
        pt_LR_x_centers_cost_only = ida_cost_only_preload("lookup-table-5x5x5-step22-LR-x-centers-stage.cost-only.txt", 65281);
        break;

    case CENTERS_SOLVE_555:
        ida_prune_table_preload(&ULFRBD_centers_555, "lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt");
        UL_centers_cost_only_555 = ida_cost_only_preload("lookup-table-5x5x5-step31-UL-centers-solve.hash-cost-only.txt", 24010032);
        UF_centers_cost_only_555 = ida_cost_only_preload("lookup-table-5x5x5-step32-UF-centers-solve.hash-cost-only.txt", 24010032);
        LF_centers_cost_only_555 = ida_cost_only_preload("lookup-table-5x5x5-step33-LF-centers-solve.hash-cost-only.txt", 24010032);
        break;

    // 6x6x6
    case UD_OBLIQUE_EDGES_STAGE_666:
        break;

    case LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_STAGE_666:
        ida_prune_table_preload(&LR_inner_x_centers_and_oblique_edges_666, "lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt");
        LR_oblique_edges_666 = ida_cost_only_preload("lookup-table-6x6x6-step31-LR-oblique-edges-stage.hash-cost-only.txt", 165636908);
        LR_inner_x_centers_666 = ida_cost_only_preload("lookup-table-6x6x6-step32-LR-inner-x-center-stage.cost-only.txt", 65281);
        break;

    // 7x7x7
    case UD_OBLIQUE_EDGES_STAGE_777:
    case LR_OBLIQUE_EDGES_STAGE_777:
        break;

    case STEP40_777:
        ida_prune_table_preload(&step40_777, "lookup-table-7x7x7-step40.txt");
        step41_777 = ida_cost_only_preload("lookup-table-7x7x7-step41.hash-cost-only.txt", 24010032);
        step42_777 = ida_cost_only_preload("lookup-table-7x7x7-step42.hash-cost-only.txt", 24010032);
        break;

    case STEP50_777:
        ida_prune_table_preload(&step50_777, "lookup-table-7x7x7-step50.txt");
        step51_777 = ida_cost_only_preload("lookup-table-7x7x7-step51.hash-cost-only.txt", 24010032);
        step52_777 = ida_cost_only_preload("lookup-table-7x7x7-step52.hash-cost-only.txt", 24010032);
        break;

    case STEP60_777:
        ida_prune_table_preload(&step60_777, "lookup-table-7x7x7-step60.txt");
        step61_777 = ida_cost_only_preload("lookup-table-7x7x7-step61.hash-cost-only.txt", 24010032);
        step62_777 = ida_cost_only_preload("lookup-table-7x7x7-step62.hash-cost-only.txt", 24010032);
        step63_777 = ida_cost_only_preload("lookup-table-7x7x7-step63.hash-cost-only.txt", 6350412);
        break;

    default:
        printf("ERROR: ida_solve() does not yet support this --type\n");
        exit(1);
    }

    result = ida_heuristic(cube, type, 99);
    min_ida_threshold = result.cost_to_goal;
    LOG("min_ida_threshold %d\n", min_ida_threshold);

    for (int threshold = min_ida_threshold; threshold <= MAX_SEARCH_DEPTH; threshold++) {
        ida_count = 0;
        memset(moves_to_here, MOVE_NONE, sizeof(move_type) * MAX_SEARCH_DEPTH);
        hash_delete_all(&ida_explored);

        if (ida_search(0, moves_to_here, threshold, MOVE_NONE, cube, cube_size,
                       type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns)) {
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
    lookup_table_type type = NONE;
    unsigned int cube_size_type = 0;
    unsigned int cube_size_kociemba = 0;
    unsigned int orbit0_wide_quarter_turns = 0;
    unsigned int orbit1_wide_quarter_turns = 0;
    char kociemba[300];
    memset(kociemba, 0, sizeof(char) * 300);

    for (int i = 1; i < argc; i++) {
        if (strmatch(argv[i], "-k") || strmatch(argv[i], "--kociemba")) {
            i++;
            strcpy(kociemba, argv[i]);
            cube_size_kociemba = (unsigned int) sqrt(strlen(kociemba) / 6);

        } else if (strmatch(argv[i], "-t") || strmatch(argv[i], "--type")) {
            i++;

            // 4x4x4
            if (strmatch(argv[i], "4x4x4-centers-stage")) {
                type = CENTERS_STAGE_444;
                cube_size_type = 4;

            // 5x5x5
            } else if (strmatch(argv[i], "5x5x5-UD-centers-stage")) {
                type = UD_CENTERS_STAGE_555;
                cube_size_type = 5;

            } else if (strmatch(argv[i], "5x5x5-LR-centers-stage")) {
                type = LR_CENTERS_STAGE_555;
                cube_size_type = 5;

            } else if (strmatch(argv[i], "5x5x5-centers-solve")) {
                type = CENTERS_SOLVE_555;
                cube_size_type = 5;

            // 6x6x6
            } else if (strmatch(argv[i], "6x6x6-UD-oblique-edges-stage")) {
                type = UD_OBLIQUE_EDGES_STAGE_666;
                cube_size_type = 6;

            } else if (strmatch(argv[i], "6x6x6-LR-inner-x-centers-oblique-edges-stage")) {
                type = LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_STAGE_666,
                cube_size_type = 6;

            // 7x7x7
            } else if (strmatch(argv[i], "7x7x7-UD-oblique-edges-stage")) {
                type = UD_OBLIQUE_EDGES_STAGE_777;
                cube_size_type = 7;

            } else if (strmatch(argv[i], "7x7x7-LR-oblique-edges-stage")) {
                type = LR_OBLIQUE_EDGES_STAGE_777;
                cube_size_type = 7;

            } else if (strmatch(argv[i], "7x7x7-step40")) {
                type = STEP40_777;
                cube_size_type = 7;

            } else if (strmatch(argv[i], "7x7x7-step50")) {
                type = STEP50_777;
                cube_size_type = 7;

            } else if (strmatch(argv[i], "7x7x7-step60")) {
                type = STEP60_777;
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

        } else if (strmatch(argv[i], "-h") || strmatch(argv[i], "--help")) {
            printf("\nida_search --kociemba KOCIEMBA_STRING --type 5x5x5-UD-centers-stage\n\n");
            exit(0);

        } else {
            printf("ERROR: %s is an invalid arg\n", argv[i]);
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

    if (cube_size_kociemba < 2 || cube_size_kociemba > 7) {
        printf("ERROR: only 2x2x2 through 7x7x7 cubes are supported, yours is %dx%dx%d\n", cube_size_kociemba, cube_size_kociemba, cube_size_kociemba);
        exit(1);
    }

    unsigned int cube_size = cube_size_kociemba;
    array_size = (cube_size * cube_size * 6) + 2;
    char cube[array_size];
    char cube_tmp[array_size];

    if (orbit1_wide_quarter_turns && cube_size != 6) {
        printf("ERROR cannot do avoid_oll on orbit1 for %dx%dx%d cubes", cube_size, cube_size, cube_size);
        exit(1);
    }

    sp_cube_state = malloc(sizeof(char) * array_size);
    memset(cube_tmp, 0, sizeof(char) * array_size);
    init_cube(cube, cube_size, type, kociemba);

    // print_cube(cube, cube_size);
    ida_solve(cube, cube_size, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns);

    // free_prune_tables();

    // Print the maximum resident set size used (in MB).
    struct rusage r_usage;
    getrusage(RUSAGE_SELF, &r_usage);
    printf("Memory usage: %lu MB\n", (unsigned long) r_usage.ru_maxrss / (1024 * 1024));
}
