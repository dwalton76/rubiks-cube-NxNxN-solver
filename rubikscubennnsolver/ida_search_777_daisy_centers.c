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

#include "center_symmetry_777.h"
#include "ida_search_core.h"

#define CUBE_SIZE 7
#define CUBE_ARRAY_SIZE 295
#define GROUP_SIZE 8
#define GROUP_COLOR_COUNT 4
#define GROUP_UNIVERSE UINT64_C(70)
#define LEAVE_ONE_OUT_UNIVERSE UINT64_C(24010000)
#define AXIS_COUNT 3
#define ORBIT_COUNT 5
#define LEAVE_ONE_OUT_TABLE_COUNT 15
#define PERFECT_TABLE_COUNT 3
#define TABLE_COUNT (LEAVE_ONE_OUT_TABLE_COUNT + PERFECT_TABLE_COUNT)
#define DEFAULT_MAX_IDA_THRESHOLD 30
#define MAX_IDA_THRESHOLD 99
#define MAX_THREADS 64
#define NO_TASK UINT_MAX

enum axis_index { AXIS_UD, AXIS_LR, AXIS_FB };

enum orbit_index {
    ORBIT_LEFT_OBLIQUE,
    ORBIT_MIDDLE_OBLIQUE,
    ORBIT_RIGHT_OBLIQUE,
    ORBIT_INNER_T,
    ORBIT_INNER_X,
};

/* The tracked orbits and their sorted colour pairs live in center_symmetry_777.h,
 * as daisy_orbit_squares_777 and daisy_axis_{small,large}_777, so the searcher
 * and the compaction tool rank a state identically. */
static const char axis_primary[AXIS_COUNT] = {'U', 'L', 'F'};
static const char axis_opposite[AXIS_COUNT] = {'D', 'R', 'B'};
static const char *axis_name[AXIS_COUNT] = {"UD", "LR", "FB"};
static const char *orbit_name[ORBIT_COUNT] = {
    "LEFT_OBLIQUE",
    "MIDDLE_OBLIQUE",
    "RIGHT_OBLIQUE",
    "INNER_T",
    "INNER_X",
};

/*
 * Inner-x spine: one raw 70^5 table of UD inner-x, LR inner-x, FB inner-x,
 * then the UD left and right obliques. LR and FB probes rewrite each group
 * rank through a cube rotation onto that square order (z' y' and x y'). The
 * rewrite is the small/large bit carried along by the rotation, so a solved
 * cube probes a depth-0 rank on every axis.
 */
#define SPINE_UNIVERSE UINT64_C(1680700000)
#define SPINE_PROBE_COUNT 3
#define SPINE_GROUP_COUNT 5

static const unsigned char spine_source_axis[SPINE_PROBE_COUNT][SPINE_GROUP_COUNT] = {
    {AXIS_UD, AXIS_LR, AXIS_FB, AXIS_UD, AXIS_UD},
    {AXIS_LR, AXIS_FB, AXIS_UD, AXIS_LR, AXIS_LR},
    {AXIS_FB, AXIS_UD, AXIS_LR, AXIS_FB, AXIS_FB},
};
static const unsigned char spine_source_orbit[SPINE_PROBE_COUNT][SPINE_GROUP_COUNT] = {
    {ORBIT_INNER_X, ORBIT_INNER_X, ORBIT_INNER_X, ORBIT_LEFT_OBLIQUE, ORBIT_RIGHT_OBLIQUE},
    {ORBIT_INNER_X, ORBIT_INNER_X, ORBIT_INNER_X, ORBIT_LEFT_OBLIQUE, ORBIT_RIGHT_OBLIQUE},
    {ORBIT_INNER_X, ORBIT_INNER_X, ORBIT_INNER_X, ORBIT_LEFT_OBLIQUE, ORBIT_RIGHT_OBLIQUE},
};

static const unsigned char spine_rank_map[SPINE_PROBE_COUNT][SPINE_GROUP_COUNT][GROUP_UNIVERSE] = {
    {
        {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69},
        {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69},
        {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69},
        {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69},
        {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69},
    },
    {
        {69, 65, 61, 51, 31, 66, 62, 52, 32, 55, 45, 25, 39, 19, 9, 67, 63, 53, 33, 56, 46, 26, 40, 20, 10, 57, 47, 27, 41, 21, 11, 35, 15, 5, 1, 68, 64, 54, 34, 58, 48, 28, 42, 22, 12, 59, 49, 29, 43, 23, 13, 36, 16, 6, 2, 60, 50, 30, 44, 24, 14, 37, 17, 7, 3, 38, 18, 8, 4, 0},
        {69, 53, 67, 33, 63, 51, 65, 31, 61, 46, 10, 40, 26, 56, 20, 54, 68, 34, 64, 50, 14, 44, 30, 60, 24, 48, 12, 42, 28, 58, 22, 7, 37, 3, 17, 52, 66, 32, 62, 47, 11, 41, 27, 57, 21, 45, 9, 39, 25, 55, 19, 5, 35, 1, 15, 49, 13, 43, 29, 59, 23, 8, 38, 4, 18, 6, 36, 2, 16, 0},
        {0, 17, 15, 18, 16, 3, 1, 4, 2, 20, 24, 22, 21, 19, 23, 37, 35, 38, 36, 56, 60, 58, 57, 55, 59, 40, 44, 42, 41, 39, 43, 63, 61, 64, 62, 7, 5, 8, 6, 26, 30, 28, 27, 25, 29, 10, 14, 12, 11, 9, 13, 33, 31, 34, 32, 46, 50, 48, 47, 45, 49, 67, 65, 68, 66, 53, 51, 54, 52, 69},
        {69, 65, 61, 51, 31, 66, 62, 52, 32, 55, 45, 25, 39, 19, 9, 67, 63, 53, 33, 56, 46, 26, 40, 20, 10, 57, 47, 27, 41, 21, 11, 35, 15, 5, 1, 68, 64, 54, 34, 58, 48, 28, 42, 22, 12, 59, 49, 29, 43, 23, 13, 36, 16, 6, 2, 60, 50, 30, 44, 24, 14, 37, 17, 7, 3, 38, 18, 8, 4, 0},
        {69, 65, 61, 51, 31, 66, 62, 52, 32, 55, 45, 25, 39, 19, 9, 67, 63, 53, 33, 56, 46, 26, 40, 20, 10, 57, 47, 27, 41, 21, 11, 35, 15, 5, 1, 68, 64, 54, 34, 58, 48, 28, 42, 22, 12, 59, 49, 29, 43, 23, 13, 36, 16, 6, 2, 60, 50, 30, 44, 24, 14, 37, 17, 7, 3, 38, 18, 8, 4, 0},
    },
    {
        {0, 6, 8, 5, 7, 36, 38, 35, 37, 49, 45, 48, 47, 50, 46, 2, 4, 1, 3, 13, 9, 12, 11, 14, 10, 43, 39, 42, 41, 44, 40, 52, 54, 51, 53, 16, 18, 15, 17, 29, 25, 28, 27, 30, 26, 59, 55, 58, 57, 60, 56, 66, 68, 65, 67, 23, 19, 22, 21, 24, 20, 32, 34, 31, 33, 62, 64, 61, 63, 69},
        {69, 34, 54, 64, 68, 33, 53, 63, 67, 14, 24, 30, 44, 50, 60, 32, 52, 62, 66, 13, 23, 29, 43, 49, 59, 11, 21, 27, 41, 47, 57, 4, 8, 18, 38, 31, 51, 61, 65, 12, 22, 28, 42, 48, 58, 10, 20, 26, 40, 46, 56, 3, 7, 17, 37, 9, 19, 25, 39, 45, 55, 2, 6, 16, 36, 1, 5, 15, 35, 0},
        {69, 53, 67, 33, 63, 51, 65, 31, 61, 46, 10, 40, 26, 56, 20, 54, 68, 34, 64, 50, 14, 44, 30, 60, 24, 48, 12, 42, 28, 58, 22, 7, 37, 3, 17, 52, 66, 32, 62, 47, 11, 41, 27, 57, 21, 45, 9, 39, 25, 55, 19, 5, 35, 1, 15, 49, 13, 43, 29, 59, 23, 8, 38, 4, 18, 6, 36, 2, 16, 0},
        {0, 6, 8, 5, 7, 36, 38, 35, 37, 49, 45, 48, 47, 50, 46, 2, 4, 1, 3, 13, 9, 12, 11, 14, 10, 43, 39, 42, 41, 44, 40, 52, 54, 51, 53, 16, 18, 15, 17, 29, 25, 28, 27, 30, 26, 59, 55, 58, 57, 60, 56, 66, 68, 65, 67, 23, 19, 22, 21, 24, 20, 32, 34, 31, 33, 62, 64, 61, 63, 69},
        {0, 17, 15, 18, 16, 3, 1, 4, 2, 20, 24, 22, 21, 19, 23, 37, 35, 38, 36, 56, 60, 58, 57, 55, 59, 40, 44, 42, 41, 39, 43, 63, 61, 64, 62, 7, 5, 8, 6, 26, 30, 28, 27, 25, 29, 10, 14, 12, 11, 9, 13, 33, 31, 34, 32, 46, 50, 48, 47, 45, 49, 67, 65, 68, 66, 53, 51, 54, 52, 69},
    },
};

