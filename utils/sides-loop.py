"""
Used to generate misc list of squares for each side
"""
foo = [17, 18, 19, 24, 25, 26, 31, 32, 33, 12, 34, 38, 16]
foo.sort()

offset = 0
side_name = {0: "Upper", 1: "Left", 2: "Front", 3: "Right", 4: "Back", 5: "Down"}

# for side_index in range(1,5):
for side_index in range(6):
    print("        %s, # %s" % (", ".join([str(x + offset) for x in foo]), side_name[side_index]))
    offset += 49
