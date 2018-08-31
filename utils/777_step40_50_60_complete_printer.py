#!/usr/bin/env python3

import sys

# ==============================
# step40 - LR in vertical bars
# ==============================
'''
for column in (58, 59, 60, 61, 62, 156, 157, 158, 159, 160): 
    sys.stdout.write("        ")
    index = column
    for x in range(4):
        sys.stdout.write("cube[{}] == cube[{}] && ".format(index, index + 7))
        index += 7
    print("")
'''

# ==============================
# step40 - LR in vertical bars
# ==============================
for column in (9, 10, 11, 12, 13, 254, 255, 256, 257, 258):
    sys.stdout.write("        ")
    index = column
    for x in range(4):
        sys.stdout.write("cube[{}] == cube[{}] && ".format(index, index + 7))
        index += 7
    print("")
sys.exit(0)

# ======
# step60
# ======
# Upper
centers = list(range(9, 14))
centers.extend(range(16, 21))
centers.extend(range(23, 28))
centers.extend(range(30, 35))
centers.extend(range(37, 42))

for x in centers:
    print("        cube[{}] == 'U' &&".format(x))

# Left
centers = list(range(58, 63))
centers.extend(range(65, 70))
centers.extend(range(72, 77))
centers.extend(range(79, 84))
centers.extend(range(86, 91))

for x in centers:
    print("        cube[{}] == 'L' &&".format(x))

# Front
centers = list(range(107, 112))
centers.extend(range(114, 119))
centers.extend(range(121, 126))
centers.extend(range(128, 133))
centers.extend(range(135, 140))

for x in centers:
    print("        cube[{}] == 'F' &&".format(x))
