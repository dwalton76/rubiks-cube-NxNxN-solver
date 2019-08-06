#!/usr/bin/env python3

'''
foo = [8, 12, 13, 14, 18]
offset = 0
side_name = {0: "Upper", 1: "Left", 2: "Front", 3: "Right", 4: "Back", 5: "Down"}

# for side_index in range(1,5):
for side_index in range(6):
    print(
        "        %s, # %s"
        % (", ".join([str(x + offset) for x in foo]), side_name[side_index])
    )
    offset += 25
'''
offset = 0

for side_index in range(6):
    print(f"""
            eo_state_both_orbits[{0 + offset}] + eo_state_both_orbits[{2 + offset}] + 
            eo_state_both_orbits[{3 + offset}] + eo_state_both_orbits[{4 + offset}] + 
            eo_state_both_orbits[{7 + offset}] + eo_state_both_orbits[{8 + offset}] + 
            eo_state_both_orbits[{9 + offset}] + eo_state_both_orbits[{11 + offset}] + 

""")
    offset += 12
