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

#include "ida_search_core.h"

#define CUBE_SIZE 6
#define CUBE_ARRAY_SIZE 217
#define GROUP_SIZE 8
#define GROUP_COLOR_COUNT 4
#define GROUP_UNIVERSE UINT64_C(70)
#define TABLE_UNIVERSE UINT64_C(24010000)
#define AXIS_COUNT 3
#define ORBIT_COUNT 9
#define ORBITS_PER_AXIS 3
#define TABLE_COUNT 18
#define DEFAULT_MAX_IDA_THRESHOLD 30
#define MAX_IDA_THRESHOLD 99
#define MATRIX_COST_MAX 13
#define MAX_THREADS 64
#define NO_TASK UINT_MAX

enum axis_index { AXIS_UD, AXIS_LR, AXIS_FB };

enum orbit_index {
    ORBIT_UD_LEFT_OBLIQUE,
    ORBIT_UD_RIGHT_OBLIQUE,
    ORBIT_UD_INNER_X,
    ORBIT_LR_LEFT_OBLIQUE,
    ORBIT_LR_RIGHT_OBLIQUE,
    ORBIT_LR_INNER_X,
    ORBIT_FB_LEFT_OBLIQUE,
    ORBIT_FB_RIGHT_OBLIQUE,
    ORBIT_FB_INNER_X,
};

/*
 * Exact 8-sticker (4,4) orbits from builder666.py DAISY_CENTER_ORBITS_666.
 * Outer-x is untracked. Order per axis is left-oblique, right-oblique, inner-x.
 */
static const unsigned int orbit_squares[ORBIT_COUNT][GROUP_SIZE] = {
    {9, 17, 28, 20, 189, 197, 208, 200},
    {10, 23, 27, 14, 190, 203, 207, 194},
    {15, 16, 21, 22, 195, 196, 201, 202},
    {45, 53, 64, 56, 117, 125, 136, 128},
    {46, 59, 63, 50, 118, 131, 135, 122},
    {51, 52, 57, 58, 123, 124, 129, 130},
    {81, 89, 100, 92, 153, 161, 172, 164},
    {82, 95, 99, 86, 154, 167, 171, 158},
    {87, 88, 93, 94, 159, 160, 165, 166},
};

static const unsigned char orbit_axis[ORBIT_COUNT] = {
    AXIS_UD, AXIS_UD, AXIS_UD, AXIS_LR, AXIS_LR, AXIS_LR, AXIS_FB, AXIS_FB, AXIS_FB,
};
static const unsigned char orbit_is_oblique[ORBIT_COUNT] = {1, 1, 0, 1, 1, 0, 1, 1, 0};
static const unsigned char axis_orbits[AXIS_COUNT][ORBITS_PER_AXIS] = {
    {ORBIT_UD_LEFT_OBLIQUE, ORBIT_UD_RIGHT_OBLIQUE, ORBIT_UD_INNER_X},
    {ORBIT_LR_LEFT_OBLIQUE, ORBIT_LR_RIGHT_OBLIQUE, ORBIT_LR_INNER_X},
    {ORBIT_FB_LEFT_OBLIQUE, ORBIT_FB_RIGHT_OBLIQUE, ORBIT_FB_INNER_X},
};

static const char axis_small[AXIS_COUNT] = {'D', 'L', 'B'};
static const char axis_large[AXIS_COUNT] = {'U', 'R', 'F'};
static const char axis_primary[AXIS_COUNT] = {'U', 'L', 'F'};
static const char axis_opposite[AXIS_COUNT] = {'D', 'R', 'B'};
static const char *axis_name[AXIS_COUNT] = {"UD", "LR", "FB"};
static const char *orbit_name[ORBIT_COUNT] = {
    "UD_LEFT_OBLIQUE",
    "UD_RIGHT_OBLIQUE",
    "UD_INNER_X",
    "LR_LEFT_OBLIQUE",
    "LR_RIGHT_OBLIQUE",
    "LR_INNER_X",
    "FB_LEFT_OBLIQUE",
    "FB_RIGHT_OBLIQUE",
    "FB_INNER_X",
};

