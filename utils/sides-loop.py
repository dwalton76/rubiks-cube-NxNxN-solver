#!/usr/bin/env python3

foo = [8, 12, 13, 14, 18]
offset = 0
side_name = {
    0 : "Upper",
    1 : "Left",
    2 : "Front",
    3 : "Right",
    4 : "Back",
    5 : "Down",
}

#for side_index in range(1,5):
for side_index in range(6):
    print("        %s, # %s" % (', '.join([str(x + offset) for x in foo]), side_name[side_index]))
    offset += 25
