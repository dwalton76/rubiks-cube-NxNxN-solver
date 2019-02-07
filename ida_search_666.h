
#ifndef _IDA_SEARCH_666_H
#define _IDA_SEARCH_666_H

#define NUM_OBLIQUE_EDGES_666 48
#define NUM_LEFT_OBLIQUE_EDGES_666 24
#define NUM_RIGHT_OBLIQUE_EDGES_666 24

#define NUM_LFRB_INNER_X_CENTERS_666 16
#define NUM_LFRB_OBLIQUE_EDGES_666 32

#define NUM_LR_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666 24
#define NUM_FB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666 24
#define NUM_LFRB_INNER_X_CENTERS_AND_OBLIQUE_EDGES_666 48

struct ida_heuristic_result ida_heuristic_UD_oblique_edges_stage_666(
    char *cube,
    unsigned int max_cost_to_goal
);
int ida_search_complete_UD_oblique_edges_stage_666(char *cube);


struct ida_heuristic_result ida_heuristic_LR_inner_x_centers_and_oblique_edges_stage_666(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **LR_inner_x_centers_and_oblique_edges_666,
    char *LR_inner_x_centers_cost_666,
    char *LR_oblique_edges_cost_666
);
int ida_search_complete_LR_inner_x_centers_and_oblique_edges_stage(char *cube);


struct ida_heuristic_result ida_heuristic_LFRB_inner_x_centers_and_oblique_edges_solve_666(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **LFRB_inner_x_centers_and_oblique_edges_solve_666,
    char *LR_inner_x_centers_and_oblique_edges_solve_666,
    char *FB_inner_x_centers_and_oblique_edges_solve_666
);
int ida_search_complete_LFRB_inner_x_centers_and_oblique_edges_solve(char *cube);

#endif /* _IDA_SEARCH_666_H */
