#ifndef CENTER_SYMMETRY_444_H
#define CENTER_SYMMETRY_444_H

#include <stdint.h>
#include <stdlib.h>

#define CENTER_SYMMETRY_COUNT_444 48
#define CENTER_SYMMETRY_STICKERS_444 24

static const int8_t center_coordinates_444[CENTER_SYMMETRY_STICKERS_444][3] = {
    {-1,  2, -1}, { 1,  2, -1}, {-1,  2,  1}, { 1,  2,  1},
    {-2,  1, -1}, {-2,  1,  1}, {-2, -1, -1}, {-2, -1,  1},
    {-1,  1,  2}, { 1,  1,  2}, {-1, -1,  2}, { 1, -1,  2},
    { 2,  1,  1}, { 2,  1, -1}, { 2, -1,  1}, { 2, -1, -1},
    { 1,  1, -2}, {-1,  1, -2}, { 1, -1, -2}, {-1, -1, -2},
    {-1, -2,  1}, { 1, -2,  1}, {-1, -2, -1}, { 1, -2, -1},
};

static const unsigned char center_axis_permutations_444[6][3] = {
    {0, 1, 2}, {0, 2, 1}, {1, 0, 2},
    {1, 2, 0}, {2, 0, 1}, {2, 1, 0},
};

static unsigned char center_symmetry_positions_444
    [CENTER_SYMMETRY_COUNT_444][CENTER_SYMMETRY_STICKERS_444];
static unsigned char center_symmetry_symbols_444[CENTER_SYMMETRY_COUNT_444][3];
static int center_symmetry_initialized_444;

static unsigned char
center_axis_symbol_444(unsigned int axis)
{
    static const unsigned char symbol_by_axis[3] = {'L', 'U', 'F'};
    return symbol_by_axis[axis];
}

static unsigned int
center_symbol_axis_444(unsigned char symbol)
{
    switch (symbol) {
        case 'L': return 0;
        case 'U': return 1;
        case 'F': return 2;
        default: abort();
    }
}

static void
init_center_symmetry_444(void)
{
    unsigned int symmetry = 0;

    if (center_symmetry_initialized_444) {
        return;
    }
    for (unsigned int permutation = 0; permutation < 6; permutation++) {
        const unsigned char *axes = center_axis_permutations_444[permutation];

        for (unsigned int sign_bits = 0; sign_bits < 8; sign_bits++, symmetry++) {
            for (unsigned int source = 0; source < CENTER_SYMMETRY_STICKERS_444; source++) {
                int8_t destination[3] = {0, 0, 0};
                unsigned int found = CENTER_SYMMETRY_STICKERS_444;

                for (unsigned int source_axis = 0; source_axis < 3; source_axis++) {
                    int sign = (sign_bits & (1U << source_axis)) ? 1 : -1;
                    destination[axes[source_axis]] =
                        (int8_t) (sign * center_coordinates_444[source][source_axis]);
                }
                for (unsigned int candidate = 0;
                        candidate < CENTER_SYMMETRY_STICKERS_444; candidate++) {
                    if (center_coordinates_444[candidate][0] == destination[0] &&
                            center_coordinates_444[candidate][1] == destination[1] &&
                            center_coordinates_444[candidate][2] == destination[2]) {
                        found = candidate;
                        break;
                    }
                }
                if (found == CENTER_SYMMETRY_STICKERS_444) {
                    abort();
                }
                center_symmetry_positions_444[symmetry][source] = (unsigned char) found;
            }
            for (unsigned int symbol = 0; symbol < 3; symbol++) {
                static const unsigned char symbols[3] = {'F', 'L', 'U'};
                unsigned int source_axis = center_symbol_axis_444(symbols[symbol]);
                center_symmetry_symbols_444[symmetry][symbol] =
                    center_axis_symbol_444(axes[source_axis]);
            }
        }
    }
    center_symmetry_initialized_444 = 1;
}

static unsigned char
transform_center_symbol_444(unsigned int symmetry, unsigned char symbol)
{
    unsigned int index;

    switch (symbol) {
        case 'F': index = 0; break;
        case 'L': index = 1; break;
        case 'U': index = 2; break;
        default: abort();
    }
    return center_symmetry_symbols_444[symmetry][index];
}

static void
transform_centers_444(
    const unsigned char source[CENTER_SYMMETRY_STICKERS_444],
    unsigned char destination[CENTER_SYMMETRY_STICKERS_444],
    unsigned int symmetry)
{
    for (unsigned int index = 0; index < CENTER_SYMMETRY_STICKERS_444; index++) {
        destination[center_symmetry_positions_444[symmetry][index]] =
            transform_center_symbol_444(symmetry, source[index]);
    }
}

#endif
