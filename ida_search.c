
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

/*
typedef enum {
    NONE,
    CPU_FAST,
    CPU_NORMAL,
    CPU_SLOW,
} cpu_mode_type;
*/

// Supported IDA searches
typedef enum {
    NONE,

    // 4x4x4
    CENTERS_STAGE_444,
    REDUCE_333_444,

    // 5x5x5
    UD_CENTERS_STAGE_555,
    LR_CENTERS_STAGE_555,
    CENTERS_SOLVE_555,

    // 6x6x6
    UD_OBLIQUE_EDGES_STAGE_666,
    LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_STAGE_666,
    LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_SOLVE_666,

    // 7x7x7
    UD_OBLIQUE_EDGES_STAGE_777,
    LR_OBLIQUE_EDGES_STAGE_777,
    STEP40_777,
    STEP50_777,
    STEP60_777,
    STEP70_777,

} lookup_table_type;

struct key_value_pair *ida_explored = NULL;

// 4x4x4
struct key_value_pair *centers_cost_444 = NULL;
char *UD_centers_cost_only_444 = NULL;
char *LR_centers_cost_only_444 = NULL;
char *FB_centers_cost_only_444 = NULL;

struct key_value_pair *reduce_333_444 = NULL;
char *reduce_333_edges_only = NULL;
char *reduce_333_centers_only = NULL;
struct wings_for_edges_recolor_pattern_444 *wings_for_recolor_444;

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
struct key_value_pair *LR_inner_x_centers_and_oblique_edges_stage_666 = NULL;
char *LR_inner_x_centers_666 = NULL;
char *LR_oblique_edges_666 = NULL;

struct key_value_pair *LFRB_inner_x_centers_and_oblique_edges_solve_666 = NULL;
char *LR_inner_x_centers_and_oblique_edges_solve_666 = NULL;
char *FB_inner_x_centers_and_oblique_edges_solve_666 = NULL;


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

struct key_value_pair *step70_777 = NULL;


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