static struct ranked_table {
    const char *flag;
    const char *label;
    unsigned char orbits[4];
    const char *filename;
    unsigned char *costs;
    int fd;
} ranked_tables[TABLE_COUNT] = {
    {"--ud-plus-lr-left-oblique-cost", "UD_PLUS_LR_LEFT_OBLIQUE",
     {ORBIT_UD_LEFT_OBLIQUE, ORBIT_UD_RIGHT_OBLIQUE, ORBIT_UD_INNER_X, ORBIT_LR_LEFT_OBLIQUE}, NULL, NULL, -1},
    {"--ud-plus-lr-right-oblique-cost", "UD_PLUS_LR_RIGHT_OBLIQUE",
     {ORBIT_UD_LEFT_OBLIQUE, ORBIT_UD_RIGHT_OBLIQUE, ORBIT_UD_INNER_X, ORBIT_LR_RIGHT_OBLIQUE}, NULL, NULL, -1},
    {"--ud-plus-lr-inner-x-cost", "UD_PLUS_LR_INNER_X",
     {ORBIT_UD_LEFT_OBLIQUE, ORBIT_UD_RIGHT_OBLIQUE, ORBIT_UD_INNER_X, ORBIT_LR_INNER_X}, NULL, NULL, -1},
    {"--ud-plus-fb-left-oblique-cost", "UD_PLUS_FB_LEFT_OBLIQUE",
     {ORBIT_UD_LEFT_OBLIQUE, ORBIT_UD_RIGHT_OBLIQUE, ORBIT_UD_INNER_X, ORBIT_FB_LEFT_OBLIQUE}, NULL, NULL, -1},
    {"--ud-plus-fb-right-oblique-cost", "UD_PLUS_FB_RIGHT_OBLIQUE",
     {ORBIT_UD_LEFT_OBLIQUE, ORBIT_UD_RIGHT_OBLIQUE, ORBIT_UD_INNER_X, ORBIT_FB_RIGHT_OBLIQUE}, NULL, NULL, -1},
    {"--ud-plus-fb-inner-x-cost", "UD_PLUS_FB_INNER_X",
     {ORBIT_UD_LEFT_OBLIQUE, ORBIT_UD_RIGHT_OBLIQUE, ORBIT_UD_INNER_X, ORBIT_FB_INNER_X}, NULL, NULL, -1},
    {"--lr-plus-ud-left-oblique-cost", "LR_PLUS_UD_LEFT_OBLIQUE",
     {ORBIT_LR_LEFT_OBLIQUE, ORBIT_LR_RIGHT_OBLIQUE, ORBIT_LR_INNER_X, ORBIT_UD_LEFT_OBLIQUE}, NULL, NULL, -1},
    {"--lr-plus-ud-right-oblique-cost", "LR_PLUS_UD_RIGHT_OBLIQUE",
     {ORBIT_LR_LEFT_OBLIQUE, ORBIT_LR_RIGHT_OBLIQUE, ORBIT_LR_INNER_X, ORBIT_UD_RIGHT_OBLIQUE}, NULL, NULL, -1},
    {"--lr-plus-ud-inner-x-cost", "LR_PLUS_UD_INNER_X",
     {ORBIT_LR_LEFT_OBLIQUE, ORBIT_LR_RIGHT_OBLIQUE, ORBIT_LR_INNER_X, ORBIT_UD_INNER_X}, NULL, NULL, -1},
    {"--lr-plus-fb-left-oblique-cost", "LR_PLUS_FB_LEFT_OBLIQUE",
     {ORBIT_LR_LEFT_OBLIQUE, ORBIT_LR_RIGHT_OBLIQUE, ORBIT_LR_INNER_X, ORBIT_FB_LEFT_OBLIQUE}, NULL, NULL, -1},
    {"--lr-plus-fb-right-oblique-cost", "LR_PLUS_FB_RIGHT_OBLIQUE",
     {ORBIT_LR_LEFT_OBLIQUE, ORBIT_LR_RIGHT_OBLIQUE, ORBIT_LR_INNER_X, ORBIT_FB_RIGHT_OBLIQUE}, NULL, NULL, -1},
    {"--lr-plus-fb-inner-x-cost", "LR_PLUS_FB_INNER_X",
     {ORBIT_LR_LEFT_OBLIQUE, ORBIT_LR_RIGHT_OBLIQUE, ORBIT_LR_INNER_X, ORBIT_FB_INNER_X}, NULL, NULL, -1},
    {"--fb-plus-ud-left-oblique-cost", "FB_PLUS_UD_LEFT_OBLIQUE",
     {ORBIT_FB_LEFT_OBLIQUE, ORBIT_FB_RIGHT_OBLIQUE, ORBIT_FB_INNER_X, ORBIT_UD_LEFT_OBLIQUE}, NULL, NULL, -1},
    {"--fb-plus-ud-right-oblique-cost", "FB_PLUS_UD_RIGHT_OBLIQUE",
     {ORBIT_FB_LEFT_OBLIQUE, ORBIT_FB_RIGHT_OBLIQUE, ORBIT_FB_INNER_X, ORBIT_UD_RIGHT_OBLIQUE}, NULL, NULL, -1},
    {"--fb-plus-ud-inner-x-cost", "FB_PLUS_UD_INNER_X",
     {ORBIT_FB_LEFT_OBLIQUE, ORBIT_FB_RIGHT_OBLIQUE, ORBIT_FB_INNER_X, ORBIT_UD_INNER_X}, NULL, NULL, -1},
    {"--fb-plus-lr-left-oblique-cost", "FB_PLUS_LR_LEFT_OBLIQUE",
     {ORBIT_FB_LEFT_OBLIQUE, ORBIT_FB_RIGHT_OBLIQUE, ORBIT_FB_INNER_X, ORBIT_LR_LEFT_OBLIQUE}, NULL, NULL, -1},
    {"--fb-plus-lr-right-oblique-cost", "FB_PLUS_LR_RIGHT_OBLIQUE",
     {ORBIT_FB_LEFT_OBLIQUE, ORBIT_FB_RIGHT_OBLIQUE, ORBIT_FB_INNER_X, ORBIT_LR_RIGHT_OBLIQUE}, NULL, NULL, -1},
    {"--fb-plus-lr-inner-x-cost", "FB_PLUS_LR_INNER_X",
     {ORBIT_FB_LEFT_OBLIQUE, ORBIT_FB_RIGHT_OBLIQUE, ORBIT_FB_INNER_X, ORBIT_LR_INNER_X}, NULL, NULL, -1},
};

