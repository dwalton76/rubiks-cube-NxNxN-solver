
#ifndef _IDA_SEARCH_666_H
#define _IDA_SEARCH_666_H

#define NUM_OBLIQUE_EDGES_666 48
#define NUM_LEFT_OBLIQUE_EDGES_666 24
#define NUM_RIGHT_OBLIQUE_EDGES_666 24

unsigned long get_UD_oblique_edges_stage_666(char *cube);
unsigned long ida_heuristic_UD_oblique_edges_stage_666(char *cube);
int ida_search_complete_UD_oblique_edges_stage_666(char *cube);

#endif /* _IDA_SEARCH_666_H */
