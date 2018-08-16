#!/usr/bin/env python3

from rubikscubennnsolver import symmetry_48
from rubikscubennnsolver.RubiksCube222 import RubiksCube222, rotate_222, solved_222
from rubikscubennnsolver.RubiksCube333 import RubiksCube333, rotate_333, solved_333
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, rotate_444, solved_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, rotate_555, solved_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, rotate_666, solved_666
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, rotate_777, solved_777
from rubikscubennnsolver.misc import parse_ascii_222, parse_ascii_333, parse_ascii_444, parse_ascii_555, parse_ascii_666, parse_ascii_777
from pprint import pformat
import logging
import math
import sys

def build_symmetry_48():
    """
    http://kociemba.org/math/symmetric.htm

    I ran this once to build symmetry_48
    """
    half_edge_rotations = (
        "x x y",
        "x x y'",
        "x y y",
        "z y y",
        "x' y y",
        "z' y y",
    )

    half_rotations = (
        "x x",
        "y y",
        "z z",
    )

    reflections_xyz = (
        "reflect-x",
        "reflect-y",
        "reflect-z",
    )

    quarter_rotations = (
        "x", "x'",
        "y", "y'",
        "z", "z'",
    )

    third_edge_rotations = (
        "x y",
        "x y'",
        "z y'",
        "x' y'",
    )

    rotations = [""]
    rotations.extend(quarter_rotations)
    rotations.extend(half_rotations)
    '''
    rotations.extend(quarter_rotations)
    rotations.extend(half_rotations)
    rotations.extend(half_edge_rotations)
    rotations.extend(third_edge_rotations)
    '''

    for a in quarter_rotations:
        for b in quarter_rotations + half_rotations:
            rotation = "%s %s" % (a, b)

            if rotation in ("x x x", "y y y", "z z z"):
                continue

            if ("x x'" in rotation or
                "x' x" in rotation or
                "y y'" in rotation or
                "y' y" in rotation or
                "z z'" in rotation or
                "z' z" in rotation):
                continue

            if rotation not in rotations:
                rotations.append(rotation)

    #log.info("rotations:\n%s" % pformat(rotations))
    #log.info("Found %d rotations" % len(rotations))

    reflections = [""]
    reflections.extend(reflections_xyz)

    cube = RubiksCube444('FLDFDLBDFBLFFRRBDRFRRURBRDUBBDLURUDRRBFFBDLUBLUULUFRRFBLDDUULBDBDFLDBLUBFRFUFBDDUBFLLRFLURDULLRU', 'URFDLB')
    #cube.print_cube()

    found_cubes = []
    tmp_state = cube.state[:]
    attempts = 0
    symmetry_48 = []

    for reflect in reflections:
        for rotate in rotations:
            cube.state = tmp_state[:]

            if reflect:
                cube.state = rotate_444(cube.state[:], reflect)

            if rotate:
                for step in rotate.split():
                    cube.state = rotate_444(cube.state[:], step)

            cube_state_string = ''.join(cube.state)

            if cube_state_string not in found_cubes:
                tmp = "%s %s" % (reflect, rotate)
                symmetry_48.append(tuple(tmp.strip().split()))
                #print("%d: %s %s" % (len(found_cubes) + 1, reflect, rotate))
                found_cubes.append(cube_state_string)
            attempts += 1

    symmetry_48 = tuple(symmetry_48)
    #print("attempts: %d" % attempts)
    log.info("symmetry_48 = \n%s\n" % pformat(symmetry_48))

    print("symmetry_48 = (")
    for seq in symmetry_48:
        print("    \"%s\"," % ' '.join(seq))
    print(")")