/*
 * Indexed by the maximum table cost in each complete-axis group (UD, LR, FB).
 * utils/build-666-daisy-cost-matrix.py samples and rebuilds this matrix.
 *
 * Built from 100 random 60-move legal scrambles solved with multiplier 1.2:
 * 100 solved, 0 timed out, 1,588 path samples, 353 directly populated cells.
 * Median solve time was 0.8s (mean 5.6s, max 69.4s); median length was 15.
 */
static const unsigned char daisy_axis_costs_666[MATRIX_COST_MAX + 1][MATRIX_COST_MAX + 1][MATRIX_COST_MAX + 1] = {
    {  // UD 0
        { 0,  1,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 0
        { 1,  1,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 1
        { 2,  2,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 2
        { 4,  4,  4,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 3
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 4
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 5
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 6
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13, 14, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 1
        { 1,  1,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 0
        { 1,  1,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 1
        { 2,  2,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 2
        { 4,  4,  4,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 3
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 4
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 5
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 6
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13, 14, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 2
        { 2,  2,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 0
        { 2,  2,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 1
        { 2,  2,  2,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 2
        { 4,  4,  4,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 3
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 4
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 5
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 6
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13, 14, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 3
        { 4,  4,  4,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 0
        { 4,  4,  4,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 1
        { 4,  4,  4,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 2
        { 4,  4,  4,  4,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 3
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 4
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 5
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 6
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13, 14, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 4
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 0
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 1
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 2
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 3
        { 5,  5,  5,  5,  5,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 4
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 5
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 6
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 14, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 14, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 5
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 0
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 1
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 2
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 3
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 4
        { 6,  6,  6,  6,  6,  6,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 5
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 6
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 14, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 14, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 6
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 0
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 1
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 2
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 3
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 4
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 5
        { 7,  7,  7,  7,  7,  7,  7,  8, 10, 11, 12, 13, 14, 16},  // LR 6
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 14, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 14, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 7
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 0
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 1
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 2
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 3
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 4
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 5
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 6
        { 8,  8,  8,  8,  8,  8,  8,  8, 10, 11, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 15, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 15, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 15, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 8
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13, 14, 16},  // LR 0
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13, 14, 16},  // LR 1
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13, 14, 16},  // LR 2
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 11, 12, 13, 14, 16},  // LR 3
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 13, 14, 16},  // LR 4
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 13, 14, 16},  // LR 5
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 13, 14, 16},  // LR 6
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 13, 14, 16},  // LR 7
        {10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 13, 13, 14, 16},  // LR 8
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 15, 16},  // LR 9
        {12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 15, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 15, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 9
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13, 14, 16},  // LR 0
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13, 14, 16},  // LR 1
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13, 14, 16},  // LR 2
        {11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 12, 13, 14, 16},  // LR 3
        {11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 14, 16},  // LR 4
        {11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 14, 16},  // LR 5
        {11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 14, 16},  // LR 6
        {11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 13, 13, 15, 16},  // LR 7
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 15, 16},  // LR 8
        {11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 13, 13, 15, 16},  // LR 9
        {12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 15, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 15, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 10
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 16},  // LR 0
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 16},  // LR 1
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 16},  // LR 2
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 14, 16},  // LR 3
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 14, 16},  // LR 4
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 14, 16},  // LR 5
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 14, 16},  // LR 6
        {12, 12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 15, 16},  // LR 7
        {12, 12, 12, 12, 12, 12, 12, 12, 13, 13, 13, 13, 15, 16},  // LR 8
        {12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 15, 16},  // LR 9
        {12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 14, 15, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16, 16, 16},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 16, 16, 16},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 13
    },
    {  // UD 11
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 0
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 1
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 2
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 3
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 4
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 5
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16},  // LR 6
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 15, 16},  // LR 7
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 15, 16},  // LR 8
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 15, 16},  // LR 9
        {13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 16, 16, 16},  // LR 10
        {13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 16, 16, 17, 17},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 16, 17, 17, 17},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17},  // LR 13
    },
    {  // UD 12
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 0
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 1
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 2
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 3
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 4
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 5
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14, 16},  // LR 6
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 16},  // LR 7
        {14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 16},  // LR 8
        {14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 16},  // LR 9
        {14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 16, 16, 16},  // LR 10
        {14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 16, 17, 17, 17},  // LR 11
        {14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 16, 17, 17, 17},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17},  // LR 13
    },
    {  // UD 13
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 0
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 1
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 2
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 3
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 4
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 5
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 6
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 7
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 8
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 9
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16},  // LR 10
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17},  // LR 11
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17},  // LR 12
        {16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17, 17},  // LR 13
    },
};

