#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>

#include "ida_search_core.h"

#define CUBE_SIZE 7
#define CUBE_ARRAY_SIZE 295
#define GROUP_SIZE 16
#define GROUP_U_COUNT 8
#define GROUP_UNIVERSE UINT64_C(12870)
#define PRODUCT_UNIVERSE UINT64_C(165636900)
#define OBLIQUE_COUNT 24
#define MATRIX_UNPAIRED_MAX 16
#define MATRIX_COST_MAX 12
#define MATRIX_ORBIT1_COST_MAX 13
#define DEFAULT_MAX_IDA_THRESHOLD 30
#define MAX_IDA_THRESHOLD 99
#define MAX_THREADS 64
#define PARITY_ODD 1
#define PARITY_EVEN 2

/*
 * Cheapest solution from a goal state that flips one orbit's wide quarter turn
 * parity, measured by running this binary from a solved cube with each
 * --orbitN-need-odd-w flag:
 *
 *   orbit0   1   Uw
 *   orbit1   7   3Lw' U2 D2 3Lw U2 D2 3Lw
 */
#define PARITY_FLOOR_ORBIT0 1
#define PARITY_FLOOR_ORBIT1 7

/*
 * These are UFBD_INNER_T_CENTERS_777 and UFBD_INNER_X_CENTERS_777 from
 * RubiksCube777.py. Their order must remain identical to the two rank groups
 * in Build777Phase2UDInnerCentersStage.
 */
static const unsigned int inner_t_centers[GROUP_SIZE] = {
    18, 24, 26, 32, 116, 122, 124, 130, 214, 220, 222, 228, 263, 269, 271, 277,
};
static const unsigned int inner_x_centers[GROUP_SIZE] = {
    17, 19, 31, 33, 115, 117, 129, 131, 213, 215, 227, 229, 262, 264, 276, 278,
};

/*
 * Matching left/middle/right positions for all 24 oblique triplets. Eight
 * triplets contain LR centers once the obliques are fully paired.
 */
static const unsigned int left_obliques[OBLIQUE_COUNT] = {
    10, 30, 20, 40, 59, 79, 69, 89, 108, 128, 118, 138,
    157, 177, 167, 187, 206, 226, 216, 236, 255, 275, 265, 285,
};
static const unsigned int middle_obliques[OBLIQUE_COUNT] = {
    11, 23, 27, 39, 60, 72, 76, 88, 109, 121, 125, 137,
    158, 170, 174, 186, 207, 219, 223, 235, 256, 268, 272, 284,
};
static const unsigned int right_obliques[OBLIQUE_COUNT] = {
    12, 16, 34, 38, 61, 65, 83, 87, 110, 114, 132, 136,
    159, 163, 181, 185, 208, 212, 230, 234, 257, 261, 279, 283,
};

/* Same face order as the oblique orbits: 4 squares each on U L F R B D. */
static const unsigned int outer_x_centers[OBLIQUE_COUNT] = {
    9, 13, 37, 41, 58, 62, 86, 90, 107, 111, 135, 139,
    156, 160, 184, 188, 205, 209, 233, 237, 254, 258, 282, 286,
};

/*
 * Combined heuristic for staging the UD inner t/x centers while pairing the
 * LR obliques. Rows are the unpaired oblique count (0..16), columns are the
 * exact ranked table cost (0..12, the table's completed depth).
 *
 * The table only sees the UD inner centers and one move pairs at most four
 * obliques, so max(table, ceil(unpaired/4)) is admissible yet far below the
 * real remaining distance, which makes the search crawl.
 *
 * Column 0 seeds from the unpaired-count costs the old oblique-only phase 2 used.
 * Every other cell is the smallest remaining move count observed for that pair
 * while sampling solutions, never below max(column 0, table cost).
 *
 * utils/build-777-UD-inner-centers-oblique-matrix.py was used to build this.
 */
static const unsigned char unpaired_count_UD_inner_centers_777[MATRIX_UNPAIRED_MAX + 1][MATRIX_COST_MAX + 1][MATRIX_ORBIT1_COST_MAX + 1] = {
    {  // unpaired 0
        { 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 0
        { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 1
        { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 2
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 3
        { 4,  4,  4,  4,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 4
        { 5,  5,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 5
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 6
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12, 13},  // centers 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12, 13},  // centers 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 12
    },
    {  // unpaired 1
        { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 0
        { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 1
        { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 2
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 3
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 4
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12, 13},  // centers 5
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12, 13},  // centers 6
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12, 13},  // centers 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12, 13},  // centers 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 12
    },
    {  // unpaired 2
        { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 0
        { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 1
        { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 2
        { 3,  3,  3,  3,  6,  7,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 3
        { 6,  6,  6,  6,  7,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 4
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12, 13},  // centers 5
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 6
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12, 13},  // centers 7
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12, 13},  // centers 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12, 13},  // centers 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 12
    },
    {  // unpaired 3
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 0
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 1
        { 6,  6,  8,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 2
        { 6,  6,  6,  8,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 3
        { 6,  6,  6,  6,  8,  6,  8,  7,  8,  9, 10, 11, 12, 13},  // centers 4
        { 7,  7,  7,  7,  7,  9,  7,  9,  8,  9, 10, 11, 12, 13},  // centers 5
        { 8,  8,  8,  8,  8,  8, 10,  8,  8,  9, 10, 11, 12, 13},  // centers 6
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12, 13},  // centers 7
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 8
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13},  // centers 9
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13},  // centers 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13},  // centers 11
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13},  // centers 12
    },
    {  // unpaired 4
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 0
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 1
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12, 13},  // centers 2
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12, 13},  // centers 3
        { 7,  7,  7,  7,  9,  7,  7,  7,  8,  9, 10, 11, 12, 13},  // centers 4
        { 7,  7,  7,  7,  7,  9,  9,  7,  8,  9, 10, 11, 12, 13},  // centers 5
        { 8,  8,  8,  8,  8,  8, 10,  8,  8,  9, 10, 11, 12, 13},  // centers 6
        { 9,  9,  9,  9,  9,  9,  9, 11,  9,  9, 10, 11, 12, 13},  // centers 7
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 8
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13},  // centers 9
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 10
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 11
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 12
    },
    {  // unpaired 5
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 0
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 1
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 2
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 3
        { 8,  8,  8,  8, 10,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 4
        { 8,  8,  8,  8,  8, 10,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 5
        { 8,  8,  8,  8,  8,  8, 10, 10, 10,  9, 10, 11, 12, 13},  // centers 6
        { 9,  9,  9,  9,  9,  9,  9, 11, 11, 11, 10, 11, 12, 13},  // centers 7
        {11, 11, 11, 11, 11, 11, 11, 11, 13, 13, 11, 11, 12, 13},  // centers 8
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13},  // centers 9
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 10
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 11
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 12
    },
    {  // unpaired 6
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 0
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 1
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 2
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 3
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 4
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 5
        {11, 11, 11, 11, 11, 11, 13, 11, 11, 11, 11, 11, 12, 13},  // centers 6
        {11, 11, 11, 11, 11, 11, 11, 13, 13, 13, 11, 11, 12, 13},  // centers 7
        {11, 11, 11, 11, 11, 11, 11, 11, 13, 13, 11, 11, 12, 13},  // centers 8
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 15, 13, 13, 13, 13},  // centers 9
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 10
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 11
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 12
    },
    {  // unpaired 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12, 13},  // centers 0
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 1
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 2
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 3
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 4
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 5
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 6
        {12, 12, 12, 12, 12, 12, 12, 12, 14, 12, 12, 12, 12, 13},  // centers 7
        {12, 12, 12, 12, 12, 12, 12, 12, 14, 14, 14, 12, 12, 13},  // centers 8
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 15, 13, 13, 13, 13},  // centers 9
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 10
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // centers 11
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // centers 12
    },
    {  // unpaired 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12, 13},  // centers 0
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 1
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 2
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 3
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 4
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 5
        {12, 12, 12, 12, 12, 12, 14, 12, 12, 12, 12, 12, 12, 13},  // centers 6
        {12, 12, 12, 12, 12, 12, 12, 14, 14, 12, 12, 12, 12, 13},  // centers 7
        {12, 12, 12, 12, 12, 12, 12, 12, 14, 14, 12, 12, 12, 13},  // centers 8
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 15, 15, 13, 13, 13},  // centers 9
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 10
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // centers 11
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // centers 12
    },
    {  // unpaired 9
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12, 13},  // centers 0
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 5
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 6
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 7
        {14, 14, 14, 14, 14, 14, 14, 14, 16, 14, 14, 14, 14, 14},  // centers 8
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 16, 14, 14, 14, 14},  // centers 9
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 17, 15, 15, 15},  // centers 10
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // centers 11
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // centers 12
    },
    {  // unpaired 10
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13},  // centers 0
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 5
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 6
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 7
        {14, 14, 14, 14, 14, 14, 14, 14, 16, 14, 14, 14, 14, 14},  // centers 8
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 16, 16, 14, 14, 14},  // centers 9
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 17, 15, 15, 15},  // centers 10
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 11
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 12
    },
    {  // unpaired 11
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 0
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 5
        {14, 14, 14, 14, 14, 14, 16, 14, 14, 14, 14, 14, 14, 14},  // centers 6
        {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17},  // centers 7
        {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17},  // centers 8
        {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17},  // centers 9
        {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17},  // centers 10
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 11
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 12
    },
    {  // unpaired 12
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 0
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13},  // centers 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 5
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 6
        {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17},  // centers 7
        {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17},  // centers 8
        {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17},  // centers 9
        {17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17, 17},  // centers 10
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 11
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 12
    },
    {  // unpaired 13
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 0
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 5
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 6
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 7
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 8
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 9
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 10
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 11
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 12
    },
    {  // unpaired 14
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 0
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 5
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 6
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 7
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 8
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 9
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 10
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 11
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 12
    },
    {  // unpaired 15
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 0
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 5
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 6
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 7
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 8
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 9
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 10
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 11
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 12
    },
    {  // unpaired 16
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 0
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13},  // centers 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14},  // centers 5
        {15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15},  // centers 6
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 7
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 8
        {18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18, 18},  // centers 9
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 10
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 11
        {19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19},  // centers 12
    },
};