#include "ida_search_777_daisy_mixed_rank_maps.h"

/*
 * The three perfect entries share one file. Their costs are one function under
 * three indexings, and each is constant on the orbits of the 16 symmetries that
 * fix its axis, so --perfect-cost holds 105,356,972 orbits rather than three
 * copies of 1,680,700,000 raw ranks. See center_symmetry_777.h.
 */
static struct ranked_table {
    const char *flag;
    const char *label;
    unsigned char axis;
    unsigned char omitted;
    uint64_t universe;
    const char *filename;
    unsigned char *costs;
    int fd;
} ranked_tables[TABLE_COUNT] = {
    {"--ud-without-left-oblique-cost", "UD_WITHOUT_LEFT_OBLIQUE", AXIS_UD, ORBIT_LEFT_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--ud-without-middle-oblique-cost", "UD_WITHOUT_MIDDLE_OBLIQUE", AXIS_UD, ORBIT_MIDDLE_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--ud-without-right-oblique-cost", "UD_WITHOUT_RIGHT_OBLIQUE", AXIS_UD, ORBIT_RIGHT_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--ud-without-inner-t-cost", "UD_WITHOUT_INNER_T", AXIS_UD, ORBIT_INNER_T, LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--ud-without-inner-x-cost", "UD_WITHOUT_INNER_X", AXIS_UD, ORBIT_INNER_X, LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--lr-without-left-oblique-cost", "LR_WITHOUT_LEFT_OBLIQUE", AXIS_LR, ORBIT_LEFT_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--lr-without-middle-oblique-cost", "LR_WITHOUT_MIDDLE_OBLIQUE", AXIS_LR, ORBIT_MIDDLE_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--lr-without-right-oblique-cost", "LR_WITHOUT_RIGHT_OBLIQUE", AXIS_LR, ORBIT_RIGHT_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--lr-without-inner-t-cost", "LR_WITHOUT_INNER_T", AXIS_LR, ORBIT_INNER_T, LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--lr-without-inner-x-cost", "LR_WITHOUT_INNER_X", AXIS_LR, ORBIT_INNER_X, LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--fb-without-left-oblique-cost", "FB_WITHOUT_LEFT_OBLIQUE", AXIS_FB, ORBIT_LEFT_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--fb-without-middle-oblique-cost", "FB_WITHOUT_MIDDLE_OBLIQUE", AXIS_FB, ORBIT_MIDDLE_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--fb-without-right-oblique-cost", "FB_WITHOUT_RIGHT_OBLIQUE", AXIS_FB, ORBIT_RIGHT_OBLIQUE,
     LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--fb-without-inner-t-cost", "FB_WITHOUT_INNER_T", AXIS_FB, ORBIT_INNER_T, LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    {"--fb-without-inner-x-cost", "FB_WITHOUT_INNER_X", AXIS_FB, ORBIT_INNER_X, LEAVE_ONE_OUT_UNIVERSE, NULL, NULL, -1},
    /* Filled from --perfect-cost, which all three share, so they carry no flag. */
    {NULL, "UD_PERFECT", AXIS_UD, ORBIT_COUNT, DAISY_PERFECT_ORBIT_COUNT_777, NULL, NULL, -1},
    {NULL, "LR_PERFECT", AXIS_LR, ORBIT_COUNT, DAISY_PERFECT_ORBIT_COUNT_777, NULL, NULL, -1},
    {NULL, "FB_PERFECT", AXIS_FB, ORBIT_COUNT, DAISY_PERFECT_ORBIT_COUNT_777, NULL, NULL, -1},
};

static struct daisy_symmetry_index_777 perfect_index = {-1, 0, NULL, NULL, NULL, NULL};

static move_type inverse_move[MOVE_MAX];
static unsigned char legal_move_count[MOVE_MAX];
static unsigned char legal_move_index[MOVE_MAX][MOVE_COUNT_777];
static move_type solution[MAX_IDA_THRESHOLD + 1];
static atomic_uint next_task;
static atomic_uint solution_task = NO_TASK;
static pthread_mutex_t solution_lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned char search_threshold;
static unsigned int loaded_table_count;
static unsigned int loaded_tables[TABLE_COUNT];
static float cost_to_goal_multiplier;
static int native_only;

/* Phase 7 pairs the LR inners and the LR oblique bars. Phase 8 daisy-solves
 * every axis using only moves that keep that state. */
enum search_phase { PHASE_UNSET, PHASE_7, PHASE_8 };
static enum search_phase search_phase;
static const char *perfect_index_filename;
static const char *spine_filename;
static unsigned char *spine_costs;
static int spine_fd = -1;

/* Phase 7: LR inner-t then LR inner-x, each C(8, 4) = 70. One native goal. */
#define LR_INNER_GROUP UINT64_C(70)
#define LR_INNER_UNIVERSE (LR_INNER_GROUP * LR_INNER_GROUP)
static const char *lr_inner_filename;
static unsigned char *lr_inner_costs;
static int lr_inner_fd = -1;

/* Phase 8 tables. Ranks are the mixed radix of orbit ranks already computed
 * for the daisy, in the builder's square-group order. */
#define PHASE8_TABLE_COUNT 8
#define PHASE8_AXIS_UNIVERSE UINT64_C(1680700000)
#define PHASE8_QUARTIC_UNIVERSE UINT64_C(24010000)
struct phase8_cost_table {
    const char *flag;
    const char *label;
    const char *filename;
    unsigned char *costs;
    int fd;
    uint64_t universe;
    unsigned int group_count;
    unsigned char axis[5];
    unsigned char orbit[5];
};
static struct phase8_cost_table phase8_tables[PHASE8_TABLE_COUNT] = {
    {"--ud-axis-cost", "UD_AXIS", NULL, NULL, -1, PHASE8_AXIS_UNIVERSE, 5,
     {AXIS_UD, AXIS_UD, AXIS_UD, AXIS_UD, AXIS_UD},
     {ORBIT_LEFT_OBLIQUE, ORBIT_MIDDLE_OBLIQUE, ORBIT_RIGHT_OBLIQUE, ORBIT_INNER_T, ORBIT_INNER_X}},
    {"--fb-axis-cost", "FB_AXIS", NULL, NULL, -1, PHASE8_AXIS_UNIVERSE, 5,
     {AXIS_FB, AXIS_FB, AXIS_FB, AXIS_FB, AXIS_FB},
     {ORBIT_LEFT_OBLIQUE, ORBIT_MIDDLE_OBLIQUE, ORBIT_RIGHT_OBLIQUE, ORBIT_INNER_T, ORBIT_INNER_X}},
    {"--lr-oblique-cost", "LR_OBLIQUE", NULL, NULL, -1, GROUP_UNIVERSE, 1,
     {AXIS_LR, 0, 0, 0, 0},
     {ORBIT_LEFT_OBLIQUE, 0, 0, 0, 0}},
    {"--inner-interaction-cost", "INNER_INTERACTION", NULL, NULL, -1, PHASE8_QUARTIC_UNIVERSE, 4,
     {AXIS_UD, AXIS_UD, AXIS_FB, AXIS_FB, 0},
     {ORBIT_INNER_T, ORBIT_INNER_X, ORBIT_INNER_T, ORBIT_INNER_X, 0}},
    {"--middle-interaction-cost", "MIDDLE_INTERACTION", NULL, NULL, -1, PHASE8_QUARTIC_UNIVERSE, 4,
     {AXIS_UD, AXIS_FB, AXIS_UD, AXIS_FB, 0},
     {ORBIT_INNER_X, ORBIT_INNER_X, ORBIT_MIDDLE_OBLIQUE, ORBIT_MIDDLE_OBLIQUE, 0}},
    {"--ud-obliques-fb-edges-cost", "UD_OBLIQUES_FB_EDGES", NULL, NULL, -1, PHASE8_AXIS_UNIVERSE, 5,
     {AXIS_UD, AXIS_UD, AXIS_UD, AXIS_FB, AXIS_FB},
     {ORBIT_LEFT_OBLIQUE, ORBIT_MIDDLE_OBLIQUE, ORBIT_RIGHT_OBLIQUE, ORBIT_LEFT_OBLIQUE, ORBIT_RIGHT_OBLIQUE}},
    {"--fb-obliques-ud-edges-cost", "FB_OBLIQUES_UD_EDGES", NULL, NULL, -1, PHASE8_AXIS_UNIVERSE, 5,
     {AXIS_UD, AXIS_UD, AXIS_FB, AXIS_FB, AXIS_FB},
     {ORBIT_LEFT_OBLIQUE, ORBIT_RIGHT_OBLIQUE, ORBIT_LEFT_OBLIQUE, ORBIT_MIDDLE_OBLIQUE, ORBIT_RIGHT_OBLIQUE}},
    {"--ud-obliques-fb-inner-t-cost", "UD_OBLIQUES_FB_INNER_T", NULL, NULL, -1, PHASE8_AXIS_UNIVERSE, 5,
     {AXIS_UD, AXIS_UD, AXIS_UD, AXIS_UD, AXIS_FB},
     {ORBIT_LEFT_OBLIQUE, ORBIT_MIDDLE_OBLIQUE, ORBIT_RIGHT_OBLIQUE, ORBIT_INNER_T, ORBIT_INNER_T}},
};

/* Search probes in this order and stops once one cost already exceeds the
 * remaining moves. UD comes first, then the UD-oblique/FB-inner-t table, then
 * FB. The other two 1.68 GiB tables come last. */
static const unsigned char phase8_probe_order[PHASE8_TABLE_COUNT] = {
    0, 7, 1, 3, 4, 2, 5, 6
};
static const char *const phase8_short_label[PHASE8_TABLE_COUNT] = {
    "UD", "FB", "LR", "INNER", "MIDDLE", "UD_OBL", "FB_OBL", "UD_IT"
};

struct mixed_cost_table {
    const char *flag;
    const char *filename;
    unsigned char *costs;
    int fd;
    const char *const *probe_name;
    const unsigned char (*source_axis)[SPINE_GROUP_COUNT];
    const unsigned char (*source_orbit)[SPINE_GROUP_COUNT];
    const unsigned char (*rank_map)[SPINE_GROUP_COUNT][GROUP_UNIVERSE];
};

static const char *const mixed_ix2it_probe_name[MIXED_PROBE_COUNT] = {
    "IX2IT_OMIT_FB", "IX2IT_OMIT_LR", "IX2IT_OMIT_UD"
};
static const char *const mixed_it2ix_probe_name[MIXED_PROBE_COUNT] = {
    "IT2IX_OMIT_FB", "IT2IX_OMIT_LR", "IT2IX_OMIT_UD"
};
static const char *const mixed_mid2it_probe_name[MIXED_PROBE_COUNT] = {
    "MID2IT_OMIT_FB", "MID2IT_OMIT_LR", "MID2IT_OMIT_UD"
};
static const char *const mixed_weave_probe_name[MIXED_PROBE_COUNT] = {
    "WEAVE_MIDDLE_FB", "WEAVE_MIDDLE_LR", "WEAVE_MIDDLE_UD"
};

static struct mixed_cost_table mixed_tables[MIXED_TABLE_COUNT] = {
    {
        "--inner-x-plus-two-inner-t-cost", NULL, NULL, -1, mixed_ix2it_probe_name,
        mixed_ix2it_source_axis, mixed_ix2it_source_orbit, mixed_ix2it_rank_map
    },
    {
        "--inner-t-plus-two-inner-x-cost", NULL, NULL, -1, mixed_it2ix_probe_name,
        mixed_it2ix_source_axis, mixed_it2ix_source_orbit, mixed_it2ix_rank_map
    },
    {
        "--middle-plus-two-inner-t-cost", NULL, NULL, -1, mixed_mid2it_probe_name,
        mixed_mid2it_source_axis, mixed_mid2it_source_orbit, mixed_mid2it_rank_map
    },
    {
        "--oblique-weave-cost", NULL, NULL, -1, mixed_weave_probe_name,
        mixed_weave_source_axis, mixed_weave_source_orbit, mixed_weave_rank_map
    },
};

struct heuristic_result {
    uint64_t orbit_rank[AXIS_COUNT][ORBIT_COUNT];
    uint64_t table_rank[TABLE_COUNT];
    uint64_t spine_rank[SPINE_PROBE_COUNT];
    uint64_t mixed_rank[MIXED_TABLE_COUNT][MIXED_PROBE_COUNT];
    unsigned char table_cost[TABLE_COUNT];
    unsigned char axis_cost[AXIS_COUNT];
    unsigned char spine_cost[SPINE_PROBE_COUNT];
    unsigned char mixed_cost[MIXED_TABLE_COUNT][MIXED_PROBE_COUNT];
    unsigned char cost;
    unsigned char daisy;
    unsigned char goal;
    uint64_t lr_inner_rank;
    unsigned char lr_inner_cost;
    unsigned char unpaired_obliques;
    unsigned char oblique_cost;
    uint64_t phase8_rank[PHASE8_TABLE_COUNT];
    unsigned char phase8_cost[PHASE8_TABLE_COUNT];
    /* PHASE8_TABLE_COUNT when no phase 8 table proved this node is over budget. */
    unsigned char prune_table;
};

struct worker {
    const char *root_cube;
    uint64_t ida_count;
    unsigned int profile_slot;
    move_type solution[MAX_IDA_THRESHOLD + 1];
};

/* event[][PHASE8_TABLE_COUNT] counts nodes the heuristic kept. pair_ud[table]
 * is the UD-axis cost against that table's cost, for kept nodes only. */
struct prune_profile {
    uint64_t event[32][PHASE8_TABLE_COUNT + 1];
    uint64_t survivor_cost[PHASE8_TABLE_COUNT][24];
    uint64_t survivor_slack[24];
    uint64_t survivor_binding[PHASE8_TABLE_COUNT];
    uint64_t pair_ud[PHASE8_TABLE_COUNT][18][18];
};

static struct prune_profile prune_profiles[MAX_THREADS];
static int profile_prunes;

struct child {
    move_type move;
    unsigned char cost;
};

static void usage(const char *program)
{
    printf(
        "usage: %s --kociemba STATE (--phase7 | --phase8) "
        "(all 15 --{ud,lr,fb}-without-{left-oblique,middle-oblique,right-oblique,inner-t,inner-x}-cost FILE "
        "| --perfect-cost FILE --perfect-index FILE) "
        "[--inner-x-spine-cost FILE] [--lr-inner-cost FILE] "
        "[--inner-x-plus-two-inner-t-cost FILE] [--inner-t-plus-two-inner-x-cost FILE] "
        "[--middle-plus-two-inner-t-cost FILE] [--oblique-weave-cost FILE] "
        "[--ud-axis-cost FILE] [--fb-axis-cost FILE] [--lr-oblique-cost FILE] "
        "[--inner-interaction-cost FILE] [--middle-interaction-cost FILE] "
        "[--ud-obliques-fb-edges-cost FILE] [--fb-obliques-ud-edges-cost FILE] "
        "[--ud-obliques-fb-inner-t-cost FILE] "
        "[--min-ida-threshold N] [--max-ida-threshold N] [--threads N] [--multiplier F] [--native-only] "
        "[--profile-prunes] [--print-ida-summary] [--apply-move MOVE] [--print-ranks] [--print-legal-moves]\n",
        program
    );
    printf(
        "  --perfect-cost F        one 105,356,972 orbit table covering all three axes\n"
        "  --perfect-index F       the rank-select symmetry index that goes with it\n"
        "  --inner-x-spine-cost F  raw 70^5 table: three inner-x orbits plus the UD\n"
        "                          left and right obliques. LR and FB are probed by\n"
        "                          rotating onto that square order.\n"
        "  --inner-x-plus-two-inner-t-cost F\n"
        "  --inner-t-plus-two-inner-x-cost F\n"
        "  --middle-plus-two-inner-t-cost F\n"
        "  --oblique-weave-cost F  four more raw 70^5 tables. Each file is the\n"
        "                          identity probe; x y and z' y' cover the other\n"
        "                          two. The heuristic is the max of every loaded table.\n"
        "  --multiplier F          scale that max by F. F must be at least 1.0 and is\n"
        "                          not admissible.\n"
        "  --native-only           require every tracked orbit to use its native face\n"
        "                          orientation\n"
        "  --lr-inner-cost F       70^2 table: LR inner-t then LR inner-x. Exact for\n"
        "                          those two orbits. Phase 7 uses it as its cost.\n"
        "  --ud-axis-cost F        phase 8 raw 70^5 UD axis, two daisy goals\n"
        "  --fb-axis-cost F        phase 8 raw 70^5 FB axis, two daisy goals\n"
        "  --lr-oblique-cost F     phase 8 paired LR bar placement, 70 states\n"
        "  --inner-interaction-cost F\n"
        "                          phase 8 UD/FB inners, 70^4, one goal\n"
        "  --middle-interaction-cost F\n"
        "                          phase 8 UD/FB inner-x and middles, 70^4\n"
        "  --ud-obliques-fb-edges-cost F\n"
        "                          phase 8 UD obliques plus FB edge obliques, 70^5\n"
        "  --fb-obliques-ud-edges-cost F\n"
        "                          phase 8 FB obliques plus UD edge obliques, 70^5\n"
        "  --ud-obliques-fb-inner-t-cost F\n"
        "                          phase 8 UD obliques, UD inner-t, FB inner-t, 70^5\n"
        "  --phase7                LR inner-t and inner-x native, and every oblique bar\n"
        "                          on L and R one color. LR obliques stay on L/R under every move\n"
        "                          still legal after LR staging. The full daisy tables\n"
        "                          are not a lower bound on this goal.\n"
        "  --phase8                daisy-solve all six sides. Moves are the outer turns,\n"
        "                          2-wide half turns, and L/R 3-wide half turns, which keep the phase 7\n"
        "                          state. The start state has to already be a phase 7 state.\n"
    );
}

static uint64_t combination_rank(
    const char *cube,
    const unsigned int squares[GROUP_SIZE],
    char small,
    char large
)
{
    return ida_combination_rank_pair(
        cube, squares, GROUP_SIZE, GROUP_COLOR_COUNT, GROUP_UNIVERSE, small, large
    );
}

static uint64_t mixed_radix_rank(const uint64_t *ranks, unsigned int count)
{
    return ida_mixed_radix_rank(ranks, count, GROUP_UNIVERSE);
}

static uint64_t table_rank_for(const struct ranked_table *table, const uint64_t orbit_rank[ORBIT_COUNT])
{
    uint64_t selected[ORBIT_COUNT];
    unsigned int count = 0;

    /* A perfect table is shared by all three axes and indexed by symmetry
     * orbit, so normalise this axis onto the UD coordinate and look the
     * canonical rank up in the index. */
    if (table->omitted == ORBIT_COUNT) {
        uint64_t canonical = daisy_canonical_rank_777(table->axis, orbit_rank);

        if (canonical == UINT64_MAX) {
            return UINT64_MAX;
        }
        return daisy_symmetry_dense_rank_777(&perfect_index, canonical);
    }
    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        if (orbit == table->omitted) {
            continue;
        }
        selected[count++] = orbit_rank[orbit];
    }
    return mixed_radix_rank(selected, count);
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

    for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
        const unsigned int *squares = daisy_orbit_squares_777[axis][orbit];
        int native_orbit = orbit_has_colors(cube, squares, primary, opposite);
        int swapped_orbit;

        if (orbit <= ORBIT_RIGHT_OBLIQUE) {
            swapped_orbit = orbit_has_colors(cube, squares, opposite, primary);
        } else {
            swapped_orbit = native_orbit;
        }
        native = native && native_orbit;
        swapped = swapped && swapped_orbit;
    }
    return native || (!native_only && swapped);
}

