#include <stdlib.h>
#include <stdio.h>
#include <string.h>

// gcc -o binary-search binary-search.c
// gcc -Ofast -Wno-unused-result -o binary-search binary-search.c

int db_line_count = 0;
int line_width = 0;
int state_width = 0;
char line[100];

int
strmatch (char *str1, char *str2)
{
    if (strcmp(str1, str2) == 0) {
        return 1;
    }
    return 0;
}

int
file_binary_search_guts(FILE *fh, char *state_to_find, int init_left, int init_right, int *line_number, char *value)
{
    int left;
    int right;
    int strcmp_result;
    long mid; // This must be a long so when we do 'mid * line_width' we pass a long to fseek

    left = init_left;

    if (init_right) {
        right = init_right;
    } else {
        right = db_line_count - 1;
    }

    while (left <= right) {
        mid = left + ((right - left) /2);
        fseek(fh, mid * line_width, SEEK_SET);
        fgets(line, 100, fh);
        strcmp_result = strncmp(state_to_find, line, state_width);

        if (strcmp_result > 0) {
            left = mid + 1;
            //printf("%s: line %ld is \"%s\", chop left (%d)\n", state_to_find, mid, line, left);

        } else if (strcmp_result == 0) {
            // Chop the newline
            line[strlen(line)-1] = '\0';
            *line_number = mid;

            strcpy(value, &line[state_width+1]);
            //printf("%s: line %ld is \"%s\", MATCH\n", state_to_find, mid, line);
            return 1;

        } else {
            right = mid - 1;
            //printf("%s: line %ld is \"%s\", chop right (%d)\n", state_to_find, mid, line, right);
        }
    }

    // We did not find the line we were looking for
    *line_number = mid;
    return 0;
}


