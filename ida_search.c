
#include <ctype.h>
#include <math.h>
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include "uthash.h"
#include "rotate_xxx.h"


// To compile:
//  gcc -o ida_search ida_search.c rotate_xxx.c -lm
//
//  gcc -ggdb -o ida_search ida_search.c rotate_xxx.c -lm

// scratchpads that we do not want to allocate over and over again
char sp_binary_search[255];
char *sp_cube_state;
char *sp_cube_state_binary;
unsigned long array_size;
unsigned long ida_count;
unsigned long seek_calls = 0;

typedef enum {
    NONE,

    // 5x5x5
    UD_CENTERS_STAGE_555,

} lookup_table_type;


void LOG(const char *fmt, ...) {
    char date[20];
    struct timeval tv;
    va_list args;

    /* print the progname, version, and timestamp */
    gettimeofday(&tv, NULL);
    strftime(date, sizeof(date) / sizeof(*date), "%Y-%m-%dT%H:%M:%S", gmtime(&tv.tv_sec));
    printf("[%s.%03d] ", date, (int)tv.tv_usec / 1000);

    /* printf like normal */
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
}


// uthash references
// http://troydhanson.github.io/uthash/index.html
// https://cfsa-pmw.warwick.ac.uk/SDF/SDF_C/blob/3cf5bf49856ef9ee4080cf6722cf9058a1e28b01/src/uthash/tests/example.c
//
struct key_value_pair {
    char state[64]; /* we'll use this field as the key */
    unsigned long value;
    UT_hash_handle hh; /* makes this structure hashable */
};

void
hash_add (struct key_value_pair **hashtable, char *state_key, unsigned long value)
{
    struct key_value_pair *s;

    s = malloc(sizeof(struct key_value_pair));
    strcpy(s->state, state_key);
    s->value = value;

    HASH_ADD_STR(*hashtable, state, s);
}

struct key_value_pair *
hash_find (struct key_value_pair **hashtable, char *state_key)
{
    struct key_value_pair *s = NULL;
    HASH_FIND_STR(*hashtable, state_key, s);
    return s;
}

void
hash_delete (struct key_value_pair **hashtable, struct key_value_pair *s)
{
    HASH_DEL(*hashtable, s);
    free(s);
}

void
hash_delete_all(struct key_value_pair **hashtable)
{
    struct key_value_pair *s, *tmp;

    HASH_ITER(hh, *hashtable, s, tmp) {
        HASH_DEL(*hashtable, s);
        free(s);
    }
}

unsigned long
hash_count (struct key_value_pair **hashtable)
{
    struct key_value_pair *s;
    unsigned long count = 0;

    for (s = *hashtable; s != NULL; s= (struct key_value_pair*)(s->hh.next)) {
        count++;
    }

    return count;
}


void
hash_print_all (struct key_value_pair **hashtable)
{
    struct key_value_pair *s;

    for(s = *hashtable; s != NULL; s= (struct key_value_pair*)(s->hh.next)) {
        printf("key %s  value %lu\n", s->state, s->value);
    }
}



struct key_value_pair *ida_explored = NULL;
struct key_value_pair *pt_t_centers = NULL;
struct key_value_pair *pt_x_centers = NULL;
struct key_value_pair *UD_centers_555 = NULL;

char *pt_t_centers_cost_only = NULL;
char *pt_x_centers_cost_only = NULL;



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
                    strcpy(sp_binary_search, line);
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


