
#ifndef _IDA_SEARCH_777_H
#define _IDA_SEARCH_777_H

#define NUM_OBLIQUE_EDGES_777 72
#define NUM_LEFT_OBLIQUE_EDGES_777 24
#define NUM_MIDDLE_OBLIQUE_EDGES_777 24
#define NUM_RIGHT_OBLIQUE_EDGES_777 24

#define LFRB_NUM_OBLIQUE_EDGES_777 48
#define LFRB_NUM_LEFT_OBLIQUE_EDGES_777 16
#define LFRB_NUM_MIDDLE_OBLIQUE_EDGES_777 16
#define LFRB_NUM_RIGHT_OBLIQUE_EDGES_777 16

#define NUM_CENTERS_STEP40_777 50
#define NUM_CENTERS_STEP41_777 34
#define NUM_CENTERS_STEP42_777 34
#define BUCKETSIZE_STEP41_777 24010031
#define BUCKETSIZE_STEP42_777 24010031

#define NUM_CENTERS_STEP50_777 50
#define NUM_CENTERS_STEP51_777 34
#define NUM_CENTERS_STEP52_777 34
#define BUCKETSIZE_STEP51_777 24010031
#define BUCKETSIZE_STEP52_777 24010031

#define NUM_CENTERS_STEP60_777 150
#define NUM_CENTERS_STEP61_777 34
#define NUM_CENTERS_STEP62_777 34
#define NUM_CENTERS_STEP63_777 38
#define NUM_CENTERS_STEP70_777 50
#define BUCKETSIZE_STEP61_777 24010031
#define BUCKETSIZE_STEP62_777 24010031
#define BUCKETSIZE_STEP63_777 6350411


struct ida_heuristic_result ida_heuristic_UD_oblique_edges_stage_777(
    char *cube,
    unsigned int max_cost_to_goal
);
int ida_search_complete_UD_oblique_edges_stage_777(char *cube);


struct ida_heuristic_result ida_heuristic_LR_oblique_edges_stage_777(
    char *cube,
    unsigned int max_cost_to_goal
);
int ida_search_complete_LR_oblique_edges_stage_777(char *cube);


struct ida_heuristic_result ida_heuristic_step40_777(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **step40_777,
    char *step41_777,
    char *step42_777
);
int ida_search_complete_step40_777(char *cube);


struct ida_heuristic_result ida_heuristic_step50_777(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **step50_777,
    char *step51_777,
    char *step52_777
);
int ida_search_complete_step50_777(char *cube);


struct ida_heuristic_result ida_heuristic_step60_777(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **step60_777,
    char *step61_777,
    char *step62_777,
    char *step63_777
);
int ida_search_complete_step60_777(char *cube);


struct ida_heuristic_result ida_heuristic_step70_777(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **step70_777,
    char *step61_777,
    char *step62_777
);
int ida_search_complete_step70_777(char *cube);


#endif /* _IDA_SEARCH_777_H */
