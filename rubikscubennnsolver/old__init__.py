
"""
Solve any size rubiks cube:
- For 2x2x2 and 3x3x3 just solve it
- For 4x4x4 and larger, reduce to 3x3x3 and then solve

This is a work in progress
"""

from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver.RubiksSide import Side, SolveError
import logging
import math
import os
import random
import re
import subprocess
import sys

log = logging.getLogger(__name__)

opposite_side = {
    'U': 'D',
    'L': 'R',
    'F': 'B',
    'R': 'L',
    'B': 'F',
    'D': 'U'
}

babelfish = {
    ('B', 'D'): {'B': 'U', 'D': 'F', 'F': 'D', 'L': 'R', 'R': 'L', 'U': 'B', 'x': 'x'},
    ('B', 'L'): {'B': 'R', 'D': 'F', 'F': 'L', 'L': 'D', 'R': 'U', 'U': 'B', 'x': 'x'},
    ('B', 'R'): {'B': 'L', 'D': 'F', 'F': 'R', 'L': 'U', 'R': 'D', 'U': 'B', 'x': 'x'},
    ('B', 'U'): {'B': 'D', 'D': 'F', 'F': 'U', 'L': 'L', 'R': 'R', 'U': 'B', 'x': 'x'},
    ('D', 'B'): {'B': 'F', 'D': 'U', 'F': 'B', 'L': 'L', 'R': 'R', 'U': 'D', 'x': 'x'},
    ('D', 'F'): {'B': 'B', 'D': 'U', 'F': 'F', 'L': 'R', 'R': 'L', 'U': 'D', 'x': 'x'},
    ('D', 'L'): {'B': 'R', 'D': 'U', 'F': 'L', 'L': 'F', 'R': 'B', 'U': 'D', 'x': 'x'},
    ('D', 'R'): {'B': 'L', 'D': 'U', 'F': 'R', 'L': 'B', 'R': 'F', 'U': 'D', 'x': 'x'},
    ('F', 'D'): {'B': 'U', 'D': 'B', 'F': 'D', 'L': 'L', 'R': 'R', 'U': 'F', 'x': 'x'},
    ('F', 'L'): {'B': 'R', 'D': 'B', 'F': 'L', 'L': 'U', 'R': 'D', 'U': 'F', 'x': 'x'},
    ('F', 'R'): {'B': 'L', 'D': 'B', 'F': 'R', 'L': 'D', 'R': 'U', 'U': 'F', 'x': 'x'},
    ('F', 'U'): {'B': 'D', 'D': 'B', 'F': 'U', 'L': 'R', 'R': 'L', 'U': 'F', 'x': 'x'},
    ('L', 'B'): {'B': 'F', 'D': 'R', 'F': 'B', 'L': 'U', 'R': 'D', 'U': 'L', 'x': 'x'},
    ('L', 'D'): {'B': 'U', 'D': 'R', 'F': 'D', 'L': 'B', 'R': 'F', 'U': 'L', 'x': 'x'},
    ('L', 'F'): {'B': 'B', 'D': 'R', 'F': 'F', 'L': 'D', 'R': 'U', 'U': 'L', 'x': 'x'},
    ('L', 'U'): {'B': 'D', 'D': 'R', 'F': 'U', 'L': 'F', 'R': 'B', 'U': 'L', 'x': 'x'},
    ('R', 'B'): {'B': 'F', 'D': 'L', 'F': 'B', 'L': 'D', 'R': 'U', 'U': 'R', 'x': 'x'},
    ('R', 'D'): {'B': 'U', 'D': 'L', 'F': 'D', 'L': 'F', 'R': 'B', 'U': 'R', 'x': 'x'},
    ('R', 'F'): {'B': 'B', 'D': 'L', 'F': 'F', 'L': 'U', 'R': 'D', 'U': 'R', 'x': 'x'},
    ('R', 'U'): {'B': 'D', 'D': 'L', 'F': 'U', 'L': 'B', 'R': 'F', 'U': 'R', 'x': 'x'},
    ('U', 'B'): {'B': 'F', 'D': 'D', 'F': 'B', 'L': 'R', 'R': 'L', 'U': 'U', 'x': 'x'},
    ('U', 'F'): {'B': 'B', 'D': 'D', 'F': 'F', 'L': 'L', 'R': 'R', 'U': 'U', 'x': 'x'},
    ('U', 'L'): {'B': 'R', 'D': 'D', 'F': 'L', 'L': 'B', 'R': 'F', 'U': 'U', 'x': 'x'},
    ('U', 'R'): {'B': 'L', 'D': 'D', 'F': 'R', 'L': 'F', 'R': 'B', 'U': 'U', 'x': 'x'}
}

all_moves_4x4x4 = {
    "U" :  ["L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "U'":  ["L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "U2":  ["L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2U":  ["L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2U'": ["L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2U2": ["L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],

    "L" :  ["U","U'","U2","2U","2U'","2U2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "L'":  ["U","U'","U2","2U","2U'","2U2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "L2":  ["U","U'","U2","2U","2U'","2U2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2L":  ["U","U'","U2","2U","2U'","2U2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2L'": ["U","U'","U2","2U","2U'","2U2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2L2": ["U","U'","U2","2U","2U'","2U2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],

    "F" :  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "F'":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "F2":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2F":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2F'": ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2F2": ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],

    "R" :  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "R'":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "R2":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2R":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2R'": ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],
    "2R2": ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","B","B'","B2","2B","2B'","2B2","D","D'","D2","2D","2D'","2D2"],

    "B" :  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","D","D'","D2","2D","2D'","2D2"],
    "B'":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","D","D'","D2","2D","2D'","2D2"],
    "B2":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","D","D'","D2","2D","2D'","2D2"],
    "2B":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","D","D'","D2","2D","2D'","2D2"],
    "2B'": ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","D","D'","D2","2D","2D'","2D2"],
    "2B2": ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","D","D'","D2","2D","2D'","2D2"],

    "D" :  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2"],
    "D'":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2"],
    "D2":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2"],
    "2D":  ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2"],
    "2D'": ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2"],
    "2D2": ["U","U'","U2","2U","2U'","2U2","L","L'","L2","2L","2L'","2L2","F","F'","F2","2F","2F'","2F2","R","R'","R2","2R","2R'","2R2","B","B'","B2","2B","2B'","2B2"],
}

all_moves_5x5x5 = all_moves_4x4x4

all_moves_3x3x3 = {
    "U" :  ["L","L'","L2","F","F'","F2","R","R'","R2","B","B'","B2","D","D'","D2"],
    "U'":  ["L","L'","L2","F","F'","F2","R","R'","R2","B","B'","B2","D","D'","D2"],
    "U2":  ["L","L'","L2","F","F'","F2","R","R'","R2","B","B'","B2","D","D'","D2"],

    "L" :  ["U","U'","U2","F","F'","F2","R","R'","R2","B","B'","B2","D","D'","D2"],
    "L'":  ["U","U'","U2","F","F'","F2","R","R'","R2","B","B'","B2","D","D'","D2"],
    "L2":  ["U","U'","U2","F","F'","F2","R","R'","R2","B","B'","B2","D","D'","D2"],

    "F" :  ["U","U'","U2","L","L'","L2","R","R'","R2","B","B'","B2","D","D'","D2"],
    "F'":  ["U","U'","U2","L","L'","L2","R","R'","R2","B","B'","B2","D","D'","D2"],
    "F2":  ["U","U'","U2","L","L'","L2","R","R'","R2","B","B'","B2","D","D'","D2"],

    "R" :  ["U","U'","U2","L","L'","L2","F","F'","F2","B","B'","B2","D","D'","D2"],
    "R'":  ["U","U'","U2","L","L'","L2","F","F'","F2","B","B'","B2","D","D'","D2"],
    "R2":  ["U","U'","U2","L","L'","L2","F","F'","F2","B","B'","B2","D","D'","D2"],

    "B" :  ["U","U'","U2","L","L'","L2","F","F'","F2","R","R'","R2","D","D'","D2"],
    "B'":  ["U","U'","U2","L","L'","L2","F","F'","F2","R","R'","R2","D","D'","D2"],
    "B2":  ["U","U'","U2","L","L'","L2","F","F'","F2","R","R'","R2","D","D'","D2"],

    "D" :  ["U","U'","U2","L","L'","L2","F","F'","F2","R","R'","R2","B","B'","B2"],
    "D'":  ["U","U'","U2","L","L'","L2","F","F'","F2","R","R'","R2","B","B'","B2"],
    "D2":  ["U","U'","U2","L","L'","L2","F","F'","F2","R","R'","R2","B","B'","B2"],
}


# Move a wing to (44, 57)
lookup_table_444_last_two_edges_place_F_east = {
    (2, 67)  : "B' R2",
    (3, 66)  : "U R'",
    (5, 18)  : "U2 R'",
    (9, 19)  : "U B' R2",
    (14, 34) : "U' R'",
    (15, 35) : "U F' U' F",
    (8, 51)  : "F' U F",
    (12, 50) : "R'",
    (21, 72) : "B' U R'",
    (25, 76) : "B2 R2",
    (30, 89) : "F D F'",
    (31, 85) : "D2 R",
    (40, 53) : "R U' B' R2",
    (44, 57) : "",
    (46, 82) : "D F D' F'",
    (47, 83) : "D R",
    (56, 69) : "R2",
    (60, 73) : "B U R'",
    (62, 88) : "F D' F'",
    (63, 92) : "R",
    (78, 95) : "B R2",
    (79, 94) : "D' R",
}

# Move a wing to (40, 53)
lookup_table_444_sister_wing_to_F_east = {
    (2, 67)  : "U R'",
    (3, 66)  : "B' R2",
    (5, 18)  : "U B' R2",
    (9, 19)  : "U2 R'",
    (14, 34) : "L F L'",
    (15, 35) : "U' R'",
    (8, 51)  : "R'",
    (12, 50) : "F' U F",
    (21, 72) : "B2 R2",
    (25, 76) : "B D' R",
    (30, 89) : "D2 R",
    (31, 85) : "F D F'",
    (40, 53) : "",
    (44, 57) : "F D F' R",
    (46, 82) : "D R",
    (47, 83) : "D2 B R2",
    (56, 69) : "B U R'",
    (60, 73) : "R2",
    (62, 88) : "R",
    (63, 92) : "F D' F'",
    (78, 95) : "D' R",
    (79, 94) : "B R2",
}

# Move a wing to (5, 18)
lookup_table_444_sister_wing_to_U_west = {
    (2, 67)  : "L' B L",
    (3, 66)  : "U'",
    (5, 18)  : "",
    (9, 19)  : "L' B' L U'",
    (14, 34) : "U",
    (15, 35) : "F' L' F",
    (8, 51)  : "U' B F L F'",
    (12, 50) : "U2",
    (21, 72) : "B' U'",
    (25, 76) : "L U L' U'",
    (30, 89) : "L B' L' U'",
    (31, 85) : "D' B2 U'",
    (37, 24) : None,
    #(40, 53) : "",
    #(44, 57) : "",
    (46, 82) : "F L' F'",
    (47, 83) : "D2 B2 U'",
    (56, 69) : "R' U2 R",
    (60, 73) : "B U'",
    (62, 88) : "R' B R U'",
    (63, 92) : "D B2 U'",
    (78, 95) : "B2 U'",
    (79, 94) : "B2 U'",
}

lookup_table_444_sister_wing_to_R_east = {
    (2, 67)  : "B'", # U-north
    (3, 66)  : "R' U R", # U-north
    (5, 18)  : "L' B2 L", # U-west
    (9, 19)  : "U B'", # U-west
    (14, 34) : "R' U' R", # U-south
    (15, 35) : "U2 B'", # U-south
    (8, 51)  : "U' B'", # U-east
    (12, 50) : "F R F'", # U-east
    (21, 72) : "B R D' R'", # L-west
    (25, 76) : "B2", # L-west
    (37, 24) : None, # L-east
    #(41, 28) : "", # L-east
    #(40, 53) : "", # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "D", # R-east
    (60, 73) : "B R' U R", # R-east
    (46, 82) : "D2 B", # D-north
    (47, 83) : "R D R'", # D-north
    (30, 89) : "D' B", # D-west
    (31, 85) : "L B2 L'", # D-west
    (78, 95) : "B", # D-south
    (79, 94) : "R D' R'", # D-south
    (62, 88) : "D B", # D-east
    (63, 92) : "D B", # D-east
}

lookup_table_444_sister_wing_to_B_east = {
    (2, 67)  : "L U' L'", # U-north
    (3, 66)  : "R B R'", # U-north
    (5, 18)  : "B' U B", # U-west
    (9, 19)  : "F L' F'", # U-west
    (14, 34) : "B' U2 B", # U-south
    (15, 35) : "L U L'", # U-south
    (8, 51)  : "L U2 L'", # U-east
    (12, 50) : "B' U' B", # U-east
    (21, 72) : "D", # L-west
    (25, 76) : "B L' D B' L", # L-west
    (37, 24) : None, # L-east
    #(41, 28) : "", # L-east
    #(40, 53) : "", # R-west
    (44, 57) : None, # R-west
    #(56, 69) : "", # R-east
    #(60, 73) : "", # R-east
    (46, 82) : "L' D' L", # D-north
    (47, 83) : "B D2 B'", # D-north
    (30, 89) : "F L F'", # D-west
    (31, 85) : "B D' B'", # D-west
    (78, 95) : "L' D L", # D-south
    (79, 94) : "R B' R'", # D-south
    (62, 88) : "L' D2 L", # D-east
    (63, 92) : "B D B'", # D-east
}

lookup_table_444_sister_wing_to_F_west = {
    (2, 67)  : "F U2 F'", # U-north
    (3, 66)  : "L' U' L", # U-north
    (5, 18)  : "L F L' F'", # U-west
    (9, 19)  : "F U' F'", # U-west
    #(14, 34) : "", # U-south
    #(15, 35) : "", # U-south
    (8, 51)  : "F U F'", # U-east
    (12, 50) : "L' U2 L", # U-east
    (21, 72) : "B L D B' L'", # L-west
    (25, 76) : "B L2 B' L2", # L-west
    (37, 24) : "D", # L-east
    (41, 28) : "F L' U F' L", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "L2 B2 L2 B2", # R-east
    (60, 73) : "B L' U' B' L", # R-east
    #(46, 82) : "", # D-north
    #(47, 83) : "", # D-north
    (30, 89) : "F' D F", # D-west
    (31, 85) : "D L D' L'", # D-west
    #(78, 95) : "", # D-south
    #(79, 94) : "", # D-south
    (62, 88) : "F' D' F", # D-east
    (63, 92) : "L D2 L'", # D-east
}

lookup_table_444_sister_wing_to_L_west = {
    (2, 67)  : "L U' L'", # U-north
    (3, 66)  : "B L B' L'", # U-north
    (5, 18)  : "B' U B", # U-west
    (9, 19)  : "L' B L B'", # U-west
    (14, 34) : "B' U2 B", # U-south
    (15, 35) : "L U L'", # U-south
    (8, 51)  : "L U2 L'", # U-east
    (12, 50) : "B' U' B", # U-east
    (21, 72) : "D", # L-west
    (25, 76) : "B L' D B' L", # L-west
    #(37, 24) : "", # L-east
    #(41, 28) : "", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "B L U' B' L'", # R-east
    (60, 73) : "B2 L B2 L'", # R-east
    (46, 82) : "L' D' L", # D-north
    (47, 83) : "B D2 B'", # D-north
    (30, 89) : "D L' D' L", # D-west
    (31, 85) : "B D' B'", # D-west
    (78, 95) : "L' D L", # D-south
    (79, 94) : "B' L B L'", # D-south
    (62, 88) : "L' D2 L", # D-east
    (63, 92) : "B D B'", # D-east
}

lookup_table_444_sister_wing_to_B_west = {
    (2, 67)  : "B' R B R'", # U-north
    (3, 66)  : "R' U R", # U-north
    (5, 18)  : "R' U2 R", # U-west
    (9, 19)  : "B U B'", # U-west
    (14, 34) : "R' U' R", # U-south
    (15, 35) : "B U2 B'", # U-south
    (8, 51)  : "B U' B'", # U-east
    (12, 50) : "R B R' B'", # U-east
    #(21, 72) : "", # L-west
    #(25, 76) : "", # L-west
    #(37, 24) : "", # L-east
    #(41, 28) : "", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "D", # R-east
    (60, 73) : "B R' U B' R", # R-east
    (46, 82) : "B' D2 B", # D-north
    (47, 83) : "R D R'", # D-north
    (30, 89) : "B' D' B", # D-west
    (31, 85) : "R D2 R'", # D-west
    (78, 95) : "B R B' R'", # D-south
    (79, 94) : "R D' R'", # D-south
    (62, 88) : "B' D B", # D-east
    (63, 92) : "D R D' R'", # D-east
}

class StuckInALoop(Exception):
    pass

class ImplementThis(Exception):
    pass

def get_cube_layout(size):
    """
    Example: size is 3, return the following string:

              01 02 03
              04 05 06
              07 08 09

    10 11 12  19 20 21  28 29 30  37 38 39
    13 14 15  22 23 24  31 32 33  40 41 42
    16 17 18  25 26 27  34 35 36  43 44 45

              46 47 48
              49 50 51
              52 53 54
    """
    result = []

    squares = (size * size) * 6
    square_index = 1

    if squares >= 1000:
        digits_size = 4
        digits_format = "%04d "
    elif squares >= 100:
        digits_size = 3
        digits_format = "%03d "
    else:
        digits_size = 2
        digits_format = "%02d "

    indent = ((digits_size * size) + size + 1) * ' '
    rows = size * 3

    for row in range(1, rows + 1):
        line = []

        if row <= size:
            line.append(indent)
            for col in range(1, size + 1):
                line.append(digits_format % square_index)
                square_index += 1

        elif row > rows - size:
            line.append(indent)
            for col in range(1, size + 1):
                line.append(digits_format % square_index)
                square_index += 1

        else:
            init_square_index = square_index
            last_col = size * 4
            for col in range(1, last_col + 1):
                line.append(digits_format % square_index)

                if col == last_col:
                    square_index += 1
                elif col % size == 0:
                    square_index += (size * size) - size + 1
                    line.append(' ')
                else:
                    square_index += 1

            if row % size:
                square_index = init_square_index + size

        result.append(''.join(line))

        if row == size or row == rows - size:
            result.append('')
    return '\n'.join(result)


def get_babelfish_states(cube_state):
    results = [cube_state, ]

    for (upper_front_key, translator) in babelfish.items():
        results.append(''.join([translator[char] for char in cube_state]))

    return list(reversed(sorted(results)))