unsigned int
wide_turn_count(move_type *moves)
{
    int i = 0;
    unsigned int count = 0;

    while (moves[i] != MOVE_NONE) {
        switch (moves[i]) {
        case Uw:
        case Uw_PRIME:
        case Uw2:
        case Lw:
        case Lw_PRIME:
        case Lw2:
        case Fw:
        case Fw_PRIME:
        case Fw2:
        case Rw:
        case Rw_PRIME:
        case Rw2:
        case Bw:
        case Bw_PRIME:
        case Bw2:
        case Dw:
        case Dw_PRIME:
        case Dw2:
            count += 1;
            break;
        default:
            break;
        }
        i++;
    }

    return count;
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

    case REDUCE_333_444:
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

    case LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_SOLVE_666:
        // Convert to 1s and 0s
        str_replace_for_binary(cube, ones_LF);
        print_cube(cube, size);
        break;

    case CENTERS_SOLVE_555:
        // Remember what the cube looked like so we can restore the edges
        memcpy(cube_copy, cube, sizeof(char) * array_size);

        // Convert to 1s and 0s
        str_replace_for_binary(cube, ones_ULF);
        unsigned int offset = 0;

        // Restore the edges
        for (int side_index = 0; side_index < 6; side_index++) {
            cube[2 + offset] = cube_copy[2 + offset];
            cube[3 + offset] = cube_copy[3 + offset];
            cube[4 + offset] = cube_copy[4 + offset];

            cube[6 + offset] = cube_copy[6 + offset];
            cube[11 + offset] = cube_copy[11 + offset];
            cube[16 + offset] = cube_copy[16 + offset];

            cube[10 + offset] = cube_copy[10 + offset];
            cube[15 + offset] = cube_copy[15 + offset];
            cube[20 + offset] = cube_copy[20 + offset];

            cube[22 + offset] = cube_copy[22 + offset];
            cube[23 + offset] = cube_copy[23 + offset];
            cube[24 + offset] = cube_copy[24 + offset];
            offset += 25;
        }

        print_cube(cube, size);
        break;

    case STEP40_777:
    case STEP50_777:
    case STEP60_777:
    case STEP70_777:
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

    } else if (strmatch(filename, "lookup-table-4x4x4-step30-reduce333.txt")) {

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // DDDDLLLLBBBBRRRRFFFFUUUU10362745a8b9ecfdhgkiljnm:R2 Bw2 D' F2 D Bw2
            // 0..47 are the state
            // 48 is the :
            // 49 is the move count
            buffer[48] = '\0';
            cost = atoi(&buffer[49]);
            hash_add(hashtable, buffer, cost);
        }

    } else if (strmatch(filename, "lookup-table-5x5x5-step10-UD-centers-stage.txt")) {

        // The hash_add() here is the expensive part but disk IO is a factor.  If I
        // comment out hash_add():
        // - fread() the entire file takes 15ms and 14M of memory
        // - fgets() line by line takes 55ms but 0M of memory
        //
        // With hash_add():
        // - fread() takes 419ms
        // - fgets() takes 470ms

        /*
        int size = 14759145;
        char *ptr = malloc(sizeof(char) * size);
        char *orig_ptr = ptr;
        memset(ptr, 0, sizeof(char) * size);
        int line_length = 17;
        int line_count = 868185;

        if (fread(ptr, size, 1, fh_read)) {
            fclose(fh_read);

            for (int i = 0; i < line_count; i++) {
                ptr[14] = '\0';
                cost = atoi(&ptr[15]);
                hash_add(hashtable, ptr, cost);
                ptr += line_length;
            }
            free(orig_ptr);
            orig_ptr = NULL;

            //LOG("ida_prune_table_preload %s: end\n", filename);
            //exit(0);
        } else {
            printf("ERROR: ida_prune_table_preload read failed %s\n", filename);
            exit(1);
        }
        */

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // 0..13 are the state
            // 14 is the :
            // 15 is the move count
            buffer[14] = '\0';
            cost = atoi(&buffer[15]);
            hash_add(hashtable, buffer, cost);
        }

    } else if (strmatch(filename, "lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt")) {

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


    } else if (strmatch(filename, "lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt") ||
        strmatch(filename, "lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt")) {

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

    } else if (strmatch(filename, "lookup-table-7x7x7-step70.txt")) {

        while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
            // 0002001ffefff:4
            // 0..12 are the state
            // 13 is the :
            // 14 is the move count
            buffer[13] = '\0';
            cost = atoi(&buffer[14]);
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
ida_heuristic (char *cube, lookup_table_type type, unsigned int max_cost_to_goal, cpu_mode_type cpu_mode)
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
            FB_centers_cost_only_444,
            cpu_mode);

    case REDUCE_333_444:
        return ida_heuristic_reduce_333_444(
            cube,
            max_cost_to_goal,
            &reduce_333_444,
            reduce_333_edges_only,
            reduce_333_centers_only,
            wings_for_recolor_444);

    // 5x5x5
    case UD_CENTERS_STAGE_555:
        return ida_heuristic_UD_centers_555(
            cube,
            max_cost_to_goal,
            &UD_centers_555,
            pt_UD_t_centers_cost_only,
            pt_UD_x_centers_cost_only,
            cpu_mode);

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
            &LR_inner_x_centers_and_oblique_edges_stage_666,
            LR_inner_x_centers_666,
            LR_oblique_edges_666);

    case LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_SOLVE_666:
        return ida_heuristic_LFRB_inner_x_centers_and_oblique_edges_solve_666(
            cube,
            max_cost_to_goal,
            &LFRB_inner_x_centers_and_oblique_edges_solve_666,
            LR_inner_x_centers_and_oblique_edges_solve_666,
            FB_inner_x_centers_and_oblique_edges_solve_666);

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

    case STEP70_777:
        return ida_heuristic_step70_777(
            cube,
            max_cost_to_goal,
            &step70_777,
            step61_777,
            step62_777);
    default:
        printf("ERROR: ida_heuristic() does not yet support this --type\n");
        exit(1);
    }
}