static unsigned char *ranked_costs;
static int ranked_cost_fd = -1;
static const char *inner_even_filename;
static const char *inner_odd_filename;
static unsigned char *inner_even_costs;
static unsigned char *inner_odd_costs;
static int inner_even_fd = -1;
static int inner_odd_fd = -1;
static move_type inverse_move[MOVE_MAX];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_777];
static move_type solution[MAX_IDA_THRESHOLD + 1];
static unsigned int solution_limit;
static int collect_solutions;
static unsigned int collected_count;
static unsigned int collected_capacity;
static unsigned int root_limit;
static move_type (*collected)[MAX_IDA_THRESHOLD + 1];
struct phase5_root_key {
    char colors[64];
    unsigned char orbit0_odd;
};
static struct phase5_root_key *collected_keys;
static unsigned int raw_solution_count;
static unsigned char initial_orbit0_odd;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;
static float unpaired_multiplier = 0.25f;
static int use_unpaired_multiplier;
static int obliques_only;
static int stage_lr_obliques;
static float cost_to_goal_multiplier;
static unsigned char orbit0_requirement;
static unsigned char orbit1_requirement;

/* Roots the matrix prices exactly at the winning depth were never searched
 * one ply lower. A few of those can hide a shorter path when the matrix
 * overestimated. Roots below that price were already exhausted. */
#define SHORTER_ROOT_CHECKS 8

struct search_root {
    unsigned int index;
    unsigned char orbit0_requirement;
    unsigned char orbit1_requirement;
    unsigned char initial_cost;
    unsigned char quality_cost;
    unsigned char unpaired;
    char cube[CUBE_ARRAY_SIZE];
};

static void usage(const char *program)
{
    printf(
        "usage: %s {--kociemba STATE | --kociemba-file FILE} "
        "(--ranked-UD-inner-centers-cost FILE | --obliques-only | --stage-lr-obliques) "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] "
        "[--multiplier F] [--unpaired-multiplier F] "
        "[--print-ida-summary] "
        "[--solution-count N] [--root-cap N] [--initial-orbit0-odd] "
        "[--orbit0-need-odd-w] [--orbit0-need-even-w] "
        "[--orbit1-need-odd-w] [--orbit1-need-even-w] "
        "[--ud-inner-even-cost FILE --ud-inner-odd-cost FILE]\n",
        program
    );
    printf(
        "  --kociemba-file lines: ROOT_INDEX,ORBIT0_REQUIREMENT,ORBIT1_REQUIREMENT,STATE\n"
        "                       parity requirements are 0=any, 1=odd, 2=even\n"
        "  --obliques-only          pair LR obliques only; ignore the UD inner-center table\n"
        "  --stage-lr-obliques      put LR left/middle/right obliques and outer x on L and R;\n"
        "                           3-wide quarters stay illegal\n"
        "  --solution-count N       with --stage-lr-obliques, keep N solutions at the shortest\n"
        "                           length with distinct phase-5 roots; 0 keeps every distinct root\n"
        "  --initial-orbit0-odd     phase 3 starts with orbit-0 OLL parity\n"
        "  --multiplier F           scale the cost to goal by F to trade solution length for\n"
        "                           search speed, used to bootstrap the matrix samples\n"
        "  --unpaired-multiplier F  use max(table, ceil(unpaired * F)) instead of the combined\n"
        "                           matrix, and rank roots with that same estimate;\n"
        "                           0.25 is admissible and larger values are not\n"
        "  --print-ida-summary      accepted for compatibility; the path table is always printed\n"
    );
}

static uint64_t combination_rank(const char *cube, const unsigned int squares[GROUP_SIZE])
{
    return ida_combination_rank_ud(cube, squares, GROUP_SIZE, GROUP_U_COUNT);
}

static int is_lr(char sticker)
{
    return sticker == 'L' || sticker == 'R';
}

static unsigned char unpaired_oblique_count(const char *cube)
{
    unsigned char paired = 0;

    for (unsigned int index = 0; index < OBLIQUE_COUNT; index++) {
        if (is_lr(cube[middle_obliques[index]])) {
            paired += is_lr(cube[left_obliques[index]]);
            paired += is_lr(cube[right_obliques[index]]);
        }
    }
    return 16 - paired;
}

/*
 * One move can pair at most four obliques, so a multiplier of 0.25 is
 * admissible. Larger multipliers are inadmissible but are the only way to
 * solve enough cubes to sample the matrix.
 */
static unsigned char unpaired_cost(unsigned char unpaired)
{
    unsigned char cost = (unsigned char)ceilf(unpaired * unpaired_multiplier);

    return unpaired && !cost ? 1 : cost;
}

static uint64_t inner_centers_rank(const char *cube)
{
    uint64_t t_rank = combination_rank(cube, inner_t_centers);
    uint64_t x_rank = combination_rank(cube, inner_x_centers);

    if (t_rank == UINT64_MAX || x_rank == UINT64_MAX) {
        return UINT64_MAX;
    }
    return (t_rank * GROUP_UNIVERSE) + x_rank;
}

static unsigned char decode_product_cost(const unsigned char *costs, uint64_t rank)
{
    unsigned char encoded;

    if (!costs || rank >= PRODUCT_UNIVERSE) {
        return UINT8_MAX;
    }
    encoded = costs[rank];
    return encoded ? (unsigned char)(encoded - 1) : UINT8_MAX;
}

static unsigned char centers_table_cost(const char *cube)
{
    return decode_product_cost(ranked_costs, inner_centers_rank(cube));
}

/* Remaining orbit-1 parity selects the file. PARITY_ANY keeps the cheaper one. */
static unsigned char inner_orbit1_cost(uint64_t rank, unsigned char parity)
{
    unsigned char current_odd = (parity >> 1) & 1;
    unsigned char even_cost = decode_product_cost(inner_even_costs, rank);
    unsigned char odd_cost = decode_product_cost(inner_odd_costs, rank);
    int need_odd;

    if (!inner_even_costs) {
        return 0;
    }
    if (orbit1_requirement != PARITY_ODD && orbit1_requirement != PARITY_EVEN) {
        if (even_cost == UINT8_MAX) {
            return odd_cost;
        }
        if (odd_cost == UINT8_MAX) {
            return even_cost;
        }
        return even_cost < odd_cost ? even_cost : odd_cost;
    }
    need_odd = (orbit1_requirement == PARITY_ODD) != current_odd;
    return need_odd ? odd_cost : even_cost;
}

static unsigned char combined_cost(
    unsigned char centers_cost, unsigned char orbit1_cost, unsigned char unpaired)
{
    unsigned char obliques_cost;

    if (!use_unpaired_multiplier && centers_cost <= MATRIX_COST_MAX &&
        orbit1_cost <= MATRIX_ORBIT1_COST_MAX) {
        unsigned char cost = unpaired_count_UD_inner_centers_777[unpaired][centers_cost][0];

        return orbit1_cost > cost ? orbit1_cost : cost;
    }
    obliques_cost = unpaired_cost(unpaired);
    if (centers_cost > obliques_cost) {
        obliques_cost = centers_cost;
    }
    return orbit1_cost > obliques_cost ? orbit1_cost : obliques_cost;
}

/* Bit 0 counts orbit0 wide quarter turns, bit 1 counts orbit1 wide quarter turns. */
static unsigned char parity_bit_of_move(move_type move)
{
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
            return 1;
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
            return 2;
        default:
            return 0;
    }
}

static unsigned char parity_after_move(unsigned char parity, move_type move)
{
    return parity ^ parity_bit_of_move(move);
}

/*
 * A solution that leaves an orbit on the wrong wide quarter turn parity hands
 * OLL parity to the edge pairing that follows, so keep searching past it. The
 * floor is what it costs to flip an orbit from a goal state.
 */
static unsigned char parity_flip_floor(unsigned char parity)
{
    unsigned char orbit0 = parity & 1;
    unsigned char orbit1 = (parity >> 1) & 1;
    unsigned char floor = 0;

    if ((orbit0_requirement == PARITY_ODD && !orbit0) ||
        (orbit0_requirement == PARITY_EVEN && orbit0)) {
        floor = PARITY_FLOOR_ORBIT0;
    }
    if (((orbit1_requirement == PARITY_ODD && !orbit1) ||
         (orbit1_requirement == PARITY_EVEN && orbit1)) &&
        PARITY_FLOOR_ORBIT1 > floor) {
        floor = PARITY_FLOOR_ORBIT1;
    }
    return floor;
}