def get_first_babelfish_state(cube_state):
    """
    TODO document this
    """
    return get_babelfish_states(cube_state)[0]


def rotate_2d_list(squares_list):
    """
    http://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python
    """
    return [x for x in zip(*squares_list[::-1])]


def rotate_clockwise(squares_list):
    return rotate_2d_list(squares_list)


def rotate_counter_clockwise(squares_list):
    squares_list = rotate_2d_list(squares_list)
    squares_list = rotate_2d_list(squares_list)
    squares_list = rotate_2d_list(squares_list)
    return squares_list


def compress_2d_list(squares_list):
    """
    Convert 2d list to a 1d list
    """
    return [col for row in squares_list for col in row]


def find_index_for_value(list_foo, target, min_index):
    for (index, value) in enumerate(list_foo):
        if value == target and index >= min_index:
            return index
    raise SolveError("Did not find %s in list %s" % (target, pformat(list_foo)))


def get_swap_count(listA, listB, debug):
    """
    How many swaps do we have to make in listB for it to match listA
    Example:

        A = [1, 2, 3, 0, 4]
        B = [3, 4, 1, 0, 2]

    would require 2 swaps
    """
    A_length = len(listA)
    B_length = len(listB)
    swaps = 0
    index = 0

    if A_length != B_length:
        log.info("listA %s" % ' '.join(listA))
        log.info("listB %s" % ' '.join(listB))
        assert False, "listA (len %d) and listB (len %d) must be the same length" % (A_length, B_length)

    if debug:
        log.info("INIT")
        log.info("listA: %s" % ' '.join(listA))
        log.info("listB: %s" % ' '.join(listB))
        log.info("")

    while listA != listB:
        if listA[index] != listB[index]:
            listA_value = listA[index]
            listB_index_with_A_value = find_index_for_value(listB, listA_value, index+1)
            tmp = listB[index]
            listB[index] = listB[listB_index_with_A_value]
            listB[listB_index_with_A_value] = tmp
            swaps += 1

            if debug:
                log.info("index %d, swaps %d" % (index, swaps))
                log.info("listA: %s" % ' '.join(listA))
                log.info("listB: %s" % ' '.join(listB))
                log.info("")
        index += 1

    if debug:
        log.info("swaps: %d" % swaps)
        log.info("")
    return swaps


def apply_rotations(step, rotations):
    """
    Apply the "rotations" to step and return the step. This is used by
    compress_solution() to remove all of the whole cube rotations from
    the solution.
    """

    if step in ('CENTERS_SOLVED', 'EDGES_GROUPED'):
        return step

    for rotation in rotations:
        # remove the number at the start of the rotation...for a 4x4x4 cube
        # there might be a 4U rotation (to rotate about the y-axis) but we
        # don't need to keep the '4' part.
        rotation = rotation[1:]

        if rotation == "U" or rotation == "D'":
            if "U" in step:
                pass
            elif "L" in step:
                step = step.replace("L", "F")
            elif "F" in step:
                step = step.replace("F", "R")
            elif "R" in step:
                step = step.replace("R", "B")
            elif "B" in step:
                step = step.replace("B", "L")
            elif "D" in step:
                pass

        elif rotation == "U'" or rotation == "D":
            if "U" in step:
                pass
            elif "L" in step:
                step = step.replace("L", "B")
            elif "F" in step:
                step = step.replace("F", "L")
            elif "R" in step:
                step = step.replace("R", "F")
            elif "B" in step:
                step = step.replace("B", "R")
            elif "D" in step:
                pass

        elif rotation == "F" or rotation == "B'":
            if "U" in step:
                step = step.replace("U", "L")
            elif "L" in step:
                step = step.replace("L", "D")
            elif "F" in step:
                pass
            elif "R" in step:
                step = step.replace("R", "U")
            elif "B" in step:
                pass
            elif "D" in step:
                step = step.replace("D", "R")

        elif rotation == "F'" or rotation == "B":
            if "U" in step:
                step = step.replace("U", "R")
            elif "L" in step:
                step = step.replace("L", "U")
            elif "F" in step:
                pass
            elif "R" in step:
                step = step.replace("R", "D")
            elif "B" in step:
                pass
            elif "D" in step:
                step = step.replace("D", "L")

        elif rotation == "R" or rotation == "L'":
            if "U" in step:
                step = step.replace("U", "F")
            elif "L" in step:
                pass
            elif "F" in step:
                step = step.replace("F", "D")
            elif "R" in step:
                pass
            elif "B" in step:
                step = step.replace("B", "U")
            elif "D" in step:
                step = step.replace("D", "B")

        elif rotation == "R'" or rotation == "L":
            if "U" in step:
                step = step.replace("U", "B")
            elif "L" in step:
                pass
            elif "F" in step:
                step = step.replace("F", "U")
            elif "R" in step:
                pass
            elif "B" in step:
                step = step.replace("B", "D")
            elif "D" in step:
                step = step.replace("D", "F")

        else:
            raise Exception("%s is an invalid rotation" % rotation)

    return step