static uint64_t binom[GROUP_SIZE + 1][GROUP_SIZE + 1];
static move_type inverse_move[MOVE_MAX];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_666];
static move_type solution[MAX_IDA_THRESHOLD + 1];
static atomic_uint next_task;
static atomic_uint solution_task = NO_TASK;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned char search_threshold;
static unsigned int loaded_table_count;
static unsigned int loaded_tables[TABLE_COUNT];
static float cost_to_goal_multiplier;

struct heuristic_result {
    uint64_t orbit_rank[ORBIT_COUNT];
    uint64_t table_rank[TABLE_COUNT];
    unsigned char table_cost[TABLE_COUNT];
    unsigned char axis_cost[AXIS_COUNT];
    unsigned char cost;
    unsigned char daisy;
};

struct worker {
    const char *root_cube;
    uint64_t ida_count;
    move_type solution[MAX_IDA_THRESHOLD + 1];
};

struct child {
    move_type move;
    unsigned char cost;
};

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE "
        "all 18 --{ud,lr,fb}-plus-{ud,lr,fb}-{left-oblique,right-oblique,inner-x}-cost FILE "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] [--multiplier F] "
        "[--print-ida-summary] [--apply-move MOVE] [--print-ranks] [--print-legal-moves]\n",
        program
    );
    printf(
        "  --multiplier F  scale max(UD, LR, FB) by F instead of using the sampled\n"
        "                  daisy_axis_costs_666 matrix. F must be at least 1.0 and is\n"
        "                  not admissible. See utils/build-666-daisy-cost-matrix.py\n"
    );
}

static void init_binom(void)
{
    for (unsigned int n = 0; n <= GROUP_SIZE; n++) {
        binom[n][0] = 1;
        binom[n][n] = 1;
        for (unsigned int k = 1; k < n; k++) {
            binom[n][k] = binom[n - 1][k - 1] + binom[n - 1][k];
        }
    }
}

static uint64_t combination_rank(
    const char *cube,
    const unsigned int squares[GROUP_SIZE],
    char small,
    char large
)
{
    unsigned int remaining[2] = {GROUP_COLOR_COUNT, GROUP_COLOR_COUNT};
    uint64_t permutations = GROUP_UNIVERSE;
    uint64_t rank = 0;
    unsigned int slots = GROUP_SIZE;

    for (unsigned int position = 0; position < GROUP_SIZE; position++) {
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

static uint64_t mixed_radix_rank(const uint64_t *ranks, unsigned int count)
{
    uint64_t mixed = 0;

    for (unsigned int index = 0; index < count; index++) {
        if (ranks[index] == UINT64_MAX) {
            return UINT64_MAX;
        }
        mixed = mixed * GROUP_UNIVERSE + ranks[index];
    }
    return mixed;
}

static uint64_t table_rank_for(const struct ranked_table *table, const uint64_t orbit_rank[ORBIT_COUNT])
{
    uint64_t selected[4];

    for (unsigned int index = 0; index < 4; index++) {
        selected[index] = orbit_rank[table->orbits[index]];
    }
    return mixed_radix_rank(selected, 4);
}

static int orbit_has_colors(
    const char *cube,
    const unsigned int squares[GROUP_SIZE],
    char first,
    char second
)
{
    for (unsigned int index = 0; index < 4; index++) {
        if (cube[squares[index]] != first) {
            return 0;
        }
    }
    for (unsigned int index = 4; index < GROUP_SIZE; index++) {
        if (cube[squares[index]] != second) {
            return 0;
        }
    }
    return 1;
}

static int axis_is_daisy(const char *cube, unsigned int axis)
{
    char primary = axis_primary[axis];
    char opposite = axis_opposite[axis];
    int native = 1;
    int swapped = 1;

    for (unsigned int local = 0; local < ORBITS_PER_AXIS; local++) {
        unsigned int orbit = axis_orbits[axis][local];
        const unsigned int *squares = orbit_squares[orbit];
        int native_orbit = orbit_has_colors(cube, squares, primary, opposite);
        int swapped_orbit = orbit_is_oblique[orbit] ? orbit_has_colors(cube, squares, opposite, primary) : native_orbit;

        native = native && native_orbit;
        swapped = swapped && swapped_orbit;
    }
    return native || swapped;
}

static int cube_is_daisy(const char *cube)
{
    return axis_is_daisy(cube, AXIS_UD) && axis_is_daisy(cube, AXIS_LR) && axis_is_daisy(cube, AXIS_FB);
}

static unsigned char decode_cost(unsigned char encoded)
{
    return encoded ? encoded - 1 : UINT8_MAX;
}

static unsigned char matrix_cost(const unsigned char axis_cost[AXIS_COUNT])
{
    unsigned char index[AXIS_COUNT];

    for (unsigned int axis = 0; axis < AXIS_COUNT; axis++) {
        index[axis] = axis_cost[axis] > MATRIX_COST_MAX ? MATRIX_COST_MAX : axis_cost[axis];
    }
    return daisy_axis_costs_666[index[AXIS_UD]][index[AXIS_LR]][index[AXIS_FB]];
}

static struct heuristic_result heuristic(const char *cube)
{
    struct heuristic_result result;
    int valid = 1;

    memset(&result, 0, sizeof(result));
    result.daisy = cube_is_daisy(cube) ? 1 : 0;
    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        unsigned int axis = orbit_axis[orbit];

        result.orbit_rank[orbit] = combination_rank(cube, orbit_squares[orbit], axis_small[axis], axis_large[axis]);
        if (result.orbit_rank[orbit] == UINT64_MAX) {
            valid = 0;
        }
    }
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        unsigned int index = loaded_tables[loaded];
        struct ranked_table *table = &ranked_tables[index];
        unsigned char encoded;

        if (!valid || !table->costs) {
            result.table_rank[index] = UINT64_MAX;
            result.table_cost[index] = UINT8_MAX;
            result.cost = UINT8_MAX;
            continue;
        }
        result.table_rank[index] = table_rank_for(table, result.orbit_rank);
        if (result.table_rank[index] == UINT64_MAX || result.table_rank[index] >= TABLE_UNIVERSE) {
            result.table_cost[index] = UINT8_MAX;
            result.cost = UINT8_MAX;
            continue;
        }
        encoded = table->costs[result.table_rank[index]];
        result.table_cost[index] = decode_cost(encoded);
        if (result.table_cost[index] == UINT8_MAX) {
            result.cost = UINT8_MAX;
            result.axis_cost[index / 6] = UINT8_MAX;
        } else if (result.axis_cost[index / 6] != UINT8_MAX &&
                   result.table_cost[index] > result.axis_cost[index / 6]) {
            result.axis_cost[index / 6] = result.table_cost[index];
        }
    }
    for (unsigned int axis = 0; axis < AXIS_COUNT; axis++) {
        if (result.axis_cost[axis] == UINT8_MAX) {
            result.cost = UINT8_MAX;
        } else if (result.cost != UINT8_MAX && result.axis_cost[axis] > result.cost) {
            result.cost = result.axis_cost[axis];
        }
    }
    if (result.cost != UINT8_MAX) {
        if (cost_to_goal_multiplier && result.cost) {
            float scaled = roundf(result.cost * cost_to_goal_multiplier);

            result.cost = scaled > MAX_IDA_THRESHOLD ? MAX_IDA_THRESHOLD + 1 : (unsigned char)scaled;
        } else {
            result.cost = matrix_cost(result.axis_cost);
        }
    }
    if (result.daisy) {
        result.cost = 0;
    } else if (result.cost == 0) {
        result.cost = 1;
    }
    return result;
}

