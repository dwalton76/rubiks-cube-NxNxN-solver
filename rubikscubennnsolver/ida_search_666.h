
#ifndef _IDA_SEARCH_666_H
#define _IDA_SEARCH_666_H

#define NUM_OBLIQUE_EDGES_666 48
#define NUM_LEFT_OBLIQUE_EDGES_666 24
#define NUM_RIGHT_OBLIQUE_EDGES_666 24

struct ida_heuristic_result ida_heuristic_LR_oblique_edges_stage_666(
    char *cube,
    unsigned int max_cost_to_goal
);
int ida_search_complete_LR_oblique_edges_stage_666(char *cube);

#endif /* _IDA_SEARCH_666_H */
