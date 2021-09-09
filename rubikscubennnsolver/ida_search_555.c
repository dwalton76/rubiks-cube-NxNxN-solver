#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "ida_search_core.h"
#include "ida_search_555.h"

unsigned int t_centers_555[NUM_T_CENTERS_555] = {
    8, 14, 18, 12, // Upper
    33, 39, 43, 37, // Left
    58, 64, 68, 62, // Front
    83, 89, 93, 87, // Right
    108, 114, 118, 112, // Back
    133, 139, 143, 137, // Down
};

unsigned int left_of_t_centers_555[NUM_T_CENTERS_555] = {
    7, 9, 19, 17, // Upper
    32, 34, 44, 42, // Left
    57, 59, 69, 67, // Front
    82, 84, 94, 92, // Right
    107, 109, 119, 117, // Back
    132, 134, 144, 142, // Down
};

unsigned int right_of_t_centers_555[NUM_T_CENTERS_555] = {
    9, 19, 17, 7, // Upper
    34, 44, 42, 32, // Left
    59, 69, 67, 57, // Front
    84, 94, 92, 82, // Right
    109, 119, 117, 107, // Back
    134, 144, 142, 132, // Down
};

unsigned char get_unpaired_centers_stage_count_555(char *cube) {
    unsigned char unpaired_count = 32;

    for (int i = 0; i < NUM_T_CENTERS_555; i++) {
        if (cube[t_centers_555[i]] == 'U') {
            if (cube[left_of_t_centers_555[i]] == 'U') {
                unpaired_count--;
            }

            if (cube[right_of_t_centers_555[i]] == 'U') {
                unpaired_count--;
            }

        } else if (cube[t_centers_555[i]] == 'L') {
            if (cube[left_of_t_centers_555[i]] == 'L') {
                unpaired_count--;
            }

            if (cube[right_of_t_centers_555[i]] == 'L') {
                unpaired_count--;
            }
        }
    }

    return unpaired_count;
}


struct ida_heuristic_result ida_heuristic_centers_stage_555(char *cube) {
    struct ida_heuristic_result result;
    result.unpaired_count = get_unpaired_centers_stage_count_555(cube);
    result.cost_to_goal = result.unpaired_count / 4;

    return result;
}
