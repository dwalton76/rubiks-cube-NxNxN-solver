# standard libraries
import json
import logging
from collections import OrderedDict

# rubiks cube libraries
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCubeNNNEven import solved_888
from rubikscubennnsolver.RubiksCubeNNNOdd import solved_999

# from rubikscubennnsolver.RubiksCube222 import solved_222
# from rubikscubennnsolver.RubiksCube333 import solved_333
# from rubikscubennnsolver.RubiksCube444 import solved_444
# from rubikscubennnsolver.RubiksCube555 import solved_555
# from rubikscubennnsolver.RubiksCube666 import solved_666
# from rubikscubennnsolver.RubiksCube777 import solved_777

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(filename)12s %(levelname)8s: %(message)s")
log = logging.getLogger(__name__)

test_cases = OrderedDict()
test_cases["2x2x2"] = []
test_cases["3x3x3"] = []
test_cases["4x4x4"] = []
test_cases["5x5x5"] = []
test_cases["6x6x6"] = []
test_cases["7x7x7"] = []
test_cases["8x8x8"] = []
test_cases["9x9x9"] = []
test_cases["10x10x10"] = []
test_cases["11x11x11"] = []
test_cases["12x12x12"] = []
test_cases["13x13x13"] = []
test_cases["14x14x14"] = []
test_cases["15x15x15"] = []
test_cases["17x17x17"] = []

cubes = OrderedDict()
# cubes["2x2x2"] = RubiksCube(solved_222, 'URFDLB')
# cubes["3x3x3"] = RubiksCube(solved_333, 'URFDLB')
# cubes["4x4x4"] = RubiksCube(solved_444, 'URFDLB')
# cubes["5x5x5"] = RubiksCube(solved_555, 'URFDLB')
# cubes["6x6x6"] = RubiksCube(solved_666, 'URFDLB')
# cubes["7x7x7"] = RubiksCube(solved_777, 'URFDLB')
cubes["8x8x8"] = RubiksCube(solved_888, "URFDLB")
cubes["9x9x9"] = RubiksCube(solved_999, "URFDLB")
# cubes["10x10x10"] = RubiksCube(solved_101010, 'URFDLB')
# cubes["11x11x11"] = RubiksCube(solved_111111, 'URFDLB')
# cubes["12x12x12"] = RubiksCube(solved_121212, 'URFDLB')
# cubes["13x13x13"] = RubiksCube(solved_131313, 'URFDLB')
# cubes["14x14x14"] = RubiksCube(solved_141414, 'URFDLB')
# cubes["15x15x15"] = RubiksCube(solved_151515, 'URFDLB')
# cubes["17x17x17"] = RubiksCube(solved_171717, 'URFDLB')

for (size, cube) in cubes.items():
    log.info("size %s has cube %s" % (size, cube))
    for x in range(10):
        cube.re_init()
        cube.randomize()
        ks = cube.get_kociemba_string(True)
        test_cases[size].append(ks)

print(json.dumps(test_cases, indent=4))

# Build cube in:
# https://www.speedsolving.com/forum/threads/arnauds-5x5x5-edge-pairing-method-examples.1447/
"""
cube = RubiksCube(solved_555)
for step in "Rw U Rw' U Rw U2 Rw' F' U Lw' U2 Lw U Lw' U Lw L2 R2 F2 B2 Rw U Rw' U Rw U2 Rw' F' U Lw' U2 Lw U Lw' U Lw L R' F2 D' B2 Rw U Rw' U Rw U2 Rw' F' U Lw' U2 Lw U Lw' U Lw".split():
    cube.rotate(step)
ks = cube.get_kociemba_string(True)
print(ks)
"""