static unsigned char cost_from_rank(uint64_t rank, unsigned char parity, unsigned char unpaired)
{
    unsigned char cost;

    if (obliques_only) {
        cost = use_unpaired_multiplier ? unpaired_cost(unpaired)
                                       : unpaired_count_UD_inner_centers_777[unpaired][0][0];
    } else {
        unsigned char centers_cost = decode_product_cost(ranked_costs, rank);
        unsigned char orbit_cost = 0;

        if (centers_cost == UINT8_MAX) {
            return UINT8_MAX;
        }
        if (inner_even_costs) {
            orbit_cost = inner_orbit1_cost(rank, parity);
            if (orbit_cost == UINT8_MAX) {
                return UINT8_MAX;
            }
        }
        cost = combined_cost(centers_cost, orbit_cost, unpaired);
    }
    if (cost && cost_to_goal_multiplier) {
        cost = (unsigned char)roundf(cost * cost_to_goal_multiplier);
    }
    return cost ? cost : parity_flip_floor(parity);
}

/*
 * Phase 3. Each orbit is C(24, 8) = 735,471. The single goal puts the eight
 * L/R colors on the L and R faces. Distance is exact for one orbit, so the
 * max of the four (three oblique orbits plus outer x) is admissible. 3-wide
 * quarters stay illegal: they would flip the orbit-1 parity phase 2 already set.
 */
#define STAGE_ORBIT_COUNT 4
#define STAGE_POSITIONS 24
#define STAGE_LR_COUNT 8
#define STAGE_UNIVERSE 735471u
#define STAGE_CACHE "rubikscubennnsolver/lr-oblique-stage-777.bin"
static const char STAGE_CACHE_MAGIC[4] = {'L', 'R', 'O', '4'};

static int move_is_allowed(move_type move);
static double elapsed_seconds(const struct timeval *start, const struct timeval *end);

static unsigned char *stage_cost[STAGE_ORBIT_COUNT];
static unsigned char stage_src[STAGE_ORBIT_COUNT][MOVE_COUNT_777][STAGE_POSITIONS];
static unsigned char stage_moves[MOVE_COUNT_777];
static unsigned int stage_move_count;

static const unsigned int *stage_orbits[STAGE_ORBIT_COUNT] = {
    left_obliques,
    middle_obliques,
    right_obliques,
    outer_x_centers,
};

static uint32_t stage_mask_rank(uint32_t mask)
{
    unsigned int remaining = STAGE_LR_COUNT;
    uint32_t rank = 0;

    for (unsigned int position = 0; position < STAGE_POSITIONS; position++) {
        unsigned int after = STAGE_POSITIONS - position - 1;

        if (mask & (1u << position)) {
            remaining--;
        } else if (remaining) {
            rank += (uint32_t)binom[after][remaining - 1];
        }
    }
    return remaining ? UINT32_MAX : rank;
}

static uint32_t stage_rank(const char *cube, const unsigned int squares[STAGE_POSITIONS])
{
    unsigned int remaining = STAGE_LR_COUNT;
    uint32_t rank = 0;

    for (unsigned int position = 0; position < STAGE_POSITIONS; position++) {
        unsigned int after = STAGE_POSITIONS - position - 1;

        if (cube[squares[position]] == 'L') {
            if (!remaining) {
                return UINT32_MAX;
            }
            remaining--;
        } else if (remaining) {
            rank += (uint32_t)binom[after][remaining - 1];
        }
    }
    return remaining ? UINT32_MAX : rank;
}

static unsigned char stage_lr_cost(const char *cube)
{
    unsigned char best = 0;

    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        uint32_t rank = stage_rank(cube, stage_orbits[orbit]);
        unsigned char encoded;

        if (rank >= STAGE_UNIVERSE) {
            return UINT8_MAX;
        }
        encoded = stage_cost[orbit][rank];
        if (!encoded) {
            return UINT8_MAX;
        }
        if ((unsigned char)(encoded - 1) > best) {
            best = (unsigned char)(encoded - 1);
        }
    }
    return best;
}

static void free_stage_tables(void)
{
    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        free(stage_cost[orbit]);
        stage_cost[orbit] = NULL;
    }
}

static int load_stage_cache(void)
{
    FILE *file = fopen(STAGE_CACHE, "rb");
    char magic[4];

    if (!file) {
        return 0;
    }
    if (fread(magic, 1, 4, file) != 4 || memcmp(magic, STAGE_CACHE_MAGIC, 4) != 0) {
        fclose(file);
        return 0;
    }
    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        stage_cost[orbit] = malloc(STAGE_UNIVERSE);
        if (!stage_cost[orbit] || fread(stage_cost[orbit], 1, STAGE_UNIVERSE, file) != STAGE_UNIVERSE) {
            fclose(file);
            free_stage_tables();
            return 0;
        }
    }
    fclose(file);
    return 1;
}

static void save_stage_cache(void)
{
    FILE *file = fopen(STAGE_CACHE, "wb");

    if (!file) {
        return;
    }
    fwrite(STAGE_CACHE_MAGIC, 1, 4, file);
    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        fwrite(stage_cost[orbit], 1, STAGE_UNIVERSE, file);
    }
    fclose(file);
}

static void build_stage_permutations(void)
{
    stage_move_count = 0;
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_777; move_index++) {
        if (move_is_allowed(moves_777[move_index])) {
            stage_moves[stage_move_count++] = (unsigned char)move_index;
        }
    }

    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        const unsigned int *squares = stage_orbits[orbit];

        for (unsigned int list_index = 0; list_index < stage_move_count; list_index++) {
            unsigned int move_index = stage_moves[list_index];
            unsigned char cube[CUBE_ARRAY_SIZE];
            unsigned char scratch[CUBE_ARRAY_SIZE];

            memset(cube, 0xFF, sizeof(cube));
            for (unsigned int position = 0; position < STAGE_POSITIONS; position++) {
                cube[squares[position]] = (unsigned char)position;
            }
            rotate_777_centers((char *)cube, (char *)scratch, CUBE_ARRAY_SIZE, moves_777[move_index]);
            for (unsigned int destination = 0; destination < STAGE_POSITIONS; destination++) {
                unsigned char source = cube[squares[destination]];

                if (source >= STAGE_POSITIONS) {
                    fprintf(
                        stderr,
                        "ERROR: LR stage orbit is not closed under %s\n",
                        move2str[moves_777[move_index]]
                    );
                    exit(1);
                }
                stage_src[orbit][move_index][destination] = source;
            }
        }
    }
}

static void build_stage_tables(void)
{
    uint32_t goal_mask = (0xFu << 4) | (0xFu << 12);
    uint32_t goal_rank = stage_mask_rank(goal_mask);
    uint32_t *masks;
    uint32_t *ranks;
    struct timeval start;
    struct timeval end;

    if (goal_rank >= STAGE_UNIVERSE) {
        fprintf(stderr, "ERROR: LR stage goal rank is outside C(24, 8)\n");
        exit(1);
    }
    masks = malloc(sizeof(uint32_t) * STAGE_UNIVERSE);
    ranks = malloc(sizeof(uint32_t) * STAGE_UNIVERSE);
    if (!masks || !ranks) {
        fprintf(stderr, "ERROR: out of memory building LR stage tables\n");
        exit(1);
    }
    build_stage_permutations();
    gettimeofday(&start, NULL);
    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        uint32_t head = 0;
        uint32_t tail = 0;

        stage_cost[orbit] = calloc(STAGE_UNIVERSE, 1);
        if (!stage_cost[orbit]) {
            fprintf(stderr, "ERROR: out of memory building LR stage tables\n");
            exit(1);
        }
        stage_cost[orbit][goal_rank] = 1;
        masks[tail] = goal_mask;
        ranks[tail] = goal_rank;
        tail++;
        while (head < tail) {
            uint32_t mask = masks[head];
            unsigned char encoded = stage_cost[orbit][ranks[head]];

            head++;
            for (unsigned int list_index = 0; list_index < stage_move_count; list_index++) {
                unsigned int move_index = stage_moves[list_index];
                uint32_t next_mask = 0;
                uint32_t next_rank;

                for (unsigned int destination = 0; destination < STAGE_POSITIONS; destination++) {
                    unsigned char source = stage_src[orbit][move_index][destination];

                    if (mask & (1u << source)) {
                        next_mask |= 1u << destination;
                    }
                }
                next_rank = stage_mask_rank(next_mask);
                if (next_rank >= STAGE_UNIVERSE || stage_cost[orbit][next_rank]) {
                    continue;
                }
                stage_cost[orbit][next_rank] = (unsigned char)(encoded + 1);
                masks[tail] = next_mask;
                ranks[tail] = next_rank;
                tail++;
            }
        }
        LOG("LR stage orbit %u reached %" PRIu32 " states\n", orbit, tail);
    }
    gettimeofday(&end, NULL);
    LOG("LR stage tables built in %.3fs\n", elapsed_seconds(&start, &end));
    free(masks);
    free(ranks);
}

static unsigned char cube_cost(const char *cube, unsigned char parity)
{
    if (stage_lr_obliques) {
        (void)parity;
        return stage_lr_cost(cube);
    }
    return cost_from_rank(obliques_only ? 0 : inner_centers_rank(cube), parity, unpaired_oblique_count(cube));
}

