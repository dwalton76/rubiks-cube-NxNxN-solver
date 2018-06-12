#!/usr/bin/env python3

from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube222 import solved_222
from rubikscubennnsolver.RubiksCube333 import solved_333
from rubikscubennnsolver.RubiksCube444 import solved_444
from rubikscubennnsolver.RubiksCube555 import solved_555
from rubikscubennnsolver.RubiksCube666 import solved_666
from rubikscubennnsolver.RubiksCube777 import solved_777
from rubikscubennnsolver.RubiksCubeNNNEven import solved_888, solved_101010, solved_121212, solved_141414
from rubikscubennnsolver.RubiksCubeNNNOdd import solved_999, solved_111111, solved_131313, solved_151515, solved_171717
import json
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

test_cases = {
    "2x2x2" : [],
    "3x3x3" : [],
    "4x4x4" : [],
    "5x5x5" : [],
    "6x6x6" : [],
    "7x7x7" : [],
    "8x8x8" : [],
    "9x9x9" : [],
    "10x10x10" : [],
    "11x11x11" : [],
    "12x12x12" : [],
    "13x13x13" : [],
    "14x14x14" : [],
    "15x15x15" : [],
    "17x17x17" : [],
}

#for x in range(500):
for x in range(5):
    cube = RubiksCube(solved_222, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["2x2x2"].append(ks)

    cube = RubiksCube(solved_333, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["3x3x3"].append(ks)

    cube = RubiksCube(solved_444, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["4x4x4"].append(ks)

    cube = RubiksCube(solved_555, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["5x5x5"].append(ks)

    cube = RubiksCube(solved_666, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["6x6x6"].append(ks)

    cube = RubiksCube(solved_777, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["7x7x7"].append(ks)

    cube = RubiksCube(solved_888, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["8x8x8"].append(ks)

    cube = RubiksCube(solved_999, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["9x9x9"].append(ks)

    cube = RubiksCube(solved_101010, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["10x10x10"].append(ks)

    cube = RubiksCube(solved_111111, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["11x11x11"].append(ks)

    cube = RubiksCube(solved_121212, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["12x12x12"].append(ks)

    cube = RubiksCube(solved_131313, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["13x13x13"].append(ks)

    cube = RubiksCube(solved_141414, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["14x14x14"].append(ks)

    cube = RubiksCube(solved_151515, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["15x15x15"].append(ks)

    cube = RubiksCube(solved_171717, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["17x17x17"].append(ks)

print(json.dumps(test_cases, indent=4, sort_keys=True))

# Build cube in:
# https://www.speedsolving.com/forum/threads/arnauds-5x5x5-edge-pairing-method-examples.1447/
'''
cube = RubiksCube(solved_555)
for step in "Rw U Rw' U Rw U2 Rw' F' U Lw' U2 Lw U Lw' U Lw L2 R2 F2 B2 Rw U Rw' U Rw U2 Rw' F' U Lw' U2 Lw U Lw' U Lw L R' F2 D' B2 Rw U Rw' U Rw U2 Rw' F' U Lw' U2 Lw U Lw' U Lw".split():
    cube.rotate(step)
ks = cube.get_kociemba_string(True)
print(ks)
'''