unsigned int
get_orbit0_wide_half_turn_count (move_type *moves)
{
    unsigned int i = 0;
    unsigned int count = 0;

    while (moves[i] != MOVE_NONE) {
        switch (moves[i]) {
        case Uw2:
        case Lw2:
        case Fw2:
        case Rw2:
        case Bw2:
        case Dw2:
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

unsigned int
get_outer_layer_quarter_turn_count(move_type *moves)
{
    unsigned int i = 0;
    unsigned int count = 0;

    while (moves[i] != MOVE_NONE) {
        switch (moves[i]) {
        case U:
        case U_PRIME:
        case L:
        case L_PRIME:
        case F:
        case F_PRIME:
        case R:
        case R_PRIME:
        case B:
        case B_PRIME:
        case D:
        case D_PRIME:
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


int
ida_search_complete (
    char *cube,
    lookup_table_type type,
    unsigned int orbit0_wide_quarter_turns,
    unsigned int orbit1_wide_quarter_turns,
    unsigned int avoid_pll,
    move_type *moves_to_here)
{
    struct key_value_pair * pt_entry = NULL;
    unsigned int orbit0_wide_half_turn_count = 0;
    unsigned int orbit0_wide_quarter_turn_count = 0;
    unsigned int orbit1_wide_quarter_turn_count = 0;
    unsigned int outer_layer_quarter_turn_count = 0;
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

    switch (type)  {
    // 4x4x4
    case CENTERS_STAGE_444:
        return ida_search_complete_centers_444(cube);

    case REDUCE_333_444:
        result = ida_search_complete_reduce_333_444(cube);

        if (result) {

            // This will only be true when solving 4x4x4 phase3 where we must avoid PLL. To avoid
            // PLL the edge parity and corner parity must match (both odd or both even).
            if (avoid_pll) {
                FILE *fp;
                char path[64];
                char command[256];

                memset(command, '\0', 256);
                strcpy(command, "usr/bin/has_pll.py ");
                unsigned int command_i = strlen(command);

                for (unsigned int i = 1; i <= 96; i++) {
                    command[command_i] = cube[i];
                    command_i++;
                }

                /* Open the command for reading. */
                fp = popen(command, "r");
                if (fp == NULL) {
                    printf("Failed to run command\n" );
                    exit(1);
                }

                /* Read the output a line at a time - output it. */
                while (fgets(path, sizeof(path)-1, fp) != NULL) {
                    if (strmatch(path, "True\n")) {
                        //LOG("Found solution but it has PLL\n");
                        result = 0;
                        break;
                    } else if (strmatch(path, "False\n")) {
                        LOG("Found solution without PLL\n");
                        result = 1;
                        break;
                    } else {
                        printf("ERROR: invalid has_pll.py output %s\n", path);
                        exit(1);
                    }
                }

                /* close */
                pclose(fp);

                return result;
            }
            return 1;

        } else {
            return 0;
        }


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

    case LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_SOLVE_666:
        return ida_search_complete_LFRB_inner_x_centers_and_oblique_edges_solve(cube);

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

    case STEP70_777:
        return ida_search_complete_step70_777(cube);

    default:
        printf("ERROR: ida_search_complete() does not yet support type %d\n", type);
        exit(1);
    }

    return 0;
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

    case REDUCE_333_444:
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
        case L:
        case L_PRIME:
        case R:
        case R_PRIME:
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

        // Uncomment if LR are staged to one of 432 states
        // case L:
        // case L_PRIME:
        // case R:
        // case R_PRIME:
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

    case LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_SOLVE_666:
        switch (move) {
        // do not mess up staged centers
        case threeUw:
        case threeUw_PRIME:
        case threeDw:
        case threeDw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeRw2:
        case threeLw2:
        case threeFw2:
        case threeBw2:
        case Uw:
        case Uw_PRIME:
        case Dw:
        case Dw_PRIME:
        case Lw:
        case Lw_PRIME:
        case Rw:
        case Rw_PRIME:
        case Fw:
        case Fw_PRIME:
        case Bw:
        case Bw_PRIME:

        // can skip these for 6x6x6 cubes
        //case threeLw:
        //case threeLw_PRIME:
        //case threeLw2:
        //case threeDw:
        //case threeDw_PRIME:
        case threeDw2:
        //case threeBw:
        //case threeBw_PRIME:
        //case threeBw2:
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
    case STEP70_777:
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

struct ida_search_result {
    unsigned int f_cost;
    unsigned int found_solution;
};

struct ida_search_result
ida_search (unsigned int cost_to_here,
            move_type *moves_to_here,
            unsigned int threshold,
            move_type prev_move,
            char *cube,
            unsigned int cube_size,
            lookup_table_type type,
            unsigned int orbit0_wide_quarter_turns,
            unsigned int orbit1_wide_quarter_turns,
            unsigned int avoid_pll,
            cpu_mode_type cpu_mode)
{
    unsigned int cost_to_goal = 0;
    unsigned int f_cost = 0;
    move_type move, skip_other_steps_this_face;
    struct ida_heuristic_result heuristic_result;
    char cube_tmp[array_size];
    char cost_to_here_str[3];
    skip_other_steps_this_face = MOVE_NONE;
    struct ida_search_result search_result, tmp_search_result;

    ida_count++;
    unsigned int max_cost_to_goal = threshold - cost_to_here;
    heuristic_result = ida_heuristic(cube, type, max_cost_to_goal, cpu_mode);
    cost_to_goal = heuristic_result.cost_to_goal;
    f_cost = cost_to_here + cost_to_goal;
    search_result.f_cost = f_cost;
    search_result.found_solution = 0;

    // Abort Searching
    if (f_cost >= threshold) {
        //if (debug) {
        //    LOG("IDA prune f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
        //        f_cost, threshold, cost_to_here, cost_to_goal);
        //    LOG("\n");
        //}
        return search_result;
    }

    if (ida_search_complete(cube, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, avoid_pll, moves_to_here)) {
        // We are finished!!
        LOG("IDA count %d, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
            ida_count, f_cost, threshold, cost_to_here, cost_to_goal);
        print_moves(moves_to_here, cost_to_here);
        search_result.found_solution = 1;
        return search_result;
    }

    sprintf(cost_to_here_str, "%d", cost_to_here);
    strcat(heuristic_result.lt_state, cost_to_here_str);

    if (hash_find(&ida_explored, heuristic_result.lt_state)) {
        return search_result;
    }

    hash_add(&ida_explored, heuristic_result.lt_state, 0);

    if (cube_size == 4) {

        for (int i = 0; i < MOVE_COUNT_444; i++) {
            move = moves_444[i];

            if (steps_on_same_face_and_layer(move, prev_move)) {
                continue;
            }

            if (!step_allowed_by_ida_search(type, move)) {
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

            char cube_copy[array_size];
            memcpy(cube_copy, cube, sizeof(char) * array_size);
            rotate_444(cube_copy, cube_tmp, array_size, move);
            moves_to_here[cost_to_here] = move;

            tmp_search_result = ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size,
                                           type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, avoid_pll, cpu_mode);

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

    } else if (cube_size == 5) {

        for (int i = 0; i < MOVE_COUNT_555; i++) {
            move = moves_555[i];

            if (steps_on_same_face_and_layer(move, prev_move)) {
                continue;
            }

            if (!step_allowed_by_ida_search(type, move)) {
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

            char cube_copy[array_size];
            memcpy(cube_copy, cube, sizeof(char) * array_size);
            rotate_555(cube_copy, cube_tmp, array_size, move);
            moves_to_here[cost_to_here] = move;

            tmp_search_result = ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size,
                                           type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, avoid_pll, cpu_mode);

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

    } else if (cube_size == 6) {

        for (int i = 0; i < MOVE_COUNT_666; i++) {
            move = moves_666[i];

            if (steps_on_same_face_and_layer(move, prev_move)) {
                continue;
            }

            if (!step_allowed_by_ida_search(type, move)) {
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

            char cube_copy[array_size];
            memcpy(cube_copy, cube, sizeof(char) * array_size);
            rotate_666(cube_copy, cube_tmp, array_size, move);
            moves_to_here[cost_to_here] = move;

            tmp_search_result = ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size,
                                           type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, avoid_pll, cpu_mode);

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

    } else if (cube_size == 7) {

        for (int i = 0; i < MOVE_COUNT_777; i++) {
            move = moves_777[i];

            if (steps_on_same_face_and_layer(move, prev_move)) {
                continue;
            }

            if (!step_allowed_by_ida_search(type, move)) {
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

            char cube_copy[array_size];
            memcpy(cube_copy, cube, sizeof(char) * array_size);
            rotate_777(cube_copy, cube_tmp, array_size, move);
            moves_to_here[cost_to_here] = move;

            tmp_search_result = ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, cube_size,
                                           type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, avoid_pll, cpu_mode);

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

    } else {
        printf("ERROR: ida_search() does not have rotate_xxx() for this cube size\n");
        exit(1);
    }

    return search_result;
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

    if (LR_inner_x_centers_and_oblique_edges_stage_666 == NULL) {
        free(LR_inner_x_centers_and_oblique_edges_stage_666);
        LR_inner_x_centers_and_oblique_edges_stage_666 = NULL;
    }

    if (LFRB_inner_x_centers_and_oblique_edges_solve_666 == NULL) {
        free(LFRB_inner_x_centers_and_oblique_edges_solve_666);
        LFRB_inner_x_centers_and_oblique_edges_solve_666 = NULL;
    }
}


int
ida_solve (
    char *cube,
    unsigned int cube_size,
    lookup_table_type type,
    unsigned int orbit0_wide_quarter_turns,
    unsigned int orbit1_wide_quarter_turns,
    unsigned int avoid_pll,
    cpu_mode_type cpu_mode)
{
    int MAX_SEARCH_DEPTH = 30;
    move_type moves_to_here[MAX_SEARCH_DEPTH];
    int min_ida_threshold = 0;
    struct ida_heuristic_result heuristic_result;
    struct ida_search_result search_result;

    memset(moves_to_here, MOVE_NONE, MAX_SEARCH_DEPTH);

    if (ida_search_complete(cube, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, avoid_pll, moves_to_here)) {
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

    case REDUCE_333_444:
        ida_prune_table_preload(&reduce_333_444, "lookup-table-4x4x4-step30-reduce333.txt");
        reduce_333_edges_only = ida_cost_only_preload("lookup-table-4x4x4-step31-reduce333-edges.hash-cost-only.txt", 239500848);
        reduce_333_centers_only = ida_cost_only_preload("lookup-table-4x4x4-step32-reduce333-centers.hash-cost-only.txt", 58832);
        wings_for_recolor_444 = init_wings_for_edges_recolor_pattern_444();
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
        ida_prune_table_preload(&LR_inner_x_centers_and_oblique_edges_stage_666, "lookup-table-6x6x6-step30-LR-inner-x-centers-oblique-edges-stage.txt");
        LR_oblique_edges_666 = ida_cost_only_preload("lookup-table-6x6x6-step31-LR-oblique-edges-stage.hash-cost-only.txt", 165636908);
        LR_inner_x_centers_666 = ida_cost_only_preload("lookup-table-6x6x6-step32-LR-inner-x-center-stage.cost-only.txt", 65281);
        break;

    case LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_SOLVE_666:
        ida_prune_table_preload(&LFRB_inner_x_centers_and_oblique_edges_solve_666, "lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt");
        LR_inner_x_centers_and_oblique_edges_solve_666 = ida_cost_only_preload("lookup-table-6x6x6-step61-LR-solve-inner-x-center-and-oblique-edges.cost-only.txt", 16773121);
        FB_inner_x_centers_and_oblique_edges_solve_666 = ida_cost_only_preload("lookup-table-6x6x6-step62-FB-solve-inner-x-center-and-oblique-edges.cost-only.txt", 16773121);

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

    case STEP70_777:
        ida_prune_table_preload(&step70_777, "lookup-table-7x7x7-step70.txt");
        step61_777 = ida_cost_only_preload("lookup-table-7x7x7-step61.hash-cost-only.txt", 24010032);
        step62_777 = ida_cost_only_preload("lookup-table-7x7x7-step62.hash-cost-only.txt", 24010032);
        step63_777 = ida_cost_only_preload("lookup-table-7x7x7-step63.hash-cost-only.txt", 6350412);
        break;

    default:
        printf("ERROR: ida_solve() does not yet support this --type\n");
        exit(1);
    }

    heuristic_result = ida_heuristic(cube, type, 99, cpu_mode);
    min_ida_threshold = heuristic_result.cost_to_goal;
    LOG("min_ida_threshold %d\n", min_ida_threshold);

    for (int threshold = min_ida_threshold; threshold <= MAX_SEARCH_DEPTH; threshold++) {
        ida_count = 0;
        memset(moves_to_here, MOVE_NONE, sizeof(move_type) * MAX_SEARCH_DEPTH);
        hash_delete_all(&ida_explored);

        search_result = ida_search(0, moves_to_here, threshold, MOVE_NONE, cube, cube_size,
                                   type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns,
                                   avoid_pll, cpu_mode);

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
    lookup_table_type type = NONE;
    unsigned int cube_size_type = 0;
    unsigned int cube_size_kociemba = 0;
    unsigned int orbit0_wide_quarter_turns = 0;
    unsigned int orbit1_wide_quarter_turns = 0;
    unsigned int avoid_pll = 0;
    char kociemba[300];
    memset(kociemba, 0, sizeof(char) * 300);
    cpu_mode_type cpu_mode = CPU_FAST;

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

            } else if (strmatch(argv[i], "4x4x4-reduce-333")) {
                type = REDUCE_333_444;
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

            } else if (strmatch(argv[i], "6x6x6-LFRB-solve-inner-x-center-and-oblique-edges")) {
                type = LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_SOLVE_666,
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

            } else if (strmatch(argv[i], "7x7x7-step70")) {
                type = STEP70_777;
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

        } else if (strmatch(argv[i], "--avoid-pll")) {
            avoid_pll = 1;

        } else if (strmatch(argv[i], "--fast")) {
            cpu_mode = CPU_FAST;

        } else if (strmatch(argv[i], "--normal")) {
            cpu_mode = CPU_NORMAL;

        } else if (strmatch(argv[i], "--slow")) {
            cpu_mode = CPU_SLOW;

        } else if (strmatch(argv[i], "-h") || strmatch(argv[i], "--help")) {
            printf("\nida_search --kociemba KOCIEMBA_STRING --type 5x5x5-UD-centers-stage\n\n");
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
    ida_solve(cube, cube_size, type, orbit0_wide_quarter_turns, orbit1_wide_quarter_turns, avoid_pll, cpu_mode);

    // free_prune_tables();

    // Print the maximum resident set size used (in MB).
    struct rusage r_usage;
    getrusage(RUSAGE_SELF, &r_usage);
    printf("Memory usage: %lu MB\n", (unsigned long) r_usage.ru_maxrss / (1024 * 1024));
}
