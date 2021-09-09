
#include "ida_search_core.h"

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <time.h>

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

unsigned long hex_to_int(char value) {
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

unsigned long max(unsigned long a, unsigned long b) { return (a > b ? a : b); }

// uthash references
// http://troydhanson.github.io/uthash/index.html
// https://cfsa-pmw.warwick.ac.uk/SDF/SDF_C/blob/3cf5bf49856ef9ee4080cf6722cf9058a1e28b01/src/uthash/tests/example.c
inline void hash_add(struct key_value_pair **hashtable, char *state_key, unsigned long value) {
    struct key_value_pair *s;

    s = malloc(sizeof(struct key_value_pair));
    strcpy(s->state, state_key);
    s->value = value;

    HASH_ADD_STR(*hashtable, state, s);
}

inline struct key_value_pair *hash_find(struct key_value_pair **hashtable, char *state_key) {
    struct key_value_pair *s = NULL;
    HASH_FIND_STR(*hashtable, state_key, s);
    return s;
}

void hash_delete(struct key_value_pair **hashtable, struct key_value_pair *s) {
    HASH_DEL(*hashtable, s);
    free(s);
}

void hash_delete_all(struct key_value_pair **hashtable) {
    struct key_value_pair *s, *tmp;

    HASH_ITER(hh, *hashtable, s, tmp) {
        HASH_DEL(*hashtable, s);
        free(s);
    }
}

unsigned long hash_count(struct key_value_pair **hashtable) {
    struct key_value_pair *s;
    unsigned long count = 0;

    for (s = *hashtable; s != NULL; s = (struct key_value_pair *)(s->hh.next)) {
        count++;
    }

    return count;
}

void hash_print_all(struct key_value_pair **hashtable) {
    struct key_value_pair *s;

    for (s = *hashtable; s != NULL; s = (struct key_value_pair *)(s->hh.next)) {
        printf("key %s  value %u\n", s->state, s->value);
    }
}

void print_cube(char *cube, int size) {
    int squares_per_side = size * size;
    int square_count = squares_per_side * 6;
    int rows = size * 3;
    printf("\n");

    for (int row = 1; row <= rows; row++) {
        // U
        if (row <= size) {
            int i = ((row - 1) * size) + 1;
            int i_end = i + size - 1;

            for (int z = 0; z < size; z++) {
                printf("  ");
            }

            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            printf("\n");

            if (row == size) {
                printf("\n");
            }

            // D
        } else if (row > (size * 2)) {
            int i = (squares_per_side * 5) + 1 + ((row - (size * 2) - 1) * size);
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
            int i_start = squares_per_side + 1 + ((row - 1 - size) * size);
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

int strmatch(char *str1, char *str2) {
    if (strcmp(str1, str2) == 0) {
        return 1;
    }
    return 0;
}

void print_moves(move_type *moves, int max_i) {
    int i = 0;
    int count = 0;

    while (moves[count] != MOVE_NONE) {
        count++;
    }

    printf("SOLUTION (%d steps): ", count);

    while (moves[i] != MOVE_NONE) {
        printf("%s ", move2str[moves[i]]);
        i++;

        if (i >= max_i) {
            break;
        }
    }
    printf("\n");
}

unsigned char wide_turn_count(move_type *moves) {
    unsigned char i = 0;
    unsigned char count = 0;

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

unsigned char get_orbit0_wide_half_turn_count(move_type *moves) {
    unsigned char i = 0;
    unsigned char count = 0;

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

unsigned char get_orbit0_wide_quarter_turn_count(move_type *moves) {
    unsigned char i = 0;
    unsigned char count = 0;

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

unsigned char get_orbit1_wide_quarter_turn_count(move_type *moves) {
    unsigned char i = 0;
    unsigned char count = 0;

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

unsigned char get_outer_layer_quarter_turn_count(move_type *moves) {
    unsigned char i = 0;
    unsigned char count = 0;

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

unsigned char moves_cancel_out(move_type prev_move, move_type move) {
    switch (prev_move) {
        case U:
            return (move == U_PRIME);
        case U_PRIME:
            return (move == U);
        case U2:
            return (move == U2);
        case L:
            return (move == L_PRIME);
        case L_PRIME:
            return (move == L);
        case L2:
            return (move == L2);
        case F:
            return (move == F_PRIME);
        case F_PRIME:
            return (move == F);
        case F2:
            return (move == F2);
        case R:
            return (move == R_PRIME);
        case R_PRIME:
            return (move == R);
        case R2:
            return (move == R2);
        case B:
            return (move == B_PRIME);
        case B_PRIME:
            return (move == B);
        case B2:
            return (move == B2);
        case D:
            return (move == D_PRIME);
        case D_PRIME:
            return (move == D);
        case D2:
            return (move == D2);
        case Uw:
            return (move == Uw_PRIME);
        case Uw_PRIME:
            return (move == Uw);
        case Uw2:
            return (move == Uw2);
        case Lw:
            return (move == Lw_PRIME);
        case Lw_PRIME:
            return (move == Lw);
        case Lw2:
            return (move == Lw2);
        case Fw:
            return (move == Fw_PRIME);
        case Fw_PRIME:
            return (move == Fw);
        case Fw2:
            return (move == Fw2);
        case Rw:
            return (move == Rw_PRIME);
        case Rw_PRIME:
            return (move == Rw);
        case Rw2:
            return (move == Rw2);
        case Bw:
            return (move == Bw_PRIME);
        case Bw_PRIME:
            return (move == Bw);
        case Bw2:
            return (move == Bw2);
        case Dw:
            return (move == Dw_PRIME);
        case Dw_PRIME:
            return (move == Dw);
        case Dw2:
            return (move == Dw2);
        default:
            printf("ERROR: moves_cancel_out add support for %d\n", move);
            exit(1);
    }

    return 0;
}

unsigned char outer_layer_move(move_type move) {
    switch (move) {
        case U:
        case U_PRIME:
        case U2:
        case L:
        case L_PRIME:
        case L2:
        case F:
        case F_PRIME:
        case F2:
        case R:
        case R_PRIME:
        case R2:
        case B:
        case B_PRIME:
        case B2:
        case D:
        case D_PRIME:
        case D2:
            return 1;
        default:
            return 0;
    }
}

unsigned char outer_layer_moves_in_order(move_type prev_move, move_type move) {
    if (!outer_layer_move(prev_move)) {
        return 1;
    }

    if (!outer_layer_move(move)) {
        return 1;
    }

    switch (prev_move) {
        case U:
        case U_PRIME:
        case U2:
            return 1;

        case L:
        case L_PRIME:
        case L2:
            switch (move) {
                case F:
                case F_PRIME:
                case F2:
                case R:
                case R_PRIME:
                case R2:
                case B:
                case B_PRIME:
                case B2:
                case D:
                case D_PRIME:
                case D2:
                    return 1;
                default:
                    return 0;
            }

        case F:
        case F_PRIME:
        case F2:
            switch (move) {
                case R:
                case R_PRIME:
                case R2:
                case B:
                case B_PRIME:
                case B2:
                case D:
                case D_PRIME:
                case D2:
                    return 1;
                default:
                    return 0;
            }

        case R:
        case R_PRIME:
        case R2:
            switch (move) {
                case B:
                case B_PRIME:
                case B2:
                case D:
                case D_PRIME:
                case D2:
                    return 1;
                default:
                    return 0;
            }

        case B:
        case B_PRIME:
        case B2:
            switch (move) {
                case D:
                case D_PRIME:
                case D2:
                    return 1;
                default:
                    return 0;
            }

        case D:
        case D_PRIME:
        case D2:
            return 0;
        default:
            return 1;
    }
}

unsigned char steps_on_same_face_and_layer(move_type prev_move, move_type move) {
    switch (prev_move) {
        case U:
        case U_PRIME:
        case U2:
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
                case Dw:
                case Dw_PRIME:
                case Dw2:
                    return 1;
                default:
                    return 0;
            }
            break;

        // 3-layer turns
        case threeUw:
        case threeUw_PRIME:
        case threeUw2:
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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
            switch (move) {
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

unsigned char steps_on_same_face(move_type prev_move, move_type move) {
    switch (prev_move) {
        case U:
        case U_PRIME:
        case U2:
        case Uw:
        case Uw_PRIME:
        case Uw2:
        case threeUw:
        case threeUw_PRIME:
        case threeUw2:
            switch (move) {
                case U:
                case U_PRIME:
                case U2:
                case Uw:
                case Uw_PRIME:
                case Uw2:
                case threeUw:
                case threeUw_PRIME:
                case threeUw2:
                    return 1;
                default:
                    return 0;
            }
            break;

        case L:
        case L_PRIME:
        case L2:
        case Lw:
        case Lw_PRIME:
        case Lw2:
        case threeLw:
        case threeLw_PRIME:
        case threeLw2:
            switch (move) {
                case L:
                case L_PRIME:
                case L2:
                case Lw:
                case Lw_PRIME:
                case Lw2:
                case threeLw:
                case threeLw_PRIME:
                case threeLw2:
                    return 1;
                default:
                    return 0;
            }
            break;

        case F:
        case F_PRIME:
        case F2:
        case Fw:
        case Fw_PRIME:
        case Fw2:
        case threeFw:
        case threeFw_PRIME:
        case threeFw2:
            switch (move) {
                case F:
                case F_PRIME:
                case F2:
                case Fw:
                case Fw_PRIME:
                case Fw2:
                case threeFw:
                case threeFw_PRIME:
                case threeFw2:
                    return 1;
                default:
                    return 0;
            }
            break;

        case R:
        case R_PRIME:
        case R2:
        case Rw:
        case Rw_PRIME:
        case Rw2:
        case threeRw:
        case threeRw_PRIME:
        case threeRw2:
            switch (move) {
                case R:
                case R_PRIME:
                case R2:
                case Rw:
                case Rw_PRIME:
                case Rw2:
                case threeRw:
                case threeRw_PRIME:
                case threeRw2:
                    return 1;
                default:
                    return 0;
            }
            break;

        case B:
        case B_PRIME:
        case B2:
        case Bw:
        case Bw_PRIME:
        case Bw2:
        case threeBw:
        case threeBw_PRIME:
        case threeBw2:
            switch (move) {
                case B:
                case B_PRIME:
                case B2:
                case Bw:
                case Bw_PRIME:
                case Bw2:
                case threeBw:
                case threeBw_PRIME:
                case threeBw2:
                    return 1;
                default:
                    return 0;
            }
            break;

        case D:
        case D_PRIME:
        case D2:
        case Dw:
        case Dw_PRIME:
        case Dw2:
        case threeDw:
        case threeDw_PRIME:
        case threeDw2:
            switch (move) {
                case D:
                case D_PRIME:
                case D2:
                case Dw:
                case Dw_PRIME:
                case Dw2:
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
            printf("ERROR: steps_on_same_face add support for %d\n", move);
            exit(1);
    }

    return 0;
}

unsigned char steps_on_same_face_in_order(move_type prev_move, move_type move) {
    if (!steps_on_same_face(prev_move, move)) {
        return 1;
    }

    switch (prev_move) {
        case U:
        case U_PRIME:
        case U2:
            return 1;
        case Uw:
        case Uw_PRIME:
        case Uw2:
            switch (move) {
                case threeUw:
                case threeUw_PRIME:
                case threeUw2:
                    return 1;
                default:
                    return 0;
            }

        case L:
        case L_PRIME:
        case L2:
            return 1;
        case Lw:
        case Lw_PRIME:
        case Lw2:
            switch (move) {
                case threeLw:
                case threeLw_PRIME:
                case threeLw2:
                    return 1;
                default:
                    return 0;
            }

        case F:
        case F_PRIME:
        case F2:
            return 1;
        case Fw:
        case Fw_PRIME:
        case Fw2:
            switch (move) {
                case threeFw:
                case threeFw_PRIME:
                case threeFw2:
                    return 1;
                default:
                    return 0;
            }

        case R:
        case R_PRIME:
        case R2:
            return 1;
        case Rw:
        case Rw_PRIME:
        case Rw2:
            switch (move) {
                case threeRw:
                case threeRw_PRIME:
                case threeRw2:
                    return 1;
                default:
                    return 0;
            }

        case B:
        case B_PRIME:
        case B2:
            return 1;
        case Bw:
        case Bw_PRIME:
        case Bw2:
            switch (move) {
                case threeBw:
                case threeBw_PRIME:
                case threeBw2:
                    return 1;
                default:
                    return 0;
            }

        case D:
        case D_PRIME:
        case D2:
            return 1;
        case Dw:
        case Dw_PRIME:
        case Dw2:
            switch (move) {
                case threeDw:
                case threeDw_PRIME:
                case threeDw2:
                    return 1;
                default:
                    return 0;
            }

        default:
            return 0;
    }
}

unsigned char steps_on_opposite_faces(move_type prev_move, move_type move) {
    switch (prev_move) {
        case U:
        case U_PRIME:
        case U2:
        case Uw:
        case Uw_PRIME:
        case Uw2:
        case threeUw:
        case threeUw_PRIME:
        case threeUw2:
            switch (move) {
                case D:
                case D_PRIME:
                case D2:
                case Dw:
                case Dw_PRIME:
                case Dw2:
                case threeDw:
                case threeDw_PRIME:
                case threeDw2:
                    return 1;
                default:
                    return 0;
            }

        case D:
        case D_PRIME:
        case D2:
        case Dw:
        case Dw_PRIME:
        case Dw2:
        case threeDw:
        case threeDw_PRIME:
        case threeDw2:
            switch (move) {
                case U:
                case U_PRIME:
                case U2:
                case Uw:
                case Uw_PRIME:
                case Uw2:
                case threeUw:
                case threeUw_PRIME:
                case threeUw2:
                    return 1;
                default:
                    return 0;
            }

        case L:
        case L_PRIME:
        case L2:
        case Lw:
        case Lw_PRIME:
        case Lw2:
        case threeLw:
        case threeLw_PRIME:
        case threeLw2:
            switch (move) {
                case R:
                case R_PRIME:
                case R2:
                case Rw:
                case Rw_PRIME:
                case Rw2:
                case threeRw:
                case threeRw_PRIME:
                case threeRw2:
                    return 1;
                default:
                    return 0;
            }

        case R:
        case R_PRIME:
        case R2:
        case Rw:
        case Rw_PRIME:
        case Rw2:
        case threeRw:
        case threeRw_PRIME:
        case threeRw2:
            switch (move) {
                case L:
                case L_PRIME:
                case L2:
                case Lw:
                case Lw_PRIME:
                case Lw2:
                case threeLw:
                case threeLw_PRIME:
                case threeLw2:
                    return 1;
                default:
                    return 0;
            }

        case F:
        case F_PRIME:
        case F2:
        case Fw:
        case Fw_PRIME:
        case Fw2:
        case threeFw:
        case threeFw_PRIME:
        case threeFw2:
            switch (move) {
                case B:
                case B_PRIME:
                case B2:
                case Bw:
                case Bw_PRIME:
                case Bw2:
                case threeBw:
                case threeBw_PRIME:
                case threeBw2:
                    return 1;
                default:
                    return 0;
            }

        case B:
        case B_PRIME:
        case B2:
        case Bw:
        case Bw_PRIME:
        case Bw2:
        case threeBw:
        case threeBw_PRIME:
        case threeBw2:
            switch (move) {
                case F:
                case F_PRIME:
                case F2:
                case Fw:
                case Fw_PRIME:
                case Fw2:
                case threeFw:
                case threeFw_PRIME:
                case threeFw2:
                    return 1;
                default:
                    return 0;
            }
        default:
            printf("ERROR: steps_on_opposite_layers add support for %d\n", move);
            exit(1);
    }
}

unsigned char steps_on_opposite_faces_in_order(move_type prev_move, move_type move) {
    if (!steps_on_opposite_faces(prev_move, move)) {
        return 1;
    }
    switch (prev_move) {
        case U:
        case U_PRIME:
        case U2:
        case Uw:
        case Uw_PRIME:
        case Uw2:
        case threeUw:
        case threeUw_PRIME:
        case threeUw2:
            return 1;
        case D:
        case D_PRIME:
        case D2:
        case Dw:
        case Dw_PRIME:
        case Dw2:
        case threeDw:
        case threeDw_PRIME:
        case threeDw2:
            return 0;

        case L:
        case L_PRIME:
        case L2:
        case Lw:
        case Lw_PRIME:
        case Lw2:
        case threeLw:
        case threeLw_PRIME:
        case threeLw2:
            return 1;
        case R:
        case R_PRIME:
        case R2:
        case Rw:
        case Rw_PRIME:
        case Rw2:
        case threeRw:
        case threeRw_PRIME:
        case threeRw2:
            return 0;

        case F:
        case F_PRIME:
        case F2:
        case Fw:
        case Fw_PRIME:
        case Fw2:
        case threeFw:
        case threeFw_PRIME:
        case threeFw2:
            return 1;
        case B:
        case B_PRIME:
        case B2:
        case Bw:
        case Bw_PRIME:
        case Bw2:
        case threeBw:
        case threeBw_PRIME:
        case threeBw2:
            return 0;

        default:
            printf("ERROR: steps_on_opposite_faces_in_order add support for %d\n", move);
            exit(1);
    }
}

unsigned char invalid_prune(unsigned char cost_to_here, move_type *moves_to_here, unsigned int threshold) {
    // Lw2 R2 D2 F U' Lw2 D2 Lw2 R2 Fw2 B Uw2 D Fw2
    move_type move_seq[14];

    move_seq[0] = Lw2;
    move_seq[1] = R2;
    move_seq[2] = D2;
    move_seq[3] = F;
    move_seq[4] = U_PRIME;
    move_seq[5] = Lw2;
    move_seq[6] = D2;
    move_seq[7] = Lw2;
    move_seq[8] = R2;
    move_seq[9] = Fw2;
    move_seq[10] = B;
    move_seq[11] = Uw2;
    move_seq[12] = D;
    move_seq[13] = Fw2;

    if (threshold == 15) {
        if (memcmp(moves_to_here, move_seq, sizeof(move_type) * cost_to_here) == 0) {
            return 1;
        }
    }

    return 0;
}