class RubiksCube(object):

    def __init__(self, kociemba_string):
        init_state = ['dummy', ]
        init_state.extend(list(kociemba_string))
        self.squares_per_side = int((len(init_state) - 1)/6)
        self.size = math.sqrt(self.squares_per_side)
        assert str(self.size).endswith('.0'), "Cube has %d squares per side which is not possible" % self.squares_per_side
        self.size = int(self.size)
        self.solution = []
        self.steps_to_rotate_cube = 0
        self.steps_to_solve_centers = 0
        self.steps_to_group_edges = 0
        self.steps_to_solve_3x3x3 = 0

        # kociemba_string is in URFDLB order so split this apart and re-arrange it to
        # be ULFRBD so that is is sequential with the normal square numbering scheme
        foo = []
        foo.extend(init_state[1:self.squares_per_side + 1])                                       # U
        foo.extend(init_state[(self.squares_per_side * 4) + 1 : (self.squares_per_side * 5) + 1]) # L
        foo.extend(init_state[(self.squares_per_side * 2) + 1 : (self.squares_per_side * 3) + 1]) # F
        foo.extend(init_state[(self.squares_per_side * 1) + 1 : (self.squares_per_side * 2) + 1]) # R
        foo.extend(init_state[(self.squares_per_side * 5) + 1 : (self.squares_per_side * 6) + 1]) # B
        foo.extend(init_state[(self.squares_per_side * 3) + 1 : (self.squares_per_side * 4) + 1]) # D

        self.state = {}
        for (square_index, side_name) in enumerate(foo):
            self.state[square_index+1] = side_name

        self.sides = OrderedDict()
        self.sides['U'] = Side(self, 'U')
        self.sides['L'] = Side(self, 'L')
        self.sides['F'] = Side(self, 'F')
        self.sides['R'] = Side(self, 'R')
        self.sides['B'] = Side(self, 'B')
        self.sides['D'] = Side(self, 'D')
        self.sideU = self.sides['U']
        self.sideL = self.sides['L']
        self.sideF = self.sides['F']
        self.sideR = self.sides['R']
        self.sideB = self.sides['B']
        self.sideD = self.sides['D']
        self.all_edge_positions = []

        # U and B
        for (pos1, pos2) in zip(self.sideU.edge_north_pos, reversed(self.sideB.edge_north_pos)):
            self.all_edge_positions.append((pos1, pos2))

        # U and L
        for (pos1, pos2) in zip(self.sideU.edge_west_pos, self.sideL.edge_north_pos):
            self.all_edge_positions.append((pos1, pos2))

        # U and F
        for (pos1, pos2) in zip(self.sideU.edge_south_pos, self.sideF.edge_north_pos):
            self.all_edge_positions.append((pos1, pos2))

        # U and R
        for (pos1, pos2) in zip(self.sideU.edge_east_pos, reversed(self.sideR.edge_north_pos)):
            self.all_edge_positions.append((pos1, pos2))

        # F and L
        for (pos1, pos2) in zip(self.sideF.edge_west_pos, self.sideL.edge_east_pos):
            self.all_edge_positions.append((pos1, pos2))

        # F and R
        for (pos1, pos2) in zip(self.sideF.edge_east_pos, self.sideR.edge_west_pos):
            self.all_edge_positions.append((pos1, pos2))

        # F and D
        for (pos1, pos2) in zip(self.sideF.edge_south_pos, self.sideD.edge_north_pos):
            self.all_edge_positions.append((pos1, pos2))

        # L and B
        for (pos1, pos2) in zip(self.sideL.edge_west_pos, self.sideB.edge_east_pos):
            self.all_edge_positions.append((pos1, pos2))

        # L and D
        for (pos1, pos2) in zip(self.sideL.edge_south_pos, reversed(self.sideD.edge_west_pos)):
            self.all_edge_positions.append((pos1, pos2))

        # R and D
        for (pos1, pos2) in zip(self.sideR.edge_south_pos, self.sideD.edge_east_pos):
            self.all_edge_positions.append((pos1, pos2))

        # R and B
        for (pos1, pos2) in zip(self.sideR.edge_east_pos, self.sideB.edge_west_pos):
            self.all_edge_positions.append((pos1, pos2))

        # B and D
        for (pos1, pos2) in zip(reversed(self.sideB.edge_south_pos), self.sideD.edge_south_pos):
            self.all_edge_positions.append((pos1, pos2))

        for side in self.sides.values():
            side.calculate_wing_partners()

    def is_even(self):
        if self.size % 2 == 0:
            return True
        return False

    def is_odd(self):
        if self.size % 2 == 0:
            return False
        return True

    def is_solved(self):
        """
        Return True if the cube is solved
        """
        for side in self.sides.values():
            if not side.is_solved():
                return False
        return True

    def rotate(self, action):
        """
        self.state is a dictionary where the key is the square_index and the
        value is that square side name (U, F, etc)
        """
        self.solution.append(action)
        result = copy(self.state)
        # log.info("move %s" % action)

        if action[-1] in ("'", "`"):
            reverse = True
            action = action[0:-1]
        else:
            reverse = False

        if action[0].isdigit():
            rows_to_rotate = int(action[0])
            action = action[1:]
        else:
            rows_to_rotate = 1

        if action[-1].isdigit():
            quarter_turns = int(action[-1])
            action = action[0:-1]
        else:
            quarter_turns = 1

        side_name = action

        if side_name == 'x':
            side_name = 'R'
            rows_to_rotate = self.size
        elif side_name == 'y':
            side_name = 'U'
            rows_to_rotate = self.size
        elif side_name == 'z':
            side_name = 'F'
            rows_to_rotate = self.size

        if side_name in ('CENTERS_SOLVED', 'EDGES_GROUPED'):
            return

        side = self.sides[side_name]
        min_pos = side.min_pos
        max_pos = side.max_pos

        # rotate the face...this is the same for all sides
        for turn in range(quarter_turns):
            face = side.get_face_as_2d_list()

            if reverse:
                face = rotate_counter_clockwise(face)
            else:
                face = rotate_clockwise(face)

            face = compress_2d_list(face)

            for (index, value) in enumerate(face):
                square_index = min_pos + index
                result[square_index] = value
            self.state = copy(result)

        # If we are rotating the entire self.state we must rotate the opposite face as well
        if rows_to_rotate == self.size:

            if side_name == 'U':
                opp_side_name = 'D'
            elif side_name == 'D':
                opp_side_name = 'U'
            elif side_name == 'L':
                opp_side_name = 'R'
            elif side_name == 'R':
                opp_side_name = 'L'
            elif side_name == 'B':
                opp_side_name = 'F'
            elif side_name == 'F':
                opp_side_name = 'B'
            else:
                raise SolveError("")

            opp_side = self.sides[opp_side_name]
            opp_min_pos = opp_side.min_pos
            face = opp_side.get_face_as_2d_list()

            # This is reversed from what we did with the original layer
            if reverse:
                face = rotate_clockwise(face)
            else:
                face = rotate_counter_clockwise(face)

            face = compress_2d_list(face)

            for (index, value) in enumerate(face):
                square_index = opp_min_pos + index
                result[square_index] = value
            self.state = copy(result)

        if side_name == "U":

            for turn in range(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in range(rows_to_rotate):
                    left_first_square = self.squares_per_side + 1 + (row * self.size)
                    left_last_square = left_first_square + self.size - 1

                    front_first_square = (self.squares_per_side * 2) + 1 + (row * self.size)
                    front_last_square = front_first_square + self.size - 1

                    right_first_square = (self.squares_per_side * 3) + 1 + (row * self.size)
                    right_last_square = right_first_square + self.size - 1

                    back_first_square = (self.squares_per_side * 4) + 1 + (row * self.size)
                    back_last_square = back_first_square + self.size - 1

                    #log.info("left first %d, last %d" % (left_first_square, left_last_square))
                    #log.info("front first %d, last %d" % (front_first_square, front_last_square))
                    #log.info("right first %d, last %d" % (right_first_square, right_last_square))
                    #log.info("back first %d, last %d" % (back_first_square, back_last_square))

                    if reverse:
                        for square_index in range(left_first_square, left_last_square + 1):
                            result[square_index] = self.state[square_index + (3 * self.squares_per_side)]

                        for square_index in range(front_first_square, front_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                        for square_index in range(right_first_square, right_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                        for square_index in range(back_first_square, back_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                    else:
                        for square_index in range(left_first_square, left_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in range(front_first_square, front_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in range(right_first_square, right_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in range(back_first_square, back_last_square + 1):
                            result[square_index] = self.state[square_index - (3 * self.squares_per_side)]

                self.state = copy(result)

        elif side_name == "L":

            for turn in range(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in range(rows_to_rotate):

                    top_first_square = 1 + row
                    top_last_square = top_first_square + ((self.size - 1) * self.size)

                    front_first_square = (self.squares_per_side * 2) + 1 + row
                    front_last_square = front_first_square + ((self.size - 1) * self.size)

                    down_first_square = (self.squares_per_side * 5) + 1 + row
                    down_last_square = down_first_square + ((self.size - 1) * self.size)

                    back_first_square = (self.squares_per_side * 4) + self.size - row
                    back_last_square = back_first_square + ((self.size - 1) * self.size)

                    #log.info("top first %d, last %d" % (top_first_square, top_last_square))
                    #log.info("front first %d, last %d" % (front_first_square, front_last_square))
                    #log.info("down first %d, last %d" % (down_first_square, down_last_square))
                    #log.info("back first %d, last %d" % (back_first_square, back_last_square))

                    top_squares = []
                    for square_index in range(top_first_square, top_last_square + 1, self.size):
                        top_squares.append(self.state[square_index])

                    front_squares = []
                    for square_index in range(front_first_square, front_last_square + 1, self.size):
                        front_squares.append(self.state[square_index])

                    down_squares = []
                    for square_index in range(down_first_square, down_last_square + 1, self.size):
                        down_squares.append(self.state[square_index])

                    back_squares = []
                    for square_index in range(back_first_square, back_last_square + 1, self.size):
                        back_squares.append(self.state[square_index])

                    if reverse:
                        for (index, square_index) in enumerate(range(top_first_square, top_last_square + 1, self.size)):
                            result[square_index] = front_squares[index]

                        for (index, square_index) in enumerate(range(front_first_square, front_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                        back_squares = list(reversed(back_squares))
                        for (index, square_index) in enumerate(range(down_first_square, down_last_square + 1, self.size)):
                            result[square_index] = back_squares[index]

                        top_squares = list(reversed(top_squares))
                        for (index, square_index) in enumerate(range(back_first_square, back_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]
                    else:
                        back_squares = list(reversed(back_squares))
                        for (index, square_index) in enumerate(range(top_first_square, top_last_square + 1, self.size)):
                            result[square_index] = back_squares[index]

                        for (index, square_index) in enumerate(range(front_first_square, front_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                        for (index, square_index) in enumerate(range(down_first_square, down_last_square + 1, self.size)):
                            result[square_index] = front_squares[index]

                        down_squares = list(reversed(down_squares))
                        for (index, square_index) in enumerate(range(back_first_square, back_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                self.state = copy(result)

        elif side_name == "F":

            for turn in range(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in range(rows_to_rotate):
                    top_first_square = (self.squares_per_side - self.size) + 1 - (row * self.size)
                    top_last_square = top_first_square + self.size - 1

                    left_first_square = self.squares_per_side + self.size - row
                    left_last_square = left_first_square + ((self.size - 1) * self.size)

                    down_first_square = (self.squares_per_side * 5) + 1 + (row * self.size)
                    down_last_square = down_first_square + self.size - 1

                    right_first_square = (self.squares_per_side * 3) + 1 + row
                    right_last_square = right_first_square + ((self.size - 1) * self.size)

                    #log.info("top first %d, last %d" % (top_first_square, top_last_square))
                    #log.info("left first %d, last %d" % (left_first_square, left_last_square))
                    #log.info("down first %d, last %d" % (down_first_square, down_last_square))
                    #log.info("right first %d, last %d" % (right_first_square, right_last_square))

                    top_squares = []
                    for square_index in range(top_first_square, top_last_square + 1):
                        top_squares.append(self.state[square_index])

                    left_squares = []
                    for square_index in range(left_first_square, left_last_square + 1, self.size):
                        left_squares.append(self.state[square_index])

                    down_squares = []
                    for square_index in range(down_first_square, down_last_square + 1):
                        down_squares.append(self.state[square_index])

                    right_squares = []
                    for square_index in range(right_first_square, right_last_square + 1, self.size):
                        right_squares.append(self.state[square_index])

                    if reverse:
                        for (index, square_index) in enumerate(range(top_first_square, top_last_square + 1)):
                            result[square_index] = right_squares[index]

                        top_squares = list(reversed(top_squares))
                        for (index, square_index) in enumerate(range(left_first_square, left_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                        for (index, square_index) in enumerate(range(down_first_square, down_last_square + 1)):
                            result[square_index] = left_squares[index]

                        down_squares = list(reversed(down_squares))
                        for (index, square_index) in enumerate(range(right_first_square, right_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                    else:
                        left_squares = list(reversed(left_squares))
                        for (index, square_index) in enumerate(range(top_first_square, top_last_square + 1)):
                            result[square_index] = left_squares[index]

                        for (index, square_index) in enumerate(range(left_first_square, left_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                        right_squares = list(reversed(right_squares))
                        for (index, square_index) in enumerate(range(down_first_square, down_last_square + 1)):
                            result[square_index] = right_squares[index]

                        for (index, square_index) in enumerate(range(right_first_square, right_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                self.state = copy(result)

        elif side_name == "R":

            for turn in range(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in range(rows_to_rotate):

                    top_first_square = self.size - row
                    top_last_square = self.squares_per_side

                    front_first_square = (self.squares_per_side * 2) + self.size - row
                    front_last_square = front_first_square + ((self.size - 1) * self.size)

                    down_first_square = (self.squares_per_side * 5) + self.size - row
                    down_last_square = down_first_square + ((self.size - 1) * self.size)

                    back_first_square = (self.squares_per_side * 4) + 1 + row
                    back_last_square = back_first_square + ((self.size - 1) * self.size)

                    #log.info("top first %d, last %d" % (top_first_square, top_last_square))
                    #log.info("front first %d, last %d" % (front_first_square, front_last_square))
                    #log.info("down first %d, last %d" % (down_first_square, down_last_square))
                    #log.info("back first %d, last %d" % (back_first_square, back_last_square))

                    top_squares = []
                    for square_index in range(top_first_square, top_last_square + 1, self.size):
                        top_squares.append(self.state[square_index])

                    front_squares = []
                    for square_index in range(front_first_square, front_last_square + 1, self.size):
                        front_squares.append(self.state[square_index])

                    down_squares = []
                    for square_index in range(down_first_square, down_last_square + 1, self.size):
                        down_squares.append(self.state[square_index])

                    back_squares = []
                    for square_index in range(back_first_square, back_last_square + 1, self.size):
                        back_squares.append(self.state[square_index])

                    if reverse:
                        back_squares = list(reversed(back_squares))
                        for (index, square_index) in enumerate(range(top_first_square, top_last_square + 1, self.size)):
                            result[square_index] = back_squares[index]

                        for (index, square_index) in enumerate(range(front_first_square, front_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                        for (index, square_index) in enumerate(range(down_first_square, down_last_square + 1, self.size)):
                            result[square_index] = front_squares[index]

                        down_squares = list(reversed(down_squares))
                        for (index, square_index) in enumerate(range(back_first_square, back_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                    else:
                        for (index, square_index) in enumerate(range(top_first_square, top_last_square + 1, self.size)):
                            result[square_index] = front_squares[index]

                        for (index, square_index) in enumerate(range(front_first_square, front_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                        back_squares = list(reversed(back_squares))
                        for (index, square_index) in enumerate(range(down_first_square, down_last_square + 1, self.size)):
                            result[square_index] = back_squares[index]

                        top_squares = list(reversed(top_squares))
                        for (index, square_index) in enumerate(range(back_first_square, back_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                self.state = copy(result)

        elif side_name == "B":

            for turn in range(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in range(rows_to_rotate):
                    top_first_square = 1 + (row * self.size)
                    top_last_square = top_first_square + self.size - 1

                    left_first_square = self.squares_per_side + 1 + row
                    left_last_square = left_first_square + ((self.size - 1) * self.size)

                    down_first_square = (self.squares_per_side * 6)  - self.size + 1 - (row * self.size)
                    down_last_square = down_first_square + self.size - 1

                    right_first_square = (self.squares_per_side * 3) + self.size - row
                    right_last_square = right_first_square + ((self.size - 1) * self.size)

                    #log.info("top first %d, last %d" % (top_first_square, top_last_square))
                    #log.info("left first %d, last %d" % (left_first_square, left_last_square))
                    #log.info("down first %d, last %d" % (down_first_square, down_last_square))
                    #log.info("right first %d, last %d" % (right_first_square, right_last_square))

                    top_squares = []
                    for square_index in range(top_first_square, top_last_square + 1):
                        top_squares.append(self.state[square_index])

                    left_squares = []
                    for square_index in range(left_first_square, left_last_square + 1, self.size):
                        left_squares.append(self.state[square_index])

                    down_squares = []
                    for square_index in range(down_first_square, down_last_square + 1):
                        down_squares.append(self.state[square_index])

                    right_squares = []
                    for square_index in range(right_first_square, right_last_square + 1, self.size):
                        right_squares.append(self.state[square_index])

                    if reverse:
                        left_squares = list(reversed(left_squares))
                        for (index, square_index) in enumerate(range(top_first_square, top_last_square + 1)):
                            result[square_index] = left_squares[index]

                        for (index, square_index) in enumerate(range(left_first_square, left_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                        right_squares = list(reversed(right_squares))
                        for (index, square_index) in enumerate(range(down_first_square, down_last_square + 1)):
                            result[square_index] = right_squares[index]

                        for (index, square_index) in enumerate(range(right_first_square, right_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                    else:
                        for (index, square_index) in enumerate(range(top_first_square, top_last_square + 1)):
                            result[square_index] = right_squares[index]

                        top_squares = list(reversed(top_squares))
                        for (index, square_index) in enumerate(range(left_first_square, left_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                        for (index, square_index) in enumerate(range(down_first_square, down_last_square + 1)):
                            result[square_index] = left_squares[index]

                        down_squares = list(reversed(down_squares))
                        for (index, square_index) in enumerate(range(right_first_square, right_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                self.state = copy(result)

        elif side_name == "D":

            for turn in range(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in range(rows_to_rotate):
                    left_first_square = (self.squares_per_side * 2) - self.size + 1 - (row * self.size)
                    left_last_square = left_first_square + self.size - 1

                    front_first_square = (self.squares_per_side * 3) - self.size + 1 - (row * self.size)
                    front_last_square = front_first_square + self.size - 1

                    right_first_square = (self.squares_per_side * 4) - self.size + 1 - (row * self.size)
                    right_last_square = right_first_square + self.size - 1

                    back_first_square = (self.squares_per_side * 5) - self.size + 1 - (row * self.size)
                    back_last_square = back_first_square + self.size - 1

                    #log.info("left first %d, last %d" % (left_first_square, left_last_square))
                    #log.info("front first %d, last %d" % (front_first_square, front_last_square))
                    #log.info("right first %d, last %d" % (right_first_square, right_last_square))
                    #log.info("back first %d, last %d" % (back_first_square, back_last_square))

                    if reverse:
                        for square_index in range(left_first_square, left_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in range(front_first_square, front_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in range(right_first_square, right_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in range(back_first_square, back_last_square + 1):
                            result[square_index] = self.state[square_index - (3 * self.squares_per_side)]

                    else:
                        for square_index in range(left_first_square, left_last_square + 1):
                            result[square_index] = self.state[square_index + (3 * self.squares_per_side)]

                        for square_index in range(front_first_square, front_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                        for square_index in range(right_first_square, right_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                        for square_index in range(back_first_square, back_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                self.state = copy(result)

        else:
            raise Exception("Unsupported action %s" % action)

    def print_cube_layout(self):
        print(get_cube_layout(self.size) + '\n')

    def print_cube(self):
        color_codes = {
          'U': 97, # Wh
          'L': 92, # Gr
          'F': 91, # Rd
          'R': 94, # Bu
          'B': 90, # Or
          'D': 93, # Ye
        }

        side_names = ('U', 'L', 'F', 'R', 'B', 'D')
        side_name_index = 0
        rows = []
        row_index = 0
        printing_numbers = False

        for x in range(self.size * 3):
            rows.append([])

        for square_index in sorted(self.state.keys()):
            side_name = side_names[side_name_index]
            square_state = self.state[square_index]
            color = color_codes.get(square_state, None)

            # end of the row
            if color:
                if square_index % self.size == 0:
                    rows[row_index].append("\033[%dm%s\033[0m " % (color, square_state))
                    row_index += 1
                else:
                    rows[row_index].append("\033[%dm%s\033[0m" % (color, square_state))
            else:
                printing_numbers = True
                if square_index % self.size == 0:

                    if square_state.endswith('x'):
                        rows[row_index].append("%s" % square_state)
                    else:
                        rows[row_index].append("%02d" % int(square_state))

                    row_index += 1
                else:
                    if square_state.endswith('x'):
                        rows[row_index].append("%s" % square_state)
                    else:
                        rows[row_index].append("%02d" % int(square_state))

            # end of the side
            if square_index % self.squares_per_side == 0:
                if side_name in ('L', 'F', 'R'):
                    row_index = self.size
                side_name_index += 1

        for (row_index, row) in enumerate(rows):
            if row_index < self.size or row_index >= (self.size * 2):
                if printing_numbers:
                    sys.stdout.write(' ' * (self.size * 3))
                else:
                    sys.stdout.write(' ' * (self.size + self.size + 1))

            print(' '.join(row))
            if ((row_index+1) % self.size) == 0:
                print('')
        print('')

    def print_case_statement_C(self, case):
        """
        This is called via --rotate-printer, it is used to print the
        case statements used by lookup-table-builder.c
        """
        print("    } else if (strcmp(move, \"%s\") == 0) {" % case)
        for (key, value) in self.state.items():
            if str(key) != str(value):
                print("        cube[%s] = cube_tmp[%s];" % (key, value))
        print("")

        #print("    case %s:" % case)
        #for (key, value) in self.state.items():
        #    if str(key) != str(value):
        #        print("        cube[%s] = cube_tmp[%s];" % (key, value))
        #print("        break;")

    def print_case_statement_python(self, case):
        """
        This is called via --rotate-printer, it is used to print the
        if/elif statements used by rotate.py
        """
        print('    elif action == "%s":' % case)
        for (key, value) in self.state.items():
            if str(key) != str(value):
                print("        cube[%s] = cube_tmp[%s]" % (key, value))

    def randomize(self):
        """
        Perform a bunch of random moves to scramble a cube. This was used to generate test cases.
        """

        if self.is_even():
            max_rows = int(self.size/2)
        else:
            max_rows = int((self.size - 1)/2)

        sides = ['U', 'L', 'F', 'R', 'B', 'D']
        count = ((self.size * self.size) * 6) * 3

        for x in range(count):
            rows = random.randint(1, max_rows)
            side_index = random.randint(0, 5)
            side = sides[side_index]
            quarter_turns = random.randint(1, 2)
            clockwise = random.randint(0, 1)

            if rows > 1:
                move = "%d%s" % (rows, side)
            else:
                move = side

            if quarter_turns > 1:
                move += str(quarter_turns)

            if not clockwise:
                move += "'"

            self.rotate(move)

    def get_side_for_index(self, square_index):
        """
        Return the Side object that owns square_index
        """
        for side in self.sides.values():
            if square_index >= side.min_pos and square_index <= side.max_pos:
                return side
        raise SolveError("We should not be here, square_index %d" % square_index)

    def get_non_paired_wings(self):
        return (self.sideU.non_paired_wings(True, True, True, True) +
                self.sideF.non_paired_wings(False, True, False, True) +
                self.sideB.non_paired_wings(False, True, False, True) +
                self.sideD.non_paired_wings(True, True, True, True))

    def get_non_paired_wings_count(self):
        return len(self.get_non_paired_wings())

    def get_non_paired_edges(self):
        # north, west, south, east
        return (self.sideU.non_paired_edges(True, True, True, True) +
                self.sideF.non_paired_edges(False, True, False, True) +
                self.sideB.non_paired_edges(False, True, False, True) +
                self.sideD.non_paired_edges(True, True, True, True))

    def get_non_paired_edges_count(self):
        non_paired_edges = self.get_non_paired_edges()
        result = len(non_paired_edges)

        if result > 12:
            raise SolveError("Found %d unpaired edges but a cube only has 12 edges" % result)

        return result

    def find_edge(self, color1, color2):
        positions = []
        for (pos1, pos2) in self.all_edge_positions:
            if ((self.state[pos1] == color1 and self.state[pos2] == color2) or
                (self.state[pos1] == color2 and self.state[pos2] == color1)):
                positions.append((pos1, pos2))

        return positions

    def get_wings(self, pos1, remove_if_in_same_edge=False):
        pos1_side = self.get_side_for_index(pos1)
        pos2 = pos1_side.get_wing_partner(pos1)
        pos2_side = self.get_side_for_index(pos2)
        color1 = self.state[pos1]
        color2 = self.state[pos2]

        wings = self.find_edge(color1, color2)
        wings_to_remove = []
        #log.info("get_wings (%d, %d), pos1_side %s, remove_if_in_same_edge %s, %s" %
        #    (pos1, pos2, pos1_side, remove_if_in_same_edge, pformat(wings)))

        for (wing_pos1, wing_pos2) in wings:

            # Remove the one we started with
            if (wing_pos1, wing_pos2) == (pos1, pos2):
                wings_to_remove.append((wing_pos1, wing_pos2))

            elif (wing_pos1, wing_pos2) == (pos2, pos1):
                wings_to_remove.append((wing_pos1, wing_pos2))

            # Some callers do not want wings that are part of the same edge as pos1
            elif remove_if_in_same_edge:
                wing_pos1_side = self.get_side_for_index(wing_pos1)
                wing_pos2_side = self.get_side_for_index(wing_pos2)
                #log.info("wing_pos1 %s, wing_pos1_side %s, wing_pos2 %s, wing_pos2_side %s" %
                #    (wing_pos1, wing_pos1_side, wing_pos2, wing_pos2_side))

                if ((wing_pos1_side == pos1_side and wing_pos2_side == pos2_side) or
                    (wing_pos2_side == pos1_side and wing_pos1_side == pos2_side)):
                    wings_to_remove.append((wing_pos1, wing_pos2))

        #log.info("get_wings wings_to_remove %s" % pformat(wings_to_remove))
        for x in wings_to_remove:
            wings.remove(x)

        #log.info("get_wings returning %s\n" % pformat(wings))
        return wings

    def get_wings_on_edge(self, pos1, side1_name, side2_name):
        wings = self.get_wings(pos1)
        wings_to_keep = []
        #log.info("get_wings_on_edge for pos1 %d, side1 %s, side2 %s, init_wings %s" % (pos1, side1_name, side2_name, pformat(wings)))

        for (wing_pos1, wing_pos2) in wings:
            wing_pos1_side = self.get_side_for_index(wing_pos1)
            wing_pos2_side = self.get_side_for_index(wing_pos2)

            #log.info("get_wings_on_edge wing_pos1 %d side %s, wing_pos2 %d side %s\n" %
            #    (wing_pos1, wing_pos1_side, wing_pos2, wing_pos2_side))

            if ((wing_pos1_side.name == side1_name and wing_pos2_side.name == side2_name) or
                (wing_pos2_side.name == side1_name and wing_pos1_side.name == side2_name)):
                wings_to_keep.append((wing_pos1, wing_pos2))

        #log.info("get_wings_on_edge keeping %s\n" % pformat(wings_to_keep))
        return wings_to_keep

    def rotate_edge_to_F_west(self, edge):
        side = self.get_side_for_index(edge[0])
        direction = side.has_wing(edge)

        if side == self.sideU:
            if direction == 'north':
                self.rotate_y_reverse()
                self.rotate_x_reverse()

            elif direction == 'west':
                self.rotate_x_reverse()

            elif direction == 'south':
                self.rotate_x_reverse()
                self.rotate_z()

            elif direction == 'east':
                self.rotate_y()
                self.rotate_y()
                self.rotate_x_reverse()

        elif side == self.sideL:

            if direction == 'north':
                self.rotate_x_reverse()

            elif direction == 'west':
                self.rotate_x_reverse()
                self.rotate_x_reverse()

            elif direction == 'south':
                self.rotate_x()

            elif direction == 'east':
                pass

        elif side == self.sideF:
            if direction == 'north':
                self.rotate_z_reverse()

            elif direction == 'west':
                pass

            elif direction == 'south':
                self.rotate_z()

            elif direction == 'east':
                self.rotate_z_reverse()
                self.rotate_z_reverse()

        elif side == self.sideR:

            if direction == 'north':
                self.rotate_y()
                self.rotate_y()
                self.rotate_x_reverse()

            elif direction == 'west':
                self.rotate_y()

            elif direction == 'south':
                self.rotate_x()
                self.rotate_y()

            elif direction == 'east':
                self.rotate_y()
                self.rotate_y()

        elif side == self.sideB:

            if direction == 'north':
                self.rotate_y_reverse()
                self.rotate_x_reverse()

            elif direction == 'west':
                self.rotate_y()
                self.rotate_y()

            elif direction == 'south':
                self.rotate_z()
                self.rotate_x()
                self.rotate_x()

            elif direction == 'east':
                self.rotate_y_reverse()

        elif side == self.sideD:

            if direction == 'north':
                self.rotate_z()

            elif direction == 'west':
                self.rotate_x()

            elif direction == 'south':
                self.rotate_y_reverse()
                self.rotate_x()

            elif direction == 'east':
                self.rotate_y()
                self.rotate_y()
                self.rotate_x()

        # TODO reomve this once we've double checked everything
        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired, started on side %s, direction %s" % (side, direction))

    def move_wing_to_U_north(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            pass

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("U2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U", ):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("U", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("L", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L2", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B'", ):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("U'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R2", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R", "U'"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("F2", "U2"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("B2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("R2", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("L2", "U"):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to U north" % str(wing))

    def move_wing_to_U_west(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("U'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("U", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            pass

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            pass

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("L2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("L", ):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("U2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R2", "U2"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R", "U2"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D'", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D2", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("L2", ):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to U west" % str(wing))

    def move_wing_to_U_south(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("U2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            pass

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U'", ):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("U'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("L2", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("F", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("L", "U'"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("U", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R2", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R'", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R", "U"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("F2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D2", "F2"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D'", "F2"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D", "F2"):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to U south" % str(wing))

    def move_wing_to_U_east(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("U", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("U'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            pass

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U2", ):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("U2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("L2", "U2"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("F", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("L", "U2"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            pass

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R", ):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D'", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("R2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D2", "R2"):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to U east" % str(wing))

    def move_wing_to_L_west(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("B", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("U2", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U'", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U", "B"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("L'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("L", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            pass

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R", "B2"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R'", "B2"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R2", "B2"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D'", "L"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D", "L"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D2", "L"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("L", ):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to L west" % str(wing))

    def move_wing_to_L_east(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("U'", "L"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            self.rotate("F'")

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U2", "L"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            self.rotate("L")

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            self.rotate("L")

        elif wing_pos1 in self.sideL.edge_south_pos:
            self.rotate("L'")

        elif wing_pos1 in self.sideL.edge_east_pos:
            pass

        elif wing_pos1 in self.sideL.edge_west_pos:
            self.rotate("L2")

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            self.rotate("F'")

        elif wing_pos1 in self.sideF.edge_south_pos:
            self.rotate("F")

        elif wing_pos1 in self.sideF.edge_east_pos:
            self.rotate("F2")

        elif wing_pos1 in self.sideF.edge_west_pos:
            pass

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("U2", "L"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D2", "L'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B2", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            self.rotate("F2")

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("U'", "L"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("B'", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            self.rotate("L2")

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B2", "L2"):
                self.rotate(step)

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            self.rotate("F")

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D", "L'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D2", "L'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            self.rotate("L'")

        else:
            raise ImplementThis("implement wing %s to L east" % str(wing))

    def move_wing_to_F_west(self, wing):
        self.move_wing_to_L_east(wing)

    def move_wing_to_R_west(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("U", "R'"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("U'", "R'"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("R'",):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U2", "R'"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("U2", "R'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("D2", "R"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("F2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B2", "R2"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("F", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("D", "R"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            pass

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F2", ):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R2",):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            pass

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("U", "R'"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("D'", "R"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B2", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("R2",):
                self.rotate(step)

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D", "R"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D'", "R"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("R", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D2", "R"):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to R west" % str(wing))

    def move_wing_to_R_east(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("B'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("U'", "R"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("R", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U2", "R"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
           for step in ("L'", "B2"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
           for step in ("L", "B2"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("F2", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B2", ):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            pass

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R2", ):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D", "R'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D'", "R'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("R'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D2", "R'"):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to R east" % str(wing))

    def move_wing_to_F_east(self, wing):
        self.move_wing_to_R_west(wing)

    def move_wing_to_D_north(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("B2", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("F2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("R2", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("L2", "D"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("L2", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("D", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("L'", "D"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R2", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R'", "D'"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            pass

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D", ):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to D north" % str(wing))

    def move_wing_to_D_west(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("U'", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("U", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U2", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("L2", ):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("L2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            pass

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("L'", ):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R2", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R'", "D2"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            pass

        else:
            raise ImplementThis("implement wing %s to D west" % str(wing))

    def move_wing_to_D_south(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("B2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("F2", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("R2", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("L2", "D'"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("L2", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("L'", "D'"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R2", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R'", "D"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            pass

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D'", ):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to D south" % str(wing))

    def move_wing_to_D_east(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("U", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("U'", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("R2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U2", "R2"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("L2", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("D2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("L'", "D2"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            raise ImplementThis("F north")

        elif wing_pos1 in self.sideF.edge_south_pos:
            raise ImplementThis("F south")

        elif wing_pos1 in self.sideF.edge_east_pos:
            raise ImplementThis("F east")

        elif wing_pos1 in self.sideF.edge_west_pos:
            raise ImplementThis("F west")

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            pass

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R'", ):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            raise ImplementThis("B north")

        elif wing_pos1 in self.sideB.edge_south_pos:
            raise ImplementThis("B south")

        elif wing_pos1 in self.sideB.edge_east_pos:
            raise ImplementThis("B east")

        elif wing_pos1 in self.sideB.edge_west_pos:
            raise ImplementThis("B west")

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            pass

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D2", ):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to D east" % str(wing))

    def make_B_north_have_unpaired_edge(self):

        if not self.sideB.north_edge_paired():
            return

        # D until we get a non-paired edge to B
        while self.sideB.all_edges_paired():
            self.rotate_D()

        # B until a non-paired edge is in on the North side of B
        while self.sideB.north_edge_paired():
            self.rotate_B()

    def make_B_north_have_unpaired_wing(self):

        if not self.sideB.north_wing_paired():
            return

        # D until we get a non-paired wing to B
        if self.sideB.all_wings_paired():
            while self.sideB.south_wing_paired():
                self.rotate_D()

        # B until a non-paired wing is in on the North side of B
        while self.sideB.north_wing_paired():
            self.rotate_B()

    def find_wing(self, wing_to_find):

        U_edge = self.sideU.has_wing(wing_to_find)

        if U_edge:
            return (self.sideU, U_edge)


        B_edge = self.sideB.has_wing(wing_to_find)

        if B_edge:
            return (self.sideB, B_edge)


        D_edge = self.sideD.has_wing(wing_to_find)

        if D_edge:
            return (self.sideD, D_edge)


        F_edge = self.sideF.has_wing(wing_to_find)

        if F_edge:
            return (self.sideF, F_edge)

        raise Exception("We should not be here")


    def make_U_west_have_unpaired_edge(self):
        if not self.sideU.west_edge_paired():
            return

        if self.sideU.all_edges_paired():
            self.make_B_north_have_unpaired_edge()

        # U until a non-paired edge is in on the West side of U
        while self.sideU.west_edge_paired():
            self.rotate_U()

    def make_U_south_have_unpaired_edge(self):

        if not self.sideU.south_edge_paired():
            return

        if self.sideU.all_edges_paired():
            self.make_B_north_have_unpaired_edge()

        # U until a non-paired edge is in on the West side of U
        count = 0
        while self.sideU.south_edge_paired():
            self.rotate_U()
            count += 1
            if count > 4:
                raise StuckInALoop("")

    def make_U_west_have_unpaired_wing(self):
        if not self.sideU.west_wing_paired():
            return

        if self.sideU.all_wings_paired():
            self.make_B_north_have_unpaired_wing()

        # U until a non-paired edge is in on the West side of U
        while self.sideU.west_wing_paired():
            self.rotate_U()

    def rotate_B(self):
        self.rotate("B")

    def rotate_U(self):
        self.rotate("U")

    def rotate_F(self):
        self.rotate("F")

    def rotate_F_reverse(self):
        self.rotate("F'")

    def rotate_D(self):
        self.rotate("D")

    def rotate_x(self):
        self.rotate("%dR" % self.size)

    def rotate_x_reverse(self):
        self.rotate("%dR'" % self.size)

    def rotate_y(self):
        self.rotate("%dU" % self.size)

    def rotate_y_reverse(self):
        self.rotate("%dU'" % self.size)

    def rotate_z(self):
        self.rotate("%dF" % self.size)

    def rotate_z_reverse(self):
        self.rotate("%dF'" % self.size)

    def prep_U_for_center_corner_placement(self, target):
        """
        We need the bottom left corner to be unsolved
        """
        center_corner_pos = self.sideU.center_corner_pos

        if self.state[center_corner_pos[2]] != target:
            return
        elif self.state[center_corner_pos[0]] != target:
            self.rotate("U'")
        elif self.state[center_corner_pos[1]] != target:
            self.rotate("U2")
        elif self.state[center_corner_pos[3]] != target:
            self.rotate('U')
        else:
            raise SolveError("")

    def get_center_corner_state(self):
        return ''.join([self.state[square_index] for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD) for square_index in side.center_corner_pos])

    def get_center_corner_state_all(self):
        """
        TODO document this
        """

        baseline = self.get_center_corner_state()
        results = [baseline, ]
        for translator in babelfish.values():
            results.append(''.join([translator[char] for char in baseline]))
        return results

    def get_center_UF_state(self, target):
        u_centers = []
        for square_index in self.sideU.center_corner_pos:
            if self.state[square_index] == target:
                u_centers.append('1')
            else:
                u_centers.append('0')
        u_centers = ''.join(u_centers)

        f_centers = []
        for square_index in self.sideF.center_corner_pos:
            if self.state[square_index] == target:
                f_centers.append('1')
            else:
                f_centers.append('0')
        f_centers = ''.join(f_centers)

        return (u_centers, f_centers)

    def get_centers_solved_count(self):
        count = 6

        for side in self.sides.values():
            prev_pos = None
            for pos in side.center_pos:
                if prev_pos is not None:
                    if self.state[prev_pos] != self.state[pos]:
                        count -= 1
                        break
                prev_pos = pos
        return count

    def centers_solved(self):
        for side in self.sides.values():
            prev_pos = None
            for pos in side.center_pos:
                if prev_pos is not None:
                    if self.state[prev_pos] != self.state[pos]:
                        return False
                prev_pos = pos
        return True

    def reverse_steps(self, steps):
        results = []
        for step in reversed(steps):
            if step.endswith("2"):
                pass
            elif step.endswith("'"):
                step = step[0:-1]
            else:
                step += "'"
            results.append(step)
        return results

    def prep_D_for_center_corner_placement(self, target, debug=False):
        """
        Put a target square in the top right corner. If there are two paired
        then put the pair on the right side.
        """

        top_row = len([square_index for square_index in self.sideD.center_corner_pos[0:2] if self.state[square_index] == target])
        bottom_row = len([square_index for square_index in self.sideD.center_corner_pos[2:4] if self.state[square_index] == target])
        left_col = 0
        right_col = 0

        if self.state[self.sideD.center_corner_pos[0]] == target:
            left_col += 1

        if self.state[self.sideD.center_corner_pos[2]] == target:
            left_col += 1

        if self.state[self.sideD.center_corner_pos[1]] == target:
            right_col += 1

        if self.state[self.sideD.center_corner_pos[3]] == target:
            right_col += 1

        if debug:
            log.info("target %s, top_row %d, bottom_row %d, left_col %d, right_col %d" % (target, top_row, bottom_row, left_col, right_col))

        # 2 on right column
        if right_col == 2:
            pass

        # 2 on top row
        elif top_row == 2:
            self.rotate("D")

        # 2 on bottom row
        elif bottom_row == 2:
            self.rotate("D'")

        # 2 on left column
        elif left_col == 2:
            self.rotate("D2")

        # top left corner
        elif self.state[self.sideD.center_corner_pos[0]] == target:
            self.rotate("D")

        # top right corner
        elif self.state[self.sideD.center_corner_pos[1]] == target:
            pass

        # bottom left corner
        elif self.state[self.sideD.center_corner_pos[2]] == target:
            self.rotate("D2")

        # bottom right corner
        elif self.state[self.sideD.center_corner_pos[3]] == target:
            self.rotate("D'")

        else:
            raise SolveError("")

    def prep_F_for_center_corner_placement(self, target):
        """
        Put a target square in the top right corner. If there are two paired
        then put the pair on the right side.
        """

        # If target is U or D we do not have to worry about preserving L or R so
        # we can bring center corners from other sides around to F
        if target in ('U', 'D'):
            top_row = len([square_index for square_index in self.sideF.center_corner_pos[0:2] if self.state[square_index] == target])
            bottom_row = len([square_index for square_index in self.sideF.center_corner_pos[2:4] if self.state[square_index] == target])

            # Look on the bottom row of L, R and B, see which one has the most of target and rotate it around
            if top_row and bottom_row == 0:
                L_bottom_row = [square_index for square_index in self.sideL.center_corner_pos[2:4] if self.state[square_index] == target]
                R_bottom_row = [square_index for square_index in self.sideR.center_corner_pos[2:4] if self.state[square_index] == target]
                B_bottom_row = [square_index for square_index in self.sideB.center_corner_pos[2:4] if self.state[square_index] == target]

                if L_bottom_row >= R_bottom_row and L_bottom_row >= B_bottom_row:
                    self.rotate("2D")
                elif R_bottom_row >= L_bottom_row and R_bottom_row >= B_bottom_row:
                    self.rotate("2D'")
                else:
                    self.rotate("2D2")

            elif bottom_row and top_row == 0:
                L_top_row = [square_index for square_index in self.sideL.center_corner_pos[0:2] if self.state[square_index] == target]
                R_top_row = [square_index for square_index in self.sideR.center_corner_pos[0:2] if self.state[square_index] == target]
                B_top_row = [square_index for square_index in self.sideB.center_corner_pos[0:2] if self.state[square_index] == target]

                if L_top_row >= R_top_row and L_top_row >= B_top_row:
                    self.rotate("2U'")
                elif R_top_row >= L_top_row and R_top_row >= B_top_row:
                    self.rotate("2U")
                else:
                    self.rotate("2U2")

        # Put a target square in the top right corner
        # If there are two paired then put the pair on the right side
        top_row = len([square_index for square_index in self.sideF.center_corner_pos[0:2] if self.state[square_index] == target])
        bottom_row = len([square_index for square_index in self.sideF.center_corner_pos[2:4] if self.state[square_index] == target])
        left_col = 0
        right_col = 0

        if self.state[self.sideF.center_corner_pos[0]] == target:
            left_col += 1

        if self.state[self.sideF.center_corner_pos[2]] == target:
            left_col += 1

        if self.state[self.sideF.center_corner_pos[1]] == target:
            right_col += 1

        if self.state[self.sideF.center_corner_pos[3]] == target:
            right_col += 1

        # 2 on right column
        if right_col == 2:
            pass

        # 2 on top row
        elif top_row == 2:
            self.rotate("F")

        # 2 on bottom row
        elif bottom_row == 2:
            self.rotate("F'")

        # 2 on left column
        elif left_col == 2:
            self.rotate("F2")

        # top left corner
        elif self.state[self.sideF.center_corner_pos[0]] == target:
            self.rotate("F")

        # top right corner
        elif self.state[self.sideF.center_corner_pos[1]] == target:
            pass

        # bottom left corner
        elif self.state[self.sideF.center_corner_pos[2]] == target:
            self.rotate("F2")

        # bottom right corner
        elif self.state[self.sideF.center_corner_pos[3]] == target:
            self.rotate("F'")

        else:
            raise SolveError("")

    def lookup_table_444_UD_center_corners(self):
        filename = 'lookup-table-4x4x4-step10-solve-UD-centers.txt'

        if os.path.exists(filename):
            with open(filename, 'r') as fh:
                state = self.get_center_corner_state()
                state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x')
                state = get_first_babelfish_state(state)

                line = get_line_startswith(fh, state + ':')

                if line:
                    (key, steps) = line.split(':')
                    steps = steps.strip().split()

                    log.info("Found UD center_corners %s in lookup table, %d steps in, %s" %\
                        (state, len(self.solution), ' '.join(steps)))

                    if self.size == 4:
                        for step in steps:
                            self.rotate(step)

                    elif self.size == 5:
                        for step in steps:
                            self.rotate(step)

                        try:
                            self.sideU.verify_center_corners_solved()
                            self.sideD.verify_center_corners_solved()

                        # When using the 4x4x4 tables it is possible to get U in the center
                        # with D center corners (and vice versa).  If that happens just flip
                        # it (but without moving the U and D centers)
                        except SolveError:
                            self.rotate("2R2")
                            self.rotate("2L2")

                    elif self.size == 6:
                        log.info("%s center_corner_pos %s" % (self.sideU, self.sideU.center_corner_pos))
                        for step in steps:
                            #if step.startswith('2'):
                            #    step = '3' + step[1:]
                            #log.info("step %s" % step)
                            self.rotate(step)

                    else:
                        raise ImplementThis("size %d" % self.size)

                    self.sideU.verify_center_corners_solved()
                    self.sideD.verify_center_corners_solved()
                    self.rotate_U_to_U()
                    return True
                else:
                    log.warning("Did not find %s in %s" % (state, filename))

        return False

    def lookup_table_444_LFRB_center_corners(self):
        filename = 'lookup-table-4x4x4-step20-solve-LFRB-centers.txt'

        if os.path.exists(filename):
            with open(filename, 'r') as fh:
                state = self.get_center_corner_state()
                state = get_first_babelfish_state(state)
                line = get_line_startswith(fh, state + ':')

                if line:
                    (key, steps) = line.split(':')
                    steps = steps.strip().split()

                    log.info("Found LFFB center_corners %s in lookup table, %d steps in, %s" %\
                        (state, len(self.solution), ' '.join(steps)))

                    for step in steps:
                        self.rotate(step)

                    if self.size == 4:
                        self.sideL.verify_center_corners_solved()
                        self.sideF.verify_center_corners_solved()
                        self.sideR.verify_center_corners_solved()
                        self.sideB.verify_center_corners_solved()

                    elif self.size == 5:
                        for x in range(4):
                            try:
                                self.sideL.verify_center_corners_solved()
                                self.sideF.verify_center_corners_solved()
                                self.sideR.verify_center_corners_solved()
                                self.sideB.verify_center_corners_solved()
                                break
                            except SolveError:
                                self.rotate("2U")
                                self.rotate("2D'")
                        else:
                            raise SolveError("")

                    self.rotate_U_to_U()
                    self.rotate_F_to_F()
                    return True
                else:
                    log.warning("Did not find %s in %s" % (state, filename))

        return False

    def solve_center_corners(self, target):
        """
        Solve the center corners on sideU for 'target'
        """
        if self.centers_solved():
            return

        while not self.sideU.center_corners_solved():

            # Move target squares from F,R,B and L to U
            for tmp_side in (self.sideD, self.sideF, self.sideR, self.sideB, self.sideL):

                # Are all centers solved?
                if self.centers_solved():
                    return

                if tmp_side in (self.sideR, self.sideB, self.sideL):
                    self.rotate_y()

                # Move target squares from D to U
                if tmp_side == self.sideD:

                    while True :

                        # Are there any target squares on sideD?
                        matching_squares = [square_index for square_index in self.sideD.center_corner_pos if self.state[square_index] == target]

                        if not matching_squares:
                            break

                        self.prep_D_for_center_corner_placement(target)
                        self.prep_U_for_center_corner_placement(target)
                        self.rotate("2R2")
                        self.rotate("U'")
                        self.rotate("2R2")

                # Move target squares from F,R,B and L to U
                else:
                    while True :

                        # Are there any target squares on sideF?
                        matching_squares = [square_index for square_index in self.sideF.center_corner_pos if self.state[square_index] == target]

                        if not matching_squares:
                            break

                        self.prep_F_for_center_corner_placement(target)
                        self.prep_U_for_center_corner_placement(target)
                        self.rotate("2R")
                        self.rotate("U'")
                        self.rotate("2R'")

        self.sideU.verify_center_corners_solved()

    def prep_U_for_center_edge_placement(self, prep_position):
        """
        We need the bottom edge to be unsolved
        """
        target = self.state[self.sideU.mid_pos]
        center_edge_pos = self.sideU.center_edge_pos

        if prep_position == 3:
            if self.state[center_edge_pos[3]] != target:
                return
            elif self.state[center_edge_pos[2]] != target:
                self.rotate('U')
            elif self.state[center_edge_pos[1]] != target:
                self.rotate("U'")
            elif self.state[center_edge_pos[0]] != target:
                self.rotate("U2")
            else:
                raise SolveError("")

        elif prep_position == 0:
            if self.state[center_edge_pos[0]] != target:
                return
            elif self.state[center_edge_pos[1]] != target:
                self.rotate('U')
            elif self.state[center_edge_pos[2]] != target:
                self.rotate("U'")
            elif self.state[center_edge_pos[3]] != target:
                self.rotate("U2")
            else:
                raise SolveError("")

        else:
            raise Exception("Implement this")

    def move_555_center_edges_from_D_to_U_preserve_UD_center_corners(self, target):
        """
        Move from D to U without breaking LR center corners
        - - -
        - - -  U
        - x -

        - - -
        - - x  D
        - - -
        """
        prep_position = 3

        # Move from D to U
        while True:

            matching_squares = [square_index for square_index in self.sideD.center_edge_pos if self.state[square_index] == target]

            if not matching_squares:
                break

            original_centers_solved_count = self.get_centers_solved_count()
            square_index = matching_squares[0]
            self.prep_U_for_center_edge_placement(prep_position)
            steps = []

            # Put the square to move at the D right center edge
            if self.sideD.edge_is_top(square_index):
                steps.append("D")
            elif self.sideD.edge_is_left(square_index):
                steps.append("D2")
            elif self.sideD.edge_is_bottom(square_index):
                steps.append("D'")
            elif self.sideD.edge_is_right(square_index):
                pass

            # Put the square to move at the D top center edge
            if self.sideD.edge_is_top(square_index):
                pass
            elif self.sideD.edge_is_left(square_index):
                steps.append("D")
            elif self.sideD.edge_is_bottom(square_index):
                steps.append("D2")
            elif self.sideD.edge_is_right(square_index):
                steps.append("D'")

            steps.append("2F")
            steps.append("3R")
            steps.append("2R'")
            steps.append("2F'")
            steps.append("3R'")
            steps.append("2R")

            for step in steps:
                self.rotate(step)

            current_centers_solved_count = self.get_centers_solved_count()
            if current_centers_solved_count < original_centers_solved_count:
                raise SolveError("Went from %d centers solved to %d" % (original_centers_solved_count, current_centers_solved_count))

    def move_555_center_edges_from_D_to_U_preserve_LR_centers(self, target):
        """
        Move from D to U without breaking the LR centers
        - x -
        - - -  U
        - - -

        - - -
        - - x  D
        - - -
        """
        prep_position = 0

        # Move from D to U
        while True:

            matching_squares = [square_index for square_index in self.sideD.center_edge_pos if self.state[square_index] == target]

            if not matching_squares:
                break

            original_centers_solved_count = self.get_centers_solved_count()
            square_index = matching_squares[0]
            self.prep_U_for_center_edge_placement(prep_position)
            steps = []

            # Put the square to move at the D right center edge
            if self.sideD.edge_is_top(square_index):
                steps.append("D")
            elif self.sideD.edge_is_left(square_index):
                steps.append("D2")
            elif self.sideD.edge_is_bottom(square_index):
                steps.append("D'")
            elif self.sideD.edge_is_right(square_index):
                pass

            steps.append("3R'")
            steps.append("2R")
            steps.append("F'")
            steps.append("2L")
            steps.append("D2")
            steps.append("2L'")
            steps.append("F")
            steps.append("3R")
            steps.append("2R'")

            for step in steps:
                self.rotate(step)

            current_centers_solved_count = self.get_centers_solved_count()
            if current_centers_solved_count < original_centers_solved_count:
                raise SolveError("Went from %d centers solved to %d" % (original_centers_solved_count, current_centers_solved_count))

    def move_555_center_edges_from_LFRB_to_U_sides_one_two(self, target):
        """
        Move the center edges from LFRB to side U without disturbing the centers on side D

        - - -
        - - -  U
        - x -

        - - -
        - - -  LFRB
        - x -

        """
        prep_position = 3

        # Move from F to U
        # Move from R to U
        # Move from B to U
        # Move from L to U
        for tmp_side in (self.sideF, self.sideR, self.sideB, self.sideL):

            if tmp_side in (self.sideR, self.sideB, self.sideL):
                self.rotate_y()

            while True:

                matching_squares = [square_index for square_index in self.sideF.center_edge_pos if self.state[square_index] == target]

                if not matching_squares:
                    break

                original_centers_solved_count = self.get_centers_solved_count()
                self.prep_U_for_center_edge_placement(prep_position)

                square_index = matching_squares[0]
                steps = []

                # We want the square to move to be edge 3
                if self.sideF.edge_is_top(square_index):
                    steps.append("F2")
                elif self.sideF.edge_is_right(square_index):
                    steps.append("F")
                elif self.sideF.edge_is_left(square_index):
                    steps.append("F'")

                steps.append("2F'")
                steps.append("R") # This is to get the column from D out of the way
                steps.append("3U")
                steps.append("2U'")
                steps.append("R'")
                steps.append("2F")

                for step in steps:
                    self.rotate(step)

                current_centers_solved_count = self.get_centers_solved_count()
                if current_centers_solved_count < original_centers_solved_count:
                    raise SolveError("Went from %d centers solved to %d" % (original_centers_solved_count, current_centers_solved_count))

    def move_555_center_edges_to_U_sides_three_four(self, target, sides_to_check):

        """
        Move the center edges from FB to side U without disturbing the centers on LR
        - x -
        - - -  U
        - - -

        - x -
        - - -  LFRB
        - - -
        """
        prep_position = 0

        # Move from F to U
        # Move from R to U
        # Move from B to U
        # Move from L to U
        for tmp_side in sides_to_check:

            if tmp_side == self.sideB:
                self.rotate_y()
                self.rotate_y()

            while True:

                matching_squares = [square_index for square_index in self.sideF.center_edge_pos if self.state[square_index] == target]

                if not matching_squares:
                    break

                original_centers_solved_count = self.get_centers_solved_count()
                self.prep_U_for_center_edge_placement(prep_position)

                square_index = matching_squares[0]
                steps = []

                # We want the square to move to be edge 0
                if self.sideF.edge_is_top(square_index):
                    pass
                elif self.sideF.edge_is_left(square_index):
                    steps.append("F")
                elif self.sideF.edge_is_bottom(square_index):
                    steps.append("F2")
                elif self.sideF.edge_is_right(square_index):
                    steps.append("F'")

                steps.append("3R'")
                steps.append("2R")
                steps.append("F'")
                steps.append("2L'")
                steps.append("F")
                steps.append("3R")
                steps.append("2R'")
                steps.append("F'")
                steps.append("2L")

                for step in steps:
                    self.rotate(step)

                current_centers_solved_count = self.get_centers_solved_count()
                if current_centers_solved_count < original_centers_solved_count:
                    raise SolveError("Went from %d centers solved to %d" % (original_centers_solved_count, current_centers_solved_count))

    def move_555_center_edges_from_FB_to_U_sides_three_four(self, target):
        self.move_555_center_edges_to_U_sides_three_four(target, (self.sideF, self.sideB))

    def move_555_center_edges_from_F_to_U_sides_three_four(self, target):
        self.move_555_center_edges_to_U_sides_three_four(target, (self.sideF, ))

    def move_555_center_edges_last_two_sides(self, target):
        # Special case to place the last two centers
        # http://www.rubik.rthost.org/5x5x5_centres.htm
        prep_position = 0

        while True:

            matching_squares = [square_index for square_index in self.sideF.center_edge_pos if self.state[square_index] == target]

            if not matching_squares:
                break

            original_centers_solved_count = self.get_centers_solved_count()
            steps = []
            square_index = matching_squares[0]
            self.prep_U_for_center_edge_placement(prep_position)

            # F square to that we want to place on the top must be at edge 2
            if self.sideF.edge_is_top(square_index):
                steps.append("F")
            elif self.sideF.edge_is_bottom(square_index):
                steps.append("F'")
            elif self.sideF.edge_is_left(square_index):
                steps.append("F2")

            steps.append("2R")
            steps.append("U")
            steps.append("2R'")
            steps.append("U'")

            steps.append("2R")
            steps.append("U")
            steps.append("2R'")
            steps.append("U")

            steps.append("2R")
            steps.append("U2")
            steps.append("2R'")

            for step in steps:
                self.rotate(step)

            self.verify_all_center_corners_solved()

            current_centers_solved_count = self.get_centers_solved_count()
            if current_centers_solved_count < original_centers_solved_count:
                raise SolveError("Went from %d centers solved to %d" % (original_centers_solved_count, current_centers_solved_count))

    def solve_center_edges(self, target, side_step):
        if side_step == 1:

            while not self.sideU.center_solved():
                self.move_555_center_edges_from_D_to_U_preserve_UD_center_corners(target)
                self.move_555_center_edges_from_LFRB_to_U_sides_one_two(target)

            self.sideU.verify_center_corners_solved()
            self.sideU.verify_center_edges_solved()
            self.sideD.verify_center_corners_solved()

        elif side_step == 2:
            # Note D center is solved by this point

            while not self.sideU.center_solved():
                self.move_555_center_edges_from_LFRB_to_U_sides_one_two(target)

            self.sideU.verify_center_corners_solved()
            self.sideU.verify_center_edges_solved()
            self.sideD.verify_center_corners_solved()
            self.sideD.verify_center_edges_solved()

        elif side_step == 3:

            while not self.sideU.center_solved():
                self.move_555_center_edges_from_D_to_U_preserve_LR_centers(target)
                self.move_555_center_edges_from_FB_to_U_sides_three_four(target)

            self.sideU.verify_center_corners_solved()
            self.sideU.verify_center_edges_solved()
            self.sideL.verify_center_corners_solved()
            self.sideL.verify_center_edges_solved()
            self.sideR.verify_center_corners_solved()
            self.sideR.verify_center_edges_solved()

        elif side_step == 4:

            while not self.sideU.center_solved():
                self.move_555_center_edges_from_D_to_U_preserve_LR_centers(target)
                self.move_555_center_edges_from_F_to_U_sides_three_four(target)

            self.sideU.verify_center_corners_solved()
            self.sideU.verify_center_edges_solved()
            self.sideB.verify_center_corners_solved()
            self.sideB.verify_center_edges_solved()
            self.sideL.verify_center_corners_solved()
            self.sideL.verify_center_edges_solved()
            self.sideR.verify_center_corners_solved()
            self.sideR.verify_center_edges_solved()

        elif side_step == 5:
            self.move_555_center_edges_last_two_sides(target)
            self.verify_all_centers_solved()

    def rotate_side_X_to_Y(self, x, y):
        #assert x in ('U', 'L', 'F', 'R', 'B', 'D'), "Invalid side %s" % x
        #assert y in ('U', 'L', 'F', 'R', 'B', 'D'), "Invalid side %s" % y

        if y == 'U':
            side = self.sideU
        elif y == 'L':
            side = self.sideL
        elif y == 'F':
            side = self.sideF
        elif y == 'R':
            side = self.sideR
        elif y == 'B':
            side = self.sideB
        elif y == 'D':
            side = self.sideD

        if side.mid_pos:
            pos_to_check = side.mid_pos
            F_pos_to_check = self.sideF.mid_pos
            D_pos_to_check = self.sideD.mid_pos
        else:
            pos_to_check = side.center_corner_pos[0]
            F_pos_to_check = self.sideF.center_corner_pos[0]
            D_pos_to_check = self.sideD.center_corner_pos[0]

        count = 0

        while self.state[pos_to_check] != x:
            #log.info("%s (%s): rotate %s to %s, pos_to_check %s, state at pos_to_check %s" %
            #    (side, side.mid_pos, x, y, pos_to_check, self.state[pos_to_check]))

            if self.state[F_pos_to_check] == x and y == 'U':
                self.rotate_x()

            elif self.state[F_pos_to_check] == x and y == 'D':
                self.rotate_x_reverse()

            elif self.state[D_pos_to_check] == x and y == 'F':
                self.rotate_x()

            elif self.state[D_pos_to_check] == x and y == 'U':
                self.rotate_x()
                self.rotate_x()

            else:
                self.rotate_y()

            count += 1

            if count > 30:
                raise StuckInALoop("rotate %s to %s, %s, pos_to_check %s, state at pos_to_check %s" % (x, y, side, pos_to_check, self.state[pos_to_check]))

    def rotate_U_to_L(self):
        self.rotate_side_X_to_Y('U', 'L')

    def rotate_U_to_U(self):
        self.rotate_side_X_to_Y('U', 'U')

    def rotate_R_to_U(self):
        self.rotate_side_X_to_Y('R', 'U')

    def rotate_F_to_F(self):
        self.rotate_side_X_to_Y('F', 'F')

    def rotate_L_to_U(self):
        self.rotate_side_X_to_Y('L', 'U')

    def rotate_L_to_L(self):
        self.rotate_side_X_to_Y('L', 'L')

    def all_center_corners_solved(self):
        for side in self.sides.values():
            if not side.center_corners_solved():
                return False
        return True

    def all_center_edges_solved(self):
        for side in self.sides.values():
            if not side.center_edges_solved():
                return False
        return True

    def all_centers_solved(self):
        if self.all_center_edges_solved() and self.all_center_corners_solved():
            return True
        return False

    def verify_all_center_corners_solved(self):
        if not self.all_center_corners_solved():
            raise SolveError("%s all center corners are not solved" % self)

    def verify_all_center_edges_solved(self):
        if not self.all_center_edges_solved():
            raise SolveError("%s all center edges are not solved" % self)

    def verify_all_centers_solved(self):
        if not self.all_centers_solved():
            raise SolveError("%s all centers are not solved" % self)

    def get_kociemba_string(self, all_squares):
        # kociemba uses order U R F D L B

        foo = []

        if all_squares:
            # This is only used to print cubes for test cases (see --test-build)
            for side_name in ('U', 'R', 'F', 'D', 'L', 'B'):
                side = self.sides[side_name]

                for square_index in range(side.min_pos, side.max_pos + 1):
                    foo.append(self.state[square_index])

        else:
            # kociemba solves 3x3x3 so label the sides as if this were a 3x3x3 (so U on top, F in the front, etc)
            kociemba_babelfish = {}
            for side_name in ('U', 'R', 'F', 'D', 'L', 'B'):
                side = self.sides[side_name]
                kociemba_babelfish[self.state[side.center_corner_pos[0]]] = side_name

            # This is the normal scenario, produce a string of the reduced 3x3x3 cube
            try:
                for side_name in ('U', 'R', 'F', 'D', 'L', 'B'):
                    side = self.sides[side_name]

                    # first row
                    foo.append(kociemba_babelfish[self.state[side.corner_pos[0]]])
                    foo.append(kociemba_babelfish[self.state[side.edge_north_pos[0]]])
                    foo.append(kociemba_babelfish[self.state[side.corner_pos[1]]])

                    # second row
                    foo.append(kociemba_babelfish[self.state[side.edge_west_pos[0]]])
                    foo.append(kociemba_babelfish[self.state[side.center_corner_pos[0]]])
                    foo.append(kociemba_babelfish[self.state[side.edge_east_pos[0]]])

                    # third row
                    foo.append(kociemba_babelfish[self.state[side.corner_pos[2]]])
                    foo.append(kociemba_babelfish[self.state[side.edge_south_pos[0]]])
                    foo.append(kociemba_babelfish[self.state[side.corner_pos[3]]])
            except Exception:
                log.info("kociemba_babelfish:\n%s\n" % pformat(kociemba_babelfish))
                self.print_cube()
                raise

        # Note that you must you the copy of kociemba
        kociemba_string = ''.join(foo)
        return kociemba_string

    def solve_333(self):
        kociemba_string = self.get_kociemba_string(False)

        try:
            steps = subprocess.check_output(['kociemba', kociemba_string]).decode('ascii').splitlines()[-1].strip().split()
            kociemba_ok = True
        except Exception:
            kociemba_ok = False

        if not kociemba_ok:
            #edge_swap_count = self.get_edge_swap_count(edges_paired=True, debug=True)
            #corner_swap_count = self.get_corner_swap_count(debug=True)
            #raise SolveError("parity error made kociemba barf, edge parity %d, corner parity %d, kociemba %s" %
            #    (edge_swap_count, corner_swap_count, kociemba_string))
            raise SolveError("parity error made kociemba barf,  kociemba %s" % kociemba_string)

        log.debug("kociemba       : %s" % kociemba_string)
        log.debug("kociemba steps : %s" % ', '.join(steps))

        for step in steps:
            self.rotate(step)

    def get_corner_swap_count(self, debug=False):

        needed_corners = [
            'BLU',
            'BRU',
            'FLU',
            'FRU',
            'DFL',
            'DFR',
            'BDL',
            'BDR']

        to_check = [
            (self.sideU.corner_pos[0], self.sideL.corner_pos[0], self.sideB.corner_pos[1]), # ULB
            (self.sideU.corner_pos[1], self.sideR.corner_pos[1], self.sideB.corner_pos[0]), # URB
            (self.sideU.corner_pos[2], self.sideL.corner_pos[1], self.sideF.corner_pos[0]), # ULF
            (self.sideU.corner_pos[3], self.sideF.corner_pos[1], self.sideR.corner_pos[0]), # UFR
            (self.sideD.corner_pos[0], self.sideL.corner_pos[3], self.sideF.corner_pos[2]), # DLF
            (self.sideD.corner_pos[1], self.sideF.corner_pos[3], self.sideR.corner_pos[2]), # DFR
            (self.sideD.corner_pos[2], self.sideL.corner_pos[2], self.sideB.corner_pos[3]), # DLB
            (self.sideD.corner_pos[3], self.sideR.corner_pos[3], self.sideB.corner_pos[2])  # DRB
        ]

        current_corners = []
        for (square_index1, square_index2, square_index3) in to_check:
            square1 = self.state[square_index1]
            square2 = self.state[square_index2]
            square3 = self.state[square_index3]
            corner_str = ''.join(sorted([square1, square2, square3]))
            current_corners.append(corner_str)

        if debug:
            log.info("to_check:\n%s" % pformat(to_check))
            to_check_str = ''
            for (a, b, c) in to_check:
                to_check_str += "%4s" % a

            log.info("to_check       :%s" % to_check_str)
            log.info("needed corners : %s" % ' '.join(needed_corners))
            log.info("currnet corners: %s" % ' '.join(current_corners))
            log.info("")

        return get_swap_count(needed_corners, current_corners, debug)

    def corner_swaps_even(self, debug=False):
        if self.get_corner_swap_count(debug) % 2 == 0:
            return True
        return False

    def corner_swaps_odd(self, debug=False):
        if self.get_corner_swap_count(debug) % 2 == 1:
            return True
        return False

    def get_edge_swap_count(self, edges_paired, debug=False):
        needed_edges = []
        to_check = []

        # Upper
        for (foo_index, square_index) in enumerate(self.sideU.edge_north_pos):
            to_check.append(square_index)
            if edges_paired:
                needed_edges.append('UB')
                break
            else:
                needed_edges.append('UB%d' % foo_index)

        for (foo_index, square_index) in enumerate(reversed(self.sideU.edge_west_pos)):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('UL')
                break
            else:
                needed_edges.append('UL%d' % foo_index)

        for (foo_index, square_index) in enumerate(self.sideU.edge_south_pos):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('UF')
                break
            else:
                needed_edges.append('UF%d' % foo_index)

        for (foo_index, square_index) in enumerate(self.sideU.edge_east_pos):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('UR')
                break
            else:
                needed_edges.append('UR%d' % foo_index)


        # Left
        for (foo_index, square_index) in enumerate(reversed(self.sideL.edge_west_pos)):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('LB')
                break
            else:
                needed_edges.append('LB%d' % foo_index)

        for (foo_index, square_index) in enumerate(self.sideL.edge_east_pos):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('LF')
                break
            else:
                needed_edges.append('LF%d' % foo_index)


        # Right
        for (foo_index, square_index) in enumerate(reversed(self.sideR.edge_west_pos)):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('RF')
                break
            else:
                needed_edges.append('RF%d' % foo_index)

        for (foo_index, square_index) in enumerate(self.sideR.edge_east_pos):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('RB')
                break
            else:
                needed_edges.append('RB%d' % foo_index)

        # Down
        for (foo_index, square_index) in enumerate(self.sideD.edge_north_pos):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('DF')
                break
            else:
                needed_edges.append('DF%d' % foo_index)

        for (foo_index, square_index) in enumerate(reversed(self.sideD.edge_west_pos)):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('DL')
                break
            else:
                needed_edges.append('DL%d' % foo_index)

        for (foo_index, square_index) in enumerate(self.sideD.edge_south_pos):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('DB')
                break
            else:
                needed_edges.append('DB%d' % foo_index)

        for (foo_index, square_index) in enumerate(self.sideD.edge_east_pos):
            to_check.append(square_index)

            if edges_paired:
                needed_edges.append('DR')
                break
            else:
                needed_edges.append('DR%d' % foo_index)

        if debug:
            to_check_str = ''

            for x in to_check:
                if edges_paired:
                    to_check_str += "%3s" % x
                else:
                    to_check_str += "%4s" % x

            log.info("to_check     :%s" % to_check_str)
            log.info("needed edges : %s" % ' '.join(needed_edges))

        current_edges = []

        for square_index in to_check:
            side = self.get_side_for_index(square_index)
            partner_index = side.get_wing_partner(square_index)
            square1 = self.state[square_index]
            square2 = self.state[partner_index]

            if square1 in ('U', 'D'):
                wing_str = square1 + square2
            elif square2 in ('U', 'D'):
                wing_str = square2 + square1
            elif square1 in ('L', 'R'):
                wing_str = square1 + square2
            elif square2 in ('L', 'R'):
                wing_str = square2 + square1
            else:
                raise Exception("Could not determin wing_str for (%s, %s)" % (square1, square2))

            if not edges_paired:
                # - backup the current state
                # - add an 'x' to the end of the square_index/partner_index
                # - move square_index/partner_index to its final edge location
                # - look for the 'x' to determine if this is the '0' vs '1' wing
                # - restore the original state

                square1_with_x = square1 + 'x'
                square2_with_x = square2 + 'x'

                original_state = copy(self.state)
                original_solution = copy(self.solution)
                self.state[square_index] = square1_with_x
                self.state[partner_index] = square2_with_x

                # 'UB0', 'UB1', 'UL0', 'UL1', 'UF0', 'UF1', 'UR0', 'UR1',
                # 'LB0', 'LB1', 'LF0', 'LF1', 'RF0', 'RF1', 'RB0', 'RB1',
                # 'DF0', 'DF1', 'DL0', 'DL1', 'DB0', 'DB1', 'DR0', 'DR1
                if wing_str == 'UB':
                    self.move_wing_to_U_north(square_index)
                    edge_to_check = self.sideU.edge_north_pos
                    target_side = self.sideU

                elif wing_str == 'UL':
                    self.move_wing_to_U_west(square_index)
                    edge_to_check = reversed(self.sideU.edge_west_pos)
                    target_side = self.sideU

                elif wing_str == 'UF':
                    self.move_wing_to_U_south(square_index)
                    edge_to_check = self.sideU.edge_south_pos
                    target_side = self.sideU

                elif wing_str == 'UR':
                    self.move_wing_to_U_east(square_index)
                    edge_to_check = self.sideU.edge_east_pos
                    target_side = self.sideU

                elif wing_str == 'LB':
                    self.move_wing_to_L_west(square_index)
                    edge_to_check = reversed(self.sideL.edge_west_pos)
                    target_side = self.sideL

                elif wing_str == 'LF':
                    self.move_wing_to_L_east(square_index)
                    edge_to_check = self.sideL.edge_east_pos
                    target_side = self.sideL

                elif wing_str == 'RF':
                    self.move_wing_to_R_west(square_index)
                    edge_to_check = reversed(self.sideR.edge_west_pos)
                    target_side = self.sideR

                elif wing_str == 'RB':
                    self.move_wing_to_R_east(square_index)
                    edge_to_check = self.sideR.edge_east_pos
                    target_side = self.sideR

                elif wing_str == 'DF':
                    self.move_wing_to_D_north(square_index)
                    edge_to_check = self.sideD.edge_north_pos
                    target_side = self.sideD

                elif wing_str == 'DL':
                    self.move_wing_to_D_west(square_index)
                    edge_to_check = reversed(self.sideD.edge_west_pos)
                    target_side = self.sideD

                elif wing_str == 'DB':
                    self.move_wing_to_D_south(square_index)
                    edge_to_check = self.sideD.edge_south_pos
                    target_side = self.sideD

                elif wing_str == 'DR':
                    self.move_wing_to_D_east(square_index)
                    edge_to_check = self.sideD.edge_east_pos
                    target_side = self.sideD

                else:
                    raise SolveError("invalid wing %s" % wing_str)


                for (edge_index, wing_index) in enumerate(edge_to_check):
                    wing_value = self.state[wing_index]

                    if wing_value.endswith('x'):
                        if wing_value.startswith(target_side.name):
                            wing_str += str(edge_index)
                        else:
                            max_edge_index = len(target_side.edge_east_pos) - 1
                            wing_str += str(max_edge_index - edge_index)
                        break
                else:
                    raise SolveError("Could not find wing %s (%d, %d) among %s" % (wing_str, square_index, partner_index, str(edge_to_check)))

                self.state = copy(original_state)
                self.solution = copy(original_solution)

            current_edges.append(wing_str)

        if debug:
            log.info("current edges: %s" % ' '.join(current_edges))
        return get_swap_count(needed_edges, current_edges, debug)

    def edge_swaps_even(self, edges_paired, debug):
        if self.get_edge_swap_count(edges_paired, debug) % 2 == 0:
            return True
        return False

    def edge_swaps_odd(self, edges_paired, debug):
        if self.get_edge_swap_count(edges_paired, debug) % 2 == 1:
            return True
        return False

    def edge_solution_leads_to_pll_parity(self, debug=False):
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if self.edge_swaps_even(True, debug) == self.corner_swaps_even(debug):
            if debug:
                log.info("Predict we are free of PLL parity")
            return False

        if debug:
            log.info("Predict we have PLL parity")
        return True

    def center_solution_leads_to_oll_parity(self, debug=False):
        """
        http://www.speedcubing.com/chris/4speedsolve3.html
        http://www.rubik.rthost.org/4x4x4_edges.htm
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        # OLL Parity - "...is caused by solving the centers such that the edge permutation is odd"
        # http://www.speedcubing.com/chris/4speedsolve3.html
        if self.edge_swaps_odd(False, debug):
            log.debug("Predict we have OLL parity")
            return True
        else:
            log.debug("Predict we are free of OLL parity")
            return False

    def group_centers_444(self):
        # U (white)
        log.debug("solve U center corners")
        self.solve_center_corners('U')

        # D (yellow)
        self.rotate_x()
        self.rotate_x()
        log.debug("solve D center corners")
        self.solve_center_corners('D')

        # R (blue)
        self.rotate_x()
        self.rotate_U_to_L()
        log.debug("solve R center corners")
        self.solve_center_corners('R')
        self.rotate_U_to_L()

        # F (red)
        self.rotate_x()
        log.debug("solve F center corners")
        self.solve_center_corners('F')
        self.rotate_U_to_L()

        # L (green) corners which in turn solves the B (orange) corners
        self.rotate_x()
        log.info("solve L center corners")
        self.solve_center_corners('L')
        self.rotate_U_to_L()

    def group_centers_555(self):
        self.rotate_U_to_U()

        # U (white)
        log.debug("solve U center corners")
        self.solve_center_corners('U')

        # D (yellow)
        self.rotate_x()
        self.rotate_x()
        log.debug("solve D center corners")
        self.solve_center_corners('D')
        self.rotate_x()
        self.rotate_x()
        log.info("Took %d steps to solve UD center corners" % len(self.solution))

        # U (white)
        log.debug("solve U center edges")
        self.solve_center_edges('U', 1)
        self.rotate_U_to_U()
        log.info("Took %d steps to solve U center edges" % len(self.solution))

        # D (yellow)
        self.rotate_x()
        self.rotate_x()
        log.debug("solve D center edges")
        self.solve_center_edges('D', 2)
        log.info("Took %d steps to solve UD centers" % len(self.solution))

        # R (blue)
        self.rotate_x()
        self.rotate_U_to_L()
        self.rotate_R_to_U()

        log.debug("solve R center corners")
        self.solve_center_corners('R')
        self.rotate_U_to_L()

        log.debug("solve R center edges")
        self.solve_center_edges('R', 3)
        self.rotate_U_to_L()

        # F (red)
        self.rotate_x()
        log.debug("solve F center corners")
        self.solve_center_corners('F')
        self.rotate_U_to_L()

        log.debug("solve F center edges")
        self.solve_center_edges('F', 4)
        self.rotate_U_to_L()

        # L (green) corners which in turn solves the B (orange) corners
        self.rotate_x()
        log.info("solve L center corners")
        self.solve_center_corners('L')
        self.rotate_U_to_L()

        # Place center for the last side
        log.info("solve L center edges")
        self.solve_center_edges('L', 5)

    def group_centers_666(self):
        raise ImplementThis("")

    def group_centers(self):

        min_solution_length = None
        min_solution_state = None
        min_solution = None

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = len(self.solution)

        for upper_side_name in ('U', 'D', 'L', 'F', 'R', 'B'):
            for front_side_name in ('F', 'R', 'B', 'L', 'U', 'D'):
                for opening_move in (None, "2U", "2D", "2L", "2F", "2R", "2D", "2U'", "2D'", "2L'", "2F'", "2R'", "2D'"):

                    if upper_side_name == front_side_name:
                        continue

                    # Put the cube back in its original state
                    self.state = copy(original_state)
                    self.solution = copy(original_solution)

                    if upper_side_name == 'U':

                        if front_side_name == 'D':
                            continue

                        if front_side_name == 'L':
                            self.rotate_y_reverse()
                        elif front_side_name == 'F':
                            pass
                        elif front_side_name == 'R':
                            self.rotate_y()
                        elif front_side_name == 'B':
                            self.rotate_y()
                            self.rotate_y()

                    elif upper_side_name == 'D':

                        if front_side_name == 'U':
                            continue

                        self.rotate_x()
                        self.rotate_x()

                        if front_side_name == 'L':
                            self.rotate_y_reverse()
                        elif front_side_name == 'F':
                            self.rotate_y()
                            self.rotate_y()
                        elif front_side_name == 'R':
                            self.rotate_y()
                        elif front_side_name == 'B':
                            pass

                    elif upper_side_name == 'L':

                        if front_side_name == 'R':
                            continue

                        self.rotate_y_reverse()
                        self.rotate_x()

                        if front_side_name == 'U':
                            self.rotate_y()
                            self.rotate_y()
                        elif front_side_name == 'F':
                            self.rotate_y()
                        elif front_side_name == 'D':
                            pass
                        elif front_side_name == 'B':
                            self.rotate_y_reverse()

                    elif upper_side_name == 'F':

                        if front_side_name == 'B':
                            continue

                        self.rotate_x()

                        if front_side_name == 'L':
                            self.rotate_y_reverse()
                        elif front_side_name == 'U':
                            self.rotate_y()
                            self.rotate_y()
                        elif front_side_name == 'R':
                            self.rotate_y()
                        elif front_side_name == 'D':
                            pass

                    elif upper_side_name == 'R':

                        if front_side_name == 'L':
                            continue

                        self.rotate_y()
                        self.rotate_x()

                        if front_side_name == 'U':
                            self.rotate_y()
                            self.rotate_y()
                        elif front_side_name == 'F':
                            self.rotate_y_reverse()
                        elif front_side_name == 'D':
                            pass
                        elif front_side_name == 'B':
                            self.rotate_y()

                    elif upper_side_name == 'B':

                        if front_side_name == 'F':
                            continue

                        self.rotate_x_reverse()

                        if front_side_name == 'L':
                            self.rotate_y_reverse()
                        elif front_side_name == 'U':
                            pass
                        elif front_side_name == 'R':
                            self.rotate_y()
                        elif front_side_name == 'D':
                            self.rotate_y()
                            self.rotate_y()

                    if opening_move:
                        self.rotate(opening_move)

                    if self.size == 4:
                        self.group_centers_444()

                    elif self.size == 5:
                        self.group_centers_555()

                    elif self.size == 6:
                        self.group_centers_666()

                    else:
                        raise ImplementThis("group_centers for %dx%dx%d" % (self.size, self.size, self.size))

                    if not self.centers_solved():
                        raise SolveError("centers should be solved but they are not")

                    # Do not consider any center solution that leads to OLL parity
                    if self.size == 4 and self.center_solution_leads_to_oll_parity():
                        log.info("%s on top, %s in front, opening move %4s: creates OLL parity" % (upper_side_name, front_side_name, opening_move))
                    else:
                        center_solution_length = self.get_solution_len_minus_rotates(self.solution)

                        if min_solution_length is None or center_solution_length < min_solution_length:
                            min_solution = copy(self.solution)
                            min_solution_state = copy(self.state)
                            min_solution_length = copy(center_solution_length)
                            log.info("%s on top, %s in front, opening move %4s: solution length %d, min solution length %s (NEW MIN)" %\
                                (upper_side_name, front_side_name, opening_move, center_solution_length, min_solution_length))
                        else:
                            log.info("%s on top, %s in front, opening move %4s: solution length %d, min solution length %s" %\
                                (upper_side_name, front_side_name, opening_move, center_solution_length, min_solution_length))

                        # We found a parity free solution so break
                        break

                # If you comment this out we will keep looking through other combinations
                # of upper/front but it isn't worth it.  It takes ~3x as long to run and
                # didn't bring down the average number of moves at all across a 50 cube sample.
                #
                # Same goes for the break above...it isn't worth commenting it out
                if min_solution_length is not None:
                    break

            if min_solution_length is not None:
                break

        if min_solution_length is None:
            raise SolveError("Could not find parity free solution for centers")

        log.info("group center solution (%d steps): %s" % (min_solution_length, ' '.join(min_solution)))
        self.state = copy(min_solution_state)
        self.solution = copy(min_solution)
        self.solution.append('CENTERS_SOLVED')

    def get_last_two_555_edge_pattern_id(self, count):
        pattern_id = None
        edges_of_interest = [52, 53, 54, 22, 23, 24, 2, 3, 4, 104, 103, 102]

        def colors_in(squares):
            results = []
            for x in squares:
                results.append(self.state[x])
            return sorted(list(set(results)))

        for rotate_double_y in (False, True):

            if rotate_double_y:
                self.rotate_y()
                self.rotate_y()

            # Build a string that represents the pattern of colors for the U-south and U-north edges
            sides_in_edges_of_interest = []
            edges_of_interest_state = []

            for square_index in edges_of_interest:
                value = self.state[square_index]
                edges_of_interest_state.append(value)

                if value not in sides_in_edges_of_interest:
                    sides_in_edges_of_interest.append(value)

            edges_of_interest_state = ''.join(edges_of_interest_state)

            for (index, value) in enumerate(sides_in_edges_of_interest):
                edges_of_interest_state = edges_of_interest_state.replace(value, str(index))

            log.info("edges_of_interest_state: rotate_double_y %s,  %s" % (rotate_double_y, edges_of_interest_state))

            # Now use that string to ID the parity scenario
            if edges_of_interest_state in ('010101222333',
                                           '010101222000',
                                           '012221221002',
                                           '010101111222',
                                           '010101222111',
                                           '010101000222'):
                pattern_id = 1

            elif edges_of_interest_state in ('001222110222',
                                             '011233223001',
                                             '001112120211',
                                             '001223130312',
                                             '010222101222',
                                             '001220100012',
                                             '000112020201',
                                             '010102000221',
                                             '012101121012',
                                             '012103220331',
                                             '001220110002',
                                             '000112000221',
                                             '001112110221',
                                             '001223233011',
                                             '001223110332'):
                pattern_id = 2

            elif edges_of_interest_state in ('001223213031',
                                             '000112102020',
                                             '001222212021',
                                             '000112122000',
                                             '001222222011',
                                             '001220210001',
                                             '001222120212',
                                             '001112112021'):
                pattern_id = 3
                self.rotate_x_reverse()
                self.rotate_z()

            elif edges_of_interest_state in ('011233203021',
                                             '011200220001',
                                             '012100220001',
                                             '000122102010',
                                             '011222222001',
                                             '012321301032',
                                             '011122102011',
                                             '000122112000',
                                             '001220200011',
                                             '011222202021'):
                pattern_id = 4
                self.rotate_x_reverse()
                self.rotate_z_reverse()

            elif edges_of_interest_state in ('010101232323',):
                pattern_id = 5
                self.rotate_x_reverse()
                self.rotate_z()

            elif edges_of_interest_state in ('010232323101', '010232121303', '010202121000'):
                pattern_id = 6
                self.rotate_x_reverse()
                self.rotate_z()

            elif edges_of_interest_state in ('010232101323',):
                pattern_id = 7

            elif edges_of_interest_state in ('010121202111', '010222202121'):
                pattern_id = 8

            elif edges_of_interest_state in ('xyz',):
                pattern_id = 9

            elif edges_of_interest_state in ('012103123032',
                                             '012100200021'):
                pattern_id = 10

            elif edges_of_interest_state in ('xyz',):
                pattern_id = 11

            elif edges_of_interest_state in ('xyz',):
                pattern_id = 12

            elif edges_of_interest_state in ('xyz',):
                pattern_id = 14

            elif self.state[22] == self.state[53] and self.state[23] == self.state[52]:
                pattern_id = 1

            elif self.state[24] == self.state[53] and self.state[23] == self.state[54]:
                pattern_id = 1

            elif colors_in((22, 23, 52, 53)) == colors_in((4, 102)):
                pattern_id = 2

            elif colors_in((23, 53)) == colors_in((2, 104, 4, 102)):
                pattern_id = 2

            # playground...for testing solutions
            elif edges_of_interest_state in ('xyz',):
                pattern_id = 2

            if pattern_id:
                break

        if pattern_id is None:
            raise SolveError("Could not determine 5x5x5 last two edges pattern ID")

        return pattern_id

    def pair_last_two_555_edges(self):
        attempt = 0

        while True:
            count = self.get_non_paired_edges_count()

            if not count:
                return

            if count > 2:
                raise SolveError("There are %d un-paired edges but 2 is the max we should see" % count)

            attempt += 1
            if attempt > 20:
                raise StuckInALoop("5x5x5 edge parity")

            # All of the solutions here need the unpaired edges on U
            # http://www.rubik.rthost.org/5x5x5_edges.htm
            #
            # and here 1, 2, 7, 8, 9, and 10 need the unpaired edges on U
            # but 3, 4, 5, and 6 need the unpaired edges on F
            # https://i.imgur.com/wsTqj.png
            #
            # Put the unpaired edges on U, we'll work some magic to handle 3, 4, 5 and 6

            U_count = len(self.sideU.non_paired_edges(True, True, True, True))
            F_count = len(self.sideF.non_paired_edges(False, True, False, True))
            B_count = len(self.sideB.non_paired_edges(False, True, False, True))
            D_count = len(self.sideD.non_paired_edges(True, True, True, True))

            if count == 1:
                if U_count:
                    pass

                elif F_count:
                    self.rotate_x()

                elif B_count:
                    self.rotate_x_reverse()

                elif D_count:
                    self.rotate_x()
                    self.rotate_x()

                self.make_U_south_have_unpaired_edge()

            elif count == 2:

                if F_count == 2:
                    self.rotate_x()

                elif B_count == 2:
                    self.rotate_x_reverse()

                elif D_count == 2:
                    self.rotate_x()
                    self.rotate_x()

                elif U_count == 2:
                    while self.sideU.south_edge_paired():
                        self.rotate("U")

                else:

                    # D until we get a non-paired edge to D-north
                    if D_count:
                        while self.sideD.north_edge_paired():
                            self.rotate("D")

                    # U until we get a non-paired edge to U-south
                    if U_count:
                        while self.sideU.south_edge_paired():
                            self.rotate("U")

                    # F until we get a non-paired edge to F-east
                    if F_count:
                        if not self.sideF.east_edge_paired():
                            self.rotate("R2")
                            self.rotate("B")

                        if not self.sideF.west_edge_paired():
                            self.rotate("L2")
                            self.rotate("B'")

                    # B until we get a non-paired edge to B-north
                    if B_count:
                        if not self.sideB.east_edge_paired():
                            self.rotate("B'")

                        if not self.sideB.west_edge_paired():
                            self.rotate("B")

                    U_count = len(self.sideU.non_paired_edges(True, True, True, True))
                    F_count = len(self.sideF.non_paired_edges(False, True, False, True))
                    B_count = len(self.sideB.non_paired_edges(False, True, False, True))
                    D_count = len(self.sideD.non_paired_edges(True, True, True, True))

                    if U_count == 2:
                        while self.sideU.south_edge_paired():
                            self.rotate("U")

                    elif not self.sideU.south_edge_paired() and not self.sideD.north_edge_paired():
                        self.rotate_x()

                    elif not self.sideU.north_edge_paired() and not self.sideD.south_edge_paired():
                        self.rotate_x_reverse()

                    elif not self.sideU.north_edge_paired() and not self.sideD.north_edge_paired():
                            self.rotate("F2")

                    elif not self.sideU.west_edge_paired() and not self.sideD.west_edge_paired():
                        self.rotate_z()

                    elif not self.sideU.east_edge_paired() and not self.sideD.east_edge_paired():
                        self.rotate_z_reverse()

                    elif not self.sideU.east_edge_paired() and not self.sideD.north_edge_paired():
                        self.rotate("U")
                        self.rotate_x()

                    elif not self.sideU.south_edge_paired() and not self.sideD.east_edge_paired():
                        self.rotate("D'")
                        self.rotate_x()

                    elif not self.sideU.north_edge_paired() and not self.sideF.east_edge_paired():
                        self.rotate("F'")

                    elif not self.sideU.north_edge_paired() and not self.sideF.west_edge_paired():
                        self.rotate("F")

                    else:
                        raise SolveError("count %d, U_count %d, F_count %d, B_count %d, D_count %d" %
                            (count, U_count, F_count, B_count, D_count))

                self.make_U_south_have_unpaired_edge()

                if not self.sideU.west_edge_paired():
                    self.rotate("L'")
                    self.rotate("B'")
                elif not self.sideU.east_edge_paired():
                    self.rotate("R")
                    self.rotate("B")

            # At this point the unpaired edge(s) will be on U with one on the south side
            # and the other (if there are two) on the north side. Raise SolveError() if
            # that is not the case.
            U_count = len(self.sideU.non_paired_edges(True, True, True, True))
            L_count = len(self.sideL.non_paired_edges(True, True, True, True))
            F_count = len(self.sideF.non_paired_edges(False, True, False, True))
            R_count = len(self.sideR.non_paired_edges(True, True, True, True))
            B_count = len(self.sideB.non_paired_edges(False, True, False, True))
            D_count = len(self.sideD.non_paired_edges(True, True, True, True))

            if U_count != count or L_count or F_count or R_count or B_count or D_count:
                raise SolveError("count %d, U_count %d, L_count %d, F_count %d, R_count %d, B_count %d, D_count %d" %
                    (count, U_count, L_count, F_count, R_count, B_count, D_count))

            pattern_id = self.get_last_two_555_edge_pattern_id(count)

            # No 1 on https://imgur.com/r/all/wsTqj
            if pattern_id == 1:
                for step in "2R2 B2 U2 2L U2 2R' U2 2R U2 F2 2R F2 2L' B2 2R2".split():
                    self.rotate(step)

            # No 2 on https://imgur.com/r/all/wsTqj or the "Two edge crossover" on http://www.rubik.rthost.org/5x5x5_edges.htm
            elif pattern_id == 2 or pattern_id == 11:
                for step in "2L' U2 2L' U2 F2 2L' F2 2R U2 2R' U2 2L2".split():
                    self.rotate(step)

            # No 3 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 3:
                for step in "2D R F' U R' F 2D'".split():
                    self.rotate(step)

            # No 4 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 4:
                for step in "2D' L' U' L F' L F L' 2D".split():
                    self.rotate(step)

            # No 5 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 5:
                for step in "2D 2U' R F' U R' F 2D' 2U".split():
                    self.rotate(step)

            # No 6 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 6:
                for step in "2U2 2R2 F2 2U2 U2 F2 2R2 2U2".split():
                    self.rotate(step)

            # No 7 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 7:
                for step in "F2 2R D2 2R' F2 U2 F2 2L B2 2L'".split():
                    self.rotate(step)

            # No 8 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 8:
                for step in "2R2 B2 2R' U2 2R' U2 B2 2R' B2 2R B2 2R' B2 2R2".split():
                    self.rotate(step)

            # No 9 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 9:
                for step in "2L U2 2L2 U2 2L' U2 2L U2 2L' U2 2L2 U2 2L".split():
                    self.rotate(step)

            # No 10 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 10:
                for step in "2R' U2 2R2 U2 2R U2 2R' U2 2R U2 2R2 U2 2R'".split():
                    self.rotate(step)

            # "Two edge crossover" on http://www.rubik.rthost.org/5x5x5_edges.htm
            elif pattern_id == 11 or pattern_id == 2:
                for step in "2L' U2 2L' U2 F2 2L' F2 2R U2 2R' U2 2L2".split():
                    self.rotate(step)

            # "Flip one edge element" on http://www.rubik.rthost.org/5x5x5_edges.htm
            # The south middle edge needs to be flipped
            elif pattern_id == 12:
                for step in "2R2 B2 U2 2L U2 2R' U2 2R U2 F2 2R F2 2L' B2 2R2".split():
                    self.rotate(step)

            # "Flip two edge elements" (the 2nd one) on http://www.rubik.rthost.org/5x5x5_edges.htm
            elif pattern_id == 14:
                # This doesn't work like it claims to on the website

                self.rotate_x_reverse()
                self.rotate("2L'")
                self.rotate("2R")

                for step in "F R F' U F' U' F".split():
                    self.rotate(step)

                self.rotate_x()
                self.rotate("2L")
                self.rotate("2R'")

            # playground
            elif pattern_id == 15:
                self.print_cube()

                # 1
                for step in "2R2 B2 U2 2L U2 2R' U2 2R U2 F2 2R F2 2L' B2 2R2".split():
                    self.rotate(step)

                log.info('\n\n\n')
                self.print_cube()
                sys.exit(0)
            else:
                raise ImplementThis("Add support for 5x5x5 pattern_id %d" % pattern_id)

    def get_wing_value(self, wing):
        if isinstance(wing, tuple) or isinstance(wing, list):
            square_index = wing[0]
        else:
            square_index = wing

        side = self.get_side_for_index(square_index)
        partner_index = side.get_wing_partner(square_index)

        if square_index < partner_index:
            return (self.state[square_index], self.state[partner_index])
        else:
            return (self.state[partner_index], self.state[square_index])

    def pair_two_555_edges(self, edge):
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        self.move_wing_to_F_west(edge)

        # Work with the edge in the middle of the F west side
        # TODO the 1 here for edge_west_pos should not be hard coded
        # it will not be 1 for 7x7x7
        target_wing = self.sideF.edge_west_pos[1]
        target_wing_value = self.get_wing_value(target_wing)

        sister_wings = self.get_wings(target_wing, remove_if_in_same_edge=True)

        if not sister_wings:
            # If we are here then both sister wings are on the same edge but are flipped the wrong way
            # Do "Flip one edge element" from http://www.rubik.rthost.org/5x5x5_edges.htm
            self.rotate_z()

            for step in "2R2 B2 U2 2L U2 2R' U2 2R U2 F2 2R F2 2L' B2 2R2".split():
                self.rotate(step)

            return True

        # Move sister wing to F-east
        sister_wing = sister_wings[0]
        self.move_wing_to_F_east(sister_wing)

        # The sister wing is in the right location but does it need to be flipped?
        sister_wing = self.get_wings_on_edge(target_wing, 'F', 'R')[0]
        sister_wing_value = self.get_wing_value(sister_wing)

        if target_wing_value != sister_wing_value:

            for step in ("R", "U'", "B'", "R2"):
                self.rotate(step)
            sister_wing = self.get_wings_on_edge(target_wing, 'F', 'R')[0]
            sister_wing_value = self.get_wing_value(sister_wing)


        # If there are no unpaired wings on U,B or D then we cannot pair this wing
        # without breaking some other already paired wing. I originally returned False
        # here but there are scenarios where you have to pair the wing even though
        # it means unpairing some other wing, else you get yourself in a situation
        # where you cannot solve the edges.
        if (self.sideU.all_wings_paired() and
            self.sideB.all_wings_paired() and
            self.sideD.all_wings_paired()):

            # Now that that two edges on F are in place, put an unpaired edge at U-west
            self.make_U_west_have_unpaired_edge()

        else:
            # Now that that two edges on F are in place, put an unpaired wing at U-west
            self.make_U_west_have_unpaired_wing()

        if sister_wing[0] == 60:

            # The U F' steps are not needed but makes troubleshooting easier
            # as it puts the side you paired back at the front
            #for step in ("2U", "L'", "U'", "L", "2U'", "U", "F'"):
            for step in ("2U", "L'", "U'", "L", "2U'"):
                self.rotate(step)

        elif sister_wing[0] == 70:

            # Move the unpaired wing at U-west to U-east
            self.rotate("U2")

            # The U F' steps are not needed but makes troubleshooting easier
            # as it puts the side you paired back at the front
            #for step in ("3U'", "R", "U", "R'", "3U", "U", "F'"):
            for step in ("3U'", "R", "U", "R'", "3U"):
                self.rotate(step)

        else:
            raise SolveError("sister_wing %s is in the wrong position" % str(sister_wing))

        current_non_paired_wings_count = self.get_non_paired_wings_count()

        if current_non_paired_wings_count < original_non_paired_wings_count:
            return True

        return False

    def find_moves_to_reach_state(self, wing_to_move, target_face_side):
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        orig_f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
        orig_f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
        orig_f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
        orig_f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])

        orig_r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
        orig_r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])
        orig_r_east_top = self.get_wing_value(self.sideR.edge_east_pos[0])
        orig_r_east_bottom = self.get_wing_value(self.sideR.edge_east_pos[1])

        orig_b_west_top = self.get_wing_value(self.sideB.edge_west_pos[0])
        orig_b_west_bottom = self.get_wing_value(self.sideB.edge_west_pos[1])
        orig_b_east_top = self.get_wing_value(self.sideB.edge_east_pos[0])
        orig_b_east_bottom = self.get_wing_value(self.sideB.edge_east_pos[1])

        orig_l_west_top = self.get_wing_value(self.sideL.edge_west_pos[0])
        orig_l_west_bottom = self.get_wing_value(self.sideL.edge_west_pos[1])
        orig_l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
        orig_l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])

        orig_center_corner_state = self.get_center_corner_state()

        wing_to_move_value = sorted(self.get_wing_value(wing_to_move))

        #log.info("orig_f_west_top %s, orig_f_west_bottom %s, orig_r_west_top %s, orig_r_west_bottom %s, orig_b_west_top %s, orig_b_west_bottom %s, wing_to_move_value %s, wing_to_move_value %s" %
        #    (orig_f_west_top, orig_f_west_bottom, orig_r_west_top, orig_r_west_bottom, orig_b_west_top, orig_b_west_bottom, wing_to_move, wing_to_move_value))

        filename = 'utils/all_3x3x3_moves_6_deep.txt'
        with open(filename, 'r') as fh:
            self.print_cube()
            count = 0
            for line in fh:
                count += 1
                steps = line.strip().split()

                for step in steps:
                    self.rotate(step)

                if count % 10000 == 0:
                    log.info("count %d, step len %d" % (count, len(steps)))

                '''
                f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
                f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])
                r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
                r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])
                r_east_top = self.get_wing_value(self.sideR.edge_east_pos[0])
                r_east_bottom = self.get_wing_value(self.sideR.edge_east_pos[1])
                b_west_top = self.get_wing_value(self.sideB.edge_west_pos[0])
                b_west_bottom = self.get_wing_value(self.sideB.edge_west_pos[1])
                b_east_top = self.get_wing_value(self.sideB.edge_east_pos[0])
                b_east_bottom = self.get_wing_value(self.sideB.edge_east_pos[1])

                l_west_top = self.get_wing_value(self.sideL.edge_west_pos[0])
                l_west_bottom = self.get_wing_value(self.sideL.edge_west_pos[1])
                l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
                l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])
                '''

                # For SLICE-FORWARD
                if target_face_side == 'F-east':
                    # Find sequence that moves wing_to_move to (40, 53)
                    # F-west must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])

                    f_east_top = sorted(self.get_wing_value(self.sideF.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        f_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'R-east':
                    # Find sequence that moves wing_to_move to (56, 69)
                    # F-west and R-west must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
                    r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
                    r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])

                    r_east_top = sorted(self.get_wing_value(self.sideR.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        r_west_top == orig_r_west_top and
                        r_west_bottom == orig_r_west_bottom and
                        r_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'B-east':
                    # Find sequence that moves wing_to_move to (21, 72)
                    # F-west, R-west, and B-west edges must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
                    r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
                    r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])
                    b_west_top = self.get_wing_value(self.sideB.edge_west_pos[0])
                    b_west_bottom = self.get_wing_value(self.sideB.edge_west_pos[1])

                    b_east_top = sorted(self.get_wing_value(self.sideB.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        r_west_top == orig_r_west_top and
                        r_west_bottom == orig_r_west_bottom and
                        b_west_top == orig_b_west_top and
                        b_west_bottom == orig_b_west_bottom and
                        b_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                # For SLICE-BACK
                elif target_face_side == 'F-west':
                    # Find sequence that moves wing_to_move to (24, 37)
                    # F-east must not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    f_west_top = sorted(self.get_wing_value(self.sideF.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        f_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'L-west':
                    # Find sequence that moves wing_to_move to (21, 72)
                    # F-east and L-east ust not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])
                    l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
                    l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    l_west_top = sorted(self.get_wing_value(self.sideL.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        l_east_top == orig_l_east_top and
                        l_east_bottom == orig_l_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        l_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'B-west':
                    # Find sequence that moves wing_to_move to (56, 69)
                    # F-east, L-east and B-east must not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])
                    l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
                    l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])
                    b_east_top = self.get_wing_value(self.sideB.edge_east_pos[0])
                    b_east_bottom = self.get_wing_value(self.sideB.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    b_west_top = sorted(self.get_wing_value(self.sideB.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        l_east_top == orig_l_east_top and
                        l_east_bottom == orig_l_east_bottom and
                        b_east_top == orig_b_east_top and
                        b_east_bottom == orig_b_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        b_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                else:
                    raise ImplementThis("target_face_side %s" % target_face_side)

                self.state = copy(original_state)
                self.solution = copy(original_solution)

                if found_solution:
                    log.warning("solution to move %s to %s is %s" % (wing_to_move, target_face_side, ' '.join(steps)))
                    sys.exit(1)

            log.warning("Explored %d moves in %s but did not find a solution" % (count, filename))
            sys.exit(1)

    def pair_eight_444_edges(self, wing_to_pair):
        """
        Sections are:
        - PREP-FOR-2U-SLICE
        - 2U L R' D U L' R
        - PREP-FOR-REVERSE-2U-SLICE
        - 2U'
        """

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = len(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        self.rotate_edge_to_F_west(wing_to_pair)

        '''
        log.info("PREP-FOR-2U-SLICE (begin)")
        self.print_cube()
        '''

        # Work with the wing at the bottom of the F-west edge
        # Move the sister wing to the top of F-east
        target_wing = self.sideF.edge_west_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_F_east:
            log.warning("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'F-east')
            raise ImplementThis("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_F_east[sister_wing]

        for step in steps.split():
            self.rotate(step)
        self.verify_all_centers_solved()


        # Work with the wing at the bottom of the R-west edge
        # Move the sister wing to the top of R-east
        target_wing = self.sideR.edge_west_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_R_east:
            log.warning("lookup_table_444_sister_wing_to_R_east needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'R-east')
            raise ImplementThis("lookup_table_444_sister_wing_to_R_east needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_R_east[sister_wing]

        if steps:
            for step in steps.split():
                self.rotate(step)
        else:
            log.debug("%s cannot be moved to R-east" % pformat(sister_wing))
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False


        # Work with the wing at the bottom of the B-west edge
        # Move the sister wing to the top of B-east
        target_wing = self.sideB.edge_west_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]

        '''
        if sister_wing not in lookup_table_444_sister_wing_to_B_east:
            log.warning("lookup_table_444_sister_wing_to_B_east needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'B-east')
            raise ImplementThis("lookup_table_444_sister_wing_to_B_east needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_B_east[sister_wing]

        if steps:
            for step in steps.split():
                self.rotate(step)
        else:
            log.debug("%s cannot be moved to B-east" % pformat(sister_wing))
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        # At this point we are setup to slice forward and pair 3 edges
        '''
        log.info("PREP-FOR-2U-SLICE (end)....SLICE (begin)")
        self.print_cube()
        '''
        for step in "2U L R' D U L' R".split():
            self.rotate(step)
        '''
        log.info("SLICE (end)...PREP-FOR-2U'-SLICE-BACK (begin)")
        self.print_cube()
        '''

        # PREP-FOR-2U-SLICE 2U L R' D U L' R PREP-FOR-REVERSE-2U-SLICE 2U'
        # Now set things up so that when we slice back we pair another 3 edges.
        # Even if we didn't do the work to set these up to pair we would still
        # have to move unpaired edges into F-west, F-east, B-west and B-east so
        # if you are going to go through all of the moves to do that you may as
        # well set things up to pair on the slice back.

        # Work with the wing on the bottom of F-east
        # Move the sister wing to the top of F-west
        target_wing = self.sideF.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_F_west:
            log.warning("lookup_table_444_sister_wing_to_F_west needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'F-west')
            raise ImplementThis("lookup_table_444_sister_wing_to_F_west needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_F_west[sister_wing]

        if steps:
            for step in steps.split():
                self.rotate(step)
        else:
            log.debug("%s cannot be moved to F-west" % pformat(sister_wing))
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        # Work with the wing on the bottom of L-east
        # Move the sister wing to the top of L-west
        target_wing = self.sideL.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_L_west:
            log.warning("lookup_table_444_sister_wing_to_L_west needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'L-west')
            raise ImplementThis("lookup_table_444_sister_wing_to_L_west needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_L_west[sister_wing]

        if steps:
            for step in steps.split():
                self.rotate(step)
        else:
            log.debug("%s cannot be moved to L-west" % pformat(sister_wing))
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        # Work with the wing on the bottom of B-east
        # Move the sister wing to the top of B-west
        target_wing = self.sideB.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_B_west:
            log.warning("lookup_table_444_sister_wing_to_B_west needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'B-west')
            raise ImplementThis("lookup_table_444_sister_wing_to_B_west needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_B_west[sister_wing]

        if steps:
            for step in steps.split():
                self.rotate(step)
        else:
            log.debug("%s cannot be moved to B-west" % pformat(sister_wing))
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        '''
        log.info("PREP-FOR-2U'-SLICE-BACK (end)...SLICE BACK (begin)")
        self.print_cube()
        '''
        self.rotate("2U'")
        '''
        log.info("SLICE BACK (end)")
        self.print_cube()
        self.verify_all_centers_solved()
        '''

        current_non_paired_wings_count = self.get_non_paired_wings_count()

        log.info("pair_eight_444_edges()    paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             len(self.solution) - original_solution_len,
             current_non_paired_wings_count))

        return True

    def pair_two_444_edges(self, edge, pair_multiple_edges_at_once):
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_solution_len = len(self.solution)

        if original_non_paired_wings_count == 2:
            raise SolveError("pair_last_two_444_edges() should be used when there are only 2 edges left")

        #log.info("pair_two_444_edges count %s, pair_multiple_edges_at_once %s" %
        #    (original_non_paired_wings_count, pair_multiple_edges_at_once))
        self.rotate_edge_to_F_west(edge)

        # Work with the wing at the bottom of the F-west edge
        target_wing = self.sideF.edge_west_pos[-1]

        # Move the sister wing to F east...this uses a small lookup table
        # that I built manually. This puts the sister wing at F-east in the correct
        # orientation (it will not need to be flipped). We used to just move the
        # sister wing to F-east but then sometimes we would need to "R U' B' R2"
        # to flip it around.
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_F_east:
            log.warning("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'F-east')
            raise ImplementThis("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_F_east[sister_wing]

        for step in steps.split():
            self.rotate(step)

        # Now that that two edges on F are in place, put an unpaired edge at U-west
        if pair_multiple_edges_at_once:

            # The unpaired edge that we place at U-west should contain the
            # sister wing of the wing that is at the bottom of F-east. This
            # will allow us to pair two wings at once.
            wing_bottom_F_east = self.sideF.edge_east_pos[-1]
            sister_wing_bottom_F_east = self.get_wings(wing_bottom_F_east)[0]

            if sister_wing_bottom_F_east not in lookup_table_444_sister_wing_to_U_west:
                raise ImplementThis("sister_wing_bottom_F_east %s" % pformat(sister_wing_bottom_F_east))

            steps = lookup_table_444_sister_wing_to_U_west[sister_wing_bottom_F_east]

            # If steps is None it means sister_wing_bottom_F_east is at (37, 24)
            # which is the top wing on F-west. If that is the case we can't pair
            # two edges at once so just put some random unpaired edge at U-west
            if steps == None:
                self.make_U_west_have_unpaired_edge()
            else:
                for step in steps.split():
                    self.rotate(step)
        else:
            self.make_U_west_have_unpaired_edge()

        for step in ("2U", "L'", "U'", "L", "2U'"):
            self.rotate(step)

        current_non_paired_wings_count = self.get_non_paired_wings_count()

        log.info("pair_two_444_edges()      paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             len(self.solution) - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count < original_non_paired_wings_count:
            return True

        raise SolveError("Went from %d to %d non_paired_edges" %
            (original_non_paired_wings_count, current_non_paired_wings_count))
        return False

    def pair_last_two_444_edges(self, edge):
        original_solution_len = len(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        # Put one unpaired edge on F west
        self.rotate_edge_to_F_west(edge)
        pos1 = self.sideF.edge_west_pos[-1]

        # Put the other unpaired edge on F east...this uses a small lookup table
        # that I built manually. This puts the sister wing at F-east in the correct
        # orientation (it will not need to be flipped). We used to just move the
        # sister wing to F-east but then sometimes we would need to "R F' U R' F"
        # to flip it around.
        sister_wing = self.get_wings(pos1)[0]

        steps = lookup_table_444_last_two_edges_place_F_east[sister_wing]
        for step in steps.split():
            self.rotate(step)

        # "Solving the last 4 edge blocks" in
        # http://www.rubiksplace.com/cubes/4x4/
        for step in ("2D", "R", "F'", "U", "R'", "F", "2D'"):
            self.rotate(step)

        current_non_paired_wings_count = self.get_non_paired_wings_count()

        log.info("pair_last_two_444_edges() paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             len(self.solution) - original_solution_len,
             current_non_paired_wings_count))

    def group_edges_444(self):
        """
        I spent a lot of time in this area but it is still more moves than I would
        like (45 to 50 on average).  This section needs a lookup table but building
        a lookup table that doesn't undo the 4 centers is challenging. pair_eight_444_edges()
        can pair 6, 7 or 8 edges at a time (it depends on how the stars align).  For that
        scenario there are 8 edges that we are working with that if placed in the right
        position will pair when we slice over and slice back (2U L R' D U L' R 2U').

        Of the 12 edges, we care about the placement of 8 of them but don't care at all
        about the other 4 so there would be 12!/4! or 19,958,400 entries in the lookup
        table.  That table would get the edges in the positions needed so they are paired
        when we 2U L R' D U L' R 2U'.  Today we typically pair 7 edges at a time in ~26 moves
        but 8 of those moves are the slice over/back which we cannot get rid of. So we are
        spending ~18 moves to get these 8 edges into position...that is where the lookup table
        would save us some moves.

        After that we should have 4 unpaired edges left. Today these last four edges are typically
        resolved via one call to pair_two_444_edges() and one call to pair_last_two_444_edges(),
        each of which takes an average of 12 moves. 24 moves to do the last 4 edges seems high, to
        be sure we could save some moves by having a pair_four_444_edges() function.  We need a
        slice over/back sequence for pairing 4 edges at a time.

        If we build a lookup table for this there are 12!/8! or 11,880 ways they can be arranged.

        TODO:
        - pair_eight_444_edges() returns False a lot..investigate
        - pair_eight_444_edges() tends to pair 7 at once...why 7?
        - come up with a slice sequence for pairing 4 edges at once
        """

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = len(self.solution)

        # There are 12 edges, cycle through all 12 in terms of which edge we try to pair first.
        # Remember the one that results in the shortest solution that is free of PLL parity.
        original_non_paired_edges = self.get_non_paired_edges()
        min_solution_length = None
        min_solution_state = None
        min_solution = None

        # There are some cubes where I always hit PLL parity when I pair multiple
        # edges at a time, so try with this capability first and if we fail to find
        # a PLL free solution then turn it off.
        for pair_multiple_edges_at_once in (True, False):
            for init_wing_to_pair in original_non_paired_edges:
                log.info("init_wing_to_pair %20s" % pformat(init_wing_to_pair))

                while True:
                    non_paired_edges = self.get_non_paired_edges()
                    len_non_paired_edges = len(non_paired_edges)

                    if len_non_paired_edges >= 8:
                        if init_wing_to_pair:
                            wing_to_pair = init_wing_to_pair[0]
                            init_wing_to_pair = None
                        else:
                            wing_to_pair = non_paired_edges[0][0]

                        if not self.pair_eight_444_edges(wing_to_pair):
                            log.info("pair_eight_444_edges()    returned False")
                            self.pair_two_444_edges(wing_to_pair, pair_multiple_edges_at_once)

                    elif len_non_paired_edges > 2:
                        if init_wing_to_pair:
                            wing_to_pair = init_wing_to_pair[0]
                            init_wing_to_pair = None
                        else:
                            wing_to_pair = non_paired_edges[0][0]

                        self.pair_two_444_edges(wing_to_pair, pair_multiple_edges_at_once)

                    elif len_non_paired_edges == 2:
                        wing_to_pair = non_paired_edges[0][0]
                        self.pair_last_two_444_edges(wing_to_pair)

                    else:
                        break

                solution_len_minus_rotates = self.get_solution_len_minus_rotates(self.solution)

                if self.edge_solution_leads_to_pll_parity():
                    log.info("init_wing_to_pair %20s: edges solution length %d, leads to PLL parity" % (str(init_wing_to_pair), solution_len_minus_rotates - original_solution_len))
                else:
                    if min_solution_length is None or solution_len_minus_rotates < min_solution_length:
                        min_solution_length = solution_len_minus_rotates
                        min_solution_state = copy(self.state)
                        min_solution = copy(self.solution)
                        log.info("init_wing_to_pair %20s: edges solution length %d (NEW MIN)" % (str(init_wing_to_pair), solution_len_minus_rotates - original_solution_len))
                    else:
                        log.info("init_wing_to_pair %20s: edges solution length %d" % (str(init_wing_to_pair), solution_len_minus_rotates - original_solution_len))
                log.info('')

                # Restore to original state
                self.state = copy(original_state)
                self.solution = copy(original_solution)

            # If we were able to find a PLL free solution when pair_multiple_edges_at_once
            # was True then break, there is not point trying with pair_multiple_edges_at_once
            # False since those solutions will all be longer
            if min_solution_length:
                break
            else:
                log.warning("Could not find PLL free edge solution with pair_multiple_edges_at_once True")

        if min_solution_length:
            self.state = copy(min_solution_state)
            self.solution = copy(min_solution)

            if self.get_non_paired_edges_count():
                raise SolveError("All edges should be resolved")

            self.solution.append('EDGES_GROUPED')
        else:
            raise SolveError("Could not find a PLL free edge solution")

    def group_edges_555(self):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        # There are 12 edges, cycle through all 12 in terms of which edge we try to pair first.
        # Remember the one that results in the shortest solution that is free of PLL parity.
        original_non_paired_edges = self.get_non_paired_edges()
        min_solution_length = None
        min_solution_state = None
        min_solution = None

        for init_wing_to_pair in original_non_paired_edges:
            self.pair_two_555_edges(init_wing_to_pair[0])

            while True:
                non_paired_edges = self.get_non_paired_edges()

                if len(non_paired_edges) > 2:
                    wing_to_pair = non_paired_edges[0][0]
                    self.pair_two_555_edges(wing_to_pair)

                elif len(non_paired_edges) >= 1:
                    self.pair_last_two_555_edges()

                else:
                    break

            if min_solution_length is None or len(self.solution) < min_solution_length:
                min_solution_length = len(self.solution)
                min_solution_state = copy(self.state)
                min_solution = copy(self.solution)
                log.info("init_wing_to_pair %20s: edges solution length %d (NEW MIN)" % (str(init_wing_to_pair), min_solution_length))
            else:
                log.info("init_wing_to_pair %20s: edges solution length %d" % (str(init_wing_to_pair), min_solution_length))

            # Restore to original state
            self.state = copy(original_state)
            self.solution = copy(original_solution)

        if min_solution_length:
            self.state = copy(min_solution_state)
            self.solution = copy(min_solution)

            if self.get_non_paired_edges_count():
                raise SolveError("All edges should be resolved")

            self.solution.append('EDGES_GROUPED')
        else:
            raise SolveError("Could not find a PLL free edge solution")

    def group_edges(self):

        if self.size == 4:
            self.group_edges_444()
        elif self.size == 5:
            self.group_edges_555()

    def reduce(self):

        if self.size >= 4:
            self.group_centers()
            self.group_edges()

    def get_solution_len_minus_rotates(self, solution):
        count = 0
        size_str = str(self.size)

        for step in solution:
            if not step.startswith(size_str):
                count += 1

        return count

    def compress_solution(self):
        solution_string = ' '.join(self.solution)
        moves = set(self.solution)

        while True:
            original_solution_string = copy(solution_string)

            for move in moves:
                if move in ('CENTERS_SOLVED', 'EDGES_GROUPED'):
                    continue

                if move in ('x', 'y', 'z'):
                    raise Exception('compress_solution does not support move "%s"' % move)

                if move.endswith("2'"):
                    raise Exception('compress_solution does not support move "%s"' % move)

                if move.endswith("'"):
                    reverse_move = move[0:-1]
                else:
                    reverse_move = move + "'"

                # If the same half turn is done 2x in a row, remove it
                if move.endswith("2"):
                    solution_string = solution_string.replace(" %s %s " % (move, move), " ")

                else:
                    # If the same quarter turn is done 4x in a row, remove it
                    solution_string = solution_string.replace(" %s %s %s %s " % (move, move, move, move), " ")

                    # If the same quarter turn is done 3x in a row, replace it with one backwards move
                    solution_string = solution_string.replace(" %s %s %s " % (move, move, move), " %s " % reverse_move)

                    # If the same quarter turn is done 2x in a row, replace it with one half turn
                    # Do not bother doing this with whole cube rotations we will pull those out later
                    if not move.startswith(str(self.size)):
                        if move.endswith("'"):
                            solution_string = solution_string.replace(" %s %s " % (move, move), " %s2 " % move[0:-1])
                        else:
                            solution_string = solution_string.replace(" %s %s " % (move, move), " %s2 " % move)

                # "F F'" and "F' F" will cancel each other out, remove them
                solution_string = solution_string.replace(" %s %s " % (move, reverse_move), " ")
                solution_string = solution_string.replace(" %s %s " % (reverse_move, move), " ")

            if original_solution_string == solution_string:
                break

        # Remove full cube rotations by changing all of the steps that follow the cube rotation
        steps = solution_string.strip().split()
        final_steps = []
        rotations = []

        for (index, step) in enumerate(steps):
            if step.startswith(str(self.size)):
                rotations.append(apply_rotations(step, rotations))
            else:
                final_steps.append(apply_rotations(step, rotations))
        solution_string = ' '.join(final_steps)

        # We put some markers in the solution to track how many steps
        # each stage took...remove those markers
        solution_minus_markers = []
        self.steps_to_rotate_cube = 0
        self.steps_to_solve_centers = 0
        self.steps_to_group_edges = 0
        self.steps_to_solve_3x3x3 = 0
        index = 0

        # log.info("pre compress; %s" % ' '.join(self.solution))
        for step in solution_string.split():
            if step.startswith(str(self.size)):
                self.steps_to_rotate_cube += 1

            if step == 'CENTERS_SOLVED':
                self.steps_to_solve_centers = index
                index = 0
            elif step == 'EDGES_GROUPED':
                self.steps_to_group_edges = index
                index = 0
            else:
                solution_minus_markers.append(step)
                index += 1

        self.steps_to_solve_3x3x3 = index
        self.solution = solution_minus_markers

    def solve(self):
        """
        Assumes reduce() has already been called
        """
        if self.size == 2:
            steps = subprocess.check_output(['rubiks_2x2x2_solver.py', self.get_kociemba_string(True)]).decode('ascii').splitlines()[-1].strip().split()

            for step in steps:
                self.rotate(step)

        elif self.size == 3:
            self.solve_333()

        elif self.size >= 4:
            self.solve_333()
            self.compress_solution()

    def print_solution(self):
        print(' '.join(self.solution))
        print("%d steps to rotate entire cube" % self.steps_to_rotate_cube)
        print("%d steps to solve centers" % self.steps_to_solve_centers)
        print("%d steps to group edges" % self.steps_to_group_edges)
        print("%d steps to solve 3x3x3" % self.steps_to_solve_3x3x3)
        print("%d steps total" % len(self.solution))


# Only here so we can run vulture against this file without so many false positives
if __name__ == '__main__':
    # 4x4x4
    # cube = RubiksCube('LFBDUFLDBUBBFDFBLDLFRDFRRURFDFDLULUDLBLUUDRDUDUBBFFRBDFRRRRRRRLFBLLRDLDFBUBLFBLRLURUUBLBDUFUUFBD')

    # 5x5x5
    cube = RubiksCube('RFFFUDUDURBFULULFDBLRLDUFDBLUBBBDDURLRDRFRUDDBFUFLFURRLDFRRRUBFUUDUFLLBLBBULDDRRUFUUUBUDFFDRFLRBBLRFDLLUUBBRFRFRLLBFRLBRRFRBDLLDDFBLRDLFBBBLBLBDUUFDDD')
    cube.print_cube()
    cube.reduce()
    cube.solve()
    cube.print_cube()
    cube.print_solution()