static int cube_is_daisy(const char *cube)
{
    return axis_is_daisy(cube, AXIS_UD) && axis_is_daisy(cube, AXIS_LR) && axis_is_daisy(cube, AXIS_FB);
}

static unsigned char decode_cost(unsigned char encoded)
{
    return decode_cost_byte(encoded);
}

static uint64_t spine_probe_rank(const struct heuristic_result *result, unsigned int probe)
{
    uint64_t rank = 0;

    for (unsigned int group = 0; group < SPINE_GROUP_COUNT; group++) {
        unsigned int axis = spine_source_axis[probe][group];
        unsigned int orbit = spine_source_orbit[probe][group];
        uint64_t group_rank = result->orbit_rank[axis][orbit];

        if (group_rank >= GROUP_UNIVERSE) {
            return UINT64_MAX;
        }
        group_rank = spine_rank_map[probe][group][group_rank];
        rank = rank * GROUP_UNIVERSE + group_rank;
    }
    return rank;
}

static uint64_t phase8_table_rank(const struct phase8_cost_table *table, const struct heuristic_result *result)
{
    uint64_t rank = 0;

    for (unsigned int group = 0; group < table->group_count; group++) {
        uint64_t group_rank = result->orbit_rank[table->axis[group]][table->orbit[group]];

        if (group_rank >= GROUP_UNIVERSE) {
            return UINT64_MAX;
        }
        rank = rank * GROUP_UNIVERSE + group_rank;
    }
    return rank;
}

