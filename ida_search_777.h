
#ifndef _IDA_SEARCH_777_H
#define _IDA_SEARCH_777_H

#define NUM_OBLIQUE_EDGES_777 72
#define NUM_LEFT_OBLIQUE_EDGES_777 24
#define NUM_MIDDLE_OBLIQUE_EDGES_777 24
#define NUM_RIGHT_OBLIQUE_EDGES_777 24

struct ida_heuristic_result ida_heuristic_UD_oblique_edges_stage_777(
    char *cube,
    unsigned int max_cost_to_goal
);
int ida_search_complete_UD_oblique_edges_stage_777(char *cube);

#endif /* _IDA_SEARCH_777_H */
