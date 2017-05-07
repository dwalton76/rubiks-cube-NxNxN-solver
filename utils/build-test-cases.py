#!/usr/bin/env python2

"""
Solve any size rubiks cube:
- For 2x2x2 and 3x3x3 just solve it
- For 4x4x4 and larger, reduce to 3x3x3 and then solve

This is a work in progress
"""

from rubikscubennnsolver import RubiksCube
import json
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

# Ran this once to produce the output that is now test_cubes.json
solved_222 = 'UUUURRRRFFFFDDDDLLLLBBBB'
solved_333 = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'
solved_444 = 'UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB'
solved_555 = 'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB'

solved_666 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

solved_777 = 'UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'

test_cases = {
    "2x2x2" : [],
    "3x3x3" : [],
    "4x4x4" : [],
    "5x5x5" : [],
    "6x6x6" : [],
    "7x7x7" : [],
}

for x in range(50):
    cube = RubiksCube(solved_222)
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["2x2x2"].append(ks)

    cube = RubiksCube(solved_333)
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["3x3x3"].append(ks)

    cube = RubiksCube(solved_444)
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["4x4x4"].append(ks)

    cube = RubiksCube(solved_555)
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["5x5x5"].append(ks)

    cube = RubiksCube(solved_666)
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["6x6x6"].append(ks)

    cube = RubiksCube(solved_777)
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    test_cases["7x7x7"].append(ks)

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