static int move_is_allowed(move_type move)
{
    switch (move) {
        case Uw:
        case Uw_PRIME:
        case threeUw:
        case threeUw_PRIME:
        case Lw:
        case Lw_PRIME:
        case threeLw:
        case threeLw_PRIME:
        case Fw:
        case Fw_PRIME:
        case threeFw:
        case threeFw_PRIME:
        case Rw:
        case Rw_PRIME:
        case threeRw:
        case threeRw_PRIME:
        case Bw:
        case Bw_PRIME:
        case threeBw:
        case threeBw_PRIME:
        case Dw:
        case Dw_PRIME:
        case threeDw:
        case threeDw_PRIME:
            return 0;
        default:
            return 1;
    }
}

static void init_move_tables(void)
{
    for (unsigned int move_index = 0; move_index < MOVE_COUNT_666; move_index++) {
        move_type move = moves_666[move_index];
        unsigned int quarter_turn_offset = ((unsigned int)move - 1) % 3;

        inverse_move[move] = quarter_turn_offset == 0 ? move + 1 :
                             quarter_turn_offset == 1 ? move - 1 : move;
        if (move_is_allowed(move)) {
            legal_move_index[MOVE_NONE][legal_move_count[MOVE_NONE]++] = (unsigned char)move_index;
        }
    }

    for (unsigned int previous_index = 0; previous_index < MOVE_COUNT_666; previous_index++) {
        move_type previous_move = moves_666[previous_index];

        if (!move_is_allowed(previous_move)) {
            continue;
        }
        for (unsigned int move_index = 0; move_index < MOVE_COUNT_666; move_index++) {
            move_type move = moves_666[move_index];

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

static void map_ranked_tables(void)
{
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        struct ranked_table *table = &ranked_tables[loaded_tables[loaded]];
        struct stat file_stat;
        int mmap_flags = MAP_SHARED;

        table->fd = open(table->filename, O_RDONLY);
        if (table->fd < 0) {
            fprintf(stderr, "ERROR: could not open %s: %s\n", table->filename, strerror(errno));
            exit(1);
        }
        if (fstat(table->fd, &file_stat) != 0) {
            fprintf(stderr, "ERROR: could not stat %s: %s\n", table->filename, strerror(errno));
            exit(1);
        }
        if ((uint64_t)file_stat.st_size != TABLE_UNIVERSE) {
            fprintf(
                stderr, "ERROR: %s is %" PRIu64 " bytes, expected %" PRIu64 "\n",
                table->filename, (uint64_t)file_stat.st_size, TABLE_UNIVERSE
            );
            exit(1);
        }
#ifdef MAP_POPULATE
        if ((uint64_t)file_stat.st_blocks * 512 >= TABLE_UNIVERSE) {
            mmap_flags |= MAP_POPULATE;
        }
#endif
        table->costs = mmap(NULL, (size_t)TABLE_UNIVERSE, PROT_READ, mmap_flags, table->fd, 0);
        if (table->costs == MAP_FAILED) {
            fprintf(stderr, "ERROR: could not mmap %s: %s\n", table->filename, strerror(errno));
            exit(1);
        }
    }
}

static void unmap_ranked_tables(void)
{
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        struct ranked_table *table = &ranked_tables[loaded_tables[loaded]];

        if (table->costs && table->costs != MAP_FAILED) {
            munmap(table->costs, (size_t)TABLE_UNIVERSE);
        }
        if (table->fd >= 0) {
            close(table->fd);
        }
        table->costs = NULL;
        table->fd = -1;
    }
}

static void init_cube(char cube[CUBE_ARRAY_SIZE], const char *kociemba)
{
    const unsigned int face_size = CUBE_SIZE * CUBE_SIZE;

    if (strlen(kociemba) != face_size * 6) {
        fprintf(stderr, "ERROR: --kociemba must contain 216 stickers for a 6x6x6 cube\n");
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

static int is_edge_or_corner(unsigned int square)
{
    unsigned int face_offset = (square - 1) % (CUBE_SIZE * CUBE_SIZE);
    unsigned int row = face_offset / CUBE_SIZE;
    unsigned int col = face_offset % CUBE_SIZE;

    return row == 0 || row == CUBE_SIZE - 1 || col == 0 || col == CUBE_SIZE - 1;
}

static int is_outer_x_center(unsigned int square)
{
    unsigned int face_offset = (square - 1) % (CUBE_SIZE * CUBE_SIZE);

    return face_offset == 7 || face_offset == 10 || face_offset == 25 || face_offset == 28;
}

static void blank_untracked_squares(char cube[CUBE_ARRAY_SIZE])
{
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (is_edge_or_corner(square) || is_outer_x_center(square)) {
            cube[square] = '.';
        }
    }
}

static move_type parse_move(const char *move_string)
{
    for (unsigned int index = 0; index < MOVE_COUNT_666; index++) {
        move_type move = moves_666[index];

        if (!strcmp(move2str[move], move_string)) {
            return move;
        }
    }
    return MOVE_NONE;
}

static int ida_search(
    struct worker *worker,
    char cube[CUBE_ARRAY_SIZE],
    unsigned char depth,
    unsigned char threshold,
    move_type previous_move
)
{
    struct child children[MOVE_COUNT_666];
    unsigned int child_count = 0;
    unsigned char next_depth = depth + 1;
    char rotate_tmp[CUBE_ARRAY_SIZE];

    if (atomic_load_explicit(&solution_task, memory_order_relaxed) != NO_TASK) {
        return 0;
    }
    for (unsigned int index = 0; index < legal_move_count[previous_move]; index++) {
        move_type move = moves_666[legal_move_index[previous_move][index]];
        struct heuristic_result h;

        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        h = heuristic(cube);
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[move]);
        worker->ida_count++;

        if (h.cost == UINT8_MAX || next_depth + h.cost > threshold) {
            continue;
        }
        if (h.daisy) {
            worker->solution[depth] = move;
            worker->solution[next_depth] = MOVE_NONE;
            return 1;
        }
        children[child_count].move = move;
        children[child_count].cost = h.cost;
        child_count++;
    }

    if (next_depth >= threshold || next_depth >= MAX_IDA_THRESHOLD) {
        worker->solution[depth] = MOVE_NONE;
        return 0;
    }

    for (unsigned int index = 1; index < child_count; index++) {
        struct child pending = children[index];
        unsigned int destination = index;

        while (destination && children[destination - 1].cost > pending.cost) {
            children[destination] = children[destination - 1];
            destination--;
        }
        children[destination] = pending;
    }

    for (unsigned int index = 0; index < child_count; index++) {
        move_type move = children[index].move;

        worker->solution[depth] = move;
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        if (ida_search(worker, cube, next_depth, threshold, move)) {
            return 1;
        }
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[move]);
    }
    worker->solution[depth] = MOVE_NONE;
    return 0;
}