void
print_cube(char *cube, int size)
{
    int squares_per_side = size * size;
    int square_count = squares_per_side * 6;
    int rows = size * 3;

    for (int row=1; row <= rows; row++) {

        // U
        if (row <= size) {
            int i = ((row-1) * size) + 1;
            int i_end = i + size - 1;
            printf("\t");
            for ( ; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }
            printf("\n");

        // D
        } else if (row > (size * 2)) {
            int i = (squares_per_side * 5) + 1 + ((row - (size*2) - 1) * size);
            int i_end = i + size - 1;
            printf("\t");
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }
            printf("\n");

        // L, F, R, B
        } else {

            // L
            int i_start = squares_per_side + 1 + ((row - 1 -size) * size);
            int i_end = i_start + size - 1;
            int i = i_start;
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            // F
            i = i_start + squares_per_side;
            i_end = i + size - 1;
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            // R
            i = i_start + (squares_per_side * 2);
            i_end = i + size - 1;
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            // B
            i = i_start + (squares_per_side * 3);
            i_end = i + size - 1;
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            printf("\n");
        }
    }
    printf("\n");
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

            while (ones[j] != '\0') {

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
str_replace_list_of_chars (char *str, char *old, char new)
{
    int i = 0;
    int j;

    /* Run till end of string */
    while (str[i] != '\0') {

        j = 0;

        while (old[j] != '\0') {

            /* If occurrence of character is found */
            if (str[i] == old[j]) {
                str[i] = new;
                break;
            }
            j++;
        }

        i++;
    }
}


unsigned long
max (unsigned long a, unsigned long b)
{
    if (a >= b) {
        return a;
    } else {
        return b;
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

    char ones_UD[3] = {'U', 'D'};

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
    case UD_CENTERS_STAGE_555:
        // Convert to 1s and 0s
        str_replace_for_binary(cube, ones_UD);
        print_cube(cube, size);
        break;
    default:
        printf("ERROR: init_cube() does not yet support this --type\n");
        exit(1);
    }
}


/*
 * 5x5x5 template

sprintf(sp_cube_state,
    "%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c",
    cube[1], cube[2], cube[3], cube[4], cube[5],
    cube[6], cube[7], cube[8], cube[9], cube[10],
    cube[11], cube[12], cube[13], cube[14], cube[15],
    cube[16], cube[17], cube[18], cube[19], cube[20],
    cube[21], cube[22], cube[23], cube[24], cube[25],

    cube[26], cube[27], cube[28], cube[29], cube[30],
    cube[31], cube[32], cube[33], cube[34], cube[35],
    cube[36], cube[37], cube[38], cube[39], cube[40],
    cube[41], cube[42], cube[43], cube[44], cube[45],
    cube[46], cube[47], cube[48], cube[49], cube[50],

    cube[51], cube[52], cube[53], cube[54], cube[55],
    cube[56], cube[57], cube[58], cube[59], cube[60],
    cube[61], cube[62], cube[63], cube[64], cube[65],
    cube[66], cube[67], cube[68], cube[69], cube[70],
    cube[71], cube[72], cube[73], cube[74], cube[75],

    cube[76], cube[77], cube[78], cube[79], cube[80],
    cube[81], cube[82], cube[83], cube[84], cube[85],
    cube[86], cube[87], cube[88], cube[89], cube[90],
    cube[91], cube[92], cube[93], cube[94], cube[95],
    cube[96], cube[97], cube[98], cube[99], cube[100],

    cube[101], cube[102], cube[103], cube[104], cube[105],
    cube[106], cube[107], cube[108], cube[109], cube[110],
    cube[111], cube[112], cube[113], cube[114], cube[115],
    cube[116], cube[117], cube[118], cube[119], cube[120],
    cube[121], cube[122], cube[123], cube[124], cube[125],

    cube[126], cube[127], cube[128], cube[129], cube[130],
    cube[131], cube[132], cube[133], cube[134], cube[135],
    cube[136], cube[137], cube[138], cube[139], cube[140],
    cube[141], cube[142], cube[143], cube[144], cube[145],
    cube[146], cube[147], cube[148], cube[149], cube[150]);

*/


void
get_555_centers(char *cube)
{
    // memset(sp_cube_state, 0, sizeof(char) * array_size);

    sprintf(sp_cube_state,
        "%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c",
        // Upper
        cube[7], cube[8], cube[9],
        cube[12], cube[13], cube[14],
        cube[17], cube[18], cube[19],

        // Left
        cube[32], cube[33], cube[34],
        cube[37], cube[38], cube[39],
        cube[42], cube[43], cube[44],

        // Front
        cube[57], cube[58], cube[59],
        cube[62], cube[63], cube[64],
        cube[67], cube[68], cube[69],

        // Right
        cube[82], cube[83], cube[84],
        cube[87], cube[88], cube[89],
        cube[92], cube[93], cube[94],

        // Back
        cube[107], cube[108], cube[109],
        cube[112], cube[113], cube[114],
        cube[117], cube[118], cube[119],

        // Down
        cube[132], cube[133], cube[134],
        cube[137], cube[138], cube[139],
        cube[142], cube[143], cube[144]);
}


unsigned long
get_555_t_centers(char *cube)
{
    int MAX_PT_STATE_CHARS = 25;
    char pt_state[MAX_PT_STATE_CHARS];

    sprintf(pt_state,
        "%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c",
        // Upper
        cube[8],
        cube[12], cube[14],
        cube[18],

        // Left
        cube[33],
        cube[37], cube[39],
        cube[43],

        // Front
        cube[58],
        cube[62], cube[64],
        cube[68],

        // Right
        cube[83],
        cube[87], cube[89],
        cube[93],

        // Back
        cube[108],
        cube[112], cube[114],
        cube[118],

        // Down
        cube[133],
        cube[137], cube[139],
        cube[143]);

    return strtoul(pt_state, NULL, 2);
}


unsigned long
get_555_x_centers(char *cube)
{
    int MAX_PT_STATE_CHARS = 25;
    char pt_state[MAX_PT_STATE_CHARS];

    sprintf(pt_state,
        "%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c%c",
        // Upper
        cube[7], cube[9],
        cube[17], cube[19],

        // Left
        cube[32], cube[34],
        cube[42], cube[44],

        // Front
        cube[57], cube[59],
        cube[67], cube[69],

        // Right
        cube[82], cube[84],
        cube[92], cube[94],

        // Back
        cube[107], cube[109],
        cube[117], cube[119],

        // Down
        cube[132], cube[134],
        cube[142], cube[144]);

    return strtoul(pt_state, NULL, 2);
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
ida_prune_table_preload (struct key_value_pair **hashtable, char *filename, int linewidth)
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

    //while (fread(buffer, linewidth-1, 1, fh_read)) { // crashes...dig more later
    while (fgets(buffer, BUFFER_SIZE, fh_read) != NULL) {
        strstrip(buffer);

        // strtok modifies the buffer so make a copy
        strcpy(token_buffer, buffer);
        token_ptr = strtok(token_buffer, ":");
        strcpy(state, token_ptr);

        token_ptr = strtok(NULL, ":");
        strcpy(moves, token_ptr);
        cost = moves_cost(moves);

        // LOG("ida_prune_table_preload %s, state %s, moves %s, cost %d\n", filename, state, moves, cost);
        hash_add(hashtable, state, cost);
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


unsigned long
hex_to_int(char value)
{
    switch (value) {
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
        printf("ERROR: hex_to_int does not support %c", value);
        exit(1);
    };
}

unsigned long
ida_heuristic (char *cube, lookup_table_type type, int debug)
{
    unsigned long cost_to_goal = 0;
    unsigned long UD_t_centers_state = 0;
    unsigned long UD_x_centers_state = 0;
    unsigned long UD_t_centers_cost = 0;
    unsigned long UD_x_centers_cost = 0;

    switch (type)  {
    case UD_CENTERS_STAGE_555:
        // dwalton

        UD_t_centers_state = get_555_t_centers(cube);
        UD_t_centers_cost = hex_to_int(pt_t_centers_cost_only[UD_t_centers_state]);

        if (debug) {
            LOG("ida_heuristic t-centers state %d or 0x%x, cost %d\n", UD_t_centers_state, UD_t_centers_state, UD_t_centers_cost);
        }

        UD_x_centers_state = get_555_x_centers(cube);
        UD_x_centers_cost = hex_to_int(pt_x_centers_cost_only[UD_x_centers_state]);

        if (debug) {
            LOG("ida_heuristic x-centers state %d or 0x%x, cost %d\n", UD_x_centers_state, UD_x_centers_state, UD_x_centers_cost);
        }

        cost_to_goal = max(UD_t_centers_cost, UD_x_centers_cost);

        if (debug) {
            LOG("ida_heuristic t-centers %d, x-centers %d, cost_to_goal %d\n", UD_t_centers_cost, UD_x_centers_cost, cost_to_goal);
        }
        break;

    default:
        printf("ERROR: ida_heuristic() does not yet support this --type\n");
        exit(1);
    }

    return cost_to_goal;
}


/* Load the cube state into the scratchpad sp_cube_state */
void
ida_load_cube_state (char *cube, lookup_table_type type)
{
    switch (type)  {
    case UD_CENTERS_STAGE_555:
        get_555_centers(cube);

        // convert to hex, pad 0s up to 14 characters
        sprintf(sp_cube_state, "%014lx", strtoul(sp_cube_state, NULL, 2));
        //LOG("ida_load_cube_state() %s\n", sp_cube_state);
        break;

    default:
        printf("ERROR: ida_load_cube_state() does not yet support type %d\n", type);
        exit(1);
    }
}


int
ida_search_complete (char *cube, lookup_table_type type)
{
    struct key_value_pair * pt_entry = NULL;
    // ida_load_cube_state(cube, type) MUST be called prior to calling this.

    // LOG("ida_search_complete %s\n", sp_cube_state);
    switch (type)  {
    case UD_CENTERS_STAGE_555:

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
            LOG("UD_CENTERS_STAGE_555 sp_cube_state %s\n", sp_cube_state);
            return 1;
        } else {
            return 0;
        }

        /*
        // 3fe000000001ff
        if (strmatch(sp_cube_state, "3fe000000001ff")) {
            LOG("UD_CENTERS_STAGE_555 sp_cube_state %s\n", sp_cube_state);
            return 1;
        }
        */

        LOG("UD_CENTERS_STAGE_555 sp_cube_state %s\n", sp_cube_state);

        /*
        // avoid the file IO all together...IDA all the way
        if (file_binary_search("lookup-table-5x5x5-step10-UD-centers-stage.txt", sp_cube_state, 14, 328877780, 19)) {
            LOG("UD_CENTERS_STAGE_555 sp_cube_state %s\n", sp_cube_state);
            return 1;
        }
        */
        break;

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

    default:
        printf("ERROR: steps_on_same_face_and_layeradd support for %d\n", move);
        exit(1);
    }

    return 0;
}

int
ida_search (int cost_to_here,
            move_type *moves_to_here,
            int threshold,
            move_type prev_move,
            char *cube,
            lookup_table_type type,
            int max_depth)
{
    int cost_to_goal = 0;
    int f_cost = 0;
    move_type move;
    char cube_tmp[array_size];

    int debug = 0;

    // U Fw2 Dw' Rw F' Uw L2 Bw R' Dw Rw
    // 0   1   2  3 4   5  6  7 8   9 10
    if (cost_to_here == 1) {
        if (moves_to_here[0] == U) {
            debug = 1;
        }

    } else if (cost_to_here == 2) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2) {
            debug = 1;
        }

    } else if (cost_to_here == 3) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME) {
            debug = 1;
        }

    } else if (cost_to_here == 4) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME &&
            moves_to_here[3] == Rw) {
            debug = 1;
        }

    } else if (cost_to_here == 5) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME &&
            moves_to_here[3] == Rw &&
            moves_to_here[4] == F_PRIME) {
            debug = 1;
        }

    } else if (cost_to_here == 6) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME &&
            moves_to_here[3] == Rw &&
            moves_to_here[4] == F_PRIME &&
            moves_to_here[5] == Uw) {
            debug = 1;
        }

    } else if (cost_to_here == 7) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME &&
            moves_to_here[3] == Rw &&
            moves_to_here[4] == F_PRIME &&
            moves_to_here[5] == Uw &&
            moves_to_here[6] == L2) {
            debug = 1;
        }

    } else if (cost_to_here == 8) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME &&
            moves_to_here[3] == Rw &&
            moves_to_here[4] == F_PRIME &&
            moves_to_here[5] == Uw &&
            moves_to_here[6] == L2 &&
            moves_to_here[7] == Bw) {
            debug = 1;
        }

    } else if (cost_to_here == 9) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME &&
            moves_to_here[3] == Rw &&
            moves_to_here[4] == F_PRIME &&
            moves_to_here[5] == Uw &&
            moves_to_here[6] == L2 &&
            moves_to_here[7] == Bw &&
            moves_to_here[8] == R_PRIME) {
            debug = 1;
        }

    } else if (cost_to_here == 10) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME &&
            moves_to_here[3] == Rw &&
            moves_to_here[4] == F_PRIME &&
            moves_to_here[5] == Uw &&
            moves_to_here[6] == L2 &&
            moves_to_here[7] == Bw &&
            moves_to_here[8] == R_PRIME &&
            moves_to_here[9] == Dw) {
            debug = 1;
        }

    } else if (cost_to_here == 11) {
        if (moves_to_here[0] == U &&
            moves_to_here[1] == Fw2 &&
            moves_to_here[2] == Dw_PRIME &&
            moves_to_here[3] == Rw &&
            moves_to_here[4] == F_PRIME &&
            moves_to_here[5] == Uw &&
            moves_to_here[6] == L2 &&
            moves_to_here[7] == Bw &&
            moves_to_here[8] == R_PRIME &&
            moves_to_here[9] == Dw &&
            moves_to_here[10] == Rw) {
            debug = 1;
        }
    }

    if (debug) {
        print_moves(moves_to_here, cost_to_here);
    }

    ida_count++;
    ida_load_cube_state(cube, type);
    cost_to_goal = ida_heuristic(cube, type, debug);
    f_cost = cost_to_here + cost_to_goal;

    // Abort Searching
    if (f_cost >= threshold) {
        if (debug) {
            LOG("IDA prune f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
                f_cost, threshold, cost_to_here, cost_to_goal);
            LOG("\n");
        }
        return 0;
    }

    // We are finished!!
    // If our cost_to_goal is greater than the max_depth of our main lookup table then there is no
    // need to do a binary search through the main lookup table to look for our current state...this
    // saves us some disk IO
    //if (cost_to_goal <= max_depth && ida_search_complete(cube, type)) { // 1,827,194 seek_calls
    if (ida_search_complete(cube, type)) { // 1,827,194 seek_calls
        LOG("IDA count %d, f_cost %d vs threshold %d (cost_to_here %d, cost_to_goal %d)\n",
            ida_count, f_cost, threshold, cost_to_here, cost_to_goal);
        LOG("VICTORY\n\n");
        print_moves(moves_to_here, cost_to_here);
        return 1;
    }

    // TODO fix this hard coded 14
    // 14 because that is how many characters the UD state is
    char my_ida_explored_state[14 + 3];
    strcpy(my_ida_explored_state, sp_cube_state);
    char cost_to_here_str[3];
    sprintf(cost_to_here_str, "%d", cost_to_here);
    strcat(my_ida_explored_state, cost_to_here_str);

    if (hash_find(&ida_explored, my_ida_explored_state)) {
        return 0;
    }

    hash_add(&ida_explored, my_ida_explored_state, 0);

    for (int i = 0; i < MOVE_COUNT_555; i++) {
        move = moves_555[i];

        if (steps_on_same_face_and_layer(move, prev_move)) {
            continue;
        }

        char cube_copy[array_size];
        memcpy(cube_copy, cube, sizeof(char) * array_size);
        rotate_555(cube_copy, cube_tmp, array_size, move);
        moves_to_here[cost_to_here] = move;

        if (ida_search(cost_to_here + 1, moves_to_here, threshold, move, cube_copy, type, max_depth)) {
            return 1;
        }
    }

    return 0;
}


