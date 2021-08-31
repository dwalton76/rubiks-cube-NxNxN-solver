data = {
    (0, 0): 0,  # 10000 entries
    (1, 1): 1,  # 10000 entries
    (1, 2): 5,  # 1 entries
    (1, 3): 3,  # 123 entries
    (1, 4): 4,  # 9 entries
    (1, 5): 5,  # 2 entries
    (2, 2): 2,  # 10019 entries
    (2, 3): 3,  # 1043 entries
    (2, 4): 4,  # 324 entries
    (2, 5): 5,  # 69 entries
    (2, 6): 7,  # 8 entries
    (2, 7): 8,  # 1 entries
    (3, 1): 3,  # 107 entries
    (3, 2): 3,  # 691 entries
    (3, 3): 3,  # 8676 entries
    (3, 4): 4,  # 2507 entries
    (3, 5): 5,  # 738 entries
    (3, 6): 7,  # 127 entries
    (3, 7): 8,  # 9 entries
    (4, 1): 4,  # 17 entries
    (4, 2): 4,  # 249 entries
    (4, 3): 4,  # 1377 entries
    (4, 4): 4,  # 7745 entries
    (4, 5): 5,  # 4104 entries
    (4, 6): 7,  # 1131 entries
    (4, 7): 8,  # 159 entries
    (5, 1): 5,  # 17 entries
    (5, 2): 5,  # 76 entries
    (5, 3): 5,  # 522 entries
    (5, 4): 6,  # 3074 entries
    (5, 5): 6,  # 9211 entries
    (5, 6): 8,  # 5779 entries
    (5, 7): 9,  # 976 entries
    (5, 8): 8,  # 4 entries
    (6, 2): 7,  # 26 entries
    (6, 3): 7,  # 153 entries
    (6, 4): 7,  # 1105 entries
    (6, 5): 8,  # 5688 entries
    (6, 6): 8,  # 11889 entries
    (6, 7): 9,  # 3131 entries
    (6, 8): 10,  # 12 entries
    (7, 2): 9,  # 4 entries
    (7, 3): 8,  # 32 entries
    (7, 4): 9,  # 301 entries
    (7, 5): 9,  # 2052 entries
    (7, 6): 9,  # 5790 entries
    (7, 7): 10,  # 2000 entries
    (7, 8): 11,  # 10 entries
    (8, 4): 9,  # 2 entries
    (8, 5): 9,  # 41 entries
    (8, 6): 10,  # 143 entries
    (8, 7): 10,  # 66 entries
}
"""
int disp[2][4] = {
    {10, 11, 12, 13},
    {14, 15, 16, 17}
};
"""
print("unsigned int dwalton[9][9] = {")
for x in range(9):
    print("    {" + ", ".join([str(data.get((x, y), max([x, y]))) for y in range(9)]) + "}, // t-center cost " + str(x))
print("};")