static void *search_root_moves(void *argument)
{
    struct worker *worker = argument;

    while (1) {
        unsigned int task = atomic_fetch_add(&next_task, 1);
        char cube[CUBE_ARRAY_SIZE];
        char rotate_tmp[CUBE_ARRAY_SIZE];
        move_type first;
        struct heuristic_result h;
        int found;

        if (task >= legal_move_count[MOVE_NONE] || atomic_load(&solution_task) != NO_TASK) {
            break;
        }
        first = moves_666[legal_move_index[MOVE_NONE][task]];
        memcpy(cube, worker->root_cube, CUBE_ARRAY_SIZE);
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, first);
        worker->ida_count++;
        h = heuristic(cube);

        if (h.cost == UINT8_MAX || 1 + h.cost > search_threshold) {
            continue;
        }
        worker->solution[0] = first;
        if (h.daisy) {
            worker->solution[1] = MOVE_NONE;
            found = 1;
        } else if (search_threshold <= 1) {
            continue;
        } else {
            found = ida_search(worker, cube, 1, search_threshold, first);
        }

        if (found) {
            pthread_mutex_lock(&solution_lock);
            if (atomic_load(&solution_task) == NO_TASK) {
                memcpy(solution, worker->solution, sizeof(solution));
                atomic_store(&solution_task, task);
            }
            pthread_mutex_unlock(&solution_lock);
            break;
        }
    }
    return NULL;
}

