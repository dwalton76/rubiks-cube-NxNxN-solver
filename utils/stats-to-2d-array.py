data = {
    (0, 0): 0,  # 241 entries
    (0, 1): 1,  # 13 entries
    (0, 2): 2,  # 6 entries
    (0, 3): 3,  # 2 entries
    (1, 0): 1,  # 56 entries
    (1, 1): 1,  # 184 entries
    (1, 2): 2,  # 167 entries
    (1, 3): 3,  # 53 entries
    (1, 4): 4,  # 23 entries
    (1, 5): 5,  # 1 entries
    (1, 6): 6,  # 2 entries
    (2, 0): 2,  # 13 entries
    (2, 1): 1,  # 24 entries
    (2, 2): 2,  # 50 entries
    (2, 3): 3,  # 87 entries
    (2, 4): 4,  # 57 entries
    (2, 5): 5,  # 22 entries
    (2, 6): 7,  # 4 entries
    (3, 0): 3,  # 6 entries
    (3, 1): 3,  # 18 entries
    (3, 2): 4,  # 26 entries
    (3, 3): 3,  # 99 entries
    (3, 4): 4,  # 119 entries
    (3, 5): 6,  # 111 entries
    (3, 6): 7,  # 59 entries
    (3, 7): 8,  # 10 entries
    (4, 1): 3,  # 4 entries
    (4, 2): 4,  # 8 entries
    (4, 3): 5,  # 20 entries
    (4, 4): 4,  # 65 entries
    (4, 5): 6,  # 137 entries
    (4, 6): 8,  # 139 entries
    (4, 7): 8,  # 30 entries
    (5, 1): 4,  # 1 entries
    (5, 2): 5,  # 5 entries
    (5, 3): 5,  # 15 entries
    (5, 4): 6,  # 44 entries
    (5, 5): 7,  # 122 entries
    (5, 6): 8,  # 216 entries
    (5, 7): 9,  # 47 entries
    (6, 1): 6,  # 1 entries
    (6, 2): 6,  # 1 entries
    (6, 3): 7,  # 1 entries
    (6, 4): 8,  # 11 entries
    (6, 5): 8,  # 43 entries
    (6, 6): 9,  # 110 entries
    (6, 7): 9,  # 19 entries
    (7, 2): 7,  # 1 entries
    (7, 3): 8,  # 1 entries
    (7, 4): 9,  # 5 entries
    (7, 5): 8,  # 15 entries
    (7, 6): 9,  # 30 entries
    (7, 7): 9,  # 12 entries
    (8, 6): 10,  # 3 entries
    (8, 7): 10,  # 1 entries
}

max_x = max([x for (x, y) in data.keys()])
max_y = max([y for (x, y) in data.keys()])

print(f"unsigned int foobar[{max_x+1}][{max_y+1}] = {{")
for x in range(max_x + 1):
    values = []

    for y in range(max_y + 1):
        max_xy = max([x, y])
        value = data.get((x, y), max_xy)
        values.append(str(value))

    print("    {" + ", ".join(values) + f"}}, // x unpaired obliques ({x}), y LR centers cost")

print("};")
