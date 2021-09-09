data = {
    (0, 0): 0,  # 741 entries
    (1, 1): 1,  # 741 entries
    (1, 4): 4,  # 1 entries
    (1, 10): 11,  # 1 entries
    (2, 2): 2,  # 741 entries
    (2, 3): 3,  # 86 entries
    (2, 4): 4,  # 11 entries
    (2, 5): 5,  # 7 entries
    (2, 6): 6,  # 5 entries
    (2, 7): 7,  # 3 entries
    (2, 8): 9,  # 9 entries
    (2, 9): 10,  # 8 entries
    (2, 10): 10,  # 3 entries
    (2, 11): 13,  # 2 entries
    (3, 1): 3,  # 2 entries
    (3, 2): 3,  # 13 entries
    (3, 3): 3,  # 648 entries
    (3, 4): 4,  # 165 entries
    (3, 5): 5,  # 67 entries
    (3, 6): 6,  # 44 entries
    (3, 7): 7,  # 33 entries
    (3, 8): 8,  # 37 entries
    (3, 9): 10,  # 35 entries
    (3, 10): 12,  # 41 entries
    (3, 11): 13,  # 28 entries
    (3, 12): 13,  # 1 entries
    (4, 1): 4,  # 1 entries
    (4, 2): 4,  # 1 entries
    (4, 3): 4,  # 77 entries
    (4, 4): 4,  # 535 entries
    (4, 5): 5,  # 292 entries
    (4, 6): 6,  # 202 entries
    (4, 7): 7,  # 143 entries
    (4, 8): 9,  # 130 entries
    (4, 9): 10,  # 137 entries
    (4, 10): 12,  # 207 entries
    (4, 11): 13,  # 131 entries
    (4, 12): 14,  # 10 entries
    (5, 2): 5,  # 2 entries
    (5, 3): 6,  # 3 entries
    (5, 4): 5,  # 56 entries
    (5, 5): 5,  # 391 entries
    (5, 6): 6,  # 349 entries
    (5, 7): 7,  # 325 entries
    (5, 8): 8,  # 316 entries
    (5, 9): 10,  # 356 entries
    (5, 10): 12,  # 407 entries
    (5, 11): 13,  # 269 entries
    (5, 12): 14,  # 22 entries
    (6, 4): 7,  # 2 entries
    (6, 5): 6,  # 25 entries
    (6, 6): 6,  # 210 entries
    (6, 7): 7,  # 268 entries
    (6, 8): 8,  # 333 entries
    (6, 9): 10,  # 427 entries
    (6, 10): 12,  # 473 entries
    (6, 11): 13,  # 270 entries
    (6, 12): 14,  # 33 entries
    (7, 5): 7,  # 1 entries
    (7, 6): 7,  # 9 entries
    (7, 7): 7,  # 61 entries
    (7, 8): 8,  # 134 entries
    (7, 9): 10,  # 206 entries
    (7, 10): 12,  # 303 entries
    (7, 11): 13,  # 158 entries
    (7, 12): 13,  # 19 entries
    (8, 7): 8,  # 1 entries
    (8, 8): 8,  # 6 entries
    (8, 9): 11,  # 48 entries
    (8, 10): 12,  # 75 entries
    (8, 11): 13,  # 45 entries
    (8, 12): 13,  # 6 entries
    (9, 10): 12,  # 2 entries
    (9, 11): 13,  # 4 entries
    (9, 12): 13,  # 1 entries
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

    print("    {" + ", ".join(values) + f"}}, // centers cost {x}")

print("};")
