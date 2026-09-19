
#include "ida_search_core.h"

#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#define GROUPED_UINT64_DIGITS 20

const char *grouped_uint64(uint64_t value, char *buffer, size_t buffer_size)
{
    char digits[GROUPED_UINT64_DIGITS + 1];
    int digit_count;
    int comma_count;
    int out;
    int index;

    digit_count = snprintf(digits, sizeof(digits), "%" PRIu64, value);
    if (digit_count <= 0 || (size_t)digit_count >= sizeof(digits) || buffer_size < 2) {
        if (buffer_size) {
            buffer[0] = '\0';
        }
        return buffer;
    }

    comma_count = (digit_count - 1) / 3;
    if ((size_t)digit_count + (size_t)comma_count >= buffer_size) {
        snprintf(buffer, buffer_size, "%" PRIu64, value);
        return buffer;
    }

    out = digit_count + comma_count;
    buffer[out] = '\0';
    for (index = digit_count - 1; index >= 0; index--) {
        buffer[--out] = digits[index];
        if (index && (digit_count - index) % 3 == 0) {
            buffer[--out] = ',';
        }
    }
    return buffer;
}

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
    fflush(stdout);
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

void print_cube(char *cube, int size) {
    int squares_per_side = size * size;
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

uint64_t binom[IDA_BINOM_MAX + 1][IDA_BINOM_MAX + 1];

void init_binom(void)
{
    for (unsigned int n = 0; n <= IDA_BINOM_MAX; n++) {
        binom[n][0] = 1;
        binom[n][n] = 1;
        for (unsigned int k = 1; k < n; k++) {
            binom[n][k] = binom[n - 1][k - 1] + binom[n - 1][k];
        }
    }
}

move_type ida_parse_move(const char *move_string, const move_type *moves, unsigned int move_count)
{
    for (unsigned int move_index = 0; move_index < move_count; move_index++) {
        move_type move = moves[move_index];

        if (strmatch((char *)move2str[move], (char *)move_string)) {
            return move;
        }
    }
    return MOVE_NONE;
}

void ida_init_move_tables(
    const move_type *moves,
    unsigned int move_count,
    int (*move_is_allowed)(move_type),
    unsigned char legal_move_count[MOVE_MAX],
    unsigned char legal_move_index[MOVE_MAX][IDA_MOVE_INDEX_MAX],
    move_type inverse_move[MOVE_MAX]
)
{
    memset(legal_move_count, 0, MOVE_MAX);

    for (unsigned int move_index = 0; move_index < move_count; move_index++) {
        move_type move = moves[move_index];
        unsigned int quarter_turn_offset = ((unsigned int)move - 1) % 3;

        inverse_move[move] = quarter_turn_offset == 0 ? move + 1 :
                             quarter_turn_offset == 1 ? move - 1 : move;
        if (move_is_allowed(move)) {
            legal_move_index[MOVE_NONE][legal_move_count[MOVE_NONE]++] = (unsigned char)move_index;
        }
    }

    for (unsigned int previous_index = 0; previous_index < move_count; previous_index++) {
        move_type previous_move = moves[previous_index];

        if (!move_is_allowed(previous_move)) {
            continue;
        }
        for (unsigned int move_index = 0; move_index < move_count; move_index++) {
            move_type move = moves[move_index];

            if (!move_is_allowed(move) ||
                steps_on_same_face_and_layer(previous_move, move) ||
                !outer_layer_moves_in_order(previous_move, move) ||
                !steps_on_same_face_in_order(previous_move, move) ||
                !steps_on_opposite_faces_in_order(previous_move, move)) {
                continue;
            }
            legal_move_index[previous_move][legal_move_count[previous_move]++] = (unsigned char)move_index;
        }
    }
}

void ida_init_cube(char *cube, unsigned int cube_size, const char *kociemba)
{
    const unsigned int face_size = cube_size * cube_size;
    const unsigned int expected = face_size * 6;

    if (strlen(kociemba) != expected) {
        fprintf(
            stderr,
            "ERROR: --kociemba must contain %u stickers for a %ux%ux%u cube\n",
            expected, cube_size, cube_size, cube_size
        );
        exit(1);
    }
    cube[0] = 'x';
    memcpy(&cube[1], &kociemba[0], face_size);                            /* U */
    memcpy(&cube[1 + face_size], &kociemba[face_size * 4], face_size);    /* L */
    memcpy(&cube[1 + face_size * 2], &kociemba[face_size * 2], face_size); /* F */
    memcpy(&cube[1 + face_size * 3], &kociemba[face_size], face_size);    /* R */
    memcpy(&cube[1 + face_size * 4], &kociemba[face_size * 5], face_size); /* B */
    memcpy(&cube[1 + face_size * 5], &kociemba[face_size * 3], face_size); /* D */
}

int ida_is_edge_or_corner(unsigned int square, unsigned int cube_size)
{
    unsigned int face_offset = (square - 1) % (cube_size * cube_size);
    unsigned int row = face_offset / cube_size;
    unsigned int col = face_offset % cube_size;

    return row == 0 || row == cube_size - 1 || col == 0 || col == cube_size - 1;
}

uint64_t ida_mixed_radix_rank(const uint64_t *ranks, unsigned int count, uint64_t radix)
{
    uint64_t mixed = 0;

    for (unsigned int index = 0; index < count; index++) {
        if (ranks[index] == UINT64_MAX) {
            return UINT64_MAX;
        }
        mixed = mixed * radix + ranks[index];
    }
    return mixed;
}

uint64_t ida_combination_rank_ud(
    const char *cube,
    const unsigned int *squares,
    unsigned int group_size,
    unsigned int ud_count
)
{
    unsigned int u_remaining = ud_count;
    uint64_t rank = 0;

    for (unsigned int position = 0; position < group_size; position++) {
        unsigned int positions_after = group_size - position - 1;
        char sticker = cube[squares[position]];

        if (sticker == 'U' || sticker == 'D') {
            if (!u_remaining) {
                return UINT64_MAX;
            }
            u_remaining--;
        } else if (u_remaining) {
            rank += binom[positions_after][u_remaining - 1];
        }
    }
    return u_remaining ? UINT64_MAX : rank;
}

uint64_t ida_combination_rank_pair(
    const char *cube,
    const unsigned int *squares,
    unsigned int group_size,
    unsigned int color_count,
    uint64_t universe,
    char small,
    char large
)
{
    unsigned int remaining[2] = {color_count, color_count};
    uint64_t permutations = universe;
    uint64_t rank = 0;
    unsigned int slots = group_size;

    for (unsigned int position = 0; position < group_size; position++) {
        char sticker = cube[squares[position]];
        unsigned int symbol_index;

        if (sticker == small) {
            symbol_index = 0;
        } else if (sticker == large) {
            symbol_index = 1;
        } else {
            return UINT64_MAX;
        }
        if (!remaining[symbol_index]) {
            return UINT64_MAX;
        }
        for (unsigned int smaller = 0; smaller < symbol_index; smaller++) {
            rank += permutations * remaining[smaller] / slots;
        }
        permutations = permutations * remaining[symbol_index] / slots;
        remaining[symbol_index]--;
        slots--;
    }
    return rank;
}

struct mapped_cost_file ida_map_cost_file(const char *filename, uint64_t expected_size)
{
    struct mapped_cost_file result = {-1, NULL, 0};
    struct stat file_stat;
    int mmap_flags = MAP_SHARED;

    result.fd = open(filename, O_RDONLY);
    if (result.fd < 0) {
        fprintf(stderr, "ERROR: could not open %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if (fstat(result.fd, &file_stat) != 0) {
        fprintf(stderr, "ERROR: could not stat %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    if ((uint64_t)file_stat.st_size != expected_size) {
        fprintf(
            stderr,
            "ERROR: %s is %" PRIu64 " bytes, expected %" PRIu64 "\n",
            filename,
            (uint64_t)file_stat.st_size,
            expected_size
        );
        exit(1);
    }
#ifdef MAP_POPULATE
    if ((uint64_t)file_stat.st_blocks * 512 >= expected_size) {
        mmap_flags |= MAP_POPULATE;
    }
#endif
    result.size = (size_t)expected_size;
    result.costs = mmap(NULL, result.size, PROT_READ, mmap_flags, result.fd, 0);
    if (result.costs == MAP_FAILED) {
        fprintf(stderr, "ERROR: could not mmap %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    return result;
}

void ida_unmap_cost_file(int fd, unsigned char *costs, size_t size)
{
    if (costs && costs != MAP_FAILED) {
        munmap(costs, size);
    }
    if (fd >= 0) {
        close(fd);
    }
}

static uint64_t symmetry_select_zero(const struct symmetry_index *index, uint64_t zero)
{
    const struct symmetry_index_header *header = index->header;
    uint64_t base = (zero / header->zero_sample_rate) * header->zero_sample_rate;
    uint64_t position = index->zero_samples[zero / header->zero_sample_rate];
    uint64_t remaining = zero - base;

    if (!remaining) {
        return position;
    }
    position++;
    while (position < header->high_bit_count) {
        uint64_t word_index = position >> 6;
        unsigned int offset = position & 63;
        uint64_t zeros = ~index->high[word_index] & (UINT64_MAX << offset);

        if (word_index + 1 == header->high_word_count &&
                (header->high_bit_count & 63)) {
            zeros &= (UINT64_C(1) << (header->high_bit_count & 63)) - 1;
        }
        unsigned int count = __builtin_popcountll(zeros);
        if (remaining <= count) {
            for (uint64_t candidate = zeros; candidate; candidate &= candidate - 1) {
                if (!--remaining) {
                    return (word_index << 6) + __builtin_ctzll(candidate);
                }
            }
        }
        remaining -= count;
        position = (word_index + 1) << 6;
    }
    return UINT64_MAX;
}

static uint64_t symmetry_low_value(const struct symmetry_index *index, uint64_t dense)
{
    uint64_t bit = dense * index->header->low_bits;
    unsigned int offset = bit & 63;
    uint64_t value = index->low[bit >> 6] >> offset;

    if (offset > 64 - index->header->low_bits) {
        value |= index->low[(bit >> 6) + 1] << (64 - offset);
    }
    return value & ((UINT64_C(1) << index->header->low_bits) - 1);
}

uint64_t symmetry_dense_rank(const struct symmetry_index *index, uint64_t raw)
{
    uint64_t high = raw >> index->header->low_bits;
    uint64_t low = raw & ((UINT64_C(1) << index->header->low_bits) - 1);
    uint64_t start = high
        ? symmetry_select_zero(index, high - 1) - (high - 1)
        : 0;
    uint64_t end = symmetry_select_zero(index, high) - high;

    if (start == UINT64_MAX || end == UINT64_MAX || end > index->header->orbit_count) {
        return UINT64_MAX;
    }
    for (uint64_t dense = start; dense < end; dense++) {
        uint64_t candidate = symmetry_low_value(index, dense);
        if (candidate == low) {
            return dense;
        }
        if (candidate > low) {
            break;
        }
    }
    return UINT64_MAX;
}

void map_symmetry_index(
    struct symmetry_index *index,
    const char *filename,
    uint64_t expected_raw_universe,
    const char *kind
)
{
    struct stat file_stat;
    uint64_t expected_size;

    index->fd = open(filename, O_RDONLY);
    if (index->fd < 0 || fstat(index->fd, &file_stat) != 0) {
        fprintf(stderr, "ERROR: could not open %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    index->size = (size_t)file_stat.st_size;
    index->mapping = mmap(NULL, index->size, PROT_READ, MAP_SHARED, index->fd, 0);
    if (index->mapping == MAP_FAILED) {
        fprintf(stderr, "ERROR: could not mmap %s: %s\n", filename, strerror(errno));
        exit(1);
    }
    index->header = (const struct symmetry_index_header *)index->mapping;
    if (index->size < sizeof(*index->header) ||
            memcmp(index->header->magic, "CS444EF1", 8) ||
            index->header->raw_universe != expected_raw_universe ||
            index->header->low_bits != 5 ||
            index->header->zero_sample_rate != 512) {
        fprintf(stderr, "ERROR: %s is not a supported %s\n", filename, kind);
        exit(1);
    }
    expected_size = sizeof(*index->header) +
        (index->header->low_word_count * sizeof(uint64_t)) +
        (index->header->high_word_count * sizeof(uint64_t)) +
        (index->header->zero_sample_count * sizeof(uint32_t));
    if (expected_size != index->size) {
        fprintf(stderr, "ERROR: %s has an invalid size\n", filename);
        exit(1);
    }
    index->low = (const uint64_t *)(index->mapping + sizeof(*index->header));
    index->high = index->low + index->header->low_word_count;
    index->zero_samples = (const uint32_t *)(index->high + index->header->high_word_count);
}

void unmap_symmetry_index(struct symmetry_index *index)
{
    if (index->mapping && index->mapping != MAP_FAILED) {
        munmap(index->mapping, index->size);
    }
    if (index->fd >= 0) {
        close(index->fd);
    }
    index->fd = -1;
    index->mapping = NULL;
    index->header = NULL;
    index->low = NULL;
    index->high = NULL;
    index->zero_samples = NULL;
}
