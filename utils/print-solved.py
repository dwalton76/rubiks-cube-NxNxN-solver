#!/usr/bin/env python

"""
Print the kociemba string for solved cubes from 2x2x2 up to 15x15x15
"""

for x in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15):
    solved = ''
    for side in ('U', 'R', 'F', 'D', 'L', 'B'):
        solved += side * (x * x)

    print("solved_%d%d%d = '%s'\n" % (x, x, x, solved))