static uint64_t mixed_probe_rank(const struct mixed_cost_table *table, const struct heuristic_result *result, unsigned int probe)
{
    uint64_t rank = 0;

    for (unsigned int group = 0; group < SPINE_GROUP_COUNT; group++) {
        unsigned int axis = table->source_axis[probe][group];
        unsigned int orbit = table->source_orbit[probe][group];
        uint64_t group_rank = result->orbit_rank[axis][orbit];

        if (group_rank >= GROUP_UNIVERSE) {
            return UINT64_MAX;
        }
        group_rank = table->rank_map[probe][group][group_rank];
        rank = rank * GROUP_UNIVERSE + group_rank;
    }
    return rank;
}

/* Same left/middle/right triplets as LR_LEFT/MIDDLE/RIGHT_OBLIQUES_777. */
#define OBLIQUE_BAR_COUNT 24
static const unsigned int oblique_bar_777[OBLIQUE_BAR_COUNT][3] = {
    {10, 11, 12}, {30, 23, 16}, {20, 27, 34}, {40, 39, 38},
    {59, 60, 61}, {79, 72, 65}, {69, 76, 83}, {89, 88, 87},
    {108, 109, 110}, {128, 121, 114}, {118, 125, 132}, {138, 137, 136},
    {157, 158, 159}, {177, 170, 163}, {167, 174, 181}, {187, 186, 185},
    {206, 207, 208}, {226, 219, 212}, {216, 223, 230}, {236, 235, 234},
    {255, 256, 257}, {275, 268, 261}, {265, 272, 279}, {285, 284, 283},
};

static int square_on_lr_face(unsigned int square)
{
    return (square >= 50 && square <= 98) || (square >= 148 && square <= 196);
}

static int lr_oblique_bars_paired(const char *cube)
{
    for (unsigned int bar = 0; bar < OBLIQUE_BAR_COUNT; bar++) {
        char color = cube[oblique_bar_777[bar][0]];

        if (!square_on_lr_face(oblique_bar_777[bar][1])) {
            continue;
        }
        if (cube[oblique_bar_777[bar][1]] != color || cube[oblique_bar_777[bar][2]] != color) {
            return 0;
        }
    }
    return 1;
}

/* L is squares 50-98 and R is 148-196. Phase 7 only prices the oblique bars
 * on those faces. One move pairs at most four of their wings, so
 * ceil(unpaired / 4) is a lower bound. */
static unsigned char unpaired_oblique_wings(const char *cube)
{
    unsigned char unpaired = 0;

    for (unsigned int bar = 0; bar < OBLIQUE_BAR_COUNT; bar++) {
        char middle;

        if (!square_on_lr_face(oblique_bar_777[bar][1])) {
            continue;
        }
        middle = cube[oblique_bar_777[bar][1]];
        unpaired += cube[oblique_bar_777[bar][0]] != middle;
        unpaired += cube[oblique_bar_777[bar][2]] != middle;
    }
    return unpaired;
}

static unsigned char oblique_wing_cost(unsigned char unpaired)
{
    return unpaired ? (unsigned char)((unpaired + 3) / 4) : 0;
}

static int lr_inners_native(const char *cube)
{
    return orbit_has_colors(cube, daisy_orbit_squares_777[AXIS_LR][ORBIT_INNER_T], 'L', 'R') &&
        orbit_has_colors(cube, daisy_orbit_squares_777[AXIS_LR][ORBIT_INNER_X], 'L', 'R');
}

/* LR centers are staged before this search, and every later legal move keeps
 * an LR oblique on L or R. Phase 7 only has to solve the LR inners and pair
 * the bars. The inners do not swap, so they have to be native. */
static int phase7_reached(const char *cube)
{
    return lr_inners_native(cube) && lr_oblique_bars_paired(cube);
}

static void take_cost(struct heuristic_result *result, unsigned char decoded)
{
    if (decoded == UINT8_MAX) {
        result->cost = UINT8_MAX;
    } else if (result->cost != UINT8_MAX && decoded > result->cost) {
        result->cost = decoded;
    }
}

static void rank_one_orbit(
    struct heuristic_result *result,
    const char *cube,
    uint16_t *ready,
    int *valid,
    unsigned int axis,
    unsigned int orbit
)
{
    unsigned int bit = axis * ORBIT_COUNT + orbit;

    if (*ready & (1u << bit)) {
        return;
    }
    *ready |= (uint16_t)(1u << bit);
    result->orbit_rank[axis][orbit] = combination_rank(
        cube, daisy_orbit_squares_777[axis][orbit],
        daisy_axis_small_777[axis], daisy_axis_large_777[axis]);
    if (result->orbit_rank[axis][orbit] == UINT64_MAX) {
        *valid = 0;
    }
}

static void rank_every_orbit(
    struct heuristic_result *result,
    const char *cube,
    uint16_t *ready,
    int *valid
)
{
    for (unsigned int axis = 0; axis < AXIS_COUNT; axis++) {
        for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
            rank_one_orbit(result, cube, ready, valid, axis, orbit);
        }
    }
}

static int legacy_cost_tables_loaded(void)
{
    if (loaded_table_count || spine_costs) {
        return 1;
    }
    for (unsigned int index = 0; index < MIXED_TABLE_COUNT; index++) {
        if (mixed_tables[index].costs) {
            return 1;
        }
    }
    return 0;
}

