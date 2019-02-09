
from copy import copy
from collections import OrderedDict
from pprint import pformat
from rubikscubennnsolver.RubiksSide import Side, SolveError, StuckInALoop, ImplementThis, NotSolving
from rubikscubennnsolver.misc import get_swap_count
import itertools
import json
import logging
import math
import random
import os
import shutil
import subprocess
import sys

log = logging.getLogger(__name__)

HTML_DIRECTORY = '/tmp/rubiks-cube-NxNxN-solver/'
HTML_FILENAME = os.path.join(HTML_DIRECTORY, 'index.html')

wing_str_map = {
    'UB' : 'UB',
    'BU' : 'UB',
    'UL' : 'UL',
    'LU' : 'UL',
    'UR' : 'UR',
    'RU' : 'UR',
    'UF' : 'UF',
    'FU' : 'UF',
    'LB' : 'LB',
    'BL' : 'LB',
    'LF' : 'LF',
    'FL' : 'LF',
    'RB' : 'RB',
    'BR' : 'RB',
    'RF' : 'RF',
    'FR' : 'RF',
    'DB' : 'DB',
    'BD' : 'DB',
    'DL' : 'DL',
    'LD' : 'DL',
    'DR' : 'DR',
    'RD' : 'DR',
    'DF' : 'DF',
    'FD' : 'DF',
    '--' : '--',
}


wing_strs_all = (
    'UB',
    'UL',
    'UR',
    'UF',
    'LB',
    'LF',
    'RB',
    'RF',
    'DB',
    'DL',
    'DR',
    'DF',
)


symmetry_48 = (
    (),
    ('x',),
    ("x'",),
    ('y',),
    ("y'",),
    ('z',),
    ("z'",),
    ('x', 'x'),
    ('y', 'y'),
    ('z', 'z'),
    ('x', 'y'),
    ('x', "y'"),
    ('x', 'z'),
    ('x', "z'"),
    ('x', 'y', 'y'),
    ('x', 'z', 'z'),
    ("x'", 'y'),
    ("x'", "y'"),
    ("x'", 'z'),
    ("x'", "z'"),
    ('y', 'x', 'x'),
    ('y', 'z', 'z'),
    ('z', 'x', 'x'),
    ('z', 'y', 'y'),
    ('reflect-x',),
    ('reflect-x', 'x'),
    ('reflect-x', "x'"),
    ('reflect-x', 'y'),
    ('reflect-x', "y'"),
    ('reflect-x', 'z'),
    ('reflect-x', "z'"),
    ('reflect-x', 'x', 'x'),
    ('reflect-x', 'y', 'y'),
    ('reflect-x', 'z', 'z'),
    ('reflect-x', 'x', 'y'),
    ('reflect-x', 'x', "y'"),
    ('reflect-x', 'x', 'z'),
    ('reflect-x', 'x', "z'"),
    ('reflect-x', 'x', 'y', 'y'),
    ('reflect-x', 'x', 'z', 'z'),
    ('reflect-x', "x'", 'y'),
    ('reflect-x', "x'", "y'"),
    ('reflect-x', "x'", 'z'),
    ('reflect-x', "x'", "z'"),
    ('reflect-x', 'y', 'x', 'x'),
    ('reflect-x', 'y', 'z', 'z'),
    ('reflect-x', 'z', 'x', 'x'),
    ('reflect-x', 'z', 'y', 'y')
)

class InvalidCubeReduction(Exception):
    pass


def reverse_steps(steps):
    """
    Reverse the order of all steps and the direction of each individual step
    """
    assert isinstance(steps, list)
    results = []

    for step in reversed(steps):

        if step.endswith("2"):
            reverse_step = step

        elif step.endswith("'"):
            reverse_step = step[0:-1]

        else:
            reverse_step = step + "'"

        results.append(reverse_step)

    return results


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


def apply_rotations(size, step, rotations):
    """
    Apply the "rotations" to step and return the step. This is used by
    compress_solution() to remove all of the whole cube rotations from
    the solution.
    """

    if step in ('CENTERS_SOLVED', 'EDGES_GROUPED'):
        return step

    if step.startswith('COMMENT'):
        return step

    for rotation in rotations:
        # remove the number at the start of the rotation...for a 4x4x4 cube
        # there might be a 4U rotation (to rotate about the y-axis) but we
        # don't need to keep the '4' part.

        if size <= 9:
            rotation = rotation[1:]
        elif size <= 99:
            rotation = rotation[2:]
        else:
            rotation = rotation[3:] # For a 100x or larger cube!!

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


def orbit_matches(edges_per_side, orbit, edge_index):

    if orbit is None:
        return True

    # Even cube
    if edges_per_side % 2 == 0:

        if edges_per_side == 2:
            assert edge_index in (0, 1), "Invalid edge_index %d" % edge_index
        elif edges_per_side == 4:
            assert edge_index in (0, 1, 2, 3), "Invalid edge_index %d" % edge_index
        else:
            assert False, "Only 4x4x4 and 6x6x6 supported"

        if orbit == 0:
            if edge_index == 0 or edge_index == edges_per_side-1:
                return True
            return False

        elif orbit == 1:
            if edge_index == 1 or edge_index == edges_per_side-2:
                return True
            return False

        else:
            raise Exception("Invalid oribit %d" % orbit)

        #if edge_index == orbit or edge_index == (edges_per_side - 1 - orbit):
        #    return True

    # Odd cube
    else:
        assert edges_per_side == 3, "Only 5x5x5 supported here"
        assert edge_index in (0, 1, 2), "Invalid edge_index %d" % edge_index

        if orbit == 0:
            if edge_index == 0 or edge_index == 2:
                return True
            return False

        elif orbit == 1:
            if edge_index == 1:
                return True
            return False

        else:
            raise Exception("Invalid oribit %d" % orbit)

    return False


def get_important_square_indexes(size):
    """
    Used for writing www pages
    """
    squares_per_side = size * size
    max_square = squares_per_side * 6
    first_squares = []
    last_squares = []

    for index in range(1, max_square + 1):
        if (index - 1) % squares_per_side == 0:
            first_squares.append(index)
        elif index % squares_per_side == 0:
            last_squares.append(index)

    last_UBD_squares = (last_squares[0], last_squares[4], last_squares[5])
    return (first_squares, last_squares, last_UBD_squares)


