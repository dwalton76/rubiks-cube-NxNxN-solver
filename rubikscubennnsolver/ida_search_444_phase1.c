#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <unistd.h>

#include "center_symmetry_444.h"
#include "ida_search_core.h"

#define CUBE_SIZE 4
#define CUBE_ARRAY_SIZE 97
#define CENTER_COUNT 24
#define WING_COUNT 24
#define EDGE_COUNT 12
#define EVEN_MAPPING_COUNT 2048
#define LR_CENTER_UNIVERSE UINT64_C(51482970)
#define ALL_CENTER_RAW_UNIVERSE UINT64_C(9465511770)
#define WING_UNIVERSE UINT64_C(2704156)
#define DEFAULT_MAX_THRESHOLD 20
#define MAX_THRESHOLD 40
#define SEARCH_THREADS 22
#define PHASE1_COST_MAX 12
#define PARITY_EVEN 0
#define PARITY_ODD 1
/* Sentinel: the caller must pick even or odd, so a manual run cannot inherit a default. */
#define PARITY_UNSET 2

void rotate_444(char *cube, char *cube_tmp, int array_size, move_type move);

static const unsigned int center_squares[CENTER_COUNT] = {
    6, 7, 10, 11, 22, 23, 26, 27, 38, 39, 42, 43,
    54, 55, 58, 59, 70, 71, 74, 75, 86, 87, 90, 91,
};
static const unsigned int wing_squares[WING_COUNT] = {
    2, 3, 5, 8, 9, 12, 14, 15, 21, 24, 25, 28,
    53, 56, 57, 60, 82, 83, 85, 88, 89, 92, 94, 95,
};
static const unsigned int wing_partners[WING_COUNT] = {
    67, 66, 18, 51, 19, 50, 34, 35, 72, 37, 76, 41,
    40, 69, 44, 73, 46, 47, 31, 62, 30, 63, 79, 78,
};
static const char *center_targets[] = {
    "UUUULLLLxxxxRRRRxxxxUUUU",
    "UUUULLRRxxxxLLRRxxxxUUUU",
    "UUUULLRRxxxxRRLLxxxxUUUU",
    "UUUULRLRxxxxLRLRxxxxUUUU",
    "UUUULRLRxxxxRLRLxxxxUUUU",
    "UUUULRRLxxxxRLLRxxxxUUUU",
    "UUUURLLRxxxxLRRLxxxxUUUU",
    "UUUURLRLxxxxLRLRxxxxUUUU",
    "UUUURLRLxxxxRLRLxxxxUUUU",
    "UUUURRLLxxxxLLRRxxxxUUUU",
    "UUUURRLLxxxxRRLLxxxxUUUU",
    "UUUURRRRxxxxLLLLxxxxUUUU",
};

/*
 * Combined heuristic matrix built by utils/build-444-heuristic-matrices.py from
 * 200 random cubes. It is indexed by the all-centers cost, the LR centers cost
 * and the wing high/low cost. Some cells exceed the largest index, which makes
 * the heuristic inadmissible but much faster than taking the max of the three.
 */
