
#ifndef _IDA_SEARCH_777_H
#define _IDA_SEARCH_777_H

#define NUM_OBLIQUE_EDGES_777 72
#define NUM_LEFT_OBLIQUE_EDGES_777 24
#define NUM_MIDDLE_OBLIQUE_EDGES_777 24
#define NUM_RIGHT_OBLIQUE_EDGES_777 24

#define UFBD_NUM_OBLIQUE_EDGES_777 48
#define UFBD_NUM_LEFT_OBLIQUE_EDGES_777 16
#define UFBD_NUM_MIDDLE_OBLIQUE_EDGES_777 16
#define UFBD_NUM_RIGHT_OBLIQUE_EDGES_777 16

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

#endif /* _IDA_SEARCH_777_H */