/* A finite budget is the moves still allowed. UINT8_MAX prices every table,
 * which print-ranks and the initial check need. */
static int cost_proves_prune(unsigned char cost, unsigned char budget)
{
    return budget != UINT8_MAX && (cost == UINT8_MAX || cost > budget);
}

static struct heuristic_result heuristic(const char *cube, unsigned char budget)
{
    struct heuristic_result result;
    uint16_t ready = 0;
    int valid = 1;

    memset(&result, 0, sizeof(result));
    result.prune_table = PHASE8_TABLE_COUNT;
    /* Leave-one-out, spine, and mixed probes read every orbit. Print-ranks
     * does too. The search path ranks an orbit only when a table needs it. */
    if (budget == UINT8_MAX || legacy_cost_tables_loaded()) {
        rank_every_orbit(&result, cube, &ready, &valid);
    }
    /* A full-daisy cost can exceed the distance to this weaker goal, so phase 7
     * probes only the LR inner-t x inner-x table. That pair is closed, so the
     * byte is exact for the inners. The oblique term is admissible on its own,
     * and a move can reduce both, so the cost is the max of the two. */
    if (search_phase == PHASE_7) {
        uint64_t t_rank;
        uint64_t x_rank;
        unsigned char inner_cost = 1;

        result.daisy = cube_is_daisy(cube) ? 1 : 0;
        rank_one_orbit(&result, cube, &ready, &valid, AXIS_LR, ORBIT_INNER_T);
        rank_one_orbit(&result, cube, &ready, &valid, AXIS_LR, ORBIT_INNER_X);
        t_rank = result.orbit_rank[AXIS_LR][ORBIT_INNER_T];
        x_rank = result.orbit_rank[AXIS_LR][ORBIT_INNER_X];

        result.unpaired_obliques = unpaired_oblique_wings(cube);
        result.oblique_cost = oblique_wing_cost(result.unpaired_obliques);
        result.goal = phase7_reached(cube) ? 1 : 0;
        result.lr_inner_rank = UINT64_MAX;
        if (lr_inner_costs && t_rank < LR_INNER_GROUP && x_rank < LR_INNER_GROUP) {
            result.lr_inner_rank = t_rank * LR_INNER_GROUP + x_rank;
            inner_cost = decode_cost(lr_inner_costs[result.lr_inner_rank]);
        } else if (lr_inner_costs) {
            inner_cost = UINT8_MAX;
        }
        result.lr_inner_cost = inner_cost;
        if (result.goal) {
            result.cost = 0;
        } else if (inner_cost == UINT8_MAX) {
            result.cost = UINT8_MAX;
        } else if (inner_cost > result.oblique_cost) {
            result.cost = inner_cost;
        } else {
            result.cost = result.oblique_cost;
        }
        return result;
    }
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        unsigned int index = loaded_tables[loaded];
        struct ranked_table *table = &ranked_tables[index];
        unsigned char encoded;

        if (!valid || !table->costs) {
            result.table_rank[index] = UINT64_MAX;
            result.table_cost[index] = UINT8_MAX;
            result.axis_cost[table->axis] = UINT8_MAX;
            continue;
        }
        result.table_rank[index] = table_rank_for(table, result.orbit_rank[table->axis]);
        if (result.table_rank[index] == UINT64_MAX || result.table_rank[index] >= table->universe) {
            result.table_cost[index] = UINT8_MAX;
            result.axis_cost[table->axis] = UINT8_MAX;
            continue;
        }
        encoded = table->costs[result.table_rank[index]];
        result.table_cost[index] = decode_cost(encoded);
        /* Leave-one-out mode loads five tables per axis, so an axis costs the most
         * any of its tables reports. */
        if (result.table_cost[index] == UINT8_MAX) {
            result.axis_cost[table->axis] = UINT8_MAX;
        } else if (result.axis_cost[table->axis] != UINT8_MAX &&
                   result.table_cost[index] > result.axis_cost[table->axis]) {
            result.axis_cost[table->axis] = result.table_cost[index];
        }
    }
    for (unsigned int axis = 0; axis < AXIS_COUNT; axis++) {
        if (result.axis_cost[axis] == UINT8_MAX) {
            result.cost = UINT8_MAX;
        } else if (result.cost != UINT8_MAX && result.axis_cost[axis] > result.cost) {
            result.cost = result.axis_cost[axis];
        }
    }
    if (spine_costs && result.cost != UINT8_MAX) {
        for (unsigned int probe = 0; probe < SPINE_PROBE_COUNT; probe++) {
            uint64_t rank = valid ? spine_probe_rank(&result, probe) : UINT64_MAX;
            unsigned char decoded = UINT8_MAX;

            result.spine_rank[probe] = rank;
            if (rank < SPINE_UNIVERSE) {
                decoded = decode_cost(spine_costs[rank]);
            }
            result.spine_cost[probe] = decoded;
            take_cost(&result, decoded);
        }
    }
    for (unsigned int table_index = 0; table_index < MIXED_TABLE_COUNT && result.cost != UINT8_MAX; table_index++) {
        struct mixed_cost_table *table = &mixed_tables[table_index];

        if (!table->costs) {
            continue;
        }
        for (unsigned int probe = 0; probe < MIXED_PROBE_COUNT; probe++) {
            uint64_t rank = valid ? mixed_probe_rank(table, &result, probe) : UINT64_MAX;
            unsigned char decoded = UINT8_MAX;

            result.mixed_rank[table_index][probe] = rank;
            if (rank < SPINE_UNIVERSE) {
                decoded = decode_cost(table->costs[rank]);
            }
            result.mixed_cost[table_index][probe] = decoded;
            take_cost(&result, decoded);
        }
    }
    for (unsigned int probe = 0; probe < PHASE8_TABLE_COUNT && !cost_proves_prune(result.cost, budget); probe++) {
        unsigned int table_index = phase8_probe_order[probe];
        struct phase8_cost_table *table = &phase8_tables[table_index];
        uint64_t rank = UINT64_MAX;
        unsigned char decoded = UINT8_MAX;

        if (!table->costs) {
            continue;
        }
        for (unsigned int group = 0; group < table->group_count; group++) {
            rank_one_orbit(&result, cube, &ready, &valid, table->axis[group], table->orbit[group]);
        }
        if (valid) {
            rank = phase8_table_rank(table, &result);
        }
        result.phase8_rank[table_index] = rank;
        if (rank < table->universe) {
            decoded = decode_cost(table->costs[rank]);
        }
        result.phase8_cost[table_index] = decoded;
        take_cost(&result, decoded);
        if (cost_proves_prune(result.cost, budget)) {
            result.prune_table = (unsigned char)table_index;
        }
    }
    /* A cost that already exceeds the budget can only go up, so the pruned
     * node set matches a full probe. Survivors fall through and take the max. */
    if (cost_proves_prune(result.cost, budget)) {
        return result;
    }
    if (result.cost != UINT8_MAX && cost_to_goal_multiplier) {
        float scaled = roundf(result.cost * cost_to_goal_multiplier);

        /* Stay clear of the UINT8_MAX "absent from the table" sentinel. Any cost
         * above MAX_IDA_THRESHOLD prunes at every threshold we can search. */
        if (result.cost) {
            result.cost = scaled > MAX_IDA_THRESHOLD ? MAX_IDA_THRESHOLD + 1 : (unsigned char)scaled;
        }
    }
    result.daisy = cube_is_daisy(cube) ? 1 : 0;
    if (result.daisy) {
        result.cost = 0;
    } else if (result.cost == 0) {
        result.cost = 1;
    }
    result.goal = result.daisy;
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
            break;
    }

    if (search_phase == PHASE_7) {
        switch (move) {
            // none of these moves modify sides L or R and we are only interested
            // in sides L and R for phase 7
            case U:
            case U_PRIME:
            case U2:
            case D:
            case D_PRIME:
            case D2:
            case F:
            case F_PRIME:
            case F2:
            case B:
            case B_PRIME:
            case B2:
            case Lw2:
            case threeLw2:
            case Rw2:
            case threeRw2:
                return 0;
            default:
                break;
        }

    /* A 2-wide half turn swaps opposite faces, so an LR oblique stays on L or R
     * and each bar's three squares move together. The U/D/F/B 3-wide half turns
     * split an LR bar and move an LR inner between L and R. The L/R 3-wide half
     * turns preserve the LR state and remain available to solve UD/FB. */
    } else if (search_phase == PHASE_8) {
        switch (move) {
            case threeUw2:
            case threeFw2:
            case threeBw2:
            case threeDw2:
                return 0;
            default:
                break;
        }
    }
    return 1;
}

static void init_move_tables(void)
{
    ida_init_move_tables(
        moves_777, MOVE_COUNT_777, move_is_allowed, legal_move_count, legal_move_index, inverse_move
    );
}

/*
 * The three perfect entries name the same file, so only the first of them owns
 * the mapping and the other two borrow it.
 */