/*
 * Last ply must land on a goal: staged centers and both orbit parities already
 * correct. A move that leaves an orbit on the wrong parity still needs the
 * flip floor (1 for orbit0, 7 for orbit1), so it cannot be the 12th move of a
 * depth-12 solution. Skip the rotate and table lookup for those moves.
 */
static int last_ply_can_be_goal(unsigned char parity, move_type move)
{
    return !parity_flip_floor(parity_after_move(parity, move));
}

static int move_is_allowed(move_type move)
{
    switch (move) {
        case threeUw:
        case threeUw_PRIME:
        case threeFw:
        case threeFw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case threeDw:
        case threeDw_PRIME:
            return 0;
        case threeLw:
        case threeLw_PRIME:
        case threeRw:
        case threeRw_PRIME:
            return !stage_lr_obliques;
        default:
            return 1;
    }
}

static void init_move_tables(void)
{
    ida_init_move_tables(
        moves_777, MOVE_COUNT_777, move_is_allowed, legal_move_count, legal_move_index, inverse_move
    );
}

static void map_ranked_cost_file(const char *filename)
{
    struct mapped_cost_file file = ida_map_cost_file(filename, PRODUCT_UNIVERSE);

    ranked_cost_fd = file.fd;
    ranked_costs = file.costs;
}

static void unmap_inner_tables(void)
{
    if (ranked_costs && ranked_costs != MAP_FAILED) {
        ida_unmap_cost_file(ranked_cost_fd, ranked_costs, (size_t)PRODUCT_UNIVERSE);
    }
    if (inner_even_costs && inner_even_costs != MAP_FAILED) {
        ida_unmap_cost_file(inner_even_fd, inner_even_costs, (size_t)PRODUCT_UNIVERSE);
    }
    if (inner_odd_costs && inner_odd_costs != MAP_FAILED) {
        ida_unmap_cost_file(inner_odd_fd, inner_odd_costs, (size_t)PRODUCT_UNIVERSE);
    }
    ranked_costs = inner_even_costs = inner_odd_costs = NULL;
}

static void init_cube(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    ida_init_cube(cube, CUBE_SIZE, kociemba);
}

static int is_outer_x_center(unsigned int square)
{
    unsigned int face_offset = (square - 1) % (CUBE_SIZE * CUBE_SIZE);

    return face_offset == 8 || face_offset == 12 || face_offset == 36 || face_offset == 40;
}

static int is_oblique(unsigned int square)
{
    unsigned int face_offset = (square - 1) % (CUBE_SIZE * CUBE_SIZE);

    switch (face_offset) {
        case 9:
        case 10:
        case 11:
        case 15:
        case 19:
        case 22:
        case 26:
        case 29:
        case 33:
        case 37:
        case 38:
        case 39:
            return 1;
        default:
            return 0;
    }
}

static void recolor_cube(char cube[CUBE_ARRAY_SIZE])
{
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (ida_is_edge_or_corner(square, CUBE_SIZE) ||
            (!stage_lr_obliques && is_outer_x_center(square))) {
            cube[square] = '.';
        } else if (!stage_lr_obliques && (is_oblique(square) || is_outer_x_center(square))) {
            cube[square] = is_lr(cube[square]) ? 'L' : 'x';
        } else if (cube[square] == 'R') {
            cube[square] = 'L';
        } else if (cube[square] == 'D') {
            cube[square] = 'U';
        } else if (cube[square] == 'B') {
            cube[square] = 'F';
        }
    }
}

static void phase5_root_key(
    const char cube[CUBE_ARRAY_SIZE], unsigned char path_parity, struct phase5_root_key *key)
{
    unsigned int used = 0;

    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        for (unsigned int position = 0; position < STAGE_POSITIONS; position++) {
            /* Skip the four L-face and four R-face positions. */
            if ((position >= 4 && position < 8) || (position >= 12 && position < 16)) {
                continue;
            }
            key->colors[used++] = cube[stage_orbits[orbit][position]];
        }
    }
    key->orbit0_odd = initial_orbit0_odd ^ path_parity;
}

/* Append a solution with a new phase-5 root key; returns 1 once solution_limit is reached. */
static int keep_solution(const move_type *moves, const struct phase5_root_key *key)
{
    for (unsigned int index = 0; index < collected_count; index++) {
        if (!memcmp(&collected_keys[index], key, sizeof(*key))) {
            return solution_limit && collected_count >= solution_limit;
        }
    }
    if (solution_limit && collected_count >= solution_limit) {
        return 1;
    }
    if (collected_count == collected_capacity) {
        unsigned int grown = collected_capacity ? collected_capacity * 2 : 16;
        move_type (*next)[MAX_IDA_THRESHOLD + 1] = realloc(collected, grown * sizeof(*collected));
        struct phase5_root_key *next_keys;

        if (!next) {
            fprintf(stderr, "ERROR: could not store phase 3 solutions\n");
            exit(1);
        }
        collected = next;
        next_keys = realloc(collected_keys, grown * sizeof(*collected_keys));
        if (!next_keys) {
            fprintf(stderr, "ERROR: could not store phase 3 root keys\n");
            exit(1);
        }
        collected_keys = next_keys;
        collected_capacity = grown;
    }
    memcpy(collected[collected_count], moves, sizeof(collected[0]));
    collected_keys[collected_count] = *key;
    collected_count++;
    return solution_limit && collected_count >= solution_limit;
}

/*
 * lr[orbit] has bit p set when stage_orbits[orbit][p] holds an L sticker and
 * inner[group] has bit p set when that inner t or x square holds U. Moves are
 * byte lookups and ranks are table lookups, so the cube array is only rebuilt
 * for a solution's phase-5 root key.
 */
struct node {
    uint32_t lr[STAGE_ORBIT_COUNT];
    uint16_t inner[2];
};

struct child {
    struct node node;
    uint32_t stage_rank[STAGE_ORBIT_COUNT];
    uint64_t inner_rank;
    move_type move;
    unsigned char parity;
    unsigned char unpaired;
    unsigned char cost;
};

#define INNER_INVALID UINT16_MAX
static const unsigned int *inner_groups[2] = {inner_t_centers, inner_x_centers};
static uint32_t lr_move_chunk[MOVE_MAX][STAGE_ORBIT_COUNT][3][256];
static uint16_t inner_move_chunk[MOVE_MAX][2][2][256];
static uint32_t lr_rank_chunk[3][STAGE_LR_COUNT + 1][256];
static uint16_t inner_mask_rank[1 << GROUP_SIZE];

static void init_node_tables(void)
{
    for (unsigned int mask = 0; mask < (1u << GROUP_SIZE); mask++) {
        unsigned int remaining = GROUP_U_COUNT;
        unsigned int rank = 0;

        if (__builtin_popcount(mask) != GROUP_U_COUNT) {
            inner_mask_rank[mask] = INNER_INVALID;
            continue;
        }
        for (unsigned int position = 0; position < GROUP_SIZE && remaining; position++) {
            if (mask & (1u << position)) {
                remaining--;
            } else {
                rank += (unsigned int)binom[GROUP_SIZE - position - 1][remaining - 1];
            }
        }
        inner_mask_rank[mask] = (uint16_t)rank;
    }
    for (unsigned int chunk = 0; chunk < 3; chunk++) {
        for (unsigned int start = 0; start <= STAGE_LR_COUNT; start++) {
            for (unsigned int byte = 0; byte < 256; byte++) {
                unsigned int remaining = start;
                uint32_t rank = 0;

                for (unsigned int bit = 0; bit < 8 && remaining; bit++) {
                    unsigned int position = chunk * 8 + bit;

                    if (byte & (1u << bit)) {
                        remaining--;
                    } else {
                        rank += (uint32_t)binom[STAGE_POSITIONS - position - 1][remaining - 1];
                    }
                }
                lr_rank_chunk[chunk][start][byte] = rank;
            }
        }
    }

    for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
        move_type move = moves_777[legal_move_index[MOVE_NONE][index]];
        unsigned char cube[CUBE_ARRAY_SIZE];
        unsigned char scratch[CUBE_ARRAY_SIZE];

        memset(cube, 0, sizeof(cube));
        for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
            for (unsigned int position = 0; position < STAGE_POSITIONS; position++) {
                cube[stage_orbits[orbit][position]] = (unsigned char)(1 + orbit * STAGE_POSITIONS + position);
            }
        }
        for (unsigned int group = 0; group < 2; group++) {
            for (unsigned int position = 0; position < GROUP_SIZE; position++) {
                cube[inner_groups[group][position]] =
                    (unsigned char)(1 + STAGE_ORBIT_COUNT * STAGE_POSITIONS + group * GROUP_SIZE + position);
            }
        }
        rotate_777_centers((char *)cube, (char *)scratch, CUBE_ARRAY_SIZE, move);

        for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
            unsigned char source[STAGE_POSITIONS];

            for (unsigned int position = 0; position < STAGE_POSITIONS; position++) {
                int value = cube[stage_orbits[orbit][position]] - 1;

                if (value < 0 || (unsigned int)value / STAGE_POSITIONS != orbit) {
                    fprintf(stderr, "ERROR: %s moves an oblique or outer x out of its orbit\n", move2str[move]);
                    exit(1);
                }
                source[position] = (unsigned char)(value % STAGE_POSITIONS);
            }
            for (unsigned int chunk = 0; chunk < 3; chunk++) {
                for (unsigned int byte = 0; byte < 256; byte++) {
                    uint32_t bits = 0;

                    for (unsigned int position = 0; position < STAGE_POSITIONS; position++) {
                        if (source[position] / 8 == chunk && (byte & (1u << (source[position] % 8)))) {
                            bits |= 1u << position;
                        }
                    }
                    lr_move_chunk[move][orbit][chunk][byte] = bits;
                }
            }
        }
        for (unsigned int group = 0; group < 2; group++) {
            unsigned char source[GROUP_SIZE];

            for (unsigned int position = 0; position < GROUP_SIZE; position++) {
                int value = cube[inner_groups[group][position]] - 1 - STAGE_ORBIT_COUNT * STAGE_POSITIONS;

                if (value < 0 || (unsigned int)value / GROUP_SIZE != group) {
                    fprintf(stderr, "ERROR: %s moves an inner center out of its group\n", move2str[move]);
                    exit(1);
                }
                source[position] = (unsigned char)(value % GROUP_SIZE);
            }
            for (unsigned int chunk = 0; chunk < 2; chunk++) {
                for (unsigned int byte = 0; byte < 256; byte++) {
                    uint16_t bits = 0;

                    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
                        if (source[position] / 8 == chunk && (byte & (1u << (source[position] % 8)))) {
                            bits |= (uint16_t)(1u << position);
                        }
                    }
                    inner_move_chunk[move][group][chunk][byte] = bits;
                }
            }
        }
    }
}

