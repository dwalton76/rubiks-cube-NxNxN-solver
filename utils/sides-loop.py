#!/usr/bin/env python3

foo = sorted([
11, 17, 18, 19, 23, 24, 25, 26, 27, 31, 32, 33, 39,
])

offset = 0
side_name = {0: "Upper", 1: "Left", 2: "Front", 3: "Right", 4: "Back", 5: "Down"}

# for side_index in range(1,5):
for side_index in range(6):
    print(
        "        %s, # %s"
        % (", ".join([str(x + offset) for x in foo]), side_name[side_index])
    )
    offset += 49