static unsigned int owner_of_mapping(unsigned int loaded)
{
    const struct ranked_table *table = &ranked_tables[loaded_tables[loaded]];

    for (unsigned int earlier = 0; earlier < loaded; earlier++) {
        if (!strcmp(ranked_tables[loaded_tables[earlier]].filename, table->filename)) {
            return earlier;
        }
    }
    return loaded;
}

static void map_ranked_tables(void)
{
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        struct ranked_table *table = &ranked_tables[loaded_tables[loaded]];
        unsigned int owner = owner_of_mapping(loaded);

        if (owner != loaded) {
            table->costs = ranked_tables[loaded_tables[owner]].costs;
            table->fd = ranked_tables[loaded_tables[owner]].fd;
            continue;
        }

        struct mapped_cost_file file = ida_map_cost_file(table->filename, table->universe);

        table->fd = file.fd;
        table->costs = file.costs;
    }
    if (perfect_index_filename) {
        const char *problem = NULL;

        if (!daisy_symmetry_index_open_777(&perfect_index, perfect_index_filename, &problem)) {
            fprintf(stderr, "ERROR: %s %s", problem, perfect_index_filename);
            fprintf(stderr, errno ? ": %s\n" : "\n", strerror(errno));
            exit(1);
        }
    }
    if (spine_filename) {
        struct mapped_cost_file file = ida_map_cost_file(spine_filename, SPINE_UNIVERSE);

        spine_fd = file.fd;
        spine_costs = file.costs;
    }
    if (lr_inner_filename) {
        struct mapped_cost_file file = ida_map_cost_file(lr_inner_filename, LR_INNER_UNIVERSE);

        lr_inner_fd = file.fd;
        lr_inner_costs = file.costs;
    }
    for (unsigned int table_index = 0; table_index < MIXED_TABLE_COUNT; table_index++) {
        struct mixed_cost_table *table = &mixed_tables[table_index];

        if (!table->filename) {
            continue;
        }
        struct mapped_cost_file file = ida_map_cost_file(table->filename, SPINE_UNIVERSE);

        table->fd = file.fd;
        table->costs = file.costs;
    }
    for (unsigned int table_index = 0; table_index < PHASE8_TABLE_COUNT; table_index++) {
        struct phase8_cost_table *table = &phase8_tables[table_index];

        if (!table->filename) {
            continue;
        }
        struct mapped_cost_file file = ida_map_cost_file(table->filename, table->universe);

        table->fd = file.fd;
        table->costs = file.costs;
    }
}

static void unmap_ranked_tables(void)
{
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        struct ranked_table *table = &ranked_tables[loaded_tables[loaded]];

        if (owner_of_mapping(loaded) == loaded) {
            ida_unmap_cost_file(table->fd, table->costs, (size_t)table->universe);
        }
    }
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        ranked_tables[loaded_tables[loaded]].costs = NULL;
        ranked_tables[loaded_tables[loaded]].fd = -1;
    }
    daisy_symmetry_index_close_777(&perfect_index);
    if (spine_costs) {
        ida_unmap_cost_file(spine_fd, spine_costs, (size_t)SPINE_UNIVERSE);
        spine_costs = NULL;
        spine_fd = -1;
    }
    if (lr_inner_costs) {
        ida_unmap_cost_file(lr_inner_fd, lr_inner_costs, (size_t)LR_INNER_UNIVERSE);
        lr_inner_costs = NULL;
        lr_inner_fd = -1;
    }
    for (unsigned int table_index = 0; table_index < MIXED_TABLE_COUNT; table_index++) {
        struct mixed_cost_table *table = &mixed_tables[table_index];

        if (table->costs) {
            ida_unmap_cost_file(table->fd, table->costs, (size_t)SPINE_UNIVERSE);
            table->costs = NULL;
            table->fd = -1;
        }
    }
    for (unsigned int table_index = 0; table_index < PHASE8_TABLE_COUNT; table_index++) {
        struct phase8_cost_table *table = &phase8_tables[table_index];

        if (table->costs) {
            ida_unmap_cost_file(table->fd, table->costs, (size_t)table->universe);
            table->costs = NULL;
            table->fd = -1;
        }
    }
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

/*
 * The daisy only tracks the five (4,4) orbits per axis. Blanking everything it
 * ignores keeps those squares out of print_cube and makes a placeholder outer-x
 * from a fake 7x7x7 harmless: moves only ever shuffle '.' among '.' positions.
 */
static void blank_untracked_squares(char cube[CUBE_ARRAY_SIZE])
{
    for (unsigned int square = 1; square < CUBE_ARRAY_SIZE; square++) {
        if (ida_is_edge_or_corner(square, CUBE_SIZE) || is_outer_x_center(square)) {
            cube[square] = '.';
        }
    }
}

static move_type parse_move(const char *move_string)
{
    return ida_parse_move(move_string, moves_777, MOVE_COUNT_777);
}

static void note_prune_profile(
    struct worker *worker,
    unsigned char depth,
    const struct heuristic_result *h,
    unsigned char budget
)
{
    struct prune_profile *profile;
    unsigned char slot;
    unsigned char table;
    unsigned char ud;
    unsigned char slack;

    if (!profile_prunes || worker->profile_slot >= MAX_THREADS) {
        return;
    }
    profile = &prune_profiles[worker->profile_slot];
    slot = depth < 31 ? depth : 31;
    if (h->cost == UINT8_MAX || h->cost > budget) {
        table = h->prune_table <= PHASE8_TABLE_COUNT ? h->prune_table : PHASE8_TABLE_COUNT;
        profile->event[slot][table]++;
        return;
    }
    profile->event[slot][PHASE8_TABLE_COUNT]++;
    ud = h->phase8_cost[0] > 17 ? 17 : h->phase8_cost[0];
    for (table = 0; table < PHASE8_TABLE_COUNT; table++) {
        unsigned char cost = h->phase8_cost[table];
        unsigned char capped = cost > 17 ? 17 : cost;

        if (cost > 23) {
            cost = 23;
        }
        profile->survivor_cost[table][cost]++;
        if (cost == h->cost) {
            profile->survivor_binding[table]++;
        }
        profile->pair_ud[table][ud][capped]++;
    }
    slack = budget >= h->cost ? (unsigned char)(budget - h->cost) : 0;
    if (slack > 23) {
        slack = 23;
    }
    profile->survivor_slack[slack]++;
}

