
#ifndef _IDA_SEARCH_555_H
#define _IDA_SEARCH_555_H

#define NUM_CENTERS_555 54
#define NUM_T_CENTERS_555 24
#define NUM_X_CENTERS_555 24

#define NUM_LFRB_T_CENTERS_555 16
#define NUM_LFRB_X_CENTERS_555 16

#define NUM_ULRD_CENTERS_555 36
#define NUM_UFBD_CENTERS_555 36
#define NUM_LFRB_CENTERS_555 36

struct ida_heuristic_result ida_heuristic_UD_centers_555(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **UD_centers_cost_555,
    char *pt_UD_t_centers_cost_only,
    char *pt_UD_x_centers_cost_only,
    cpu_mode_type cpu_mode
);
int ida_search_complete_UD_centers_555 (char *cube);


struct ida_heuristic_result ida_heuristic_LR_centers_555(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **LR_centers_cost_555,
    char *pt_LR_t_centers_cost_only,
    char *pt_LR_x_centers_cost_only
);
int ida_search_complete_LR_centers_555 (char *cube);


struct ida_heuristic_result ida_heuristic_ULFRBD_centers_555(
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **ULFRBD_centers_cost_555,
    char *UL_centers_cost_only_555,
    char *UF_centers_cost_only_555,
    char *LF_centers_cost_only_555
);
int ida_search_complete_ULFRBD_centers_555 (char *cube);

#endif /* _IDA_SEARCH_555_H */
