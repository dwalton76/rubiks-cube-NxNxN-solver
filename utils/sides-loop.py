#!/usr/bin/env python3

foo = (10, 11, 12, 16, 20, 23, 27, 30, 34, 38, 39, 40)
foo = (10, 12, 16, 20, 30, 34, 38, 40,)
offset = 0
side_name = {
    0 : "Upper",
    1 : "Left",
    2 : "Front",
    3 : "Right",
    4 : "Back",
    5 : "Down",
}

for side_index in range(6):
    print("    %s, # %s" % (', '.join([str(x + offset) for x in foo]), side_name[side_index]))
    offset += 49