int
ida_solve (char *cube, lookup_table_type type)
{
    int MAX_SEARCH_DEPTH = 20;
    move_type moves_to_here[MAX_SEARCH_DEPTH];
    int min_ida_threshold = 0;

    // dwalton
    //ida_prune_table_preload(&pt_t_centers, "lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.txt", 46);
    //ida_prune_table_preload(&pt_x_centers, "lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.txt", 45);
    //ida_prune_table_preload(&UD_centers_555, "lookup-table-5x5x5-step10-UD-centers-stage.txt.6-deep.all_steps");

    pt_t_centers_cost_only = ida_cost_only_preload("lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.cost-only.txt", 16711681);
    pt_x_centers_cost_only = ida_cost_only_preload("lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.cost-only.txt", 16711681);

    ida_load_cube_state(cube, type);
    min_ida_threshold = ida_heuristic(cube, type, 0);
    LOG("min_ida_threshold %d\n", min_ida_threshold);

    for (int threshold = min_ida_threshold; threshold <= MAX_SEARCH_DEPTH; threshold++) {
        ida_count = 0;
        memset(moves_to_here, MOVE_NONE, sizeof(move_type) * MAX_SEARCH_DEPTH);
        hash_delete_all(&ida_explored);

        // TODO fix this hard-coded 6 (for 6-deep)
        if (ida_search(0, moves_to_here, threshold, MOVE_NONE, cube, type, 6)) {
            LOG("IDA threshold %d, explored %d branches, found solution\n", threshold, ida_count);
            free(pt_t_centers_cost_only);
            pt_t_centers_cost_only = NULL;
            free(pt_x_centers_cost_only);
            pt_x_centers_cost_only = NULL;
            return 1;
        } else {
            LOG("IDA threshold %d, explored %d branches\n\n\n\n\n", threshold, ida_count);
        }
    }

    free(pt_t_centers_cost_only);
    pt_t_centers_cost_only = NULL;
    free(pt_x_centers_cost_only);
    pt_x_centers_cost_only = NULL;

    LOG("IDA failed with range %d->%d\n", min_ida_threshold, MAX_SEARCH_DEPTH);
    return 0;
}