static struct node node_from_cube(const char *cube)
{
    struct node node;

    memset(&node, 0, sizeof(node));
    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        for (unsigned int position = 0; position < STAGE_POSITIONS; position++) {
            if (cube[stage_orbits[orbit][position]] == 'L') {
                node.lr[orbit] |= 1u << position;
            }
        }
    }
    for (unsigned int group = 0; group < 2; group++) {
        for (unsigned int position = 0; position < GROUP_SIZE; position++) {
            char sticker = cube[inner_groups[group][position]];

            if (sticker == 'U' || sticker == 'D') {
                node.inner[group] |= (uint16_t)(1u << position);
            }
        }
    }
    return node;
}

static inline struct node node_apply_move(const struct node *node, move_type move)
{
    struct node next;

    for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
        const uint32_t (*chunk)[256] = lr_move_chunk[move][orbit];
        uint32_t mask = node->lr[orbit];

        next.lr[orbit] = chunk[0][mask & 0xFF] | chunk[1][(mask >> 8) & 0xFF] | chunk[2][mask >> 16];
    }
    for (unsigned int group = 0; group < 2; group++) {
        const uint16_t (*chunk)[256] = inner_move_chunk[move][group];
        uint16_t mask = node->inner[group];

        next.inner[group] = chunk[0][mask & 0xFF] | chunk[1][mask >> 8];
    }
    return next;
}

static inline unsigned char node_unpaired(const struct node *node)
{
    return (unsigned char)(16 - __builtin_popcount(node->lr[1] & node->lr[0]) -
                           __builtin_popcount(node->lr[1] & node->lr[2]));
}

static inline uint32_t lr_rank(uint32_t mask)
{
    unsigned int first = mask & 0xFF;
    unsigned int second = (mask >> 8) & 0xFF;
    unsigned int remaining = STAGE_LR_COUNT;
    uint32_t rank;

    if (__builtin_popcount(mask) != STAGE_LR_COUNT) {
        return UINT32_MAX;
    }
    rank = lr_rank_chunk[0][remaining][first];
    remaining -= (unsigned int)__builtin_popcount(first);
    rank += lr_rank_chunk[1][remaining][second];
    remaining -= (unsigned int)__builtin_popcount(second);
    return rank + lr_rank_chunk[2][remaining][mask >> 16];
}

static inline uint64_t node_inner_rank(const struct node *node)
{
    uint16_t t_rank = inner_mask_rank[node->inner[0]];
    uint16_t x_rank = inner_mask_rank[node->inner[1]];

    if (t_rank == INNER_INVALID || x_rank == INNER_INVALID) {
        return UINT64_MAX;
    }
    return (uint64_t)t_rank * GROUP_UNIVERSE + x_rank;
}

/* Rank the child and start its table reads; child_cost() reads them. */
static inline void child_prefetch(struct child *child)
{
    if (stage_lr_obliques) {
        for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
            child->stage_rank[orbit] = lr_rank(child->node.lr[orbit]);
            if (child->stage_rank[orbit] < STAGE_UNIVERSE) {
                __builtin_prefetch(&stage_cost[orbit][child->stage_rank[orbit]]);
            }
        }
        return;
    }
    if (obliques_only) {
        return;
    }
    child->inner_rank = node_inner_rank(&child->node);
    if (child->inner_rank < PRODUCT_UNIVERSE) {
        __builtin_prefetch(&ranked_costs[child->inner_rank]);
        if (inner_even_costs) {
            __builtin_prefetch(&inner_even_costs[child->inner_rank]);
            __builtin_prefetch(&inner_odd_costs[child->inner_rank]);
        }
    }
}

static inline unsigned char child_cost(const struct child *child)
{
    if (stage_lr_obliques) {
        unsigned char best = 0;

        for (unsigned int orbit = 0; orbit < STAGE_ORBIT_COUNT; orbit++) {
            unsigned char encoded;

            if (child->stage_rank[orbit] >= STAGE_UNIVERSE) {
                return UINT8_MAX;
            }
            encoded = stage_cost[orbit][child->stage_rank[orbit]];
            if (!encoded) {
                return UINT8_MAX;
            }
            if ((unsigned char)(encoded - 1) > best) {
                best = (unsigned char)(encoded - 1);
            }
        }
        return best;
    }
    return cost_from_rank(child->inner_rank, child->parity, child->unpaired);
}

struct found_solution {
    move_type moves[MAX_IDA_THRESHOLD + 1];
    struct phase5_root_key key;
};

/* --solution-count results for one task: distinct keys, capped at solution_limit. */
struct task_solutions {
    struct found_solution *items;
    unsigned int count;
    unsigned int capacity;
    unsigned int raw;
};

struct walker {
    const struct ida_ordered_tasks *tasks;
    size_t task;
    unsigned char threshold;
    uint64_t nodes;
    const char *root_cube;
    struct task_solutions *found;
    move_type path[MAX_IDA_THRESHOLD + 1];
};

/* Record walker->path, which ends on a goal; returns 1 once this task holds solution_limit keys. */
static int record_solution(struct walker *walker, unsigned char path_parity)
{
    struct task_solutions *found = walker->found;
    struct found_solution solution_found;
    char cube[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];

    memcpy(cube, walker->root_cube, CUBE_ARRAY_SIZE);
    for (unsigned int index = 0; walker->path[index] != MOVE_NONE; index++) {
        rotate_777_centers(cube, scratch, CUBE_ARRAY_SIZE, walker->path[index]);
    }
    phase5_root_key(cube, path_parity, &solution_found.key);
    found->raw++;
    for (unsigned int index = 0; index < found->count; index++) {
        if (!memcmp(&found->items[index].key, &solution_found.key, sizeof(solution_found.key))) {
            return 0;
        }
    }
    if (found->count == found->capacity) {
        unsigned int capacity = found->capacity ? found->capacity * 2 : 8;
        struct found_solution *grown = realloc(found->items, capacity * sizeof(*grown));

        if (!grown) {
            fprintf(stderr, "ERROR: could not store phase 3 solutions\n");
            exit(1);
        }
        found->items = grown;
        found->capacity = capacity;
    }
    memcpy(solution_found.moves, walker->path, sizeof(solution_found.moves));
    found->items[found->count++] = solution_found;
    return solution_limit && found->count >= solution_limit;
}

/*
 * Score every legal child of node. A child that undoes oblique pairing is
 * dropped before any table read. Below the root, the first goal child in move
 * order is returned alone with *goal set; otherwise the children that fit
 * under the threshold come back cheapest first. The root keeps move order and
 * its goal children, because each root move is searched on its own.
 */
static unsigned int score_children(
    struct walker *walker,
    const struct node *node,
    unsigned char depth,
    move_type previous_move,
    unsigned char parity,
    int root,
    struct child children[MOVE_COUNT_777],
    int *goal
)
{
    unsigned char next_depth = depth + 1;
    unsigned char threshold = walker->threshold;
    int last_ply = next_depth == threshold;
    unsigned char unpaired_before = node_unpaired(node);
    unsigned int count = 0;
    unsigned int kept = 0;

    *goal = 0;
    for (unsigned int index = 0; index < legal_move_count[previous_move]; index++) {
        move_type move = moves_777[legal_move_index[previous_move][index]];
        struct child *child = &children[count];

        if (last_ply && !last_ply_can_be_goal(parity, move)) {
            continue;
        }
        walker->nodes++;
        child->node = node_apply_move(node, move);
        if (!stage_lr_obliques) {
            child->unpaired = node_unpaired(&child->node);
            if (child->unpaired > unpaired_before) {
                continue;
            }
        }
        child->move = move;
        child->parity = parity_after_move(parity, move);
        child_prefetch(child);
        count++;
    }
    for (unsigned int index = 0; index < count; index++) {
        unsigned char cost = child_cost(&children[index]);

        if (cost == UINT8_MAX || next_depth + cost > threshold) {
            continue;
        }
        children[index].cost = cost;
        if (!cost && !root) {
            children[0] = children[index];
            *goal = 1;
            return 1;
        }
        children[kept++] = children[index];
    }
    if (root || next_depth >= threshold) {
        return kept;
    }
    for (unsigned int index = 1; index < kept; index++) {
        struct child pending = children[index];
        unsigned int destination = index;

        while (destination && children[destination - 1].cost > pending.cost) {
            children[destination] = children[destination - 1];
            destination--;
        }
        children[destination] = pending;
    }
    return kept;
}