void
main (int argc, char *argv[])
{
    FILE *fh_states_read = NULL;
    FILE *fh_db_read = NULL;
    FILE *fh_write = NULL;

    char input_filename[100];
    char db_filename[100];
    char output_filename[100];
    int exit_on_first_match = 0;
    memset(input_filename, 0, sizeof(char) * 100);
    memset(db_filename, 0, sizeof(char) * 100);
    memset(output_filename, 0, sizeof(char) * 100);

    for (int i = 1; i < argc; i++) {
        if (strmatch(argv[i], "--input")) {
            i++;
            strcpy(input_filename, argv[i]);

        } else if (strmatch(argv[i], "--output")) {
            i++;
            strcpy(output_filename, argv[i]);

        } else if (strmatch(argv[i], "--db")) {
            i++;
            strcpy(db_filename, argv[i]);

        } else if (strmatch(argv[i], "--line-width")) {
            i++;
            line_width = atoi(argv[i]);

        } else if (strmatch(argv[i], "--state-width")) {
            i++;
            state_width = atoi(argv[i]);

        } else if (strmatch(argv[i], "--line-count")) {
            i++;
            db_line_count = atoi(argv[i]);

        } else if (strmatch(argv[i], "--exit-on-first-match")) {
            exit_on_first_match = 1;

        } else if (strmatch(argv[i], "-h") || strmatch(argv[i], "--help")) {
            printf("binary-search --input STATE_TO_GET_FILENAME --output RESULTS_FILENAME --db DATABASE_FILENAME --line-width NUMBER --state-width NUMBER --line-count NUMBER\n");
            exit(0);

        } else {
            printf("%s is an invalid arg\n", argv[i]);
            exit(1);
        }
    }

    if (!line_width || !state_width || !db_line_count) {
        printf("binary-search --input STATE_TO_GET_FILENAME --output RESULTS_FILENAME --db DATABASE_FILENAME --line-width NUMBER --state-width NUMBER --line-count NUMBER\n");
        exit(1);
    }

    fh_states_read = fopen(input_filename, "r");
    if (fh_states_read == NULL) {
        printf("ERROR: could not open %s\n", input_filename);
        exit(1);
    }

    fh_db_read = fopen(db_filename, "r");
    if (fh_db_read == NULL) {
        printf("ERROR: could not open %s\n", db_filename);
        fclose(fh_states_read);
        exit(1);
    }

    fh_write = fopen(output_filename, "w");
    if (fh_write == NULL) {
        printf("ERROR: could not open %s\n", output_filename);
        fclose(fh_states_read);
        fclose(fh_db_read);
        exit(1);
    }

    // Find out how many states we are looking for
    char state_buffer[100];
    int states_to_find_count = 0;

    while (fgets(state_buffer, 100, fh_states_read) != NULL) {
        states_to_find_count++;
    }
    // reset the filehandle back to the start of the file
    fseek(fh_states_read, 0, SEEK_SET);


    // Create a 2D array of chars to store all of the states
    char states_to_find[states_to_find_count][100];
    int line_number = 0;
    memset(state_buffer, 0, sizeof(char) * 100);
    memset(states_to_find, 0, sizeof(char) * states_to_find_count * 100);

    while (fgets(state_buffer, sizeof(char) * 100, fh_states_read) != NULL) {
        // chop the newline
        state_buffer[strlen(state_buffer)-1] = '\0';

        strcpy(states_to_find[line_number], state_buffer);
        line_number++;
    }

    int min_left = 0;
    int max_right = db_line_count;
    int first_index = 0;
    int last_index = states_to_find_count - 1;
    int found_match = 0;
    char *first_state_to_find;
    char *last_state_to_find;
    char value[100];
    line_number = 0;

    // printf("Need to find %d states\n", states_to_find_count);

    while (states_to_find_count) {
        first_state_to_find = states_to_find[first_index];
        last_state_to_find = states_to_find[last_index];

        /*
        if (exit_on_first_match && found_match) {
            printf("first state %s (%d), last state %s (%d), min_left %d, max_right %d\n",
                first_state_to_find, first_index, last_state_to_find, last_index, min_left, max_right);

            if (states_to_find_count == 1) {
                fprintf(fh_write, "%s:None\n", first_state_to_find);
                break;
            } else {
                fprintf(fh_write, "%s:None\n", first_state_to_find);
                fprintf(fh_write, "%s:None\n", last_state_to_find);
            }
            first_index += 1;
            last_index -= 1;
            states_to_find_count -= 2;
            continue;
        }
         */

        if (states_to_find_count == 1) {
            if (file_binary_search_guts(fh_db_read, first_state_to_find, min_left, max_right, &line_number, value)) {
                fprintf(fh_write, "%s:%s\n", first_state_to_find, value);
                found_match = 1;
            } else {
                fprintf(fh_write, "%s:None\n", first_state_to_find);
            }
            break;
        }

        // We sorted states_to_find so find the first state and its line_number (or the line_number
        // where it would be if it were there) and remember that line_number as the furthest
        // left we ever need to look in the file when looking for other states.
        if (file_binary_search_guts(fh_db_read, first_state_to_find, min_left, max_right, &line_number, value)) {
            fprintf(fh_write, "%s:%s\n", first_state_to_find, value);
            min_left = line_number;
            found_match = 1;

        } else {
            fprintf(fh_write, "%s:None\n", first_state_to_find);

            if (line_number) {
                min_left = line_number - 1;
            } else {
                min_left = 0;
            }
        }

        // Now do the same with the last state to determine the furthest right we
        // ever need look when looking for other states
        if (file_binary_search_guts(fh_db_read, last_state_to_find, min_left, max_right, &line_number, value)) {
            fprintf(fh_write, "%s:%s\n", last_state_to_find, value);
            max_right = line_number;
            found_match = 1;

        } else {
            fprintf(fh_write, "%s:None\n", last_state_to_find);

            if (db_line_count < line_number + 1) {
                max_right = db_line_count;
            } else {
                max_right = line_number + 1;
            }
        }

        // printf("first state %s, last state %s, min_left %d, max_right %d\n", first_state_to_find, last_state_to_find, min_left, max_right);
        first_index += 1;
        last_index -= 1;
        states_to_find_count -= 2;
    }
}
