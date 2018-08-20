
#ifndef _IDA_SEARCH_555_H
#define _IDA_SEARCH_555_H

#define NUM_CENTERS_555 54
#define NUM_T_CENTERS_555 24
#define NUM_X_CENTERS_555 24

struct ida_heuristic_result ida_heuristic_UD_centers_555(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **UD_centers_cost_555,
    char *pt_t_centers_cost_only,
    char *pt_x_centers_cost_only
);
int ida_search_complete_UD_centers_555 (char *cube);

struct ida_heuristic_result ida_heuristic_ULFRBD_centers_555(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **ULFRBD_centers_cost_555,
    char *pt_t_centers_cost_only,
    char *pt_x_centers_cost_only
);
int ida_search_complete_ULFRBD_centers_555 (char *cube);

#endif /* _IDA_SEARCH_555_H */