/* Returns 1 when the task is done: a solution, or solution_limit distinct keys. */
static int ida_search(
    struct walker *walker,
    const struct node *node,
    unsigned char depth,
    move_type previous_move,
    unsigned char parity
)
{
    struct child children[MOVE_COUNT_777];
    unsigned char next_depth = depth + 1;
    unsigned int count;
    int goal;

    if (ida_task_abandoned(walker->tasks, walker->task)) {
        return 0;
    }
    count = score_children(walker, node, depth, previous_move, parity, 0, children, &goal);
    if (goal) {
        walker->path[depth] = children[0].move;
        walker->path[next_depth] = MOVE_NONE;
        return collect_solutions ? record_solution(walker, children[0].parity) : 1;
    }
    if (next_depth >= walker->threshold || next_depth >= MAX_IDA_THRESHOLD) {
        return 0;
    }
    for (unsigned int index = 0; index < count; index++) {
        walker->path[depth] = children[index].move;
        if (ida_search(walker, &children[index].node, next_depth, children[index].move, children[index].parity)) {
            return 1;
        }
    }
    return 0;
}

/*
 * The first few plies are walked once and every surviving node at split_depth
 * becomes a task. Tasks run cheapest first, ties in search order. Without
 * --solution-count the first solution found stops every task: making later
 * tasks wait on earlier ones costs up to ten times the nodes at the solving
 * threshold. With it, task results merge in task order until solution_limit
 * distinct keys are kept, so the kept set does not depend on the thread count.
 */
#define MAX_SPLIT_DEPTH 3
#define SPLIT_TASK_TARGET 2048
#define SPLIT_BRANCHING 24

struct split_task {
    struct node node;
    move_type prefix[MAX_SPLIT_DEPTH];
    unsigned char depth;
    unsigned char parity;
    unsigned char solved;
    unsigned char cost;
    unsigned char done;
    uint32_t order;
    uint64_t nodes;
    move_type *solution;
    struct task_solutions found;
};

struct split_search {
    struct ida_ordered_tasks tasks;
    unsigned char threshold;
    unsigned char split_depth;
    const char *root_cube;
    struct split_task *items;
    size_t count;
    size_t capacity;
    size_t merged;
};

static int compare_split_tasks(const void *left, const void *right)
{
    const struct split_task *a = left;
    const struct split_task *b = right;

    if (a->cost != b->cost) {
        return a->cost < b->cost ? -1 : 1;
    }
    return a->order < b->order ? -1 : a->order > b->order;
}

static void add_split_task(
    struct split_search *search,
    const move_type *prefix,
    unsigned char depth,
    const struct child *child,
    int solved
)
{
    struct split_task *task;

    if (search->count == search->capacity) {
        size_t capacity = search->capacity ? search->capacity * 2 : 1024;
        struct split_task *grown = realloc(search->items, capacity * sizeof(*grown));

        if (!grown) {
            fprintf(stderr, "ERROR: could not allocate search tasks\n");
            exit(1);
        }
        search->items = grown;
        search->capacity = capacity;
    }
    task = &search->items[search->count++];
    memset(task, 0, sizeof(*task));
    memcpy(task->prefix, prefix, depth * sizeof(*prefix));
    task->node = child->node;
    task->depth = depth;
    task->parity = child->parity;
    task->solved = (unsigned char)solved;
    task->cost = solved ? 0 : child->cost;
    task->order = (uint32_t)(search->count - 1);
}

/*
 * Mirrors ida_search down to split_depth. Returns 1 once a goal ends the walk;
 * with --solution-count a goal only ends its parent, as in ida_search.
 */
static int split_node(
    struct split_search *search,
    struct walker *walker,
    const struct node *node,
    unsigned char depth,
    move_type previous_move,
    unsigned char parity
)
{
    struct child children[MOVE_COUNT_777];
    unsigned char next_depth = depth + 1;
    unsigned int count;
    int goal;

    count = score_children(walker, node, depth, previous_move, parity, 0, children, &goal);
    if (goal) {
        walker->path[depth] = children[0].move;
        add_split_task(search, walker->path, next_depth, &children[0], 1);
        return !collect_solutions;
    }
    if (next_depth >= walker->threshold || next_depth >= MAX_IDA_THRESHOLD) {
        return 0;
    }
    for (unsigned int index = 0; index < count; index++) {
        walker->path[depth] = children[index].move;
        if (next_depth == search->split_depth) {
            add_split_task(search, walker->path, next_depth, &children[index], 0);
        } else if (split_node(search, walker, &children[index].node, next_depth, children[index].move, children[index].parity)) {
            return 1;
        }
    }
    return 0;
}

/* Merge finished tasks in order; stop the rest once solution_limit keys are kept. */
static void merge_finished_tasks(struct split_search *search, size_t index)
{
    pthread_mutex_lock(&solution_lock);
    search->items[index].done = 1;
    while (search->merged < search->count && search->items[search->merged].done &&
           !(solution_limit && collected_count >= solution_limit)) {
        struct task_solutions *found = &search->items[search->merged].found;

        raw_solution_count += found->raw;
        for (unsigned int which = 0; which < found->count; which++) {
            if (keep_solution(found->items[which].moves, &found->items[which].key)) {
                break;
            }
        }
        search->merged++;
    }
    if (solution_limit && collected_count >= solution_limit) {
        ida_stop_tasks_after(&search->tasks, search->merged - 1);
    }
    pthread_mutex_unlock(&solution_lock);
}

static void run_split_task(struct ida_ordered_tasks *tasks, size_t index)
{
    struct split_search *search = tasks->context;
    struct split_task *task = &search->items[index];
    struct walker walker;
    int found = 1;

    walker.tasks = tasks;
    walker.task = index;
    walker.threshold = search->threshold;
    walker.nodes = 0;
    walker.root_cube = search->root_cube;
    walker.found = &task->found;
    memcpy(walker.path, task->prefix, task->depth * sizeof(*task->prefix));
    walker.path[task->depth] = MOVE_NONE;
    if (task->solved) {
        if (collect_solutions) {
            found = record_solution(&walker, task->parity);
        }
    } else {
        found = ida_search(&walker, &task->node, task->depth, task->prefix[task->depth - 1], task->parity);
    }
    task->nodes = walker.nodes;
    if (collect_solutions) {
        if (found) {
            ida_stop_tasks_after(tasks, index);
        }
        merge_finished_tasks(search, index);
        return;
    }
    if (found) {
        task->solution = malloc(sizeof(walker.path));
        if (!task->solution) {
            fprintf(stderr, "ERROR: could not allocate a solution\n");
            exit(1);
        }
        memcpy(task->solution, walker.path, sizeof(walker.path));
        ida_stop_all_tasks(tasks);
    }
}

static int search_at_threshold(
    const char cube[CUBE_ARRAY_SIZE],
    unsigned char threshold,
    unsigned int thread_count,
    uint64_t *nodes
)
{
    struct split_search search;
    struct walker walker;
    struct node root = node_from_cube(cube);
    struct child children[MOVE_COUNT_777];
    unsigned int count;
    unsigned int estimate = legal_move_count[MOVE_NONE];
    int goal;
    int found = 0;

    if (collect_solutions) {
        collected_count = 0;
        raw_solution_count = 0;
    }
    memset(&search, 0, sizeof(search));
    search.threshold = threshold;
    search.root_cube = cube;
    search.split_depth = 1;
    while (estimate < SPLIT_TASK_TARGET && search.split_depth < MAX_SPLIT_DEPTH && search.split_depth + 1 < threshold) {
        estimate *= SPLIT_BRANCHING;
        search.split_depth++;
    }
    search.tasks.stop_from = SIZE_MAX;
    walker.tasks = &search.tasks;
    walker.task = 0;
    walker.threshold = threshold;
    walker.nodes = 1;
    walker.root_cube = cube;
    walker.found = NULL;

    count = score_children(&walker, &root, 0, MOVE_NONE, 0, 1, children, &goal);
    for (unsigned int index = 0; index < count; index++) {
        walker.path[0] = children[index].move;
        if (!children[index].cost) {
            add_split_task(&search, walker.path, 1, &children[index], 1);
            if (!collect_solutions) {
                break;
            }
            continue;
        }
        if (threshold <= 1) {
            continue;
        }
        if (search.split_depth == 1) {
            add_split_task(&search, walker.path, 1, &children[index], 0);
        } else if (split_node(&search, &walker, &children[index].node, 1, children[index].move, children[index].parity)) {
            break;
        }
    }

    qsort(search.items, search.count, sizeof(*search.items), compare_split_tasks);
    search.tasks.task_count = search.count;
    search.tasks.run = run_split_task;
    search.tasks.context = &search;
    ida_run_ordered_tasks(&search.tasks, thread_count);

    *nodes = walker.nodes;
    for (size_t index = 0; index < search.count; index++) {
        struct split_task *task = &search.items[index];

        *nodes += task->nodes;
        if (task->solution && !found) {
            memcpy(solution, task->solution, sizeof(solution));
            found = 1;
        }
        free(task->solution);
        free(task->found.items);
    }
    free(search.items);
    if (collect_solutions) {
        return collected_count > 0;
    }
    return found;
}

