
#ifndef _IDA_SEARCH_CORE_H
#define _IDA_SEARCH_CORE_H

#include "uthash.h"

typedef enum {
    CPU_NONE,
    CPU_FAST,
    CPU_NORMAL,
    CPU_SLOW,
} cpu_mode_type;


void LOG(const char *fmt, ...);
unsigned long hex_to_int(char value);
unsigned long max (unsigned long a, unsigned long b);

struct ida_heuristic_result {
    char lt_state[64];
    unsigned int cost_to_goal;
};

// uthash references
// http://troydhanson.github.io/uthash/index.html
// https://cfsa-pmw.warwick.ac.uk/SDF/SDF_C/blob/3cf5bf49856ef9ee4080cf6722cf9058a1e28b01/src/uthash/tests/example.c
//
struct key_value_pair {
    char state[64]; /* we'll use this field as the key */
    unsigned int value;
    UT_hash_handle hh; /* makes this structure hashable */
};


void hash_add (struct key_value_pair **hashtable, char *state_key, unsigned long value);
struct key_value_pair *hash_find (struct key_value_pair **hashtable, char *state_key);
void hash_delete (struct key_value_pair **hashtable, struct key_value_pair *s);
void hash_delete_all(struct key_value_pair **hashtable);
unsigned long hash_count (struct key_value_pair **hashtable);
void hash_print_all (struct key_value_pair **hashtable);
void print_cube (char *cube, int size);
int strmatch (char *str1, char *str2);

#endif /* _IDA_SEARCH_CORE_H */
