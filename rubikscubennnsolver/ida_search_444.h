
#ifndef _IDA_SEARCH_444_H
#define _IDA_SEARCH_444_H

#define BUCKETSIZE_EDGES_444 239500847
#define BUCKETSIZE_CENTERS_444 58831

#define NUM_EDGES_444 24
#define NUM_CENTERS_444 24
#define NUM_EDGES_AND_CENTERS_444 48

struct wings_for_edges_recolor_pattern_444 {
    char edge_index[1];
    unsigned int square_index;
    unsigned int partner_index;
};

struct wings_for_edges_recolor_pattern_444* init_wings_for_edges_recolor_pattern_444 ();
int strmatch (char *str1, char *str2);

struct ida_heuristic_result ida_heuristic_reduce_333_444 (
    char *cube,
    unsigned int max_cost_to_goal,
    struct key_value_pair **reduce_333_444,
    char *reduce_333_edges_only,
    char *reduce_333_centers_only,
    struct wings_for_edges_recolor_pattern_444 *wings_for_recolor
);
int ida_search_complete_reduce_333_444 (char *cube);

#endif /* _IDA_SEARCH_444_H */