static double elapsed_seconds(const struct timeval *start, const struct timeval *end)
{
    return (end->tv_sec - start->tv_sec) + (end->tv_usec - start->tv_usec) / 1000000.0;
}

/*
 * One row per state along the solution. TRU is the true remaining distance,
 * which is what the matrix builder samples for each (UNPR, TBL, ORB) tuple.
 */
static void print_ida_summary(const char cube[CUBE_ARRAY_SIZE], unsigned int length)
{
    char walk[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];
    unsigned char parity = 0;

    memcpy(walk, cube, CUBE_ARRAY_SIZE);
    printf("\n       TBL  ORB UNPR  CTG  TRU  IDX\n      ==== ==== ====  ===  ===  ===\n");
    for (unsigned int step = 0; step <= length; step++) {
        unsigned char unpaired = unpaired_oblique_count(walk);
        unsigned char centers_cost = obliques_only ? 0 : centers_table_cost(walk);
        unsigned char orbit_cost = inner_even_costs ?
                                   inner_orbit1_cost(inner_centers_rank(walk), parity) : 0;

        if (step) {
            printf("%5s ", move2str[solution[step - 1]]);
        } else {
            printf(" INIT ");
        }
        printf(
            " %4u %4u %4u  %3u  %3u  %3u\n",
            centers_cost,
            orbit_cost,
            unpaired,
            combined_cost(centers_cost, orbit_cost, unpaired),
            length - step,
            step
        );
        if (step < length) {
            parity = parity_after_move(parity, solution[step]);
            rotate_777_centers(walk, rotate_tmp, CUBE_ARRAY_SIZE, solution[step]);
        }
    }
    printf("\n");
}

static int compare_search_roots(const void *left, const void *right)
{
    const struct search_root *a = left;
    const struct search_root *b = right;

    if (a->initial_cost != b->initial_cost) {
        return a->initial_cost < b->initial_cost ? -1 : 1;
    }
    /* The max heuristic ties often. Prefer the root whose component costs are
     * collectively smaller before using pairing and input order as tie-breakers. */
    if (a->quality_cost != b->quality_cost) {
        return a->quality_cost < b->quality_cost ? -1 : 1;
    }
    if (a->unpaired != b->unpaired) {
        return a->unpaired < b->unpaired ? -1 : 1;
    }
    if (a->index != b->index) {
        return a->index < b->index ? -1 : 1;
    }
    return 0;
}

/* 7*7*6 stickers. The scan width has to be a literal, so it matches CUBE_ARRAY_SIZE - 1. */
static struct search_root *read_search_roots(const char *filename, unsigned int *root_count)
{
    FILE *stream = fopen(filename, "r");
    char *line = NULL;
    size_t capacity = 0;
    ssize_t length;
    unsigned int allocated = 0;
    unsigned int line_number = 0;
    struct search_root *roots = NULL;

    if (!stream) {
        fprintf(stderr, "ERROR: could not open --kociemba-file %s: %s\n", filename, strerror(errno));
        exit(1);
    }

    while ((length = getline(&line, &capacity, stream)) != -1) {
        unsigned int index;
        unsigned int orbit0;
        unsigned int orbit1;
        char kociemba[CUBE_ARRAY_SIZE];

        line_number++;
        if (length == 0 || line[0] == '\n' || line[0] == '\r') {
            continue;
        }
        if (sscanf(line, "%u,%u,%u,%294[^\r\n]", &index, &orbit0, &orbit1, kociemba) != 4 ||
            strlen(kociemba) != CUBE_ARRAY_SIZE - 1 || orbit0 > PARITY_EVEN || orbit1 > PARITY_EVEN) {
            fprintf(
                stderr,
                "ERROR: invalid --kociemba-file line %u; expected "
                "ROOT_INDEX,ORBIT0_REQUIREMENT,ORBIT1_REQUIREMENT,294-STICKER-STATE\n",
                line_number
            );
            free(line);
            free(roots);
            fclose(stream);
            exit(1);
        }

        if (*root_count == allocated) {
            struct search_root *grown;

            allocated = allocated ? allocated * 2 : 16;
            grown = realloc(roots, allocated * sizeof(*roots));
            if (!grown) {
                fprintf(stderr, "ERROR: could not allocate search roots\n");
                free(line);
                free(roots);
                fclose(stream);
                exit(1);
            }
            roots = grown;
        }

        roots[*root_count].index = index;
        roots[*root_count].orbit0_requirement = (unsigned char)orbit0;
        roots[*root_count].orbit1_requirement = (unsigned char)orbit1;
        roots[*root_count].initial_cost = UINT8_MAX;
        init_cube(roots[*root_count].cube, kociemba);
        recolor_cube(roots[*root_count].cube);
        (*root_count)++;
    }

    free(line);
    fclose(stream);
    if (!*root_count) {
        fprintf(stderr, "ERROR: --kociemba-file %s contains no roots\n", filename);
        free(roots);
        exit(1);
    }
    return roots;
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *kociemba_filename = NULL;
    const char *ranked_filename = NULL;
    unsigned char min_threshold = 0;
    unsigned char max_threshold = DEFAULT_MAX_IDA_THRESHOLD;
    long detected_cpus = sysconf(_SC_NPROCESSORS_ONLN);
    unsigned int thread_count = detected_cpus > 0 ? (unsigned int)detected_cpus : 1;
    struct search_root *roots = NULL;
    unsigned int root_count = 0;