static const unsigned char phase1_cost_matrix_444[PHASE1_COST_MAX + 1][PHASE1_COST_MAX + 1][PHASE1_COST_MAX + 1] = {
    {  // CTR 0
        { 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 0
        { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 1
        { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 2
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 3
        { 4,  4,  4,  4,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 4
        { 5,  5,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 5
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 6
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 1
        { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 0
        { 1,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 1
        { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 2
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 3
        { 4,  4,  4,  4,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 4
        { 5,  5,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 5
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 6
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 2
        { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 0
        { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 1
        { 2,  2,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 2
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 3
        { 4,  4,  4,  4,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 4
        { 5,  5,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 5
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 6
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 3
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 0
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 1
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 2
        { 3,  3,  3,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 3
        { 4,  4,  4,  4,  4,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 4
        { 5,  5,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 5
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 6
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 4
        { 4,  4,  4,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 0
        { 4,  4,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 1
        { 4,  4,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 2
        { 4,  4,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 3
        { 4,  4,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 4
        { 5,  5,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 5
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 6
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 5
        { 5,  5,  5,  5,  5,  5,  6,  7,  8,  9, 10, 11, 12},  // LR 0
        { 5,  5,  5,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 1
        { 5,  5,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 2
        { 5,  5,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 3
        { 5,  5,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 4
        { 5,  5,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 5
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 6
        { 7,  7,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 7
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 6
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 0
        { 6,  6,  6,  6,  6,  6,  6,  7,  8,  9, 10, 11, 12},  // LR 1
        { 6,  6,  6,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 2
        { 6,  6,  6,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 3
        { 6,  6,  6,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 4
        { 6,  6,  6,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 5
        { 6,  6,  6,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 6
        { 7,  7,  8,  8,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 7
        { 8,  8,  8,  8,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 7
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 0
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 1
        { 7,  7,  7,  7,  7,  7,  7,  7,  8,  9, 10, 11, 12},  // LR 2
        { 7,  7,  7,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 3
        { 7,  7,  7,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 4
        { 7,  7,  7,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 5
        { 7,  7,  7,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 6
        { 7,  7,  8,  8,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 7
        { 8,  8,  8,  8,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 8
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 0
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 1
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 2
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 3
        { 8,  8,  8,  8,  8,  8,  8,  8,  8,  9, 10, 11, 12},  // LR 4
        { 8,  8,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 5
        { 8,  8,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 6
        { 8,  8,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 7
        { 8,  8,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 8
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 9
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 0
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 1
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 2
        { 9,  9,  9,  9,  9,  9,  9,  9,  9,  9, 10, 11, 12},  // LR 3
        { 9,  9,  9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 4
        { 9,  9,  9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 5
        { 9,  9,  9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 6
        { 9,  9,  9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 7
        { 9,  9,  9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 8
        { 9,  9,  9, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 9
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 10
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 0
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 1
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 2
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 3
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 4
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 5
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12},  // LR 6
        {10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 7
        {10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 8
        {10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 9
        {10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 10
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 11
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 0
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 1
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 2
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 3
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 4
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12},  // LR 5
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 6
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 7
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 8
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 9
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 10
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
    {  // CTR 12
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 0
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 2
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 3
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 4
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 5
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 6
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 7
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 8
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 10
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 11
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12},  // LR 12
    },
};

/*
 * Largest wing cost that wing_cost_min may stop at, per (all-centers cost, LR
 * cost, remaining budget). See init_phase1_wing_floor().
 */
static unsigned char phase1_wing_floor[PHASE1_COST_MAX + 1][PHASE1_COST_MAX + 1][MAX_THRESHOLD + 1];
static unsigned char phase1_wing_exact[PHASE1_COST_MAX + 1][PHASE1_COST_MAX + 1];

struct cost_file {
    int fd;
    unsigned char *costs;
    uint64_t universe;
};

struct worker {
    char cube[CUBE_ARRAY_SIZE];
    char highlow[CUBE_ARRAY_SIZE];
    unsigned int threshold;
    unsigned char parity;
    uint64_t nodes;
    move_type path[MAX_THRESHOLD + 1];
};

/* Two-move prefixes, so 22 threads have far more tasks than threads. */
struct root_task {
    move_type first;
    move_type second;
};

static struct cost_file all_center_table = {-1, NULL, 0};
static struct symmetry_index all_center_index = {-1, 0, NULL, NULL, NULL, NULL, NULL};
static struct cost_file lr_table = {-1, NULL, LR_CENTER_UNIVERSE};
static struct cost_file wing_table = {-1, NULL, WING_UNIVERSE};
static unsigned int max_threshold = DEFAULT_MAX_THRESHOLD;
static int max_threshold_is_explicit;
static unsigned char required_parity = PARITY_UNSET;
static atomic_int stop_search;
static atomic_uint next_root_task;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;
static char root_cube[CUBE_ARRAY_SIZE];
static char root_highlow[CUBE_ARRAY_SIZE];
static unsigned int selected_mapping_masks[EVEN_MAPPING_COUNT];
/*
 * Every mapping is a legal goal and the early exit in wing_cost_min keeps the
 * extra candidates nearly free, so consider all 2048 even mappings: more goals
 * means the search bottoms out at a smaller threshold.
 */
static struct root_task root_tasks[MOVE_COUNT_444 * MOVE_COUNT_444];
static unsigned int root_task_count;
static unsigned int root_threshold;
static float cost_to_goal_multiplier;
static move_type solution[MAX_THRESHOLD + 1];
static unsigned int solution_length;

static uint64_t center_888_rank(const unsigned char state[CENTER_COUNT])
{
    uint64_t rank = 0;
    uint64_t permutations = ALL_CENTER_RAW_UNIVERSE;
    unsigned int remaining[3] = {8, 8, 8};

    for (unsigned int position = 0; position < CENTER_COUNT; position++) {
        unsigned int slots = CENTER_COUNT - position;
        unsigned int symbol;

        switch (state[position]) {
            case 'F': symbol = 0; break;
            case 'L': symbol = 1; break;
            case 'U': symbol = 2; break;
            default: return UINT64_MAX;
        }
        if (!remaining[symbol]) {
            return UINT64_MAX;
        }
        for (unsigned int smaller = 0; smaller < symbol; smaller++) {
            rank += permutations * remaining[smaller] / slots;
        }
        permutations = permutations * remaining[symbol] / slots;
        remaining[symbol]--;
    }
    return rank;
}

static uint64_t all_center_canonical_rank(const char cube[CUBE_ARRAY_SIZE])
{
    unsigned char state[CENTER_COUNT];
    unsigned char transformed[CENTER_COUNT];
    unsigned char canonical[CENTER_COUNT];

    for (unsigned int index = 0; index < CENTER_COUNT; index++) {
        switch (cube[center_squares[index]]) {
            case 'U':
            case 'D': state[index] = 'U'; break;
            case 'L':
            case 'R': state[index] = 'L'; break;
            case 'F':
            case 'B': state[index] = 'F'; break;
            default: return UINT64_MAX;
        }
    }
    for (unsigned int symmetry = 0; symmetry < CENTER_SYMMETRY_COUNT_444; symmetry++) {
        transform_centers_444(state, transformed, symmetry);
        if (!symmetry || memcmp(transformed, canonical, sizeof(canonical)) < 0) {
            memcpy(canonical, transformed, sizeof(canonical));
        }
    }
    return center_888_rank(canonical);
}

static unsigned char decoded_cost(const struct cost_file *table, uint64_t rank)
{
    unsigned char encoded;
    if (rank >= table->universe) {
        return UINT8_MAX;
    }
    encoded = table->costs[rank];
    return decode_cost_byte(encoded);
}

static unsigned char all_center_cost(const char cube[CUBE_ARRAY_SIZE])
{
    uint64_t raw = all_center_canonical_rank(cube);
    uint64_t dense = raw == UINT64_MAX
        ? UINT64_MAX
        : symmetry_dense_rank(&all_center_index, raw);
    return decoded_cost(&all_center_table, dense);
}

static uint64_t wing_rank_from_mask(uint32_t low_slots)
{
    uint64_t rank = 0;
    unsigned int low_count = 12;

    for (unsigned int position = 0; position < WING_COUNT; position++) {
        unsigned int after = WING_COUNT - position - 1;

        if (low_slots & (UINT32_C(1) << position)) {
            if (!low_count) {
                return UINT64_MAX;
            }
            low_count--;
        } else if (low_count) {
            rank += binom[after][low_count - 1];
        }
    }
    return low_count ? UINT64_MAX : rank;
}

static unsigned int edge_id(char first, char second)
{
    unsigned int key;
    if (first > second) {
        char temporary = first;
        first = second;
        second = temporary;
    }
    key = ((unsigned int)(unsigned char)first << 8) | (unsigned char)second;
#define EDGE_KEY(a, b) (((unsigned int)(a) << 8) | (unsigned int)(b))
    switch (key) {
        case EDGE_KEY('B', 'U'): return 0;
        case EDGE_KEY('L', 'U'): return 1;
        case EDGE_KEY('R', 'U'): return 2;
        case EDGE_KEY('F', 'U'): return 3;
        case EDGE_KEY('B', 'L'): return 4;
        case EDGE_KEY('F', 'L'): return 5;
        case EDGE_KEY('B', 'R'): return 6;
        case EDGE_KEY('F', 'R'): return 7;
        case EDGE_KEY('B', 'D'): return 8;
        case EDGE_KEY('D', 'L'): return 9;
        case EDGE_KEY('D', 'R'): return 10;
        case EDGE_KEY('D', 'F'): return 11;
        default: return UINT_MAX;
    }
#undef EDGE_KEY
}

/*
 * Where each edge's two wings currently sit, plus which slots hold low wings.
 *
 * An edge mapping flips both wings of an edge, so it toggles exactly the slots
 * in that edge's mask. Every edge owns one high and one low wing and those
 * labels never change under a move, so a toggle keeps the 12/12 split intact.
 */
static int wing_slots(
    const char cube[CUBE_ARRAY_SIZE],
    const char highlow[CUBE_ARRAY_SIZE],
    uint32_t edge_slots[EDGE_COUNT],
    uint32_t *low_slots)
{
    memset(edge_slots, 0, EDGE_COUNT * sizeof(edge_slots[0]));
    *low_slots = 0;
    for (unsigned int index = 0; index < WING_COUNT; index++) {
        char value = highlow[wing_squares[index]];
        unsigned int id = edge_id(cube[wing_squares[index]], cube[wing_partners[index]]);

        if (id >= EDGE_COUNT || value != highlow[wing_partners[index]]) {
            return 0;
        }
        edge_slots[id] |= UINT32_C(1) << index;
        if (value == 'D') {
            *low_slots |= UINT32_C(1) << index;
        }
    }
    return 1;
}

static unsigned char wing_cost_for_mapping(
    const uint32_t edge_slots[EDGE_COUNT],
    uint32_t low_slots,
    unsigned int mapping)
{
    uint32_t toggle = 0;

    while (mapping) {
        toggle ^= edge_slots[__builtin_ctz(mapping)];
        mapping &= mapping - 1;
    }
    return decoded_cost(&wing_table, wing_rank_from_mask(low_slots ^ toggle));
}

/*
 * Any of the candidate mappings is an acceptable goal, so the admissible wing
 * cost is the cheapest of them. Stop as soon as one cannot raise the node cost
 * above the centers cost, which is the common case.
 */
static unsigned char wing_cost_min(
    const char cube[CUBE_ARRAY_SIZE],
    const char highlow[CUBE_ARRAY_SIZE],
    unsigned char floor_cost)
{
    uint32_t edge_slots[EDGE_COUNT];
    uint32_t low_slots;
    unsigned char best = UINT8_MAX;

    if (!wing_slots(cube, highlow, edge_slots, &low_slots)) {
        return UINT8_MAX;
    }
    for (unsigned int index = 0; index < EVEN_MAPPING_COUNT; index++) {
        unsigned char cost = wing_cost_for_mapping(edge_slots, low_slots, selected_mapping_masks[index]);

        if (cost < best) {
            best = cost;
            if (best <= floor_cost) {
                break;
            }
        }
    }
    return best;
}

static uint64_t lr_center_rank(const char cube[CUBE_ARRAY_SIZE])
{
    uint64_t rank = 0;
    uint64_t permutations = LR_CENTER_UNIVERSE;
    unsigned int remaining[3] = {4, 4, 16};

    for (unsigned int position = 0; position < CENTER_COUNT; position++) {
        unsigned int slots = CENTER_COUNT - position;
        unsigned int symbol;
        char value = cube[center_squares[position]];

        if (value == 'L') {
            symbol = 0;
        } else if (value == 'R') {
            symbol = 1;
        } else {
            symbol = 2;
        }
        if (!remaining[symbol]) {
            return UINT64_MAX;
        }
        for (unsigned int smaller = 0; smaller < symbol; smaller++) {
            rank += permutations * remaining[smaller] / slots;
        }
        permutations = permutations * remaining[symbol] / slots;
        remaining[symbol]--;
    }
    return rank;
}

static int centers_are_phase2_goal(const char cube[CUBE_ARRAY_SIZE])
{
    char state[CENTER_COUNT + 1];
    state[CENTER_COUNT] = '\0';
    for (unsigned int index = 0; index < CENTER_COUNT; index++) {
        char value = cube[center_squares[index]];
        if (value == 'U' || value == 'D') {
            state[index] = 'U';
        } else if (value == 'L' || value == 'R') {
            state[index] = value;
        } else {
            state[index] = 'x';
        }
    }
    for (unsigned int index = 0; index < sizeof(center_targets) / sizeof(center_targets[0]); index++) {
        if (!strcmp(state, center_targets[index])) {
            return 1;
        }
    }
    return 0;
}

static unsigned char scale_cost(unsigned char cost)
{
    if (cost && cost_to_goal_multiplier) {
        float scaled = roundf((float)cost * cost_to_goal_multiplier);

        if (scaled > MAX_THRESHOLD) {
            return MAX_THRESHOLD + 1;
        }
        return (unsigned char)scaled;
    }
    return cost;
}

/*
 * wing_cost_min walks all 2048 mappings, so scanning it down to the exact
 * minimum on every node costs an order of magnitude in nodes-per-sec. The
 * matrix never shrinks as the wing cost grows, which gives two wing costs the
 * scan may stop at:
 *  - phase1_wing_exact is the last wing cost that still reads the same cell as
 *    wing cost 0, so anything below it yields the exact heuristic
 *  - phase1_wing_floor is the last wing cost that keeps the heuristic within
 *    the budget left at this node, so anything below it yields the same
 *    keep-or-prune answer
 */
static void init_phase1_wing_floor(void)
{
    for (unsigned int ud = 0; ud <= PHASE1_COST_MAX; ud++) {
        for (unsigned int lr = 0; lr <= PHASE1_COST_MAX; lr++) {
            unsigned char exact = 0;

            while (exact < PHASE1_COST_MAX &&
                   phase1_cost_matrix_444[ud][lr][exact + 1] == phase1_cost_matrix_444[ud][lr][0]) {
                exact++;
            }
            phase1_wing_exact[ud][lr] = exact;
            for (unsigned int budget = 0; budget <= MAX_THRESHOLD; budget++) {
                unsigned char floor = exact;

                for (unsigned char wing = 0; wing <= PHASE1_COST_MAX; wing++) {
                    unsigned char cost = phase1_cost_matrix_444[ud][lr][wing];

                    if (scale_cost(cost > wing ? cost : wing) > budget) {
                        break;
                    }
                    if (wing > floor) {
                        floor = wing;
                    }
                }
                phase1_wing_floor[ud][lr][budget] = floor;
            }
        }
    }
}

static unsigned char combined_cost(
    const char cube[CUBE_ARRAY_SIZE],
    unsigned char parity,
    unsigned char ud,
    unsigned char lr,
    unsigned char wing)
{
    unsigned char floor = ud > lr ? ud : lr;
    unsigned char cost;

    if (wing > floor) {
        floor = wing;
    }
    cost = phase1_cost_matrix_444[ud > PHASE1_COST_MAX ? PHASE1_COST_MAX : ud]
                                  [lr > PHASE1_COST_MAX ? PHASE1_COST_MAX : lr]
                                  [wing > PHASE1_COST_MAX ? PHASE1_COST_MAX : wing];
    if (cost < floor) {
        cost = floor;
    }
    if (!cost && !centers_are_phase2_goal(cube)) {
        cost = 1;
    }
    if (!cost && parity != required_parity) {
        cost = 1;
    }
    return scale_cost(cost);
}

/*
 * The search only needs to know whether the node fits in the budget, so it can
 * stop the wing scan early. Callers that report a cost want exact_heuristic().
 */
static unsigned char heuristic(
    const char cube[CUBE_ARRAY_SIZE],
    const char highlow[CUBE_ARRAY_SIZE],
    unsigned char parity,
    unsigned char budget)
{
    unsigned char ud = all_center_cost(cube);
    unsigned char lr = decoded_cost(&lr_table, lr_center_rank(cube));
    unsigned char ud_index;
    unsigned char lr_index;
    unsigned char cost;
    unsigned char wing;

    if (ud == UINT8_MAX || lr == UINT8_MAX) {
        return UINT8_MAX;
    }
    ud_index = ud > PHASE1_COST_MAX ? PHASE1_COST_MAX : ud;
    lr_index = lr > PHASE1_COST_MAX ? PHASE1_COST_MAX : lr;
    cost = phase1_cost_matrix_444[ud_index][lr_index][0];
    if (cost < ud) {
        cost = ud;
    }
    if (cost < lr) {
        cost = lr;
    }
    /* A wing-free lookup is a lower bound, so blowing the budget here prunes
     * without paying for the mapping scan at all. */
    cost = scale_cost(cost);
    if (cost > budget) {
        return cost;
    }
    wing = wing_cost_min(cube, highlow, phase1_wing_floor[ud_index][lr_index][budget]);
    if (wing == UINT8_MAX) {
        return UINT8_MAX;
    }
    return combined_cost(cube, parity, ud, lr, wing);
}

static unsigned char exact_heuristic(
    const char cube[CUBE_ARRAY_SIZE],
    const char highlow[CUBE_ARRAY_SIZE],
    unsigned char parity)
{
    unsigned char ud = all_center_cost(cube);
    unsigned char lr = decoded_cost(&lr_table, lr_center_rank(cube));
    unsigned char wing;

    if (ud == UINT8_MAX || lr == UINT8_MAX) {
        return UINT8_MAX;
    }
    wing = wing_cost_min(
        cube,
        highlow,
        phase1_wing_exact[ud > PHASE1_COST_MAX ? PHASE1_COST_MAX : ud]
                          [lr > PHASE1_COST_MAX ? PHASE1_COST_MAX : lr]
    );
    if (wing == UINT8_MAX) {
        return UINT8_MAX;
    }
    return combined_cost(cube, parity, ud, lr, wing);
}

static unsigned char parity_after_move(unsigned char parity, move_type move)
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
            return parity ^ 1;
        default:
            return parity;
    }
}

/*
 * Last ply must land on a goal, including orbit0 wide-quarter-turn parity.
 * --orbit0-need-even-w therefore either forbids or requires an orbit0 wide
 * quarter turn as the last move, depending on the parity so far. The same
 * filter with --orbit0-need-odd-w requires the opposite last move.
 */
static int last_ply_can_be_goal(unsigned char parity, move_type move)
{
    return parity_after_move(parity, move) == required_parity;
}

static int move_follows(move_type previous, move_type move)
{
    if (previous == MOVE_NONE) {
        return 1;
    }
    return !steps_on_same_face_and_layer(previous, move) &&
           steps_on_same_face_in_order(previous, move) &&
           steps_on_opposite_faces_in_order(previous, move);
}

static void print_solution(const move_type *path, unsigned int depth)
{
    printf("SOLUTION (%u steps):", depth);
    for (unsigned int index = 0; index < depth; index++) {
        printf(" %s", move2str[path[index]]);
    }
    printf("\n");
    fflush(stdout);
}

static double elapsed_seconds(const struct timeval *start, const struct timeval *end)
{
    return (end->tv_sec - start->tv_sec) + (end->tv_usec - start->tv_usec) / 1000000.0;
}

static int search(
    struct worker *worker,
    const char cube[CUBE_ARRAY_SIZE],
    const char highlow[CUBE_ARRAY_SIZE],
    unsigned int depth,
    move_type previous,
    unsigned char parity)
{
    unsigned char cost = heuristic(cube, highlow, parity, (unsigned char)(worker->threshold - depth));
    char child_cube[CUBE_ARRAY_SIZE];
    char child_highlow[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];
    int last_ply = depth + 1 == worker->threshold;

    worker->nodes++;
    if (atomic_load_explicit(&stop_search, memory_order_relaxed)) {
        return 1;
    }
    if (cost == UINT8_MAX || depth + cost > worker->threshold) {
        return 0;
    }
    if (!cost) {
        if (depth == worker->threshold) {
            pthread_mutex_lock(&solution_lock);
            if (!atomic_exchange_explicit(&stop_search, 1, memory_order_relaxed)) {
                memcpy(solution, worker->path, depth * sizeof(move_type));
                solution[depth] = MOVE_NONE;
                solution_length = depth;
            }
            pthread_mutex_unlock(&solution_lock);
        }
        return atomic_load_explicit(&stop_search, memory_order_relaxed);
    }
    if (depth == worker->threshold) {
        return 0;
    }

    for (unsigned int index = 0; index < MOVE_COUNT_444; index++) {
        move_type move = moves_444[index];
        if (!move_follows(previous, move)) {
            continue;
        }
        if (last_ply && !last_ply_can_be_goal(parity, move)) {
            continue;
        }
        memcpy(child_cube, cube, CUBE_ARRAY_SIZE);
        rotate_444(child_cube, scratch, CUBE_ARRAY_SIZE, move);
        memcpy(child_highlow, highlow, CUBE_ARRAY_SIZE);
        rotate_444(child_highlow, scratch, CUBE_ARRAY_SIZE, move);
        worker->path[depth] = move;
        if (search(worker, child_cube, child_highlow, depth + 1, move, parity_after_move(parity, move))) {
            return 1;
        }
    }
    return 0;
}

struct pool_worker {
    uint64_t nodes;
};

static void *search_pool_worker(void *argument)
{
    struct pool_worker *pool_worker = argument;
    while (!atomic_load_explicit(&stop_search, memory_order_relaxed)) {
        unsigned int task = atomic_fetch_add_explicit(&next_root_task, 1, memory_order_relaxed);
        struct worker worker;
        char scratch[CUBE_ARRAY_SIZE];

        if (task >= root_task_count) {
            break;
        }
        memset(&worker, 0, sizeof(worker));
        memcpy(worker.cube, root_cube, CUBE_ARRAY_SIZE);
        memcpy(worker.highlow, root_highlow, CUBE_ARRAY_SIZE);
        worker.threshold = root_threshold;
        worker.parity = 0;
        for (unsigned int step = 0; step < 2; step++) {
            move_type move = step ? root_tasks[task].second : root_tasks[task].first;

            rotate_444(worker.cube, scratch, CUBE_ARRAY_SIZE, move);
            rotate_444(worker.highlow, scratch, CUBE_ARRAY_SIZE, move);
            worker.parity = parity_after_move(worker.parity, move);
            worker.path[step] = move;
        }
        search(&worker, worker.cube, worker.highlow, 2, root_tasks[task].second, worker.parity);
        pool_worker->nodes += worker.nodes;
    }
    return NULL;
}

/*
 * Thresholds below two have no two-move prefix to hand the pool, and they are
 * cheap enough to walk here.
 */
static uint64_t search_shallow_threshold(unsigned int threshold)
{
    char cube[CUBE_ARRAY_SIZE];
    char highlow[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];
    uint64_t nodes = 1;

    if (!threshold) {
        return nodes;
    }
    for (unsigned int index = 0; index < MOVE_COUNT_444; index++) {
        move_type move = moves_444[index];
        unsigned char parity = parity_after_move(0, move);

        if (!last_ply_can_be_goal(0, move)) {
            continue;
        }
        memcpy(cube, root_cube, CUBE_ARRAY_SIZE);
        memcpy(highlow, root_highlow, CUBE_ARRAY_SIZE);
        rotate_444(cube, scratch, CUBE_ARRAY_SIZE, move);
        rotate_444(highlow, scratch, CUBE_ARRAY_SIZE, move);
        nodes++;
        if (exact_heuristic(cube, highlow, parity)) {
            continue;
        }
        solution[0] = move;
        solution[1] = MOVE_NONE;
        solution_length = 1;
        atomic_store(&stop_search, 1);
        break;
    }
    return nodes;
}

static uint64_t search_threshold(unsigned int threshold)
{
    pthread_t threads[SEARCH_THREADS];
    struct pool_worker workers[SEARCH_THREADS];
    uint64_t nodes = 1;

    atomic_store(&stop_search, 0);
    atomic_store(&next_root_task, 0);
    root_threshold = threshold;
    if (threshold < 2) {
        return search_shallow_threshold(threshold);
    }
    for (unsigned int index = 0; index < SEARCH_THREADS; index++) {
        memset(&workers[index], 0, sizeof(workers[index]));
        if (pthread_create(&threads[index], NULL, search_pool_worker, &workers[index]) != 0) {
            fprintf(stderr, "ERROR: could not create search thread\n");
            exit(1);
        }
    }
    for (unsigned int index = 0; index < SEARCH_THREADS; index++) {
        pthread_join(threads[index], NULL);
        nodes += workers[index].nodes;
    }
    return nodes;
}

struct mapping_candidate {
    unsigned int mask;
    unsigned char cost;
};

static int compare_mapping_candidates(const void *left, const void *right)
{
    const struct mapping_candidate *first = left;
    const struct mapping_candidate *second = right;

    if (first->cost != second->cost) {
        return first->cost < second->cost ? -1 : 1;
    }
    return first->mask < second->mask ? -1 : (first->mask > second->mask);
}

/*
 * Keep the mappings that look cheapest from the root, best first. The search
 * walks them in this order so its early exit usually fires immediately.
 */
static int select_root_mappings(const char cube[CUBE_ARRAY_SIZE], const char highlow[CUBE_ARRAY_SIZE])
{
    struct mapping_candidate candidates[EVEN_MAPPING_COUNT];
    uint32_t edge_slots[EDGE_COUNT];
    uint32_t low_slots;
    unsigned int count = 0;

    if (!wing_slots(cube, highlow, edge_slots, &low_slots)) {
        return 0;
    }
    for (unsigned int mapping = 0; mapping < (1U << EDGE_COUNT); mapping++) {
        if (__builtin_popcount(mapping) & 1) {
            continue;
        }
        candidates[count].mask = mapping;
        candidates[count].cost = wing_cost_for_mapping(edge_slots, low_slots, mapping);
        count++;
    }
    if (count != EVEN_MAPPING_COUNT) {
        return 0;
    }
    qsort(candidates, count, sizeof(candidates[0]), compare_mapping_candidates);
    for (unsigned int index = 0; index < EVEN_MAPPING_COUNT; index++) {
        selected_mapping_masks[index] = candidates[index].mask;
    }
    return 1;
}

static void init_root_tasks(void)
{
    for (unsigned int first_index = 0; first_index < MOVE_COUNT_444; first_index++) {
        move_type first = moves_444[first_index];

        for (unsigned int second_index = 0; second_index < MOVE_COUNT_444; second_index++) {
            move_type second = moves_444[second_index];

            if (!move_follows(first, second)) {
                continue;
            }
            root_tasks[root_task_count].first = first;
            root_tasks[root_task_count].second = second;
            root_task_count++;
        }
    }
}

static void print_ida_summary(
    const char cube[CUBE_ARRAY_SIZE],
    const char highlow[CUBE_ARRAY_SIZE],
    unsigned int length)
{
    char cube_walk[CUBE_ARRAY_SIZE];
    char highlow_walk[CUBE_ARRAY_SIZE];
    char scratch[CUBE_ARRAY_SIZE];
    unsigned char parity = 0;

    memcpy(cube_walk, cube, CUBE_ARRAY_SIZE);
    memcpy(highlow_walk, highlow, CUBE_ARRAY_SIZE);
    printf("\n       CTR   LR WING  CTG  TRU  IDX\n");
    printf("       ===  === ====  ===  ===  ===\n");
    for (unsigned int step = 0; step <= length; step++) {
        unsigned char ud = all_center_cost(cube_walk);
        unsigned char lr = decoded_cost(&lr_table, lr_center_rank(cube_walk));
        unsigned char wing = wing_cost_min(cube_walk, highlow_walk, 0);

        if (step) {
            printf("%5s ", move2str[solution[step - 1]]);
        } else {
            printf(" INIT ");
        }
        printf(
            " %3u  %3u %4u  %3u  %3u  %3u\n",
            ud,
            lr,
            wing,
            exact_heuristic(cube_walk, highlow_walk, parity),
            length - step,
            step
        );
        if (step < length) {
            rotate_444(cube_walk, scratch, CUBE_ARRAY_SIZE, solution[step]);
            rotate_444(highlow_walk, scratch, CUBE_ARRAY_SIZE, solution[step]);
            parity = parity_after_move(parity, solution[step]);
        }
    }
    printf("\n");
}

static void init_cube(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    ida_init_cube(cube, CUBE_SIZE, kociemba);
}

static void init_highlow(char highlow[CUBE_ARRAY_SIZE], const char *state)
{
    if (strlen(state) != 96) {
        fprintf(stderr, "ERROR: --highlow must contain 96 symbols in ULFRBD order\n");
        exit(1);
    }
    highlow[0] = 'x';
    memcpy(&highlow[1], state, 96);
}

// UD and FB centers are only staged so each pair collapses to a single label,
// but phase 2 solves LR centers per side so L and R stay distinct.
static char remap_center(char color)
{
    switch (color) {
        case 'B':
            return 'F';
        case 'D':
            return 'U';
        default:
            return color;
    }
}

static void print_phase1_cube(const char cube[CUBE_ARRAY_SIZE], const char highlow[CUBE_ARRAY_SIZE])
{
    char display[CUBE_ARRAY_SIZE];

    memset(display, '.', CUBE_ARRAY_SIZE);
    display[0] = 'x';
    for (unsigned int index = 0; index < CENTER_COUNT; index++) {
        unsigned int square = center_squares[index];
        display[square] = remap_center(cube[square]);
    }
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (highlow[square] != '.' && highlow[square] != 'x') {
            display[square] = highlow[square];
        }
    }
    print_cube(display, CUBE_SIZE);
}

static void map_cost_file(struct cost_file *table, const char *filename)
{
    struct mapped_cost_file mapped = ida_map_cost_file(filename, table->universe);

    table->fd = mapped.fd;
    table->costs = mapped.costs;
}

static void unmap_cost_file(struct cost_file *table)
{
    ida_unmap_cost_file(table->fd, table->costs, (size_t)table->universe);
    table->fd = -1;
    table->costs = NULL;
}

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE --highlow STATE "
        "--all-center-cost FILE --all-center-index FILE "
        "--lr-cost FILE --wing-cost FILE (--orbit0-need-even-w | --orbit0-need-odd-w) "
        "[--max-ida-threshold N] [--multiplier F]\n",
        program
    );
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *highlow_state = NULL;
    const char *all_center_filename = NULL;
    const char *all_center_index_filename = NULL;
    const char *lr_filename = NULL;
    const char *wing_filename = NULL;
    char cube[CUBE_ARRAY_SIZE];
    char highlow[CUBE_ARRAY_SIZE];

    for (int index = 1; index < argc; index++) {
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--highlow") && index + 1 < argc) {
            highlow_state = argv[++index];
        } else if (!strcmp(argv[index], "--all-center-cost") && index + 1 < argc) {
            all_center_filename = argv[++index];
        } else if (!strcmp(argv[index], "--all-center-index") && index + 1 < argc) {
            all_center_index_filename = argv[++index];
        } else if (!strcmp(argv[index], "--lr-cost") && index + 1 < argc) {
            lr_filename = argv[++index];
        } else if (!strcmp(argv[index], "--wing-cost") && index + 1 < argc) {
            wing_filename = argv[++index];
        } else if (!strcmp(argv[index], "--orbit0-need-odd-w")) {
            required_parity = PARITY_ODD;
        } else if (!strcmp(argv[index], "--orbit0-need-even-w")) {
            required_parity = PARITY_EVEN;
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned int)strtoul(argv[++index], NULL, 10);
            max_threshold_is_explicit = 1;
        } else if (!strcmp(argv[index], "--multiplier") && index + 1 < argc) {
            cost_to_goal_multiplier = (float)atof(argv[++index]);
        } else if (!strcmp(argv[index], "-h") || !strcmp(argv[index], "--help")) {
            usage(argv[0]);
            return 0;
        } else {
            fprintf(stderr, "ERROR: invalid argument %s\n", argv[index]);
            return 1;
        }
    }
    if (!kociemba || !highlow_state ||
        !all_center_filename || !all_center_index_filename ||
        !lr_filename || !wing_filename ||
        max_threshold > MAX_THRESHOLD) {
        usage(argv[0]);
        return 1;
    }
    if (required_parity == PARITY_UNSET) {
        fprintf(stderr, "ERROR: --orbit0-need-even-w or --orbit0-need-odd-w is required\n");
        return 1;
    }
    if (cost_to_goal_multiplier && cost_to_goal_multiplier < 1.0f) {
        fprintf(stderr, "ERROR: --multiplier must be at least 1.0\n");
        return 1;
    }
    if (cost_to_goal_multiplier && !max_threshold_is_explicit) {
        float scaled = roundf((float)DEFAULT_MAX_THRESHOLD * cost_to_goal_multiplier);
        max_threshold = scaled > MAX_THRESHOLD ? MAX_THRESHOLD : (unsigned int)scaled;
    }

    init_binom();
    init_center_symmetry_444();
    init_cube(cube, kociemba);
    init_highlow(highlow, highlow_state);
    map_symmetry_index(&all_center_index, all_center_index_filename, ALL_CENTER_RAW_UNIVERSE, "4x4x4 center symmetry index");
    all_center_table.universe = all_center_index.header->orbit_count;
    map_cost_file(&all_center_table, all_center_filename);
    map_cost_file(&lr_table, lr_filename);
    map_cost_file(&wing_table, wing_filename);
    printf("START\n");
    print_phase1_cube(cube, highlow);

    unsigned char initial_cost;
    uint64_t total_nodes = 0;
    double total_elapsed = 0.0;
    memcpy(root_cube, cube, CUBE_ARRAY_SIZE);
    memcpy(root_highlow, highlow, CUBE_ARRAY_SIZE);
    init_root_tasks();
    if (!select_root_mappings(cube, highlow)) {
        fprintf(stderr, "ERROR: could not rank the edge mappings for this cube\n");
        return 1;
    }

    init_phase1_wing_floor();
    initial_cost = exact_heuristic(cube, highlow, 0);
    if (initial_cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial state is outside a ranked table\n");
        return 1;
    }
    if (cost_to_goal_multiplier) {
        LOG("searching with cost to goal multiplier %.2f\n", cost_to_goal_multiplier);
    }
    LOG("searching with combined heuristic matrix\n");
    LOG(
        "initial cost %u, mappings %u, root tasks %u, threads %u, orbit0 wide turns %s\n",
        initial_cost,
        EVEN_MAPPING_COUNT,
        root_task_count,
        SEARCH_THREADS,
        required_parity == PARITY_EVEN ? "even" : "odd"
    );
    if (!initial_cost) {
        solution[0] = MOVE_NONE;
        solution_length = 0;
        atomic_store(&stop_search, 1);
    }
    for (unsigned int threshold = initial_cost; initial_cost && threshold <= max_threshold; threshold++) {
        struct timeval start;
        struct timeval end;

        gettimeofday(&start, NULL);
        uint64_t nodes = search_threshold(threshold);
        gettimeofday(&end, NULL);
        double elapsed = elapsed_seconds(&start, &end);
        uint64_t nodes_per_second = elapsed > 0.0 ? (uint64_t)(nodes / elapsed) : 0;
        total_nodes += nodes;
        total_elapsed += elapsed;
        LOG(
            "IDA threshold %u, explored %" PRIu64 " nodes, took %.3fs, "
            "%" PRIu64 " nodes-per-sec\n",
            threshold,
            nodes,
            elapsed,
            nodes_per_second
        );
        if (atomic_load(&stop_search)) {
            break;
        }
    }

    int found = atomic_load(&stop_search);
    if (found) {
        char scratch[CUBE_ARRAY_SIZE];
        char display_highlow[CUBE_ARRAY_SIZE];
        print_solution(solution, solution_length);
        print_ida_summary(cube, highlow, solution_length);
        memcpy(display_highlow, highlow, CUBE_ARRAY_SIZE);
        for (unsigned int index = 0; index < solution_length; index++) {
            rotate_444(cube, scratch, CUBE_ARRAY_SIZE, solution[index]);
            rotate_444(display_highlow, scratch, CUBE_ARRAY_SIZE, solution[index]);
        }
        printf("END\n");
        print_phase1_cube(cube, display_highlow);
        fflush(stdout);
        LOG(
            "total explored %" PRIu64 " nodes, took %.3fs, %" PRIu64 " nodes-per-sec\n",
            total_nodes,
            total_elapsed,
            total_elapsed > 0.0 ? (uint64_t)(total_nodes / total_elapsed) : 0
        );
    } else {
        fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
    }
    unmap_cost_file(&all_center_table);
    unmap_symmetry_index(&all_center_index);
    unmap_cost_file(&lr_table);
    unmap_cost_file(&wing_table);
    return found ? 0 : 1;
}
