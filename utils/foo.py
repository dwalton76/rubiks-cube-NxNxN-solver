data = {
    (0, 0): 0,  # 6000 entries
    (0, 4): 4,  # 1 entries
    (1, 1): 1,  # 6033 entries
    (1, 3): 3,  # 93 entries
    (1, 4): 4,  # 9 entries
    (1, 5): 5,  # 4 entries
    (2, 1): 4,  # 1 entries
    (2, 2): 2,  # 6024 entries
    (2, 3): 3,  # 755 entries
    (2, 4): 4,  # 239 entries
    (2, 5): 5,  # 53 entries
    (2, 6): 8,  # 5 entries
    (3, 1): 3,  # 79 entries
    (3, 2): 3,  # 479 entries
    (3, 3): 3,  # 5130 entries
    (3, 4): 4,  # 1765 entries
    (3, 5): 5,  # 521 entries
    (3, 6): 7,  # 77 entries
    (3, 7): 8,  # 7 entries
    (4, 1): 4,  # 13 entries
    (4, 2): 4,  # 178 entries
    (4, 3): 4,  # 1028 entries
    (4, 4): 4,  # 4696 entries
    (4, 5): 6,  # 2860 entries
    (4, 6): 7,  # 588 entries
    (4, 7): 9,  # 93 entries
    (4, 8): 9,  # 1 entries
    (5, 1): 5,  # 9 entries
    (5, 2): 5,  # 54 entries
    (5, 3): 6,  # 383 entries
    (5, 4): 6,  # 2310 entries
    (5, 5): 6,  # 6057 entries
    (5, 6): 8,  # 3249 entries
    (5, 7): 9,  # 536 entries
    (5, 8): 10,  # 3 entries
    (6, 1): 7,  # 1 entries
    (6, 2): 8,  # 9 entries
    (6, 3): 8,  # 79 entries
    (6, 4): 8,  # 647 entries
    (6, 5): 8,  # 3441 entries
    (6, 6): 9,  # 7054 entries
    (6, 7): 10,  # 1829 entries
    (6, 8): 11,  # 5 entries
    (7, 2): 9,  # 3 entries
    (7, 3): 9,  # 14 entries
    (7, 4): 9,  # 149 entries
    (7, 5): 9,  # 1202 entries
    (7, 6): 10,  # 3564 entries
    (7, 7): 10,  # 1225 entries
    (7, 8): 11,  # 9 entries
    (8, 5): 10,  # 20 entries
    (8, 6): 11,  # 92 entries
    (8, 7): 10,  # 38 entries
}

"""
int disp[2][4] = {
    {10, 11, 12, 13},
    {14, 15, 16, 17}
};
"""
print("unsigned int dwalton[9][9] = {")
for x in range(9):
    print("    {" + ", ".join([str(data.get((x, y), max([x, y]))) for y in range(9)]) + "}, // x " + str(x))
print("};")