    if (thread_count > MAX_THREADS) {
        thread_count = MAX_THREADS;
    }
    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--kociemba-file") && index + 1 < argc) {
            kociemba_filename = argv[++index];
        } else if (!strcmp(argv[index], "--ranked-UD-inner-centers-cost") && index + 1 < argc) {
            ranked_filename = argv[++index];
        } else if (!strcmp(argv[index], "--ud-inner-even-cost") && index + 1 < argc) {
            inner_even_filename = argv[++index];
        } else if (!strcmp(argv[index], "--ud-inner-odd-cost") && index + 1 < argc) {
            inner_odd_filename = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--threads") && index + 1 < argc) {
            thread_count = (unsigned int)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--unpaired-multiplier") && index + 1 < argc) {
            unpaired_multiplier = (float)atof(argv[++index]);
            use_unpaired_multiplier = 1;
        } else if (!strcmp(argv[index], "--multiplier") && index + 1 < argc) {
            cost_to_goal_multiplier = (float)atof(argv[++index]);
        } else if (!strcmp(argv[index], "--orbit0-need-odd-w")) {
            orbit0_requirement = PARITY_ODD;
        } else if (!strcmp(argv[index], "--orbit0-need-even-w")) {
            orbit0_requirement = PARITY_EVEN;
        } else if (!strcmp(argv[index], "--orbit1-need-odd-w")) {
            orbit1_requirement = PARITY_ODD;
        } else if (!strcmp(argv[index], "--orbit1-need-even-w")) {
            orbit1_requirement = PARITY_EVEN;
        } else if (!strcmp(argv[index], "--obliques-only")) {
            obliques_only = 1;
        } else if (!strcmp(argv[index], "--stage-lr-obliques")) {
            stage_lr_obliques = 1;
        } else if (!strcmp(argv[index], "--print-ida-summary")) {
            /* The path table is printed for the solution. */
        } else if (!strcmp(argv[index], "--solution-count") && index + 1 < argc) {
            solution_limit = (unsigned int)strtoul(argv[++index], NULL, 10);
            collect_solutions = 1;
        } else if (!strcmp(argv[index], "--root-cap") && index + 1 < argc) {
            root_limit = (unsigned int)strtoul(argv[++index], NULL, 10);
        } else if (!strcmp(argv[index], "--initial-orbit0-odd")) {
            initial_orbit0_odd = 1;
        } else {
            usage(argv[0]);
            return 1;
        }
    }
    if ((kociemba == NULL) == (kociemba_filename == NULL) ||
        (!obliques_only && !stage_lr_obliques && !ranked_filename) || !thread_count ||
        thread_count > MAX_THREADS ||
        min_threshold > max_threshold || max_threshold > MAX_IDA_THRESHOLD) {
        usage(argv[0]);
        return 1;
    }
    if (use_unpaired_multiplier && (unpaired_multiplier <= 0.0f || unpaired_multiplier > 1.0f)) {
        fprintf(stderr, "ERROR: --unpaired-multiplier must be in (0.0, 1.0]\n");
        return 1;
    }
    /* Below 1.0 would weaken the heuristic rather than inflate it. */
    if (cost_to_goal_multiplier && cost_to_goal_multiplier < 1.0f) {
        fprintf(stderr, "ERROR: --multiplier must be at least 1.0\n");
        return 1;
    }
    if (obliques_only && stage_lr_obliques) {
        fprintf(stderr, "ERROR: pass only one of --obliques-only and --stage-lr-obliques\n");
        return 1;
    }
    if (kociemba_filename && (obliques_only || stage_lr_obliques)) {
        fprintf(stderr, "ERROR: --kociemba-file is only for the ranked UD inner-center search\n");
        return 1;
    }
    if (collect_solutions && !stage_lr_obliques) {
        fprintf(stderr, "ERROR: --solution-count is only for --stage-lr-obliques\n");
        return 1;
    }
    if ((inner_even_filename == NULL) != (inner_odd_filename == NULL) ||
        ((inner_even_filename || inner_odd_filename) && (obliques_only || stage_lr_obliques))) {
        fprintf(stderr, "ERROR: --ud-inner-even-cost and --ud-inner-odd-cost must be passed together\n");
        return 1;
    }

    init_binom();
    init_move_tables();
    init_node_tables();
    if (kociemba_filename) {
        roots = read_search_roots(kociemba_filename, &root_count);
    } else {
        roots = calloc(1, sizeof(*roots));
        if (!roots) {
            fprintf(stderr, "ERROR: could not allocate search roots\n");
            return 1;
        }
        roots[0].orbit0_requirement = orbit0_requirement;
        roots[0].orbit1_requirement = orbit1_requirement;
        init_cube(roots[0].cube, kociemba);
        recolor_cube(roots[0].cube);
        root_count = 1;
    }
    if (stage_lr_obliques) {
        if (!load_stage_cache()) {
            build_stage_tables();
            save_stage_cache();
        } else {
            LOG("loaded LR oblique and outer-x stage tables\n");
        }
    } else if (!obliques_only) {
        map_ranked_cost_file(ranked_filename);
        if (inner_even_filename) {
            struct mapped_cost_file even = ida_map_cost_file(inner_even_filename, PRODUCT_UNIVERSE);
            struct mapped_cost_file odd = ida_map_cost_file(inner_odd_filename, PRODUCT_UNIVERSE);

            inner_even_fd = even.fd;
            inner_even_costs = even.costs;
            inner_odd_fd = odd.fd;
            inner_odd_costs = odd.costs;
        }
    }

    for (unsigned int root_index = 0; root_index < root_count; root_index++) {
        orbit0_requirement = roots[root_index].orbit0_requirement;
        orbit1_requirement = roots[root_index].orbit1_requirement;
        roots[root_index].initial_cost = cube_cost(roots[root_index].cube, 0);
        roots[root_index].unpaired = unpaired_oblique_count(roots[root_index].cube);
        if (!stage_lr_obliques) {
            unsigned char centers = obliques_only ? 0 : centers_table_cost(roots[root_index].cube);
            unsigned char orbit = inner_even_costs ?
                                  inner_orbit1_cost(inner_centers_rank(roots[root_index].cube), 0) : 0;
            roots[root_index].quality_cost =
                centers + orbit + unpaired_cost(roots[root_index].unpaired);
        }
        if (roots[root_index].initial_cost == UINT8_MAX) {
            fprintf(
                stderr,
                "ERROR: root %u center state is absent from the table\n",
                roots[root_index].index
            );
            unmap_inner_tables();
            free_stage_tables();
            free(roots);
            return 1;
        }
    }
    qsort(roots, root_count, sizeof(*roots), compare_search_roots);
    if (root_limit && root_count > root_limit) {
        LOG("keeping %u of %u roots after heuristic ranking\n", root_limit, root_count);
        root_count = root_limit;
    }
    if (min_threshold < roots[0].initial_cost) {
        min_threshold = roots[0].initial_cost;
    }

    if (root_count == 1) {
        printf("START\n");
        print_cube(roots[0].cube, CUBE_SIZE);
    }
    if (stage_lr_obliques) {
        LOG("staging LR left/middle/right obliques and outer x\n");
    } else if (obliques_only) {
        LOG("searching LR obliques only, prune pairing regressions\n");
    } else if (use_unpaired_multiplier) {
        LOG("searching with unpaired multiplier %.2f, prune pairing regressions\n", unpaired_multiplier);
    } else {
        LOG("searching with the empirical unpaired-count matrix, prune pairing regressions\n");
    }
    if (root_count == 1) {
        LOG(
            "initial cost %u, unpaired obliques %u, threads %u\n",
            roots[0].initial_cost,
            unpaired_oblique_count(roots[0].cube),
            thread_count
        );
    } else {
        LOG(
            "loaded %u starting states from %s, min initial cost %u, threads %u\n",
            root_count,
            kociemba_filename,
            roots[0].initial_cost,
            thread_count
        );
    }

    for (unsigned char threshold = min_threshold; threshold <= max_threshold; threshold++) {
        struct timeval start;
        struct timeval end;
        struct search_root *selected = NULL;
        uint64_t threshold_nodes = 0;

        gettimeofday(&start, NULL);
        for (unsigned int root_index = 0; root_index < root_count; root_index++) {
            uint64_t root_nodes = 0;
            int found;

            if (roots[root_index].initial_cost > threshold) {
                continue;
            }
            orbit0_requirement = roots[root_index].orbit0_requirement;
            orbit1_requirement = roots[root_index].orbit1_requirement;
            if (!roots[root_index].initial_cost) {
                solution[0] = MOVE_NONE;
                if (collect_solutions) {
                    struct phase5_root_key key;

                    collected_count = 0;
                    raw_solution_count = 1;
                    phase5_root_key(roots[root_index].cube, 0, &key);
                    keep_solution(solution, &key);
                }
                found = 1;
                root_nodes = 1;
            } else {
                found = search_at_threshold(
                    roots[root_index].cube, threshold, thread_count, &root_nodes
                );
            }
            threshold_nodes += root_nodes;
            if (found) {
                selected = &roots[root_index];
                break;
            }
        }
        if (selected && !collect_solutions && selected->initial_cost) {
            move_type best_solution[MAX_IDA_THRESHOLD + 1];
            unsigned int best_length = 0;
            unsigned int checks = 0;

            while (solution[best_length] != MOVE_NONE) {
                best_length++;
            }
            memcpy(best_solution, solution, sizeof(best_solution));
            for (unsigned int root_index = 0; root_index < root_count && checks < SHORTER_ROOT_CHECKS; root_index++) {
                uint64_t root_nodes = 0;
                unsigned int length = 0;
                int found;

                if (&roots[root_index] == selected || roots[root_index].initial_cost != threshold) {
                    continue;
                }
                checks++;
                orbit0_requirement = roots[root_index].orbit0_requirement;
                orbit1_requirement = roots[root_index].orbit1_requirement;
                found = search_at_threshold(
                    roots[root_index].cube, (unsigned char)(best_length - 1), thread_count, &root_nodes
                );
                threshold_nodes += root_nodes;
                if (!found) {
                    continue;
                }
                while (solution[length] != MOVE_NONE) {
                    length++;
                }
                if (length < best_length) {
                    LOG(
                        "root %u solved in %u, shorter than root %u in %u\n",
                        roots[root_index].index, length, selected->index, best_length
                    );
                    best_length = length;
                    selected = &roots[root_index];
                    memcpy(best_solution, solution, sizeof(best_solution));
                }
            }
            memcpy(solution, best_solution, sizeof(solution));
        }
        gettimeofday(&end, NULL);
        {
            double seconds = elapsed_seconds(&start, &end);
            uint64_t nodes_per_sec = seconds > 0.0 ? (uint64_t)(threshold_nodes / seconds) : 0;

            LOG(
                "IDA threshold %u, explored %" PRIu64 " nodes, took %.3fs, %" PRIu64 " nodes-per-sec\n",
                threshold,
                threshold_nodes,
                seconds,
                nodes_per_sec
            );
        }
        if (selected && collect_solutions && collected_count) {
            LOG(
                "kept %u distinct phase-5 roots from %u shortest phase 3 solutions\n",
                collected_count,
                raw_solution_count
            );
            for (unsigned int which = 0; which < collected_count; which++) {
                unsigned int length = 0;

                while (collected[which][length] != MOVE_NONE) {
                    length++;
                }
                printf("SOLUTION (%u steps):", length);
                for (unsigned int index = 0; index < length; index++) {
                    printf(" %s", move2str[collected[which][index]]);
                }
                printf("\n");
            }
            free(collected);
            free(collected_keys);
            collected = NULL;
            collected_keys = NULL;
            collected_count = 0;
            collected_capacity = 0;
            unmap_inner_tables();
            free_stage_tables();
            free(roots);
            return 0;
        }
        if (selected) {
            unsigned int length = 0;
            char rotate_tmp[CUBE_ARRAY_SIZE];

            while (solution[length] != MOVE_NONE) {
                length++;
            }
            if (kociemba_filename) {
                printf("ROOT_INDEX %u\n", selected->index);
            }
            printf("SOLUTION (%u steps):", length);
            for (unsigned int index = 0; index < length; index++) {
                printf(" %s", move2str[solution[index]]);
            }
            printf("\n");
            print_ida_summary(selected->cube, length);
            for (unsigned int index = 0; index < length; index++) {
                rotate_777_centers(selected->cube, rotate_tmp, CUBE_ARRAY_SIZE, solution[index]);
            }
            printf("END\n");
            print_cube(selected->cube, CUBE_SIZE);
            unmap_inner_tables();
            free_stage_tables();
            free(roots);
            return 0;
        }
    }

    fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
    free(collected);
    free(collected_keys);
    unmap_inner_tables();
    free_stage_tables();
    free(roots);
    return 1;
}