int
main (int argc, char *argv[])
{
    lookup_table_type type = NONE;
    int cube_size_type = 0;
    int cube_size_kociemba = 0;
    char kociemba[300];
    memset(kociemba, 0, sizeof(char) * 300);
    memset(sp_binary_search, 0, sizeof(char) * 255);

    for (int i = 1; i < argc; i++) {
        if (strmatch(argv[i], "-k") || strmatch(argv[i], "--kociemba")) {
            i++;
            strcpy(kociemba, argv[i]);
            cube_size_kociemba = (int) sqrt(strlen(kociemba) / 6);

        } else if (strmatch(argv[i], "-t") || strmatch(argv[i], "--type")) {
            i++;

            if (strmatch(argv[i], "5x5x5-UD-centers-stage")) {
                type = UD_CENTERS_STAGE_555;
                cube_size_type = 5;
            } else {
                printf("ERROR: %s is an invalid --type\n", argv[i]);
                exit(1);
            }

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

    int cube_size = cube_size_kociemba;
    array_size = (cube_size * cube_size * 6) + 2;
    char cube[array_size];
    char cube_tmp[array_size];

    sp_cube_state = malloc(sizeof(char) * array_size);
    sp_cube_state_binary = malloc(sizeof(char) * array_size);
    memset(cube_tmp, 0, sizeof(char) * array_size);
    init_cube(cube, cube_size, type, kociemba);

    // print_cube(cube, cube_size);
    ida_solve(cube, type);
    printf("%lu seek_calls", seek_calls);

    /*
static const move_type moves_555[MOVE_COUNT_555] = {
    U, U_PRIME, U2, Uw, Uw_PRIME, Uw2,
    L, L_PRIME, L2, Lw, Lw_PRIME, Lw2,
    F, F_PRIME, F2, Fw, Fw_PRIME, Fw2,
    R, R_PRIME, R2, Rw, Rw_PRIME, Rw2,
    B, B_PRIME, B2, Bw, Bw_PRIME, Bw2,
    D, D_PRIME, D2, Dw, Dw_PRIME, Dw2
};
    */

    // Fw2 Dw' Rw B' Lw' F D' B' Lw' Dw Bw'
    /*
    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, Fw2);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, Dw_PRIME);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, Rw);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, B_PRIME);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, Lw_PRIME);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, F);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, D_PRIME);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, B_PRIME);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, Lw_PRIME);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, Dw);

    memcpy(cube_tmp, cube, sizeof(char) * array_size);
    rotate_555(cube, cube_tmp, array_size, Bw_PRIME);

    print_cube(cube, cube_size);

    ida_load_cube_state(cube, type);

    if (ida_search_complete(cube, type)) { // 1,827,194 seek_calls
        printf("ida_search_complete returned True\n");
    } else {
        printf("ida_search_complete returned False\n");
    }
    */
}
