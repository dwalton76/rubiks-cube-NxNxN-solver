
#ifndef _IDA_SEARCH_444_H
#define _IDA_SEARCH_444_H

#define NUM_CENTERS_444 24

struct ida_heuristic_result ida_heuristic_centers_444 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **centers_cost_444,
    char *UD_centers_cost_only_444,
    char *LR_centers_cost_only_444,
    char *FB_centers_cost_only_444
);
int ida_search_complete_centers_444  (char *cube);

#endif /* _IDA_SEARCH_444_H */
