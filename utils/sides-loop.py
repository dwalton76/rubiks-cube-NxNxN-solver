#!/usr/bin/env python3

foo = sorted([59, 60, 61, 65, 69, 72, 76, 79, 83, 87, 88, 89])
offset = 0
side_name = {
    0 : "Upper",
    1 : "Left",
    2 : "Front",
    3 : "Right",
    4 : "Back",
    5 : "Down",
}

for side_index in range(1,5):
    print("        %s, # %s" % (', '.join([str(x + offset) for x in foo]), side_name[side_index]))
    offset += 49