static int search_at_threshold(
    const char cube[CUBE_ARRAY_SIZE],
    unsigned char threshold,
    unsigned int thread_count,
    uint64_t *nodes
)
{
    struct worker workers[MAX_THREADS];
    pthread_t threads[MAX_THREADS];
    unsigned int worker_count = thread_count < legal_move_count[MOVE_NONE] ?
                                thread_count : legal_move_count[MOVE_NONE];

    *nodes = 1;
    search_threshold = threshold;
    atomic_store(&next_task, 0);
    atomic_store(&solution_task, NO_TASK);
    for (unsigned int index = 0; index < worker_count; index++) {
        memset(&workers[index], 0, sizeof(workers[index]));
        workers[index].root_cube = cube;
        if (pthread_create(&threads[index], NULL, search_root_moves, &workers[index]) != 0) {
            fprintf(stderr, "ERROR: could not create search thread %u\n", index);
            exit(1);
        }
    }
    for (unsigned int index = 0; index < worker_count; index++) {
        pthread_join(threads[index], NULL);
        *nodes += workers[index].ida_count;
    }
    return atomic_load(&solution_task) != NO_TASK;
}

static double elapsed_seconds(const struct timeval *start, const struct timeval *end)
{
    return (end->tv_sec - start->tv_sec) + (end->tv_usec - start->tv_usec) / 1000000.0;
}

static void print_ida_summary(const char cube[CUBE_ARRAY_SIZE], unsigned int length)
{
    char walk[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];

    memcpy(walk, cube, CUBE_ARRAY_SIZE);
    printf("\n      ");
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        printf(" %4s", ranked_tables[loaded_tables[loaded]].label);
    }
    printf("  CTG  TRU  IDX  DAY\n      ");
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        printf(" ====");
    }
    printf("  ===  ===  ===  ===\n");
    for (unsigned int step = 0; step <= length; step++) {
        struct heuristic_result h = heuristic(walk);

        if (step) {
            printf("%5s ", move2str[solution[step - 1]]);
        } else {
            printf(" INIT ");
        }
        for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
            printf(" %4u", h.table_cost[loaded_tables[loaded]]);
        }
        printf("  %3u  %3u  %3u  %3u\n", h.cost, length - step, step, h.daisy);
        if (step < length) {
            rotate_666_centers(walk, rotate_tmp, CUBE_ARRAY_SIZE, solution[step]);
        }
    }
    printf("\n");
}

static void print_ranks(const struct heuristic_result *initial)
{
    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        if (orbit) {
            printf(" ");
        }
        printf("%s_RANK %" PRIu64, orbit_name[orbit], initial->orbit_rank[orbit]);
    }
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        unsigned int index = loaded_tables[loaded];

        printf(
            " %s_RANK %" PRIu64 " %s_COST %u",
            ranked_tables[index].label, initial->table_rank[index],
            ranked_tables[index].label, initial->table_cost[index]
        );
    }
    printf(" COST %u DAISY %u\n", initial->cost, initial->daisy);
}

static int configure_loaded_tables(void)
{
    loaded_table_count = 0;
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        if (!ranked_tables[index].filename) {
            continue;
        }
        loaded_tables[loaded_table_count++] = index;
    }
    return loaded_table_count == TABLE_COUNT;
}

