
#include <stdarg.h>
#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include "ida_search_core.h"

void LOG(const char *fmt, ...) {
    char date[20];
    struct timeval tv;
    va_list args;

    /* print the progname, version, and timestamp */
    gettimeofday(&tv, NULL);
    strftime(date, sizeof(date) / sizeof(*date), "%Y-%m-%dT%H:%M:%S", gmtime(&tv.tv_sec));
    printf("[%s.%03d] ", date, (int)tv.tv_usec / 1000);

    /* printf like normal */
    va_start(args, fmt);
    vprintf(fmt, args);
    va_end(args);
}

unsigned long
hex_to_int(char value)
{
    // This is faster than calling strtoul()
    switch (value) {
    case '0':
        return 0;
    case '1':
        return 1;
    case '2':
        return 2;
    case '3':
        return 3;
    case '4':
        return 4;
    case '5':
        return 5;
    case '6':
        return 6;
    case '7':
        return 7;
    case '8':
        return 8;
    case '9':
        return 9;
    case 'a':
        return 10;
    case 'b':
        return 11;
    case 'c':
        return 12;
    case 'd':
        return 13;
    case 'e':
        return 14;
    case 'f':
        return 15;
    default:
        printf("ERROR: hex_to_int does not support '%c'\n", value);
        exit(1);
    };
}

unsigned long
max (unsigned long a, unsigned long b)
{
    return (a > b ? a : b);
}


// uthash references
// http://troydhanson.github.io/uthash/index.html
// https://cfsa-pmw.warwick.ac.uk/SDF/SDF_C/blob/3cf5bf49856ef9ee4080cf6722cf9058a1e28b01/src/uthash/tests/example.c
void
hash_add (struct key_value_pair **hashtable, char *state_key, unsigned long value)
{
    struct key_value_pair *s;

    s = malloc(sizeof(struct key_value_pair));
    strcpy(s->state, state_key);
    s->value = value;

    HASH_ADD_STR(*hashtable, state, s);
}

struct key_value_pair *
hash_find (struct key_value_pair **hashtable, char *state_key)
{
    struct key_value_pair *s = NULL;
    HASH_FIND_STR(*hashtable, state_key, s);
    return s;
}

void
hash_delete (struct key_value_pair **hashtable, struct key_value_pair *s)
{
    HASH_DEL(*hashtable, s);
    free(s);
}

void
hash_delete_all(struct key_value_pair **hashtable)
{
    struct key_value_pair *s, *tmp;

    HASH_ITER(hh, *hashtable, s, tmp) {
        HASH_DEL(*hashtable, s);
        free(s);
    }
}

unsigned long
hash_count (struct key_value_pair **hashtable)
{
    struct key_value_pair *s;
    unsigned long count = 0;

    for (s = *hashtable; s != NULL; s= (struct key_value_pair*)(s->hh.next)) {
        count++;
    }

    return count;
}


void
hash_print_all (struct key_value_pair **hashtable)
{
    struct key_value_pair *s;

    for(s = *hashtable; s != NULL; s= (struct key_value_pair*)(s->hh.next)) {
        printf("key %s  value %u\n", s->state, s->value);
    }
}

void
print_cube (char *cube, int size)
{
    int squares_per_side = size * size;
    int square_count = squares_per_side * 6;
    int rows = size * 3;
    printf("\n");

    for (int row=1; row <= rows; row++) {

        // U
        if (row <= size) {
            int i = ((row-1) * size) + 1;
            int i_end = i + size - 1;

            for (int z = 0; z < size; z++) {
                printf("  ");
            }

            for ( ; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            printf("\n");

            if (row == size) {
                printf("\n");
            }

        // D
        } else if (row > (size * 2)) {
            int i = (squares_per_side * 5) + 1 + ((row - (size*2) - 1) * size);
            int i_end = i + size - 1;

            if (row == ((size * 2) + 1)) {
                printf("\n");
            }

            for (int z = 0; z < size; z++) {
                printf("  ");
            }

            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }
            printf("\n");

        // L, F, R, B
        } else {

            // L
            int i_start = squares_per_side + 1 + ((row - 1 -size) * size);
            int i_end = i_start + size - 1;
            int i = i_start;
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            // F
            i = i_start + squares_per_side;
            i_end = i + size - 1;
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            // R
            i = i_start + (squares_per_side * 2);
            i_end = i + size - 1;
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            // B
            i = i_start + (squares_per_side * 3);
            i_end = i + size - 1;
            for (; i <= i_end; i++) {
                printf("%c ", cube[i]);
            }

            printf("\n");
        }
    }
    printf("\n");
}

int
strmatch (char *str1, char *str2)
{
    if (strcmp(str1, str2) == 0) {
        return 1;
    }
    return 0;
}
