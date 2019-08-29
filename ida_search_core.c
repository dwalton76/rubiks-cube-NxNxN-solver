
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include "ida_search_core.h"

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

unsigned long
hex_to_int(char value)
{
    // This is faster than calling strtoul()
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
        printf("ERROR: hex_to_int does not support '%c'\n", value);
        exit(1);
    };
}

unsigned long
max (unsigned long a, unsigned long b)
{
    return (a > b ? a : b);
}


// uthash references
// http://troydhanson.github.io/uthash/index.html
// https://cfsa-pmw.warwick.ac.uk/SDF/SDF_C/blob/3cf5bf49856ef9ee4080cf6722cf9058a1e28b01/src/uthash/tests/example.c
void
hash_add (struct key_value_pair **hashtable, char *state_key, unsigned long value)
{
    struct key_value_pair *s;

    s = malloc(sizeof(struct key_value_pair));
    strcpy(s->state, state_key);
    s->value = value;

    HASH_ADD_STR(*hashtable, state, s);
}

inline struct key_value_pair *
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
        printf("key %s  value %u\n", s->state, s->value);
    }
}

void
print_cube (char *cube, int size)
{
    int squares_per_side = size * size;
    int square_count = squares_per_side * 6;
    int rows = size * 3;
    printf("\n");

    for (int row=1; row <= rows; row++) {

        // U
        if (row <= size) {
            int i = ((row-1) * size) + 1;
            int i_end = i + size - 1;

            for (int z = 0; z < size; z++) {
                printf("  ");
            }

            for ( ; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            printf("\n");

            if (row == size) {
                printf("\n");
            }

        // D
        } else if (row > (size * 2)) {
            int i = (squares_per_side * 5) + 1 + ((row - (size*2) - 1) * size);
            int i_end = i + size - 1;

            if (row == ((size * 2) + 1)) {
                printf("\n");
            }

            for (int z = 0; z < size; z++) {
                printf("  ");
            }

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

int
strmatch (char *str1, char *str2)
{
    if (strcmp(str1, str2) == 0) {
        return 1;
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

    case X:
    case X_PRIME:
    case Y:
    case Y_PRIME:
    case Z:
    case Z_PRIME:
        return 0;

    default:
        printf("ERROR: steps_on_same_face_and_layer add support for %d\n", move);
        exit(1);
    }

    return 0;
}