int main(int argc, char **argv)
{
    const char *kociemba = NULL;
    const char *apply_move_string = NULL;
    unsigned char min_threshold = 0;
    unsigned char max_threshold = DEFAULT_MAX_IDA_THRESHOLD;
    long detected_cpus = sysconf(_SC_NPROCESSORS_ONLN);
    unsigned int thread_count = detected_cpus > 0 ? (unsigned int)detected_cpus : 1;
    int print_summary = 0;
    int print_ranks_flag = 0;
    int print_legal_moves = 0;
    int max_threshold_is_explicit = 0;
    char cube[CUBE_ARRAY_SIZE];
    char rotate_tmp[CUBE_ARRAY_SIZE];

    if (thread_count > MAX_THREADS) {
        thread_count = MAX_THREADS;
    }
    for (int index = 1; index < argc; index++) {
        int matched_table = 0;

        for (unsigned int table = 0; table < TABLE_COUNT; table++) {
            if (!strcmp(argv[index], ranked_tables[table].flag) && index + 1 < argc) {
                ranked_tables[table].filename = argv[++index];
                matched_table = 1;
                break;
            }
        }
        if (matched_table) {
            continue;
        }
        if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
            kociemba = argv[++index];
        } else if (!strcmp(argv[index], "--min-ida-threshold") && index + 1 < argc) {
            min_threshold = (unsigned char)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--max-ida-threshold") && index + 1 < argc) {
            max_threshold = (unsigned char)atoi(argv[++index]);
            max_threshold_is_explicit = 1;
        } else if (!strcmp(argv[index], "--threads") && index + 1 < argc) {
            thread_count = (unsigned int)atoi(argv[++index]);
        } else if (!strcmp(argv[index], "--multiplier") && index + 1 < argc) {
            cost_to_goal_multiplier = (float)atof(argv[++index]);
        } else if (!strcmp(argv[index], "--apply-move") && index + 1 < argc) {
            apply_move_string = argv[++index];
        } else if (!strcmp(argv[index], "--print-rank") || !strcmp(argv[index], "--print-ranks")) {
            print_ranks_flag = 1;
        } else if (!strcmp(argv[index], "--print-legal-moves")) {
            print_legal_moves = 1;
        } else if (!strcmp(argv[index], "--print-ida-summary")) {
            print_summary = 1;
        } else {
            usage(argv[0]);
            return 1;
        }
    }
    if (cost_to_goal_multiplier && cost_to_goal_multiplier < 1.0f) {
        fprintf(stderr, "ERROR: --multiplier must be at least 1.0\n");
        return 2;
    }
    if (cost_to_goal_multiplier && !max_threshold_is_explicit) {
        float scaled = roundf(DEFAULT_MAX_IDA_THRESHOLD * cost_to_goal_multiplier);

        max_threshold = scaled > MAX_IDA_THRESHOLD ? MAX_IDA_THRESHOLD : (unsigned char)scaled;
    }
    if (!kociemba || !thread_count || thread_count > MAX_THREADS ||
        min_threshold > max_threshold || max_threshold > MAX_IDA_THRESHOLD ||
        !configure_loaded_tables()) {
        usage(argv[0]);
        return 2;
    }

    init_binom();
    init_move_tables();
    map_ranked_tables();
    init_cube(cube, kociemba);
    blank_untracked_squares(cube);
    if (apply_move_string) {
        move_type move = parse_move(apply_move_string);

        if (move == MOVE_NONE || !move_is_allowed(move)) {
            fprintf(stderr, "ERROR: invalid --apply-move %s\n", apply_move_string);
            unmap_ranked_tables();
            return 2;
        }
        rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
    }

    struct heuristic_result initial = heuristic(cube);
    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_666[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }
    if (print_ranks_flag) {
        print_ranks(&initial);
        unmap_ranked_tables();
        return initial.cost == UINT8_MAX;
    }

    printf("START\n");
    print_cube(cube, CUBE_SIZE);

    if (initial.cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial center state is absent from a ranked cost table\n");
        unmap_ranked_tables();
        return 1;
    }
    if (cost_to_goal_multiplier) {
        LOG("searching with cost to goal multiplier %.2f\n", cost_to_goal_multiplier);
    } else {
        LOG("searching with the sampled per-axis cost matrix\n");
    }
    LOG(
        "initial cost %u, axis costs %u/%u/%u, daisy %u, threads %u, ranked tables %u\n",
        initial.cost, initial.axis_cost[AXIS_UD], initial.axis_cost[AXIS_LR], initial.axis_cost[AXIS_FB],
        initial.daisy, thread_count, loaded_table_count
    );
    if (min_threshold < initial.cost) {
        min_threshold = initial.cost;
    }

    for (unsigned char threshold = min_threshold; threshold <= max_threshold; threshold++) {
        struct timeval start;
        struct timeval end;
        uint64_t threshold_nodes = 1;

        gettimeofday(&start, NULL);
        int found = initial.daisy || search_at_threshold(cube, threshold, thread_count, &threshold_nodes);
        gettimeofday(&end, NULL);
        LOG(
            "IDA threshold %u, explored %" PRIu64 " nodes, took %.3fs\n",
            threshold,
            threshold_nodes,
            elapsed_seconds(&start, &end)
        );
        if (found) {
            unsigned int length = 0;

            while (solution[length] != MOVE_NONE) {
                length++;
            }
            printf("SOLUTION (%u steps):", length);
            for (unsigned int index = 0; index < length; index++) {
                printf(" %s", move2str[solution[index]]);
            }
            printf("\n");
            if (print_summary) {
                print_ida_summary(cube, length);
            }
            for (unsigned int index = 0; index < length; index++) {
                rotate_666_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, solution[index]);
            }
            printf("END\n");
            print_cube(cube, CUBE_SIZE);
            unmap_ranked_tables();
            return 0;
        }
    }

    fprintf(stderr, "ERROR: no solution found through threshold %u\n", max_threshold);
    unmap_ranked_tables();
    return 1;
}