def print_reflect_x(size):
    per_side_size = size * size
    total_size = (per_side_size * 6) + 1
    reflect_x = [0]

    for side_index in range(1, 7):
        first_index_for_size = ((side_index-1) * per_side_size) + 1
        #log.info("side %d, first %d" % (side_index, first_index_for_size))

        if side_index == 1:
            for row in range(size):
                for col in range(size):
                    reflect_x.append(total_size - ((row + 1) * size) + col)

        elif side_index == 6:
            for row in range(size):
                for col in range(size):
                    reflect_x.append(((size - row - 1) * size) + col + 1)
        else:

            for row in range(size):
                if size == 2:
                    if row == 0:
                        sister_row = 1
                    elif row == 1:
                        sister_row = 0
                    else:
                        raise Exception("we should not be here")

                elif size == 3:
                    if row == 0:
                        sister_row = 2
                    elif row == 1:
                        sister_row = 1
                    elif row == 2:
                        sister_row = 0
                    else:
                        raise Exception("we should not be here")

                elif size == 4:
                    if row == 0:
                        sister_row = 3
                    elif row == 1:
                        sister_row = 2
                    elif row == 2:
                        sister_row = 1
                    elif row == 3:
                        sister_row = 0
                    else:
                        raise Exception("we should not be here")

                elif size == 5:
                    if row == 0:
                        sister_row = 4
                    elif row == 1:
                        sister_row = 3
                    elif row == 2:
                        sister_row = 2
                    elif row == 3:
                        sister_row = 1
                    elif row == 4:
                        sister_row = 0
                    else:
                        raise Exception("we should not be here")

                elif size == 6:
                    if row == 0:
                        sister_row = 5
                    elif row == 1:
                        sister_row = 4
                    elif row == 2:
                        sister_row = 3
                    elif row == 3:
                        sister_row = 2
                    elif row == 4:
                        sister_row = 1
                    elif row == 5:
                        sister_row = 0
                    else:
                        raise Exception("we should not be here")

                elif size == 7:
                    if row == 0:
                        sister_row = 6
                    elif row == 1:
                        sister_row = 5
                    elif row == 2:
                        sister_row = 4
                    elif row == 3:
                        sister_row = 3
                    elif row == 4:
                        sister_row = 2
                    elif row == 5:
                        sister_row = 1
                    elif row == 6:
                        sister_row = 0
                    else:
                        raise Exception("we should not be here")
                else:
                    raise Exception("implement this")

                #log.info("side %d, row %d, sister_row %d" % (side_index, row, sister_row))
                for col in range(size):
                    reflect_x.append(first_index_for_size + (sister_row * size) + col)

    print(reflect_x)


def print_reflect_y(size):
    per_side_size = size * size
    total_size = (per_side_size * 6) + 1
    reflect_y = [0]

    for side_index in range(1, 7):
        first_index_for_size = ((side_index-1) * per_side_size) + 1
        #log.info("side %d, first %d" % (side_index, first_index_for_size))

        if side_index in (2, 4) :
            for row in range(size):
                row_entries = []
                index = first_index_for_size + (row * size)

                for col in range(size):
                    row_entries.append(index+col)

                reflect_y.extend(list(reversed(row_entries)))

        elif side_index in (1, 6):

            for row in range(size):
                if size == 4:
                    if row == 0:
                        sister_row = 3
                    elif row == 1:
                        sister_row = 2
                    elif row == 2:
                        sister_row = 1
                    elif row == 3:
                        sister_row = 0
                    else:
                        raise Exception("we should not be here")
                else:
                    raise Exception("implement this")

                for col in range(size):
                    reflect_y.append(first_index_for_size + (sister_row * size) + col)

        elif side_index == 3:
            if size == 4:
                reflect_y.extend(list(reversed(list(map(int, "65 66 67 68".split())))))
                reflect_y.extend(list(reversed(list(map(int, "69 70 71 72".split())))))
                reflect_y.extend(list(reversed(list(map(int, "73 74 75 76".split())))))
                reflect_y.extend(list(reversed(list(map(int, "77 78 79 80".split())))))
            else:
                raise Exception("implement this")

        elif side_index == 5:
            if size == 4:
                reflect_y.extend(list(reversed(list(map(int, "33 34 35 36".split())))))
                reflect_y.extend(list(reversed(list(map(int, "37 38 39 40".split())))))
                reflect_y.extend(list(reversed(list(map(int, "41 42 43 44".split())))))
                reflect_y.extend(list(reversed(list(map(int, "45 46 47 48".split())))))
            else:
                raise Exception("implement this")

    print(reflect_y)


def print_reflect_z(size):
    per_side_size = size * size
    total_size = (per_side_size * 6) + 1
    reflect_z = [0]

    for side_index in range(1, 7):
        first_index_for_size = ((side_index-1) * per_side_size) + 1
        #log.info("side %d, first %d" % (side_index, first_index_for_size))

        if side_index in (1, 3, 5, 6) :
            for row in range(size):
                row_entries = []
                index = first_index_for_size + (row * size)

                for col in range(size):
                    row_entries.append(index+col)

                reflect_z.extend(list(reversed(row_entries)))

        elif side_index == 2:
            if size == 4:
                reflect_z.extend(list(reversed(list(map(int, "49 50 51 52".split())))))
                reflect_z.extend(list(reversed(list(map(int, "53 54 55 56".split())))))
                reflect_z.extend(list(reversed(list(map(int, "57 58 59 60".split())))))
                reflect_z.extend(list(reversed(list(map(int, "61 62 63 64".split())))))
            else:
                raise Exception("implement this")

        elif side_index == 4:
            if size == 4:
                reflect_z.extend(list(reversed(list(map(int, "17 18 19 20".split())))))
                reflect_z.extend(list(reversed(list(map(int, "21 22 23 24".split())))))
                reflect_z.extend(list(reversed(list(map(int, "25 26 27 28".split())))))
                reflect_z.extend(list(reversed(list(map(int, "29 30 31 32".split())))))
            else:
                raise Exception("implement this")

    print(reflect_z)


