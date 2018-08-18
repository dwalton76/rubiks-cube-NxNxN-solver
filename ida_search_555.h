
#ifndef _IDA_SEARCH_555_H
#define _IDA_SEARCH_555_H

#define NUM_CENTERS_555 54
#define NUM_T_CENTERS_555 24
#define NUM_X_CENTERS_555 24

unsigned long get_UD_centers_stage_555(char *cube);

unsigned long ida_heuristic_UD_centers_555(
    char *cube,
    struct key_value_pair **hashtable,
    char *pt_t_centers_cost_only,
    char *pt_x_centers_cost_only,
    int debug
);

int ida_search_complete_UD_centers_555 (char *cube);

#endif /* _IDA_SEARCH_555_H */