class RubiksCube(object):

    def __init__(self, state_string, order, colormap=None, debug=False):
        init_state = ['dummy', ]
        init_state.extend(list(state_string))
        self.squares_per_side = int((len(init_state) - 1)/6)
        self.size = math.sqrt(self.squares_per_side)
        assert str(self.size).endswith('.0'), "Cube has %d squares per side which is not possible" % self.squares_per_side
        self.size = int(self.size)
        self.solution = []
        self.steps_to_rotate_cube = 0
        self.steps_to_solve_centers = 0
        self.steps_to_group_edges = 0
        self.steps_to_solve_3x3x3 = 0
        self.ida_count = 0
        self._phase = None
        self.lt_init_called = False
        self.orient_edges = {}
        self.fake_444 = None
        self.fake_555 = None
        self.fake_666 = None
        self.fake_777 = None
        self.heuristic_stats = {}
        self.enable_print_cube = True
        self.use_nuke_corners = False
        self.use_nuke_edges = False
        self.use_nuke_centers = False
        self.cpu_mode = None
        self.solution_with_markers = []

        if not os.path.exists(HTML_DIRECTORY):
            os.makedirs(HTML_DIRECTORY)
            os.chmod(HTML_DIRECTORY, 0o777)

        if colormap:
            colormap = json.loads(colormap)
            self.color_map = {}
            self.color_map_html = {}

            for (side_name, color) in list(colormap.items()):
                side_name = str(side_name)

                if color == 'Wh':
                    self.color_map[side_name] = 97
                    self.color_map_html[side_name] = (235, 254, 250)

                elif color == 'Gr':
                    self.color_map[side_name] = 92
                    self.color_map_html[side_name] = (20, 105, 74)

                elif color == 'Rd':
                    self.color_map[side_name] = 91
                    self.color_map_html[side_name] = (104, 4, 2)

                elif color == 'Bu':
                    self.color_map[side_name] = 94
                    self.color_map_html[side_name] = (22, 57, 103)

                elif color == 'OR':
                    self.color_map[side_name] = 90
                    self.color_map_html[side_name] = (148, 53, 9)

                elif color == 'Ye':
                    self.color_map[side_name] = 93
                    self.color_map_html[side_name] = (210, 208, 2)

            #log.warning("color_map:\n%s\n" % pformat(self.color_map))

        else:
            # Match the colors on alg.cubing.net to make life easier
            self.color_map = {
                'U': 97, # Wh
                'L': 90, # Or
                'F': 92, # Gr
                'R': 91, # Rd
                'B': 94, # Bu
                'D': 93, # Ye
            }

            self.color_map_html = {
                'U': (235, 254, 250), # Wh
                'L': (148, 53, 9),    # Or
                'F': (20, 105, 74),   # Gr
                'R': (104, 4, 2),     # Rd
                'B': (22, 57, 103),   # Bu
                'D': (210, 208, 2),   # Ye
                'x': (0, 0, 0),       # black
            }

        if debug:
            log.setLevel(logging.DEBUG)

        self.load_state(state_string, order)
        self.state_backup = self.state[:]

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

        self.index_to_side = {}

        for side in list(self.sides.values()):
            side.calculate_wing_partners()

            for x in range(side.min_pos, side.max_pos+1):
                self.index_to_side[x] = side

    def __str__(self):
        return "%dx%dx%d" % (self.size, self.size, self.size)


    def _sanity_check(self, desc, indexes, expected_count):
        count = {
            'U' : 0,
            'L' : 0,
            'F' : 0,
            'R' : 0,
            'B' : 0,
            'D' : 0,
            'x' : 0,
        }

        for x in indexes:
            count[self.state[x]] += 1

        for (side, value) in count.items():
            if side == 'x' or value == 0:
                continue

            if value != expected_count:
                self.print_cube()
                raise InvalidCubeReduction("side %s %s count is %d (should be %d)" % (desc, side, value, expected_count))

    def re_init(self):
        self.state = self.state_backup[:]
        self.solution = []
        self.original_state = self.state_backup[:]
        self.original_solution = []

    def sanity_check(self):
        """
        Implemented by the various child classes to verify that
        the 'state' content makes sense
        """
        pass

    def load_state(self, state_string, order):

        # kociemba_string is in URFDLB order so split this apart and re-arrange it to
        # be ULFRBD so that is is sequential with the normal square numbering scheme
        foo = []
        init_state = ['dummy', ]
        init_state.extend(list(state_string))

        if order == 'URFDLB':
            foo.extend(init_state[1:self.squares_per_side + 1])                                       # U
            foo.extend(init_state[(self.squares_per_side * 4) + 1 : (self.squares_per_side * 5) + 1]) # L
            foo.extend(init_state[(self.squares_per_side * 2) + 1 : (self.squares_per_side * 3) + 1]) # F
            foo.extend(init_state[(self.squares_per_side * 1) + 1 : (self.squares_per_side * 2) + 1]) # R
            foo.extend(init_state[(self.squares_per_side * 5) + 1 : (self.squares_per_side * 6) + 1]) # B
            foo.extend(init_state[(self.squares_per_side * 3) + 1 : (self.squares_per_side * 4) + 1]) # D
        elif order == 'ULFRBD':
            foo.extend(init_state[1:self.squares_per_side + 1])                                       # U
            foo.extend(init_state[(self.squares_per_side * 1) + 1 : (self.squares_per_side * 2) + 1]) # L
            foo.extend(init_state[(self.squares_per_side * 2) + 1 : (self.squares_per_side * 3) + 1]) # F
            foo.extend(init_state[(self.squares_per_side * 3) + 1 : (self.squares_per_side * 4) + 1]) # R
            foo.extend(init_state[(self.squares_per_side * 4) + 1 : (self.squares_per_side * 5) + 1]) # B
            foo.extend(init_state[(self.squares_per_side * 5) + 1 : (self.squares_per_side * 6) + 1]) # D
        else:
            raise Exception("Add support for order %s" % order)

        self.state = ['x', ]
        for (square_index, side_name) in enumerate(foo):
            self.state.append(side_name)

    def is_even(self):
        if self.size % 2 == 0:
            return True
        return False

    def is_odd(self):
        if self.size % 2 == 0:
            return False
        return True

    def solved(self):
        """
        Return True if the cube is solved
        """
        for side in list(self.sides.values()):
            if not side.solved():
                return False
        return True

    def rotate_guts(self, action):
        """
        self.state is a dictionary where the key is the square_index and the
        value is that square side name (U, F, etc)
        """
        self.solution.append(action)
        result = self.state[:]
        # log.info("move %s" % action)

        if action[-1] in ("'", "`"):
            reverse = True
            action = action[0:-1]
        else:
            reverse = False

        # 2Uw, Uw and 2U all mean rotate the top 2 U rows
        # 3Uw and 3U mean rotate the top 3 U rows
        if len(action) >= 2 and action[0].isdigit() and action[1].isdigit():
            rows_to_rotate = int(action[0:2])
            action = action[2:]
        elif action[0].isdigit():
            rows_to_rotate = int(action[0])
            action = action[1:]
        else:
            # Uw also means rotate the top 2 U rows
            if 'w' in action:
                rows_to_rotate = 2
            else:
                rows_to_rotate = 1

        # We've accounted for this so remove it
        if 'w' in action:
            action = action.replace('w', '')

        # The digit at the end indicates how many quarter turns to do
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
            self.state = result[:]

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
            self.state = result[:]

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

                self.state = result[:]

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

                self.state = result[:]

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

                self.state = result[:]

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

                self.state = result[:]

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

                self.state = result[:]

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

                self.state = result[:]

        else:
            raise Exception("Unsupported action %s" % action)

    def rotate(self, action):

        if action.startswith("COMMENT"):
            self.solution.append(action)

        elif action in (
                "x2", "y2", "z2",
                "2U", "2U'", "2U2",
                "2L", "2L'", "2L2",
                "2F", "2F'", "2F2",
                "2R", "2R'", "2R2",
                "2B", "2B'", "2B2",
                "2D", "2D'", "2D2",
                "3U", "3U'", "3U2",
                "3L", "3L'", "3L2",
                "3F", "3F'", "3F2",
                "3R", "3R'", "3R2",
                "3B", "3B'", "3B2",
                "3D", "3D'", "3D2",
            ):

            if action == "x2":
                self.rotate_guts("x")
                self.rotate_guts("x")
            elif action == "y2":
                self.rotate_guts("y")
                self.rotate_guts("y")
            elif action == "z2":
                self.rotate_guts("z")
                self.rotate_guts("z")

            elif action == "2U":
                self.rotate_guts("Uw")
                self.rotate_guts("U'")
            elif action == "2U'":
                self.rotate_guts("Uw'")
                self.rotate_guts("U")
            elif action == "2U2":
                self.rotate_guts("Uw2")
                self.rotate_guts("U2")
            elif action == "2D":
                self.rotate_guts("Dw")
                self.rotate_guts("D'")
            elif action == "2D'":
                self.rotate_guts("Dw'")
                self.rotate_guts("D")
            elif action == "2D2":
                self.rotate_guts("Dw2")
                self.rotate_guts("D2")

            elif action == "2L":
                self.rotate_guts("Lw")
                self.rotate_guts("L'")
            elif action == "2L'":
                self.rotate_guts("Lw'")
                self.rotate_guts("L")
            elif action == "2L2":
                self.rotate_guts("Lw2")
                self.rotate_guts("L2")
            elif action == "2R":
                self.rotate_guts("Rw")
                self.rotate_guts("R'")
            elif action == "2R'":
                self.rotate_guts("Rw'")
                self.rotate_guts("R")
            elif action == "2R2":
                self.rotate_guts("Rw2")
                self.rotate_guts("R2")

            elif action == "2F":
                self.rotate_guts("Fw")
                self.rotate_guts("F'")
            elif action == "2F'":
                self.rotate_guts("Fw'")
                self.rotate_guts("F")
            elif action == "2F2":
                self.rotate_guts("Fw2")
                self.rotate_guts("F2")
            elif action == "2B":
                self.rotate_guts("Bw")
                self.rotate_guts("B'")
            elif action == "2B'":
                self.rotate_guts("Bw'")
                self.rotate_guts("B")
            elif action == "2B2":
                self.rotate_guts("Bw2")
                self.rotate_guts("B2")

            elif action == "3U":
                self.rotate_guts("3Uw")
                self.rotate_guts("Uw'")
            elif action == "3U'":
                self.rotate_guts("3Uw'")
                self.rotate_guts("Uw")
            elif action == "3U2":
                self.rotate_guts("3Uw2")
                self.rotate_guts("Uw2")
            elif action == "3D":
                self.rotate_guts("3Dw")
                self.rotate_guts("Dw'")
            elif action == "3D'":
                self.rotate_guts("3Dw'")
                self.rotate_guts("Dw")
            elif action == "3D2":
                self.rotate_guts("3Dw2")
                self.rotate_guts("Dw2")

            elif action == "3L":
                self.rotate_guts("3Lw")
                self.rotate_guts("Lw'")
            elif action == "3L'":
                self.rotate_guts("3Lw'")
                self.rotate_guts("Lw")
            elif action == "3L2":
                self.rotate_guts("3Lw2")
                self.rotate_guts("Lw2")
            elif action == "3R":
                self.rotate_guts("3Rw")
                self.rotate_guts("Rw'")
            elif action == "3R'":
                self.rotate_guts("3Rw'")
                self.rotate_guts("Rw")
            elif action == "3R2":
                self.rotate_guts("3Rw2")
                self.rotate_guts("Rw2")

            elif action == "3F":
                self.rotate_guts("3Fw")
                self.rotate_guts("Fw'")
            elif action == "3F'":
                self.rotate_guts("3Fw'")
                self.rotate_guts("Fw")
            elif action == "3F2":
                self.rotate_guts("3Fw2")
                self.rotate_guts("Fw2")
            elif action == "3B":
                self.rotate_guts("3Bw")
                self.rotate_guts("Bw'")
            elif action == "3B'":
                self.rotate_guts("3Bw'")
                self.rotate_guts("Bw")
            elif action == "3B2":
                self.rotate_guts("3Bw2")
                self.rotate_guts("Bw2")
            else:
                raise Exception("Unsupported action %s" % action)

            self.solution.pop()
            self.solution.pop()
            self.solution.append(action)

        else:
            self.rotate_guts(action)

    def print_cube_layout(self):
        if not self.enable_print_cube:
            return
        log.info('\n' + get_cube_layout(self.size) + '\n')

    def print_cube(self, print_positions=False):
        if not self.enable_print_cube:
            return
        side_names = ('U', 'L', 'F', 'R', 'B', 'D')
        side_name_index = 0
        rows = []
        row_index = 0

        for x in range(self.size * 3):
            rows.append([])

        all_digits = True
        for (square_index, square_state) in enumerate(self.state):
            if not square_state.isdigit():
                all_digits = False
                break

        for (square_index, square_state) in enumerate(self.state):

            # ignore the placeholder (x)
            if square_index == 0:
                continue

            side_name = side_names[side_name_index]
            color = self.color_map.get(square_state, None)

            if color:
                # end of the row
                if square_index % self.size == 0:
                    rows[row_index].append("\033[%dm%s\033[0m%s " % (color, square_state, " (%4d) " % square_index if print_positions else ""))
                    row_index += 1
                else:
                    rows[row_index].append("\033[%dm%s\033[0m%s" % (color, square_state, " (%4d) " % square_index if print_positions else ""))
            else:

                # end of the row
                if square_index % self.size == 0:
                    if square_state.endswith('x') or square_state.endswith('.') or square_state.endswith('-'):
                        rows[row_index].append("%s " % square_state)
                    else:
                        if all_digits:
                            rows[row_index].append("%02d" % int(square_state))
                        else:
                            rows[row_index].append("%s" % square_state)

                    row_index += 1
                else:
                    if square_state.endswith('x') or square_state.endswith('.') or square_state.endswith('-'):
                        rows[row_index].append("%s" % square_state)
                    else:
                        if all_digits:
                            rows[row_index].append("%02d" % int(square_state))
                        else:
                            rows[row_index].append("%s" % square_state)

            # end of the side
            if square_index % self.squares_per_side == 0:
                if side_name in ('L', 'F', 'R'):
                    row_index = self.size
                side_name_index += 1

        for (row_index, row) in enumerate(rows):
            if row_index < self.size or row_index >= (self.size * 2):
                if all_digits:
                    log.info(' ' * (self.size * 3) + ' '.join(row))
                else:
                    log.info(' ' * (self.size + self.size + 1) + ' '.join(row))
            else:
                log.info((' '.join(row)))

            if ((row_index+1) % self.size) == 0:
                log.info('')

        log.info('')

    def print_case_statement_C(self, case, first_step):
        """
        This is called via --rotate-printer, it is used to print the
        case statements used by lookup-table-builder.c
        """

        if first_step:
            print("    switch (move) {")

        case = case.replace("'", "_PRIME").replace("3", "three").replace("x", "X").replace("y", "Y").replace("z", "Z")
        print("    case %s:" % case)

        for (key, value) in enumerate(self.state[1:]):
            key += 1

            if str(key) != str(value):
                print("        cube[%s] = cube_tmp[%s];" % (key, value))
        print("        break;")
        print("")

    def print_case_statement_python(self, function_name, case):
        """
        This is called via utils/rotate-printer.py, it is used to print the
        contents of rotate_xxx.py
        """
        numbers = []
        numbers.append(0)
        for (key, value) in enumerate(self.state[1:]):
            numbers.append(int(value))

        return tuple(numbers)

    def randomize(self):
        """
        Perform a bunch of random moves to scramble a cube. This was used to generate test cases.
        """

        if self.is_even():
            max_rows = int(self.size/2)
        else:
            max_rows = int((self.size - 1)/2)

        sides = ['U', 'L', 'F', 'R', 'B', 'D']
        count = ((self.size * self.size) * 6) * 10

        # uncomment to limit randomness of the scramble
        # count = 12

        for x in range(count):
            rows = random.randint(1, max_rows)
            side_index = random.randint(0, 5)
            side = sides[side_index]
            quarter_turns = random.randint(1, 2)
            clockwise = random.randint(0, 1)

            if rows == 2:
                move = "%sw" % side
            elif rows > 2:
                move = "%d%sw" % (rows, side)
            else:
                move = side

            if quarter_turns > 1:
                move += str(quarter_turns)

            if not clockwise:
                move += "'"

            # I used this move restriction to build the 3k-555-cubes-step500.json test cubes
            #if move not in ['U', "U'", 'U2', 'L2', 'Lw2', 'F2', 'Fw2', 'R2', 'Rw2', 'B2', 'Bw2', 'D', "D'", 'D2']:
            #    continue

            self.rotate(move)

    def get_side_for_index(self, square_index):
        """
        Return the Side object that owns square_index
        """
        for side in list(self.sides.values()):
            if square_index >= side.min_pos and square_index <= side.max_pos:
                return side
        raise SolveError("We should not be here, square_index %s" % pformat(square_index))

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

    def get_paired_edges_count(self):
        return 12 - self.get_non_paired_edges_count()

    def edges_paired(self):
        if self.get_non_paired_edges_count() == 0:
            return True
        return False

    def edge_paired(self, wing_index):

        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            if side.min_pos <= wing_index <= side.max_pos:

                if wing_index in side.edge_north_pos:
                    return side.north_edge_paired()

                elif wing_index in side.edge_west_pos:
                    return side.west_edge_paired()

                elif wing_index in side.edge_south_pos:
                    return side.south_edge_paired()

                elif wing_index in side.edge_east_pos:
                    return side.east_edge_paired()

        raise Exception("Invalid wing_index %s" % wing_index)

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
            for step in ("L2", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L2", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B'", ):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("U2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("F2", "U2"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("R2", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F", "U2"):
                self.rotate(step)

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
            for step in ("R2", "B"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            pass

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("B2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B", ):
                self.rotate(step)

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
            for step in ("F", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B'", "U'"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("U", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("F2", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("F'", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F", "U"):
                self.rotate(step)

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
            for step in ("F'", "U"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("U'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("B2", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B'", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B", "U'"):
                self.rotate(step)

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
            for step in ("B'", "U2"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            pass

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("F2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("F'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F", ):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("U", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R2", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R2", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("F'",):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("U2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("B2", "U2"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B'", "U2"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B", "U2"):
                self.rotate(step)

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
            for step in ("B'", "U"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("U'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("F2", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("F'", "U'"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F", "U'"):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            pass

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("F'", "U'"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("U", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("B2", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B'", "U"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B", "U"):
                self.rotate(step)

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
            for step in ("U", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("D'", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("L2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            pass

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("F'", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("F", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("F2", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("L2", ):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("U'", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("R2", "U'", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R2", "B2"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("B", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("B'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            pass

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B2", ):
                self.rotate(step)

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D2", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("B'",):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D'", "B'"):
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
            for step in ("U2", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            self.rotate("F'")

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U'", "F'"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("U'", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("D", "F"):
                self.rotate(step)

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
            for step in ("U", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D'", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B2", "L2"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            self.rotate("F2")

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("U2", "F'"):
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
            for step in ("D2", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D'", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D", "F"):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to L east" % str(wing))

    def move_wing_to_R_west(self, wing):

        if isinstance(wing, tuple) or isinstance(wing, list):
            wing_pos1 = wing[0]
        else:
            wing_pos1 = wing

        # Upper
        if wing_pos1 in self.sideU.edge_north_pos:
            for step in ("U2", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_south_pos:
            for step in ("F",):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U'", "F"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("U'", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("D", "F'"):
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
            for step in ("F'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            pass

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F2", ):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("U", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D'", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R2",):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            pass

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("U2", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("D2", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B2", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("R2",):
                self.rotate(step)

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("F'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("D2", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D'", "F'"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D", "F'"):
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
            for step in ("U2", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_east_pos:
            for step in ("U'", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideU.edge_west_pos:
            for step in ("U", "B'"):
                self.rotate(step)

        # Left
        elif wing_pos1 in self.sideL.edge_north_pos:
            for step in ("U", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_south_pos:
            for step in ("D'", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("F2", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B2", ):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("U2", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("F'", "R2"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("R2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F2", "R2"):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("U'", "B'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            pass

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R2", ):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("B'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("B", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            pass

        # Down
        elif wing_pos1 in self.sideD.edge_north_pos:
            for step in ("D2", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_south_pos:
            for step in ("B", ):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_east_pos:
            for step in ("D", "B"):
                self.rotate(step)

        elif wing_pos1 in self.sideD.edge_west_pos:
            for step in ("D'", "B"):
                self.rotate(step)

        else:
            raise ImplementThis("implement wing %s to R east" % str(wing))

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
            for step in ("F'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B", "D2"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("F2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            pass

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("F", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F'", ):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R2", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("R2", "F"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("F",):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("B2", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("D2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("R2", "F"):
                self.rotate(step)

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
            for step in ("F'", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B", "D"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("F2", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("D'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("F", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F'", "D'"):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R2", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B'", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("F", "D'"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("B2", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("D", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B'", "D"):
                self.rotate(step)

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
            for step in ("D'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_east_pos:
            for step in ("F'", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B", ):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("F2", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("D2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("F", "D2"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F'", "D2"):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R2", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            for step in ("D", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B'",):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("R2", "B'"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("B2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            pass

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B'", ):
                self.rotate(step)

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
            for step in ("F'", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideL.edge_west_pos:
            for step in ("B", "D'"):
                self.rotate(step)

        # Front
        elif wing_pos1 in self.sideF.edge_north_pos:
            for step in ("F2", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_south_pos:
            for step in ("D", ):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_east_pos:
            for step in ("F", "D"):
                self.rotate(step)

        elif wing_pos1 in self.sideF.edge_west_pos:
            for step in ("F'", "D"):
                self.rotate(step)

        # Right
        elif wing_pos1 in self.sideR.edge_north_pos:
            for step in ("R2", ):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_south_pos:
            pass

        elif wing_pos1 in self.sideR.edge_east_pos:
            for step in ("B'", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideR.edge_west_pos:
            for step in ("F", "D"):
                self.rotate(step)

        # Back
        elif wing_pos1 in self.sideB.edge_north_pos:
            for step in ("B2", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_south_pos:
            for step in ("D'", ):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_east_pos:
            for step in ("B", "D'"):
                self.rotate(step)

        elif wing_pos1 in self.sideB.edge_west_pos:
            for step in ("B'", "D'"):
                self.rotate(step)

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

    def rotate_x(self):
        self.rotate("x")

    def rotate_x_reverse(self):
        self.rotate("x'")

    def rotate_y(self):
        self.rotate("y")

    def rotate_y_reverse(self):
        self.rotate("y'")

    def rotate_z(self):
        self.rotate("z")

    def rotate_z_reverse(self):
        self.rotate("z'")

    def centers_solved(self):
        for side in list(self.sides.values()):
            if not side.centers_solved():
                return False

        return True

    def UD_centers_staged(self):
        for side in (self.sideU, self.sideD):
            for pos in side.center_pos:
                if self.state[pos] not in ('U', 'D'):
                    #log.info("%s: UD_centers_staged pos %d is %s" % (self, pos, self.state[pos]))
                    return False
        return True

    def LR_centers_staged(self):
        for side in (self.sideL, self.sideR):
            for pos in side.center_pos:
                if self.state[pos] not in ('L', 'R'):
                    #log.info("%s: LR_centers_staged pos %d is %s" % (self, pos, self.state[pos]))
                    return False
        return True

    def FB_centers_staged(self):
        for side in (self.sideF, self.sideB):
            for pos in side.center_pos:
                if self.state[pos] not in ('F', 'B'):
                    #log.info("%s: FB_centers_staged pos %d is %s" % (self, pos, self.state[pos]))
                    return False
        return True

    def centers_staged(self):
        if self.UD_centers_staged() and self.LR_centers_staged() and self.FB_centers_staged():
            return True
        return False

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

        # odd cube
        if side.mid_pos:
            pos_to_check = side.mid_pos
            F_pos_to_check = self.sideF.mid_pos
            D_pos_to_check = self.sideD.mid_pos

        # even cube
        else:
            # Use the top-right inner x-center
            offset = int(((self.size/2) * self.size) - (self.size/2))

            pos_to_check = side.min_pos + offset
            F_pos_to_check = self.sideF.min_pos + offset
            D_pos_to_check = self.sideD.min_pos + offset

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

    def rotate_U_to_U(self):
        self.rotate_side_X_to_Y('U', 'U')

    def rotate_F_to_F(self):
        self.rotate_side_X_to_Y('F', 'F')

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
            if self.size == 2:
                for side_name in ('U', 'R', 'F', 'D', 'L', 'B'):
                    side = self.sides[side_name]

                    # first row
                    foo.append(self.state[side.corner_pos[0]])
                    foo.append(self.state[side.corner_pos[1]])

                    # second row
                    foo.append(self.state[side.corner_pos[2]])
                    foo.append(self.state[side.corner_pos[3]])

            else:
                for side_name in ('U', 'R', 'F', 'D', 'L', 'B'):
                    side = self.sides[side_name]

                    # first row
                    foo.append(self.state[side.corner_pos[0]])
                    foo.append(self.state[side.edge_north_pos[0]])
                    foo.append(self.state[side.corner_pos[1]])

                    # second row
                    foo.append(self.state[side.edge_west_pos[0]])

                    if side.mid_pos:
                        foo.append(self.state[side.mid_pos])
                    else:
                        offset = int(((self.size/2) * self.size) - (self.size/2))
                        pos_to_check = side.min_pos + offset
                        foo.append(self.state[pos_to_check])

                    foo.append(self.state[side.edge_east_pos[0]])

                    # third row
                    foo.append(self.state[side.corner_pos[2]])
                    foo.append(self.state[side.edge_south_pos[0]])
                    foo.append(self.state[side.corner_pos[3]])

        kociemba_string = ''.join(foo)
        log.debug('kociemba string: %s' % kociemba_string)
        return kociemba_string

    def prevent_OLL(self):
        """
        Solving OLL at the end takes 26 moves, preventing it takes 10
        """

        # OLL only applies for even cubes
        if self.is_odd():
            return False

        orbits_with_oll_parity = self.center_solution_leads_to_oll_parity()
        steps = None

        if not orbits_with_oll_parity:
            return False

        if self.size == 4:
            if orbits_with_oll_parity == [0]:
                steps = "Rw U2 Rw U2 Rw U2 Rw U2 Rw U2"
            else:
                raise SolveError("prevent_OLL for %sx%sx%s, orbits %s have parity issues" %
                                    (self.size, self.size, self.size, pformat(orbits_with_oll_parity)))

        elif self.size == 6:
            if self.edges_paired():
                log.info("edges are already paired, cannot prevent OLL without unpairing them")
                return False

            # 10 steps
            if orbits_with_oll_parity == [0,1]:
                steps = "3Rw U2 3Rw U2 3Rw U2 3Rw U2 3Rw U2"
                log.info("6x6x6 has OLL on orbits 0 and 1")

            # 10 steps
            elif orbits_with_oll_parity == [0]:
                steps = "Rw U2 Rw U2 Rw U2 Rw U2 Rw U2"
                log.info("6x6x6 has OLL on orbit 0")

            # 15 steps for an inside orbit
            elif orbits_with_oll_parity == [1]:
                steps = "3Rw Rw' U2 3Rw Rw' U2 3Rw Rw' U2 3Rw Rw' U2 3Rw Rw' U2"
                log.info("6x6x6 has OLL on orbit 1")

            else:
                raise SolveError("prevent_OLL for %sx%sx%s, orbits %s have parity issues" %
                                    (self.size, self.size, self.size, pformat(orbits_with_oll_parity)))

        #else:
        #    raise ImplementThis("prevent_OLL for %sx%sx%s, orbits %s have parity issues" %
        #                        (self.size, self.size, self.size, pformat(orbits_with_oll_parity)))

        if steps:
            for step in steps.split():
                self.rotate(step)
            return True

        return False

    def solve_OLL(self):

        if self.size in (2, 3):
            raise SolveError("OLL should never happen on a %dx%dx%d, the cube given to us to solve is invalid" % (self.size, self.size, self.size))

        # Check all 12 edges, rotate the one with OLL to U-south
        while True:
            has_oll = False

            if self.state[self.sideU.corner_pos[2]] == self.state[self.sideF.edge_north_pos[0]]:
                has_oll = True

            elif self.state[self.sideU.corner_pos[0]] == self.state[self.sideL.edge_north_pos[0]]:
                has_oll = True
                self.rotate_y_reverse()

            elif self.state[self.sideU.corner_pos[3]] == self.state[self.sideR.edge_north_pos[0]]:
                has_oll = True
                self.rotate_y()

            elif self.state[self.sideU.corner_pos[1]] == self.state[self.sideB.edge_north_pos[0]]:
                has_oll = True
                self.rotate_y()
                self.rotate_y()

            elif self.state[self.sideD.corner_pos[0]] == self.state[self.sideF.edge_south_pos[0]]:
                has_oll = True
                self.rotate_x()

            elif self.state[self.sideD.corner_pos[0]] == self.state[self.sideL.edge_south_pos[0]]:
                has_oll = True
                self.rotate_y_reverse()
                self.rotate_x()

            elif self.state[self.sideD.corner_pos[1]] == self.state[self.sideR.edge_south_pos[0]]:
                has_oll = True
                self.rotate_y()
                self.rotate_x()

            elif self.state[self.sideD.corner_pos[2]] == self.state[self.sideB.edge_south_pos[0]]:
                has_oll = True
                self.rotate_y()
                self.rotate_y()
                self.rotate_x()

            elif self.state[self.sideF.corner_pos[0]] == self.state[self.sideL.edge_east_pos[0]]:
                has_oll = True
                self.rotate_z()

            elif self.state[self.sideF.corner_pos[1]] == self.state[self.sideR.edge_west_pos[0]]:
                has_oll = True
                self.rotate_z_reverse()

            elif self.state[self.sideB.corner_pos[0]] == self.state[self.sideR.edge_east_pos[0]]:
                has_oll = True
                self.rotate_y()
                self.rotate_z_reverse()

            elif self.state[self.sideB.corner_pos[1]] == self.state[self.sideL.edge_west_pos[0]]:
                has_oll = True
                self.rotate_y_reverse()
                self.rotate_z()

            if has_oll:

                # 26 moves :(
                oll_solution = "%dRw2 R2 U2 %dRw2 R2 U2 %dRw R' U2 %dRw R' U2 %dRw' R' U2 B2 U %dRw' R U' B2 U %dRw R' U R2" % (self.size/2, self.size/2, self.size/2, self.size/2, self.size/2, self.size/2, self.size/2)
                oll_solution = oll_solution.split()
                log.warning("Solving OLL in %d steps" % len(oll_solution))
                self.print_cube()

                for step in oll_solution:
                    self.rotate(step)
            else:
                break

    def solve_PLL(self):

        if self.size in (2, 3):
            raise SolveError("PLL should never happen on a %dx%dx%d, the cube given to us to solve is invalid" % (self.size, self.size, self.size))

        pll_id = None

        self.rotate_U_to_U()
        self.rotate_F_to_F()

        # rotate one of the hosed edges to U-south
        if self.state[self.sideU.edge_south_pos[0]] != 'U':
            pass
        elif self.state[self.sideU.edge_north_pos[0]] != 'U':
            self.rotate_y()
            self.rotate_y()
        elif self.state[self.sideU.edge_west_pos[0]] != 'U':
            self.rotate_y_reverse()
        elif self.state[self.sideU.edge_east_pos[0]] != 'U':
            self.rotate_y()
        elif self.state[self.sideL.edge_north_pos[0]] != 'L':
            raise ImplementThis("pll")
        elif self.state[self.sideL.edge_south_pos[0]] != 'L':
            self.rotate_x()
            self.rotate_x()
            self.rotate_y_reverse()
        elif self.state[self.sideL.edge_east_pos[0]] != 'L':
            self.rotate_z()
        elif self.state[self.sideL.edge_west_pos[0]] != 'L':
            self.rotate_y_reverse()
            self.rotate_z()
        elif self.state[self.sideF.edge_north_pos[0]] != 'F':
            raise ImplementThis("pll")
        elif self.state[self.sideF.edge_south_pos[0]] != 'F':
            self.rotate_x()
        elif self.state[self.sideF.edge_east_pos[0]] != 'F':
            self.rotate_z_reverse()
        elif self.state[self.sideF.edge_west_pos[0]] != 'F':
            raise ImplementThis("pll")
        elif self.state[self.sideR.edge_north_pos[0]] != 'R':
            raise ImplementThis("pll")
        elif self.state[self.sideR.edge_south_pos[0]] != 'R':
            self.rotate_y()
            self.rotate_x()
        elif self.state[self.sideR.edge_east_pos[0]] != 'R':
            self.rotate_y()
            self.rotate_z_reverse()
        elif self.state[self.sideR.edge_west_pos[0]] != 'R':
            raise ImplementThis("pll")
        elif self.state[self.sideB.edge_north_pos[0]] != 'B':
            raise ImplementThis("pll")
        elif self.state[self.sideB.edge_south_pos[0]] != 'B':
            self.rotate_x()
            self.rotate_x()
        elif self.state[self.sideB.edge_east_pos[0]] != 'B':
            raise ImplementThis("pll")
        elif self.state[self.sideB.edge_west_pos[0]] != 'B':
            raise ImplementThis("pll")
        elif self.state[self.sideD.edge_north_pos[0]] != 'D':
            raise ImplementThis("pll")
        elif self.state[self.sideD.edge_south_pos[0]] != 'D':
            raise ImplementThis("pll")
        elif self.state[self.sideD.edge_east_pos[0]] != 'D':
            raise ImplementThis("pll")
        elif self.state[self.sideD.edge_west_pos[0]] != 'D':
            raise ImplementThis("pll")
        else:
            self.print_cube()
            raise SolveError("we should not be here")

        if self.state[self.sideF.edge_north_pos[0]] == 'F':
            raise SolveError("F-north should have PLL edge")

        # rotate the other hosed edges to U-west
        if self.state[self.sideU.edge_south_pos[0]] != self.state[self.sideU.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideU.edge_north_pos[0]] != self.state[self.sideU.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideU.edge_west_pos[0]] != self.state[self.sideU.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideU.edge_east_pos[0]] != self.state[self.sideU.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideL.edge_north_pos[0]] != self.state[self.sideL.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideL.edge_south_pos[0]] != self.state[self.sideL.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideL.edge_east_pos[0]] != self.state[self.sideL.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideL.edge_west_pos[0]] != self.state[self.sideL.corner_pos[0]]:
            self.rotate_y()
            pll_id = 2
        elif self.state[self.sideF.edge_south_pos[0]] != self.state[self.sideF.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideF.edge_east_pos[0]] != self.state[self.sideF.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideF.edge_west_pos[0]] != self.state[self.sideF.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideR.edge_north_pos[0]] != self.state[self.sideR.corner_pos[0]]:
            self.rotate_y()
            pll_id = 2
        elif self.state[self.sideR.edge_south_pos[0]] != self.state[self.sideR.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideR.edge_east_pos[0]] != self.state[self.sideR.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideR.edge_west_pos[0]] != self.state[self.sideR.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideB.edge_north_pos[0]] != self.state[self.sideB.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideB.edge_south_pos[0]] != self.state[self.sideB.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideB.edge_east_pos[0]] != self.state[self.sideB.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideB.edge_west_pos[0]] != self.state[self.sideB.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideD.edge_north_pos[0]] != self.state[self.sideD.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideD.edge_south_pos[0]] != self.state[self.sideD.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideD.edge_east_pos[0]] != self.state[self.sideD.corner_pos[0]]:
            raise ImplementThis("pll")
        elif self.state[self.sideD.edge_west_pos[0]] != self.state[self.sideD.corner_pos[0]]:
            raise ImplementThis("pll")
        else:
            raise Exception("we should not be here")

        # http://www.speedcubing.com/chris/4speedsolve3.html
        if pll_id == 2:

            # Takes 12 steps
            pll_solution = "L2 D %dFw2 %dLw2 F2 %dLw2 L2 F2 %dLw2 %dFw2 D' L2" % (self.size/2, self.size/2, self.size/2, self.size/2, self.size/2)
            log.warning("Solving PLL ID %d: %s" % (pll_id, pll_solution))
            self.print_cube()

            for step in pll_solution.split():
                self.rotate(step)

        else:
            raise ImplementThis("pll_id %s" % pll_id)

    def solve_333(self):

        if self.solved():
            return

        kociemba_string = self.get_kociemba_string(False)

        try:
            steps = subprocess.check_output(['kociemba', kociemba_string]).decode('ascii').splitlines()[-1].strip().split()
            kociemba_ok = True
        except Exception:
            kociemba_ok = False

        if not kociemba_ok:
            raise SolveError("parity error made kociemba barf,  kociemba %s" % kociemba_string)

        log.debug("kociemba       : %s" % kociemba_string)
        log.info("kociemba steps            : %s" % ' '.join(steps))
        log.info("kociemba steps (reversed) : %s" % ' '.join(reverse_steps(steps)))
        reduce_333_solution_len = len(self.solution)

        for step in steps:
            step = str(step)
            self.rotate(step)

        self.solution.append("COMMENT_%d_steps_solve_333" % self.get_solution_len_minus_rotates(self.solution[reduce_333_solution_len:]))

        if not self.solved():
            self.solve_OLL()

            if not self.solved():
                self.solve_PLL()

                if not self.solved():
                    raise SolveError("We hit either OLL or PLL parity and could not solve it")

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

    def get_edge_swap_count(self, edges_paired, orbit, debug=False):
        needed_edges = []
        to_check = []

        # should not happen
        if edges_paired and orbit is not None:
            raise Exception("edges_paired is True and orbit is %s" % orbit)

        edges_per_side = len(self.sideU.edge_north_pos)

        #log.warning("edges_paired %s, orbit %s, edges_per_side %s" % (edges_paired, orbit, edges_per_side))
        #debug = True

        # Upper
        for (edge_index, square_index) in enumerate(self.sideU.edge_north_pos):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('UB')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('UB%d' % edge_index)

        for (edge_index, square_index) in enumerate(reversed(self.sideU.edge_west_pos)):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('UL')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('UL%d' % edge_index)

        for (edge_index, square_index) in enumerate(reversed(self.sideU.edge_south_pos)):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('UF')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('UF%d' % edge_index)

        for (edge_index, square_index) in enumerate(self.sideU.edge_east_pos):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('UR')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('UR%d' % edge_index)


        # Left
        for (edge_index, square_index) in enumerate(reversed(self.sideL.edge_west_pos)):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('LB')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('LB%d' % edge_index)

        for (edge_index, square_index) in enumerate(self.sideL.edge_east_pos):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('LF')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('LF%d' % edge_index)


        # Right
        for (edge_index, square_index) in enumerate(reversed(self.sideR.edge_west_pos)):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('RF')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('RF%d' % edge_index)

        for (edge_index, square_index) in enumerate(self.sideR.edge_east_pos):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('RB')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('RB%d' % edge_index)

        # Down
        for (edge_index, square_index) in enumerate(self.sideD.edge_north_pos):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('DF')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('DF%d' % edge_index)

        for (edge_index, square_index) in enumerate(reversed(self.sideD.edge_west_pos)):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('DL')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('DL%d' % edge_index)

        for (edge_index, square_index) in enumerate(reversed(self.sideD.edge_south_pos)):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('DB')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('DB%d' % edge_index)

        for (edge_index, square_index) in enumerate(self.sideD.edge_east_pos):
            if edges_paired:
                to_check.append(square_index)
                needed_edges.append('DR')
                break
            else:
                if orbit_matches(edges_per_side, orbit, edge_index):
                    to_check.append(square_index)
                    needed_edges.append('DR%d' % edge_index)

        if debug:
            to_check_str = ''

            for x in to_check:
                if edges_paired:
                    to_check_str += "%3s" % x
                else:
                    to_check_str += "%4s" % x

            log.info("orbit %d to_check     :%s" % (orbit, to_check_str))
            log.info("orbit %d needed edges : %s" % (orbit, ' '.join(needed_edges)))

        current_edges = []

        for square_index in to_check:
            side = self.index_to_side[square_index]
            partner_index = side.get_wing_partner(square_index)
            square1 = self.state[square_index]
            square2 = self.state[partner_index]
            #log.info("side %s, (%d, %d) is %s%s" % (side, square_index, partner_index, square1, square2))

            if square1 == 'U' or square1 == 'D':
                wing_str = square1 + square2
            elif square2 == 'U' or square2 == 'D':
                wing_str = square2 + square1
            elif square1 == 'L' or square1 == 'R':
                wing_str = square1 + square2
            elif square2 == 'L' or square2 == 'R':
                wing_str = square2 + square1
            elif square1 == 'x' and square2 == 'x':
                continue
            else:
                raise Exception("Could not determine wing_str for (%s, %s)" % (square1, square2))

            if not edges_paired:

                # - backup the current state
                # - add an 'x' to the end of the square_index/partner_index
                # - move square_index/partner_index to its final edge location
                # - look for the 'x' to determine if this is the '0' vs '1' wing
                # - restore the original state

                square1_with_x = square1 + 'x'
                square2_with_x = square2 + 'x'

                original_state = self.state[:]
                original_solution = self.solution[:]
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
                    edge_to_check = reversed(self.sideU.edge_south_pos)
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
                    edge_to_check = reversed(self.sideD.edge_south_pos)
                    target_side = self.sideD

                elif wing_str == 'DR':
                    self.move_wing_to_D_east(square_index)
                    edge_to_check = self.sideD.edge_east_pos
                    target_side = self.sideD

                else:
                    raise SolveError("invalid wing %s at (%d, %d)" % (wing_str, square_index, partner_index))

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

                self.state = original_state[:]
                self.solution = original_solution[:]

            current_edges.append(wing_str)

        if debug:
            log.info("orbit %d current edges: %s" % (orbit, ' '.join(current_edges)))

        return get_swap_count(needed_edges, current_edges, debug)

    def edge_swaps_even(self, edges_paired, orbit, debug):
        if self.get_edge_swap_count(edges_paired, orbit, debug) % 2 == 0:
            return True
        return False

    def edge_swaps_odd(self, edges_paired, orbit, debug):
        if self.get_edge_swap_count(edges_paired, orbit, debug) % 2 == 1:
            return True
        return False

    def edge_solution_leads_to_pll_parity(self, debug=False):

        if self.edge_swaps_even(edges_paired=True, orbit=None, debug=debug) == self.corner_swaps_even(debug):
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
        # OLL only applies to even cubes but there are times when an even cube
        # is reduced to an odd cube...this happens when solving a 6x6x6, it is
        # reduced to a 5x5x5. So we must support OLL detection on odd cubes also.
        if self.is_even():
            orbit_start = 0
            orbits = int((self.size - 2) / 2)
        else:
            if self.size == 3:
                return []

            orbit_start = 0
            orbits = int((self.size - 2 - 1) / 2) + 1

        orbits_with_oll_parity = []

        for orbit in range(orbit_start, orbits):
            # OLL Parity - "...is caused by solving the centers such that the edge permutation is odd"
            # http://www.speedcubing.com/chris/4speedsolve3.html
            if self.edge_swaps_odd(False, orbit, debug):
                orbits_with_oll_parity.append(orbit)
                #log.info("orbit %d has OLL parity" % orbit)

        if not orbits_with_oll_parity:
            log.debug("Predict we are free of OLL parity")

        return orbits_with_oll_parity

    def get_state_all(self):
        result = []

        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in range(side.min_pos, side.max_pos + 1):
                result.append(self.state[square_index])

        return ''.join(result)

    def get_staged_centers_count(self, centers):
        staged = 0

        for side in list(self.sides.values()):
            for pos in side.center_pos:

                if centers is not None and pos not in centers:
                    continue

                if side.name == 'U' or side.name == 'D':
                    if self.state[pos] == 'U' or self.state[pos] == 'D':
                        staged += 1

                elif side.name == 'L' or side.name == 'R':
                    if self.state[pos] == 'L' or self.state[pos] == 'R':
                        staged += 1

                elif side.name == 'F' or side.name == 'B':
                    if self.state[pos] == 'F' or self.state[pos] == 'B':
                        staged += 1

        return staged

    def get_solved_centers_count(self, centers):
        solved = 0

        for side in list(self.sides.values()):
            for pos in side.center_pos:

                if centers is not None and pos not in centers:
                    continue

                if side.name == self.state[pos]:
                    solved += 1

        return solved

    def rotate_for_best_centers(self, staging, centers):
        max_best_centers = 0
        max_best_centers_state = None
        max_best_centers_solution = None

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        for upper_side_name in ('U', 'D', 'L', 'F', 'R', 'B'):
            for front_side_name in ('F', 'R', 'B', 'L', 'U', 'D'):

                if upper_side_name == front_side_name:
                    continue

                # Put the cube back in its original state
                self.state = original_state[:]
                self.solution = original_solution[:]

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

                if staging:
                    best_centers = self.get_staged_centers_count(centers)
                else:
                    best_centers = self.get_solved_centers_count(centers)

                if best_centers > max_best_centers:
                    max_best_centers = best_centers
                    max_best_centers_state = self.state[:]
                    max_best_centers_solution = self.solution[:]
                    #log.info("%s: upper %s, front %s, stages %d centers" % (self, upper_side_name, front_side_name, max_best_centers))

        self.state = max_best_centers_state[:]
        self.solution = max_best_centers_solution[:]

        # Return True if we rotated the cube
        if self.solution == original_solution:
            return False
        else:
            return True

    def rotate_for_best_centers_staging(self, centers=None):
        return self.rotate_for_best_centers(True, centers)

    def rotate_for_best_centers_solving(self, centers=None):
        return self.rotate_for_best_centers(False, centers)

    def group_centers_guts(self):
        raise ImplementThis("Child class must implement group_centers_guts")

    def get_solution_len_minus_rotates(self, solution, debug=False):
        count = 0
        size_str = str(self.size)

        for step in solution:
            if step in ('CENTERS_SOLVED', 'EDGES_GROUPED'):
                continue

            if step.startswith('COMMENT'):
                continue

            if step in ("x", "x'", "x2",
                        "y", "y'", "y2",
                        "z", "z'", "z2"):
                continue

            if step.startswith(size_str):
                continue

            count += 1

            if debug:
                log.warning("solution %s, step %s, count %d" % (" ".join(solution), step, count))

        return count

    def compress_solution(self):
        moves = set(self.solution)
        solution_string = " " + " ".join(self.solution) + " "
        pass_num = 0

        #log.info("solution_string: %s" % solution_string)
        while solution_string.count(" CENTERS_SOLVED") > 1:
            solution_string = solution_string.replace(" CENTERS_SOLVED", "", 1)

        while solution_string.count(" EDGES_GROUPED") > 1:
            solution_string = solution_string.replace(" EDGES_GROUPED", "", 1)
        #log.info("solution_string: %s" % solution_string)

        while True:
            original_solution_string = solution_string[:]
            prev_move = None
            #log.info("pass %d:  init %s" % (pass_num, original_solution_string))

            for move in moves:
                if move in ('CENTERS_SOLVED', 'EDGES_GROUPED'):
                    continue

                if move.startswith('COMMENT'):
                    continue

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

                # Uw U Uw' -> U
                # Uw U2 Uw' -> U2
                solution_string = solution_string.replace(" Uw U Uw' ", " U ")
                solution_string = solution_string.replace(" Uw U' Uw' ", " U' ")
                solution_string = solution_string.replace(" Uw U2 Uw' ", " U2 ")
                solution_string = solution_string.replace(" Uw' U Uw ", " U ")
                solution_string = solution_string.replace(" Uw' U' Uw ", " U' ")
                solution_string = solution_string.replace(" Uw' U2 Uw ", " U2 ")

                solution_string = solution_string.replace(" Lw L Lw' ", " L ")
                solution_string = solution_string.replace(" Lw L' Lw' ", " L' ")
                solution_string = solution_string.replace(" Lw L2 Lw' ", " L2 ")
                solution_string = solution_string.replace(" Lw' L Lw ", " L ")
                solution_string = solution_string.replace(" Lw' L' Lw ", " L' ")
                solution_string = solution_string.replace(" Lw' L2 Lw ", " L2 ")

                solution_string = solution_string.replace(" Fw F Fw' ", " F ")
                solution_string = solution_string.replace(" Fw F' Fw' ", " F' ")
                solution_string = solution_string.replace(" Fw F2 Fw' ", " F2 ")
                solution_string = solution_string.replace(" Fw' F Fw ", " F ")
                solution_string = solution_string.replace(" Fw' F' Fw ", " F' ")
                solution_string = solution_string.replace(" Fw' F2 Fw ", " F2 ")

                solution_string = solution_string.replace(" Rw R Rw' ", " R ")
                solution_string = solution_string.replace(" Rw R' Rw' ", " R' ")
                solution_string = solution_string.replace(" Rw R2 Rw' ", " R2 ")
                solution_string = solution_string.replace(" Rw' R Rw ", " R ")
                solution_string = solution_string.replace(" Rw' R' Rw ", " R' ")
                solution_string = solution_string.replace(" Rw' R2 Rw ", " R2 ")

                solution_string = solution_string.replace(" Bw B Bw' ", " B ")
                solution_string = solution_string.replace(" Bw B' Bw' ", " B' ")
                solution_string = solution_string.replace(" Bw B2 Bw' ", " B2 ")
                solution_string = solution_string.replace(" Bw' B Bw ", " B ")
                solution_string = solution_string.replace(" Bw' B' Bw ", " B' ")
                solution_string = solution_string.replace(" Bw' B2 Bw ", " B2 ")

                solution_string = solution_string.replace(" Dw D Dw' ", " D ")
                solution_string = solution_string.replace(" Dw D' Dw' ", " D' ")
                solution_string = solution_string.replace(" Dw D2 Dw' ", " D2 ")
                solution_string = solution_string.replace(" Dw' D Dw ", " D ")
                solution_string = solution_string.replace(" Dw' D' Dw ", " D' ")
                solution_string = solution_string.replace(" Dw' D2 Dw ", " D2 ")

                prev_move = move

            #log.info("pass %d: final %s" % (pass_num, solution_string))
            if original_solution_string == solution_string:
                break
            else:
                pass_num += 1

        #log.info("Compressed solution in %d passes" % pass_num)
        solution_string = solution_string.strip()

        # We put some markers in the solution to track how many steps
        # each stage took...remove those markers
        solution_minus_markers = []
        self.steps_to_rotate_cube = 0
        self.steps_to_solve_centers = 0
        self.steps_to_group_edges = 0
        self.steps_to_solve_3x3x3 = 0
        index = 0
        self.solution_with_markers = solution_string.split()

        #log.info("pre compress; %s" % ' '.join(self.solution))
        for step in self.solution_with_markers:
            if step.startswith(str(self.size)) or step in ("x", "x'", "x2", "y", "y'", "y2", "z", "z'", "z2"):
                self.steps_to_rotate_cube += 1

            if step == 'CENTERS_SOLVED':
                self.steps_to_solve_centers = index - self.steps_to_rotate_cube
            elif step == 'EDGES_GROUPED':
                self.steps_to_group_edges = index - self.steps_to_rotate_cube - self.steps_to_solve_centers
            elif step.startswith('COMMENT'):
                pass
            else:
                solution_minus_markers.append(step)
                index += 1

        self.steps_to_solve_3x3x3 = index - self.steps_to_rotate_cube - self.steps_to_solve_centers - self.steps_to_group_edges
        self.solution = solution_minus_markers

    def recolor(self):

        if self.use_nuke_corners or self.use_nuke_edges or self.use_nuke_centers or self.recolor_positions:
            log.info("%s: recolor" % self)
            #self.print_cube()

            if self.use_nuke_corners:
                self.nuke_corners()

            if self.use_nuke_edges:
                self.nuke_edges()

            if self.use_nuke_centers:
                self.nuke_centers()

            for x in self.recolor_positions:
                x_color = self.state[x]
                x_new_color = self.recolor_map.get(x_color)

                if x_new_color:
                    self.state[x] = x_new_color

    def reduce_333(self):
        if self.centers_solved():
            log.info("centers are already solved")
        else:
            self.group_centers_guts()

        self.rotate_U_to_U()
        self.rotate_F_to_F()
        self.solution.append('CENTERS_SOLVED')

        if self.edges_paired():
            log.info("edges are already paired")
        else:
            self.group_edges()
        self.solution.append('EDGES_GROUPED')

    def reduce_333_slow(self):
        tmp_state = self.state[:]
        tmp_solution = self.solution[:]
        original_solution_len = len(self.solution)

        min_solution_len = None
        min_solution_state = None
        min_solution = None

        self.recolor_positions = list(range((self.size * self.size * 6) + 1))

        for (top, bottom) in (("U", "D"), ("L", "R"), ("F", "B")):

            if (top, bottom) == ("U", "D"):
                pass

            elif (top, bottom) == ("L", "R"):
                self.recolor_map = {
                    'U' : 'R',
                    'L' : 'U',
                    'F' : 'F',
                    'R' : 'D',
                    'B' : 'B',
                    'D' : 'L',
                }
                self.recolor()

            elif (top, bottom) == ("F", "B"):
                self.recolor_map = {
                    'U' : 'B',
                    'L' : 'L',
                    'F' : 'U',
                    'R' : 'R',
                    'B' : 'D',
                    'D' : 'F',
                }
                self.recolor()

            else:
                raise Exception("%s: invalid (top, bottom) (%s, %s)" % (self, top, bottom))

            if self.is_odd() or self.centers_solved():
                self.rotate_U_to_U()
                self.rotate_F_to_F()
            self.reduce_333()

            solution_len = self.get_solution_len_minus_rotates(self.solution)

            if min_solution_len is None or solution_len <= min_solution_len:
                log.warning("%s: (%s, %s) solution_len %d (NEW MIN)\n\n\n\n\n\n\n" % (self, top, bottom, solution_len))
                min_solution_len = solution_len
                min_solution_state = self.state[:]
                min_solution = self.solution[:]
            else:
                log.warning("%s: (%s, %s) solution_len %d\n\n\n\n\n\n\n" % (self, top, bottom, solution_len))

            self.state = tmp_state[:]
            self.solution = tmp_solution[:]

        for step in min_solution[original_solution_len:]:
            if step.startswith('COMMENT'):
                self.solution.append(step)
            else:
                self.rotate(step)

    def solve(self, solution333=None):
        """
        The RubiksCube222 and RubiksCube333 child classes will override
        this since they don't need to group centers or edges
        """
        if self.solved():
            return

        log.info("lt_init begin")
        self.lt_init()
        log.info("lt_init end")

        if self.is_odd() or self.centers_solved():
            self.rotate_U_to_U()
            self.rotate_F_to_F()

        if self.cpu_mode == "slow":
            self.reduce_333_slow()
        else:
            log.info("reduce_333 begin")
            self.reduce_333()
            log.info("reduce_333 end")

        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if solution333:
            assert isinstance(solution333, list)
            reduce_333_solution_len = len(self.solution)
            for step in solution333:
                self.rotate(step)
            self.solution.append("COMMENT_%d_steps_solve_333" % self.get_solution_len_minus_rotates(self.solution[reduce_333_solution_len:]))
        else:
            log.info("solve_333 begin")
            self.solve_333()
            log.info("solve_333 end")
        self.compress_solution()

    def print_solution(self, include_comments):

        # Print an alg.cubing.net URL for this setup/solution
        url = "https://alg.cubing.net/?puzzle=%dx%dx%d&alg=" % (self.size, self.size, self.size)

        for x in self.solution_with_markers:
            if x in ('CENTERS_SOLVED', 'EDGES_GROUPED'):
                continue
            elif x.startswith('COMMENT'):
                if include_comments:
                    url += r'''%2F%2F''' + x.replace("COMMENT", "") + "%0A%0A"
            else:
                url += x + "_"

        url += "&type=alg"
        url += "&title=dwalton76"
        url = url.replace("'", "-")
        url = url.replace(" ", "_")
        log.info("\nURL     : %s" % url)

        # Remove full cube rotations by changing all of the steps that follow the cube rotation
        # We do this so robots using the solver do not have to deal with full cube rotations as
        # that would be kinda pointless.
        final_steps = []
        rotations = []
        tmp_solution = []

        for step in self.solution:
            if step == "x":
                tmp_solution.append("%dR" % self.size)
            elif step == "x'":
                tmp_solution.append("%dR'" % self.size)
            elif step == "x2":
                tmp_solution.append("%dR" % self.size)
                tmp_solution.append("%dR" % self.size)

            elif step == "y":
                tmp_solution.append("%dU" % self.size)
            elif step == "y'":
                tmp_solution.append("%dU'" % self.size)
            elif step == "y2":
                tmp_solution.append("%dU" % self.size)
                tmp_solution.append("%dU" % self.size)

            elif step == "z":
                tmp_solution.append("%dF" % self.size)
            elif step == "z'":
                tmp_solution.append("%dF'" % self.size)
            elif step == "z2":
                tmp_solution.append("%dF" % self.size)
                tmp_solution.append("%dF" % self.size)

            else:
                tmp_solution.append(step)

        for step in tmp_solution:
            if step.startswith(str(self.size)):
                rotations.append(apply_rotations(self.size, step, rotations))
            else:
                final_steps.append(apply_rotations(self.size, step, rotations))
        print("Solution: %s" % ' '.join(final_steps))
        #log.info(len(final_steps))

        if self.steps_to_solve_centers:
            log.info("%d steps to solve centers" % self.steps_to_solve_centers)

        if self.steps_to_group_edges:
            log.info("%d steps to group edges" % self.steps_to_group_edges)

        if self.steps_to_solve_3x3x3:
            log.info("%d steps to solve 3x3x3" % self.steps_to_solve_3x3x3)

        log.info("%d steps total" % self.get_solution_len_minus_rotates(self.solution))

        solution_txt_filename = os.path.join(HTML_DIRECTORY, 'solution.txt')
        with open(solution_txt_filename, 'w') as fh:
            fh.write(' '.join(final_steps) + "\n")
        os.chmod(solution_txt_filename, 0o777)

    def nuke_corners(self):
        for side in list(self.sides.values()):
            for square_index in side.corner_pos:
                self.state[square_index] = '.'

    def nuke_centers(self):
        for side in list(self.sides.values()):
            for square_index in side.center_pos:
                self.state[square_index] = '.'

    def nuke_edges(self):
        for side in list(self.sides.values()):
            for square_index in side.edge_pos:
                self.state[square_index] = '.'

    def www_header(self):
        """
        Write the <head> including css
        """
        side_margin = 10
        square_size = 40
        size = self.size # 3 for 3x3x3, etc

        for filename in ('solution.js', 'Arrow-Next.png', 'Arrow-Prev.png'):
            www_filename = os.path.join('www', filename)
            tmp_filename = os.path.join(HTML_DIRECTORY, filename)

            if not os.path.exists(tmp_filename):
                shutil.copy(www_filename, HTML_DIRECTORY)
                os.chmod(tmp_filename, 0o777)

        if os.path.exists(HTML_FILENAME):
            os.unlink(HTML_FILENAME)

        with open(HTML_FILENAME, 'w') as fh:
            fh.write("""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
div.clear {
    clear: both;
}

div.clear_left {
    clear: left;
}

.clickable {
        cursor: pointer;
}

div.side {
    margin: %dpx;
    float: left;
}

a.prev_page {
    float: left;
}

a.next_page {
    float: right;
}

""" % side_margin)

            for x in range(1, size-1):
                fh.write("div.col%d,\n" % x)

            fh.write("""div.col%d {
    float: left;
}

div.col%d {
    margin-left: %dpx;
}
div#upper,
div#down {
    margin-left: %dpx;
}
""" % (size-1,
       size,
       (size - 1) * square_size,
       (size * square_size) + (3 * side_margin)))

            fh.write("""
span.square {
    width: %dpx;
    height: %dpx;
    white-space-collapsing: discard;
    display: inline-block;
    color: black;
    font-weight: bold;
    line-height: %dpx;
    text-align: center;
}

div.square {
    width: %dpx;
    height: %dpx;
    color: black;
    font-weight: bold;
    line-height: %dpx;
    text-align: center;
}

div.square span {
  display:        inline-block;
  vertical-align: middle;
  line-height:    normal;
}

div.page {
  display: none;
}

div#page_holder {
  width: %dpx;
}

</style>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js"></script>
<script type='text/javascript' src='http://code.jquery.com/ui/1.10.3/jquery-ui.min.js'></script>
<script type="text/javascript" src="solution.js"></script>
<title>CraneCuber</title>
</head>
<body>
<div id="page_holder">
""" % (square_size, square_size, square_size, square_size, square_size, square_size,
       (square_size * size * 4) + square_size + (4 * side_margin)))
        os.chmod(HTML_FILENAME, 0o777)

    def www_write_cube(self, desc):
        """
        'cube' is a list of (R,G,B) tuples
        """
        cube = ['dummy',]
        for square in self.state[1:]:
            cube.append(self.color_map_html[square])

        col = 1
        squares_per_side = self.size * self.size
        max_square = squares_per_side * 6

        sides = ('upper', 'left', 'front', 'right', 'back', 'down')
        side_index = -1
        (first_squares, last_squares, last_UBD_squares) = get_important_square_indexes(self.size)

        with open(HTML_FILENAME, 'a') as fh:
            fh.write("<div class='page' style='display: none;'>\n")
            fh.write("<h1>%s</h1>\n" % desc)
            for index in range(1, max_square + 1):
                if index in first_squares:
                    side_index += 1
                    fh.write("<div class='side' id='%s'>\n" % sides[side_index])

                (red, green, blue) = cube[index]
                fh.write("    <div class='square col%d' title='RGB (%d, %d, %d)' style='background-color: #%02x%02x%02x;'><span>%02d</span></div>\n" %
                    (col,
                     red, green, blue,
                     red, green, blue,
                     index))

                if index in last_squares:
                    fh.write("</div>\n")

                    if index in last_UBD_squares:
                        fh.write("<div class='clear'></div>\n")

                col += 1

                if col == self.size + 1:
                    col = 1
            fh.write("</div>\n")

    def www_footer(self):
        with open(HTML_FILENAME, 'a') as fh:
            fh.write("""
<div id="sets-browse-controls">
<a class="prev_page" style="display: block;"><img src="Arrow-Prev.png" class="clickable" width="128"></a>
<a class="next_page" style="display: block;"><img src="Arrow-Next.png" class="clickable" width="128"></a>
</div>
</div>
</body>
</html>
""")

    def rotate_to_side(self, upper_side_name, front_side_name):

        if upper_side_name == front_side_name:
            return False

        if upper_side_name == 'U':

            if front_side_name == 'D':
                return False

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
                return False

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
                return False

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
                return False

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
                return False

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
                return False

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

        return True

    def transform_x(self):
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in range(side.min_pos, side.max_pos+1):
                if self.state[square_index] == 'U':
                    self.state[square_index] = 'B'

                elif self.state[square_index] == 'L':
                    pass

                elif self.state[square_index] == 'F':
                    self.state[square_index] = 'U'

                elif self.state[square_index] == 'R':
                    pass

                elif self.state[square_index] == 'B':
                    self.state[square_index] = 'D'

                elif self.state[square_index] == 'D':
                    self.state[square_index] = 'F'

    def transform_x_prime(self):
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in range(side.min_pos, side.max_pos+1):
                if self.state[square_index] == 'U':
                    self.state[square_index] = 'F'

                elif self.state[square_index] == 'L':
                    pass

                elif self.state[square_index] == 'F':
                    self.state[square_index] = 'D'

                elif self.state[square_index] == 'R':
                    pass

                elif self.state[square_index] == 'B':
                    self.state[square_index] = 'U'

                elif self.state[square_index] == 'D':
                    self.state[square_index] = 'B'

    def transform_y(self):
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in range(side.min_pos, side.max_pos+1):
                if self.state[square_index] == 'U':
                    pass

                elif self.state[square_index] == 'L':
                    self.state[square_index] = 'B'

                elif self.state[square_index] == 'F':
                    self.state[square_index] = 'L'

                elif self.state[square_index] == 'R':
                    self.state[square_index] = 'F'

                elif self.state[square_index] == 'B':
                    self.state[square_index] = 'R'

                elif self.state[square_index] == 'D':
                    pass

    def transform_y_prime(self):
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in range(side.min_pos, side.max_pos+1):
                if self.state[square_index] == 'U':
                    pass

                elif self.state[square_index] == 'L':
                    self.state[square_index] = 'F'

                elif self.state[square_index] == 'F':
                    self.state[square_index] = 'R'

                elif self.state[square_index] == 'R':
                    self.state[square_index] = 'B'

                elif self.state[square_index] == 'B':
                    self.state[square_index] = 'L'

                elif self.state[square_index] == 'D':
                    pass

    def transform_z(self):
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in range(side.min_pos, side.max_pos+1):
                if self.state[square_index] == 'U':
                    self.state[square_index] = 'R'

                elif self.state[square_index] == 'L':
                    self.state[square_index] = 'U'

                elif self.state[square_index] == 'F':
                    pass

                elif self.state[square_index] == 'R':
                    self.state[square_index] = 'D'

                elif self.state[square_index] == 'B':
                    pass

                elif self.state[square_index] == 'D':
                    self.state[square_index] = 'L'

    def transform_z_prime(self):
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in range(side.min_pos, side.max_pos+1):
                if self.state[square_index] == 'U':
                    self.state[square_index] = 'L'

                elif self.state[square_index] == 'L':
                    self.state[square_index] = 'D'

                elif self.state[square_index] == 'F':
                    pass

                elif self.state[square_index] == 'R':
                    self.state[square_index] = 'U'

                elif self.state[square_index] == 'B':
                    pass

                elif self.state[square_index] == 'D':
                    self.state[square_index] = 'R'

    def transform(self, target):
        """
        This should cover every scenario:

        rotations = (
                (),
                ("y",),
                ("y'",),
                ("y", "y"),
                ("x", "x", "y"),
                ("x", "x", "y'"),
                ("x", "x", "y", "y"),
                ("y'", "x", "y"),
                ("y'", "x", "y'"),
                ("y'", "x", "y", "y"),
                ("x", "y"),
                ("x", "y'"),
                ("x", "y", "y"),
                ("y", "x", "y"),
                ("y", "x", "y'"),
                ("y", "x", "y", "y"),
                ("x'", "y"),
                ("x'", "y'"),
                ("x'", "y", "y")
        )
        """
        if not target:
            pass
        elif target == "x":
            self.transform_x()
        elif target == "x'":
            self.transform_x_prime()
        elif target == "y":
            self.transform_y()
        elif target == "y'":
            self.transform_y_prime()
        elif target == "z":
            self.transform_z()
        elif target == "z'":
            self.transform_z_prime()
        else:
            raise Exception("Implement target %s" % target)

    def x_plane_edges_paired(self):
        if (self.sideL.west_edge_paired() and
            self.sideL.east_edge_paired() and
            self.sideR.west_edge_paired() and
            self.sideR.east_edge_paired()):
            return True
        return False

    def x_plane_edges_unpaired_count(self):
        result = 0

        if not self.sideL.west_edge_paired():
            result += 1

        if not self.sideL.east_edge_paired():
            result += 1

        if not self.sideR.west_edge_paired():
            result += 1

        if not self.sideR.east_edge_paired():
            result += 1

        return result

    def y_plane_edges_paired(self):
        if (self.sideU.north_edge_paired() and
            self.sideU.south_edge_paired() and
            self.sideD.north_edge_paired() and
            self.sideD.south_edge_paired()):
            return True
        return False

    def y_plane_edges_unpaired_count(self):
        result = 0

        if not self.sideU.north_edge_paired():
            result += 1

        if not self.sideU.south_edge_paired():
            result += 1

        if not self.sideD.north_edge_paired():
            result += 1

        if not self.sideD.south_edge_paired():
            result += 1

        return result

    def z_plane_edges_paired(self):
        if (self.sideU.west_edge_paired() and
            self.sideU.east_edge_paired() and
            self.sideD.west_edge_paired() and
            self.sideD.east_edge_paired()):
            return True
        return False

    def z_plane_edges_unpaired_count(self):
        result = 0

        if not self.sideU.west_edge_paired():
            result += 1

        if not self.sideU.east_edge_paired():
            result += 1

        if not self.sideD.west_edge_paired():
            result += 1

        if not self.sideD.east_edge_paired():
            result += 1

        return result