def print_cubes(filename):
    state = []
    with open(filename, 'r') as fh:
        for line in fh:
            if line.strip():
                state.append(line)
    state = ''.join(state)
    order = 'ULFRBD'

    len_state = len(state.replace('\n', '').replace(' ', ''))

    if len_state == 24:
        state = parse_ascii_222(state)
        cube = RubiksCube222(state, order)
        rotate_xxx = rotate_222

    elif len_state == 54:
        state = parse_ascii_333(state)
        cube = RubiksCube333(state, order)
        rotate_xxx = rotate_333

    elif len_state == 96:
        state = parse_ascii_444(state)
        cube = RubiksCube444(state, order)
        rotate_xxx = rotate_444

    elif len_state == 150:
        state = parse_ascii_555(state)
        cube = RubiksCube555(state, order)
        rotate_xxx = rotate_555

    elif len_state == 216:
        state = parse_ascii_666(state)
        cube = RubiksCube666(state, order)
        rotate_xxx = rotate_666

    elif len_state == 294:
        state = parse_ascii_777(state)
        cube = RubiksCube777(state, order)
        rotate_xxx = rotate_777

    else:
        raise Exception("cube has %d entries, what size is this?" % len_state)

    #cube.print_cube()
    tmp_state = cube.state[:]

    keepers = []

    for seq in symmetry_48:
        cube.state = tmp_state[:]

        for step in seq:
            cube.state = rotate_xxx(cube.state[:], step)

        if cube.state == tmp_state:
            log.info("================")
            log.info(' '.join(seq))
            log.info("================")
            cube.print_cube()
            log.info("\n\n\n\n\n")
            keepers.append(' '.join(seq))

    print("foo = (\n    \"" + '",\n    "'.join(keepers) + '"\n)')


def print_symmetry_swaps(size):
    order = 'ULFRBD'

    if size == 2:
        cube = RubiksCube222(solved_222, 'URFDLB')
        rotate_xxx = rotate_222
    elif size == 3:
        cube = RubiksCube333(solved_333, 'URFDLB')
        rotate_xxx = rotate_333
    elif size == 4:
        cube = RubiksCube444(solved_444, 'URFDLB')
        rotate_xxx = rotate_444
    elif size == 5:
        cube = RubiksCube555(solved_555, 'URFDLB')
        rotate_xxx = rotate_555
    elif size == 6:
        cube = RubiksCube666(solved_666, 'URFDLB')
        rotate_xxx = rotate_666
    elif size == 7:
        cube = RubiksCube777(solved_777, 'URFDLB')
        rotate_xxx = rotate_777
    else:
        assert False

    for (index, _) in enumerate(cube.state):
        cube.state[index] = str(index)

    orig_state = cube.state[:]
    cube.print_cube()

    for seq in symmetry_48:
        cube.state = orig_state[:]
        seq_str = ' '.join(seq)

        if seq_str in ("", "x", "x'", "y", "y'", "z", "z'"):
            continue

        for step in seq:
            cube.state = rotate_xxx(cube.state[:], step)

        print('    "%s" : (%s),' % (' '.join(seq), ', '.join(cube.state)))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    #print_reflect_y(4)
    #print_reflect_z(4)
    #build_symmetry_48()

    #print_reflect_x(2)
    #print_reflect_x(3)
    #print_reflect_x(4)
    #print_reflect_x(5)
    #print_reflect_x(6)
    #print_reflect_x(7)

    #print_symmetry_swaps(2)
    #print_symmetry_swaps(3)
    #print_symmetry_swaps(4)
    #print_symmetry_swaps(5)
    #print_symmetry_swaps(6)
    #print_symmetry_swaps(7)

    if len(sys.argv) < 2:
        print("symmetry.py FILENAME")
        sys.exit(1)

    filename = sys.argv[1]
    print_cubes(filename)