static void print_prune_profile(unsigned int worker_count)
{
    uint64_t event[32][PHASE8_TABLE_COUNT + 1];
    uint64_t total_event[PHASE8_TABLE_COUNT + 1];
    uint64_t cost_hist[PHASE8_TABLE_COUNT][24];
    uint64_t slack_hist[24];
    uint64_t binding[PHASE8_TABLE_COUNT];
    uint64_t pair[PHASE8_TABLE_COUNT][18][18];
    uint64_t kept = 0;
    uint64_t slack_sum = 0;

    memset(event, 0, sizeof(event));
    memset(total_event, 0, sizeof(total_event));
    memset(cost_hist, 0, sizeof(cost_hist));
    memset(slack_hist, 0, sizeof(slack_hist));
    memset(binding, 0, sizeof(binding));
    memset(pair, 0, sizeof(pair));
    for (unsigned int worker = 0; worker < worker_count && worker < MAX_THREADS; worker++) {
        struct prune_profile *profile = &prune_profiles[worker];

        for (unsigned int depth = 0; depth < 32; depth++) {
            for (unsigned int table = 0; table < PHASE8_TABLE_COUNT + 1; table++) {
                event[depth][table] += profile->event[depth][table];
                total_event[table] += profile->event[depth][table];
            }
        }
        for (unsigned int table = 0; table < PHASE8_TABLE_COUNT; table++) {
            binding[table] += profile->survivor_binding[table];
            for (unsigned int cost = 0; cost < 24; cost++) {
                cost_hist[table][cost] += profile->survivor_cost[table][cost];
            }
            for (unsigned int ud = 0; ud < 18; ud++) {
                for (unsigned int other = 0; other < 18; other++) {
                    pair[table][ud][other] += profile->pair_ud[table][ud][other];
                }
            }
        }
        for (unsigned int slack = 0; slack < 24; slack++) {
            slack_hist[slack] += profile->survivor_slack[slack];
            slack_sum += (uint64_t)slack * profile->survivor_slack[slack];
            kept += profile->survivor_slack[slack];
        }
    }

    printf("\nprune profile: first table over the remaining budget, in probe order\n");
    printf("%5s %13s", "depth", "nodes");
    for (unsigned int probe = 0; probe < PHASE8_TABLE_COUNT; probe++) {
        printf(" %10s", phase8_short_label[phase8_probe_order[probe]]);
    }
    printf(" %10s\n", "kept");
    for (unsigned int depth = 0; depth < 32; depth++) {
        uint64_t nodes = 0;

        for (unsigned int table = 0; table < PHASE8_TABLE_COUNT + 1; table++) {
            nodes += event[depth][table];
        }
        if (!nodes) {
            continue;
        }
        printf("%5u %13" PRIu64, depth, nodes);
        for (unsigned int probe = 0; probe < PHASE8_TABLE_COUNT; probe++) {
            printf(" %10" PRIu64, event[depth][phase8_probe_order[probe]]);
        }
        printf(" %10" PRIu64 "\n", event[depth][PHASE8_TABLE_COUNT]);
    }
    {
        uint64_t nodes = 0;
        uint64_t reached = 0;

        for (unsigned int table = 0; table < PHASE8_TABLE_COUNT + 1; table++) {
            nodes += total_event[table];
        }
        printf("total %13" PRIu64, nodes);
        for (unsigned int probe = 0; probe < PHASE8_TABLE_COUNT; probe++) {
            printf(" %10" PRIu64, total_event[phase8_probe_order[probe]]);
        }
        printf(" %10" PRIu64 "\n", total_event[PHASE8_TABLE_COUNT]);
        reached = nodes;
        printf("share of nodes that reached each table and were pruned by it:\n");
        for (unsigned int probe = 0; probe < PHASE8_TABLE_COUNT; probe++) {
            unsigned int table = phase8_probe_order[probe];
            uint64_t pruned = total_event[table];
            double share = reached ? (100.0 * (double)pruned / (double)reached) : 0.0;

            printf(
                "  %-24s reached %13" PRIu64 ", pruned %13" PRIu64 " (%5.1f%%)\n",
                phase8_tables[table].label, reached, pruned, share
            );
            reached -= pruned;
        }
        printf("  %-24s kept    %13" PRIu64 "\n", "heuristic", total_event[PHASE8_TABLE_COUNT]);
    }

    printf("\nkept nodes: %" PRIu64 ", average slack %.2f\n", kept, kept ? (double)slack_sum / (double)kept : 0.0);
    printf("slack:");
    for (unsigned int slack = 0; slack < 24; slack++) {
        if (slack_hist[slack]) {
            printf(" %u:%" PRIu64, slack, slack_hist[slack]);
        }
    }
    printf("\n");
    for (unsigned int table = 0; table < PHASE8_TABLE_COUNT; table++) {
        uint64_t count = 0;
        uint64_t sum = 0;
        uint64_t above_ud = 0;
        uint64_t within_one = 0;

        for (unsigned int cost = 0; cost < 24; cost++) {
            count += cost_hist[table][cost];
            sum += (uint64_t)cost * cost_hist[table][cost];
        }
        for (unsigned int ud = 0; ud < 18; ud++) {
            for (unsigned int other = 0; other < 18; other++) {
                uint64_t n = pair[table][ud][other];

                if (other > ud) {
                    above_ud += n;
                }
                if (other + 1 >= ud) {
                    within_one += n;
                }
            }
        }
        printf(
            "  %-24s avg %5.2f, binding %13" PRIu64 ", above UD %13" PRIu64 ", within 1 of UD %13" PRIu64 "\n",
            phase8_tables[table].label,
            count ? (double)sum / (double)count : 0.0,
            binding[table],
            above_ud,
            within_one
        );
        printf("    cost");
        for (unsigned int cost = 0; cost < 24; cost++) {
            if (cost_hist[table][cost]) {
                printf(" %u:%" PRIu64, cost, cost_hist[table][cost]);
            }
        }
        printf("\n");
    }
    printf("\n");
}

static int ida_search(
    struct worker *worker,
    char cube[CUBE_ARRAY_SIZE],
    unsigned char depth,
    unsigned char threshold,
    move_type previous_move
)
{
    struct child children[MOVE_COUNT_777];
    unsigned int child_count = 0;
    unsigned char next_depth = depth + 1;
    char rotate_tmp[CUBE_ARRAY_SIZE];

    if (atomic_load_explicit(&solution_task, memory_order_relaxed) != NO_TASK) {
        return 0;
    }
    for (unsigned int index = 0; index < legal_move_count[previous_move]; index++) {
        move_type move = moves_777[legal_move_index[previous_move][index]];
        struct heuristic_result h;
        unsigned char budget = threshold > next_depth ? (unsigned char)(threshold - next_depth) : 0;

        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        h = heuristic(cube, budget);
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[move]);
        worker->ida_count++;
        note_prune_profile(worker, next_depth, &h, budget);

        if (h.cost == UINT8_MAX || next_depth + h.cost > threshold) {
            continue;
        }
        if (h.goal) {
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
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
        if (ida_search(worker, cube, next_depth, threshold, move)) {
            return 1;
        }
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, inverse_move[move]);
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
        unsigned char budget = search_threshold > 0 ? (unsigned char)(search_threshold - 1) : 0;
        int found;

        if (task >= legal_move_count[MOVE_NONE] || atomic_load(&solution_task) != NO_TASK) {
            break;
        }
        first = moves_777[legal_move_index[MOVE_NONE][task]];
        memcpy(cube, worker->root_cube, CUBE_ARRAY_SIZE);
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, first);
        worker->ida_count++;
        h = heuristic(cube, budget);
        note_prune_profile(worker, 1, &h, budget);

        if (h.cost == UINT8_MAX || 1 + h.cost > search_threshold) {
            continue;
        }
        worker->solution[0] = first;
        if (h.goal) {
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
        memset(&prune_profiles[index], 0, sizeof(prune_profiles[index]));
        workers[index].root_cube = cube;
        workers[index].profile_slot = index;
        if (pthread_create(&threads[index], NULL, search_root_moves, &workers[index]) != 0) {
            fprintf(stderr, "ERROR: could not create search thread %u\n", index);
            exit(1);
        }
    }
    for (unsigned int index = 0; index < worker_count; index++) {
        pthread_join(threads[index], NULL);
        *nodes += workers[index].ida_count;
    }
    if (profile_prunes) {
        print_prune_profile(worker_count);
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
        struct heuristic_result h = heuristic(walk, UINT8_MAX);

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
            rotate_777_centers(walk, rotate_tmp, CUBE_ARRAY_SIZE, solution[step]);
        }
    }
    printf("\n");
}

static void print_ranks(const struct heuristic_result *initial)
{
    for (unsigned int axis = 0; axis < AXIS_COUNT; axis++) {
        for (unsigned int orbit = 0; orbit < ORBIT_COUNT; orbit++) {
            if (axis || orbit) {
                printf(" ");
            }
            printf("%s_%s_RANK %" PRIu64, axis_name[axis], orbit_name[orbit], initial->orbit_rank[axis][orbit]);
        }
    }
    for (unsigned int loaded = 0; loaded < loaded_table_count; loaded++) {
        unsigned int index = loaded_tables[loaded];

        printf(
            " %s_RANK %" PRIu64 " %s_COST %u",
            ranked_tables[index].label, initial->table_rank[index],
            ranked_tables[index].label, initial->table_cost[index]
        );
    }
    if (spine_costs) {
        static const char *probe_name[SPINE_PROBE_COUNT] = {"UD", "LR", "FB"};

        for (unsigned int probe = 0; probe < SPINE_PROBE_COUNT; probe++) {
            printf(
                " SPINE_%s_RANK %" PRIu64 " SPINE_%s_COST %u",
                probe_name[probe], initial->spine_rank[probe],
                probe_name[probe], initial->spine_cost[probe]
            );
        }
    }
    for (unsigned int table_index = 0; table_index < MIXED_TABLE_COUNT; table_index++) {
        const struct mixed_cost_table *table = &mixed_tables[table_index];

        if (!table->costs) {
            continue;
        }
        for (unsigned int probe = 0; probe < MIXED_PROBE_COUNT; probe++) {
            printf(
                " %s_RANK %" PRIu64 " %s_COST %u",
                table->probe_name[probe], initial->mixed_rank[table_index][probe],
                table->probe_name[probe], initial->mixed_cost[table_index][probe]
            );
        }
    }
    if (search_phase == PHASE_7) {
        printf(
            " UNPAIRED %u OBLIQUE_COST %u",
            initial->unpaired_obliques, initial->oblique_cost
        );
        if (lr_inner_costs) {
            printf(
                " LR_INNER_RANK %" PRIu64 " LR_INNER_COST %u",
                initial->lr_inner_rank, initial->lr_inner_cost
            );
        }
    }
    for (unsigned int table_index = 0; table_index < PHASE8_TABLE_COUNT; table_index++) {
        const struct phase8_cost_table *table = &phase8_tables[table_index];

        if (!table->costs) {
            continue;
        }
        printf(
            " %s_RANK %" PRIu64 " %s_COST %u",
            table->label, initial->phase8_rank[table_index],
            table->label, initial->phase8_cost[table_index]
        );
    }
    printf(" COST %u DAISY %u GOAL %u\n", initial->cost, initial->daisy, initial->goal);
}

