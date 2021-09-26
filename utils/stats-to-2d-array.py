data = {
    (2, 6): 7,  # 17 entries
    (3, 6): 7,  # 56 entries
    (3, 7): 8,  # 26 entries
    (3, 8): 9,  # 6 entries
    (4, 3): 5,  # 24 entries
    (4, 4): 5,  # 60 entries
    (4, 5): 6,  # 113 entries
    (4, 6): 7,  # 101 entries
    (4, 7): 8,  # 95 entries
    (4, 8): 9,  # 44 entries
    (4, 9): 10,  # 10 entries
    (5, 3): 6,  # 10 entries
    (5, 4): 6,  # 28 entries
    (5, 5): 6,  # 61 entries
    (5, 6): 7,  # 109 entries
    (5, 7): 8,  # 105 entries
    (5, 8): 9,  # 84 entries
    (5, 9): 11,  # 55 entries
    (5, 10): 12,  # 12 entries
    (6, 4): 7,  # 5 entries
    (6, 5): 8,  # 24 entries
    (6, 6): 8,  # 58 entries
    (6, 7): 8,  # 103 entries
    (6, 10): 12,  # 69 entries
    (6, 11): 14,  # 6 entries
    (7, 5): 9,  # 5 entries
    (7, 6): 9,  # 20 entries
    (7, 7): 10,  # 46 entries
    (7, 8): 10,  # 113 entries
    (7, 9): 11,  # 127 entries
    (7, 10): 13,  # 75 entries
    (7, 11): 13,  # 15 entries
    (8, 7): 11,  # 15 entries
    (8, 8): 12,  # 70 entries
    (8, 9): 12,  # 127 entries
    (8, 10): 13,  # 104 entries
    (8, 11): 14,  # 14 entries
    (9, 7): 14,  # 5 entries
    (9, 8): 12,  # 41 entries
    (9, 9): 13,  # 69 entries
    (9, 10): 14,  # 84 entries
    (10, 9): 14,  # 28 entries
    (10, 10): 15,  # 30 entries
    (11, 10): 15,  # 6 entries
    (12, 9): 15,  # 5 entries
}

max_x = max([x for (x, y) in data.keys()])
max_y = max([y for (x, y) in data.keys()])
# max_x = 16
# max_y = 12

print(f"unsigned int foobar[{max_x+1}][{max_y+1}] = {{")
for x in range(max_x + 1):
    values = []

    for y in range(max_y + 1):
        max_xy = max([x, y])

        if (x, y) in data:
            value = data[(x, y)]
        else:
            lower_x_value = 0
            lower_y_value = 0

            for lower_x in reversed(range(x)):
                if (lower_x, y) in data:
                    lower_x_value = data[(lower_x, y)]
                    break

            for lower_y in reversed(range(y)):
                if (x, lower_y) in data:
                    lower_y_value = data[(x, lower_y)]
                    break

            if lower_x_value and lower_x_value:
                value = max([x, y, min([lower_x_value, lower_y_value])])
            elif lower_x_value:
                value = max([x, y, lower_x_value])
            elif lower_y_value:
                value = max([x, y, lower_y_value])
            else:
                value = max([x, y])

        values.append(str(value))

    print("    {" + ", ".join(values) + f"}}, // x unpaired obliques ({x}), y UD inner x-centers cost")

print("};")