static int configure_loaded_tables(void)
{
    unsigned int leave_one_out = 0;
    unsigned int perfect = 0;

    loaded_table_count = 0;
    for (unsigned int index = 0; index < TABLE_COUNT; index++) {
        if (!ranked_tables[index].filename) {
            continue;
        }
        if (ranked_tables[index].omitted == ORBIT_COUNT) {
            perfect++;
        } else {
            leave_one_out++;
        }
        loaded_tables[loaded_table_count++] = index;
    }
    /* Phase 7 ignores the daisy tables. Phase 8 may run with them or, for a
     * short search, with the 0/1 fallback that the missing-table path already uses. */
    if (leave_one_out == 0 && perfect == 0 && !perfect_index_filename) {
        int mixed_named = 0;

        for (unsigned int table_index = 0; table_index < MIXED_TABLE_COUNT; table_index++) {
            if (mixed_tables[table_index].filename) {
                mixed_named = 1;
            }
        }
        if (!spine_filename && !mixed_named) {
            return 1;
        }
    }
    if (leave_one_out == LEAVE_ONE_OUT_TABLE_COUNT && perfect == 0 && !perfect_index_filename) {
        return 1;
    }
    /* The shared perfect table is unreadable without its symmetry index. */
    if (perfect == PERFECT_TABLE_COUNT && leave_one_out == 0 && perfect_index_filename) {
        return 1;
    }
    return 0;
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
            if (ranked_tables[table].flag &&
                    !strcmp(argv[index], ranked_tables[table].flag) && index + 1 < argc) {
                ranked_tables[table].filename = argv[++index];
                matched_table = 1;
                break;
            }
        }
        if (!matched_table && index + 1 < argc) {
            for (unsigned int table_index = 0; table_index < MIXED_TABLE_COUNT; table_index++) {
                if (mixed_tables[table_index].flag &&
                        !strcmp(argv[index], mixed_tables[table_index].flag)) {
                    mixed_tables[table_index].filename = argv[++index];
                    matched_table = 1;
                    break;
                }
            }
        }
        if (!matched_table && index + 1 < argc) {
            for (unsigned int table_index = 0; table_index < PHASE8_TABLE_COUNT; table_index++) {
                if (!strcmp(argv[index], phase8_tables[table_index].flag)) {
                    phase8_tables[table_index].filename = argv[++index];
                    matched_table = 1;
                    break;
                }
            }
        }
        if (matched_table) {
            continue;
        }
        if (!strcmp(argv[index], "--perfect-cost") && index + 1 < argc) {
            const char *filename = argv[++index];

            for (unsigned int table = 0; table < TABLE_COUNT; table++) {
                if (ranked_tables[table].omitted == ORBIT_COUNT) {
                    ranked_tables[table].filename = filename;
                }
            }
        } else if (!strcmp(argv[index], "--perfect-index") && index + 1 < argc) {
            perfect_index_filename = argv[++index];
        } else if (!strcmp(argv[index], "--inner-x-spine-cost") && index + 1 < argc) {
            spine_filename = argv[++index];
        } else if (!strcmp(argv[index], "--lr-inner-cost") && index + 1 < argc) {
            lr_inner_filename = argv[++index];
        } else if (!strcmp(argv[index], "--kociemba") && index + 1 < argc) {
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
        } else if (!strcmp(argv[index], "--native-only")) {
            native_only = 1;
        } else if (!strcmp(argv[index], "--phase7") || !strcmp(argv[index], "--phase8")) {
            enum search_phase requested = !strcmp(argv[index], "--phase7") ? PHASE_7 : PHASE_8;

            if (search_phase != PHASE_UNSET) {
                fprintf(stderr, "ERROR: --phase7 and --phase8 are mutually exclusive\n");
                return 2;
            }
            search_phase = requested;
        } else if (!strcmp(argv[index], "--apply-move") && index + 1 < argc) {
            apply_move_string = argv[++index];
        } else if (!strcmp(argv[index], "--print-rank") || !strcmp(argv[index], "--print-ranks")) {
            print_ranks_flag = 1;
        } else if (!strcmp(argv[index], "--profile-prunes")) {
            profile_prunes = 1;
        } else if (!strcmp(argv[index], "--print-legal-moves")) {
            print_legal_moves = 1;
        } else if (!strcmp(argv[index], "--print-ida-summary")) {
            print_summary = 1;
        } else {
            usage(argv[0]);
            return 1;
        }
    }
    /* Below 1.0 would weaken an already weak heuristic rather than inflate it. */
    if (cost_to_goal_multiplier && cost_to_goal_multiplier < 1.0f) {
        fprintf(stderr, "ERROR: --multiplier must be at least 1.0\n");
        return 2;
    }
    /* A multiplier scales the initial cost too, and that seeds the first threshold.
     * Scale the default ceiling with it so it cannot start out of range. */
    if (cost_to_goal_multiplier && !max_threshold_is_explicit) {
        float scaled = roundf(DEFAULT_MAX_IDA_THRESHOLD * cost_to_goal_multiplier);

        max_threshold = scaled > MAX_IDA_THRESHOLD ? MAX_IDA_THRESHOLD : (unsigned char)scaled;
    }
    if (search_phase == PHASE_UNSET || !kociemba || !thread_count || thread_count > MAX_THREADS ||
        min_threshold > max_threshold || max_threshold > MAX_IDA_THRESHOLD ||
        !configure_loaded_tables()) {
        usage(argv[0]);
        return 2;
    }

    init_binom();
    init_move_tables();
    init_center_symmetry_777();
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
        rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, move);
    }

    struct heuristic_result initial = heuristic(cube, UINT8_MAX);
    if (print_legal_moves) {
        printf("LEGAL_MOVES");
        for (unsigned int index = 0; index < legal_move_count[MOVE_NONE]; index++) {
            printf(" %s", move2str[moves_777[legal_move_index[MOVE_NONE][index]]]);
        }
        printf("\n");
    }
    if (print_ranks_flag) {
        print_ranks(&initial);
        unmap_ranked_tables();
        return initial.cost == UINT8_MAX;
    }
    if (search_phase == PHASE_8 && !phase7_reached(cube)) {
        fprintf(
            stderr,
            "ERROR: phase 8 start does not have LR inners solved and LR oblique bars paired\n"
        );
        unmap_ranked_tables();
        return 2;
    }

    printf("START\n");
    print_cube(cube, CUBE_SIZE);

    if (initial.cost == UINT8_MAX) {
        fprintf(stderr, "ERROR: initial center state is absent from a ranked cost table\n");
        unmap_ranked_tables();
        return 1;
    }
    unsigned int mixed_loaded = 0;

    for (unsigned int table_index = 0; table_index < MIXED_TABLE_COUNT; table_index++) {
        if (mixed_tables[table_index].costs) {
            mixed_loaded++;
        }
    }
    if (search_phase == PHASE_7) {
        LOG(
            "searching phase 7: LR inners native, LR oblique bars paired%s\n",
            lr_inner_costs ? ", LR inner-t x inner-x cost table" : ""
        );
    } else {
        LOG("searching phase 8: daisy solve, keeping the phase 7 state\n");
        if (spine_costs && mixed_loaded) {
            LOG(
                "searching with max of the per-axis tables, the inner-x spine, and %u mixed-axis tables\n",
                mixed_loaded
            );
        } else if (spine_costs) {
            LOG("searching with max of the per-axis tables and the inner-x spine\n");
        } else if (mixed_loaded) {
            LOG("searching with max of the per-axis tables and %u mixed-axis tables\n", mixed_loaded);
        } else {
            LOG("searching with max of the per-axis tables\n");
        }
    }
    if (cost_to_goal_multiplier) {
        LOG("searching with cost to goal multiplier %.2f\n", cost_to_goal_multiplier);
    }
    LOG(
        "initial cost %u, axis costs %u/%u/%u, daisy %u, goal %u, threads %u, ranked tables %u\n",
        initial.cost, initial.axis_cost[AXIS_UD], initial.axis_cost[AXIS_LR], initial.axis_cost[AXIS_FB],
        initial.daisy, initial.goal, thread_count, loaded_table_count
    );
    if (spine_costs) {
        LOG(
            "inner-x spine costs %u/%u/%u\n",
            initial.spine_cost[0], initial.spine_cost[1], initial.spine_cost[2]
        );
    }
    for (unsigned int table_index = 0; table_index < MIXED_TABLE_COUNT; table_index++) {
        if (!mixed_tables[table_index].costs) {
            continue;
        }
        LOG(
            "%s costs %u/%u/%u\n",
            mixed_tables[table_index].flag,
            initial.mixed_cost[table_index][0],
            initial.mixed_cost[table_index][1],
            initial.mixed_cost[table_index][2]
        );
    }
    if (min_threshold < initial.cost) {
        min_threshold = initial.cost;
    }

    for (unsigned char threshold = min_threshold; threshold <= max_threshold; threshold++) {
        struct timeval start;
        struct timeval end;
        uint64_t threshold_nodes = 1;

        gettimeofday(&start, NULL);
        int found = initial.goal || search_at_threshold(cube, threshold, thread_count, &threshold_nodes);
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
                rotate_777_centers(cube, rotate_tmp, CUBE_ARRAY_SIZE, solution[index]);
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
