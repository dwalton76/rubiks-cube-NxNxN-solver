
from copy import copy
from collections import OrderedDict
from pprint import pformat
from rubikscubennnsolver.RubiksSide import Side, SolveError, StuckInALoop, ImplementThis
import json
import logging
import math
import os
import random
import re
import shutil
import subprocess
import sys

log = logging.getLogger(__name__)


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

    for row in xrange(1, rows + 1):
        line = []

        if row <= size:
            line.append(indent)
            for col in xrange(1, size + 1):
                line.append(digits_format % square_index)
                square_index += 1

        elif row > rows - size:
            line.append(indent)
            for col in xrange(1, size + 1):
                line.append(digits_format % square_index)
                square_index += 1

        else:
            init_square_index = square_index
            last_col = size * 4
            for col in xrange(1, last_col + 1):
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


def apply_rotations(size, step, rotations):
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

    if orbit == 0:
        if edge_index == 0 or edge_index == edges_per_side-1:
            return True
        return False

    if orbit == 1:
        if edge_index == 1 or edge_index == edges_per_side-2:
            return True
        return False

    # TODO verify this is correct
    if edge_index == orbit or edge_index == (edges_per_side - 1 - orbit):
        return True
    return False


def get_important_square_indexes(size):
    """
    Used for writing www pages
    """
    squares_per_side = size * size
    min_square = 1
    max_square = squares_per_side * 6
    first_squares = []
    last_squares = []

    for index in range(1, max_square + 1):
        if (index - 1) % squares_per_side == 0:
            first_squares.append(index)
        elif index % squares_per_side == 0:
            last_squares.append(index)

    last_UBD_squares = (last_squares[0], last_squares[4], last_squares[5])
    #log.info("first    squares: %s" % pformat(first_squares))
    #log.info("last     squares: %s" % pformat(last_squares))
    #log.info("last UBD squares: %s" % pformat(last_UBD_squares))
    return (first_squares, last_squares, last_UBD_squares)


class RubiksCube(object):

    def __init__(self, kociemba_string, colormap, debug=False):
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
        self.ida_count = 0
        self._phase = None
        self.lt_init_called = False

        if colormap:
            colormap = json.loads(colormap)
            self.color_map = {}
            self.color_map_html = {}

            for (side_name, color) in colormap.items():
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
            self.color_map = {
                'U': 97, # Wh
                'L': 92, # Gr
                'F': 91, # Rd
                'R': 94, # Bu
                'B': 90, # Or
                'D': 93, # Ye
            }

            self.color_map_html = {
                'U': (235, 254, 250), # Wh
                'L': (20, 105, 74),   # Gr
                'F': (104, 4, 2),     # Rd
                'R': (22, 57, 103),   # Bu
                'B': (148, 53, 9),    # Or
                'D': (210, 208, 2),   # Ye
            }

        if debug:
            log.setLevel(logging.DEBUG)

        # kociemba_string is in URFDLB order so split this apart and re-arrange it to
        # be ULFRBD so that is is sequential with the normal square numbering scheme
        foo = []
        foo.extend(init_state[1:self.squares_per_side + 1])                                       # U
        foo.extend(init_state[(self.squares_per_side * 4) + 1 : (self.squares_per_side * 5) + 1]) # L
        foo.extend(init_state[(self.squares_per_side * 2) + 1 : (self.squares_per_side * 3) + 1]) # F
        foo.extend(init_state[(self.squares_per_side * 1) + 1 : (self.squares_per_side * 2) + 1]) # R
        foo.extend(init_state[(self.squares_per_side * 5) + 1 : (self.squares_per_side * 6) + 1]) # B
        foo.extend(init_state[(self.squares_per_side * 3) + 1 : (self.squares_per_side * 4) + 1]) # D

        self.state = ['placeholder', ]
        for (square_index, side_name) in enumerate(foo):
            self.state.append(side_name)

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

    def solved(self):
        """
        Return True if the cube is solved
        """
        for side in self.sides.values():
            if not side.solved():
                return False
        return True

    def rotate(self, action):
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
        for turn in xrange(quarter_turns):
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

            for turn in xrange(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in xrange(rows_to_rotate):
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
                        for square_index in xrange(left_first_square, left_last_square + 1):
                            result[square_index] = self.state[square_index + (3 * self.squares_per_side)]

                        for square_index in xrange(front_first_square, front_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                        for square_index in xrange(right_first_square, right_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                        for square_index in xrange(back_first_square, back_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                    else:
                        for square_index in xrange(left_first_square, left_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in xrange(front_first_square, front_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in xrange(right_first_square, right_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in xrange(back_first_square, back_last_square + 1):
                            result[square_index] = self.state[square_index - (3 * self.squares_per_side)]

                self.state = result[:]

        elif side_name == "L":

            for turn in xrange(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in xrange(rows_to_rotate):

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
                    for square_index in xrange(top_first_square, top_last_square + 1, self.size):
                        top_squares.append(self.state[square_index])

                    front_squares = []
                    for square_index in xrange(front_first_square, front_last_square + 1, self.size):
                        front_squares.append(self.state[square_index])

                    down_squares = []
                    for square_index in xrange(down_first_square, down_last_square + 1, self.size):
                        down_squares.append(self.state[square_index])

                    back_squares = []
                    for square_index in xrange(back_first_square, back_last_square + 1, self.size):
                        back_squares.append(self.state[square_index])

                    if reverse:
                        for (index, square_index) in enumerate(xrange(top_first_square, top_last_square + 1, self.size)):
                            result[square_index] = front_squares[index]

                        for (index, square_index) in enumerate(xrange(front_first_square, front_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                        back_squares = list(reversed(back_squares))
                        for (index, square_index) in enumerate(xrange(down_first_square, down_last_square + 1, self.size)):
                            result[square_index] = back_squares[index]

                        top_squares = list(reversed(top_squares))
                        for (index, square_index) in enumerate(xrange(back_first_square, back_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]
                    else:
                        back_squares = list(reversed(back_squares))
                        for (index, square_index) in enumerate(xrange(top_first_square, top_last_square + 1, self.size)):
                            result[square_index] = back_squares[index]

                        for (index, square_index) in enumerate(xrange(front_first_square, front_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                        for (index, square_index) in enumerate(xrange(down_first_square, down_last_square + 1, self.size)):
                            result[square_index] = front_squares[index]

                        down_squares = list(reversed(down_squares))
                        for (index, square_index) in enumerate(xrange(back_first_square, back_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                self.state = result[:]

        elif side_name == "F":

            for turn in xrange(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in xrange(rows_to_rotate):
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
                    for square_index in xrange(top_first_square, top_last_square + 1):
                        top_squares.append(self.state[square_index])

                    left_squares = []
                    for square_index in xrange(left_first_square, left_last_square + 1, self.size):
                        left_squares.append(self.state[square_index])

                    down_squares = []
                    for square_index in xrange(down_first_square, down_last_square + 1):
                        down_squares.append(self.state[square_index])

                    right_squares = []
                    for square_index in xrange(right_first_square, right_last_square + 1, self.size):
                        right_squares.append(self.state[square_index])

                    if reverse:
                        for (index, square_index) in enumerate(xrange(top_first_square, top_last_square + 1)):
                            result[square_index] = right_squares[index]

                        top_squares = list(reversed(top_squares))
                        for (index, square_index) in enumerate(xrange(left_first_square, left_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                        for (index, square_index) in enumerate(xrange(down_first_square, down_last_square + 1)):
                            result[square_index] = left_squares[index]

                        down_squares = list(reversed(down_squares))
                        for (index, square_index) in enumerate(xrange(right_first_square, right_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                    else:
                        left_squares = list(reversed(left_squares))
                        for (index, square_index) in enumerate(xrange(top_first_square, top_last_square + 1)):
                            result[square_index] = left_squares[index]

                        for (index, square_index) in enumerate(xrange(left_first_square, left_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                        right_squares = list(reversed(right_squares))
                        for (index, square_index) in enumerate(xrange(down_first_square, down_last_square + 1)):
                            result[square_index] = right_squares[index]

                        for (index, square_index) in enumerate(xrange(right_first_square, right_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                self.state = result[:]

        elif side_name == "R":

            for turn in xrange(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in xrange(rows_to_rotate):

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
                    for square_index in xrange(top_first_square, top_last_square + 1, self.size):
                        top_squares.append(self.state[square_index])

                    front_squares = []
                    for square_index in xrange(front_first_square, front_last_square + 1, self.size):
                        front_squares.append(self.state[square_index])

                    down_squares = []
                    for square_index in xrange(down_first_square, down_last_square + 1, self.size):
                        down_squares.append(self.state[square_index])

                    back_squares = []
                    for square_index in xrange(back_first_square, back_last_square + 1, self.size):
                        back_squares.append(self.state[square_index])

                    if reverse:
                        back_squares = list(reversed(back_squares))
                        for (index, square_index) in enumerate(xrange(top_first_square, top_last_square + 1, self.size)):
                            result[square_index] = back_squares[index]

                        for (index, square_index) in enumerate(xrange(front_first_square, front_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                        for (index, square_index) in enumerate(xrange(down_first_square, down_last_square + 1, self.size)):
                            result[square_index] = front_squares[index]

                        down_squares = list(reversed(down_squares))
                        for (index, square_index) in enumerate(xrange(back_first_square, back_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                    else:
                        for (index, square_index) in enumerate(xrange(top_first_square, top_last_square + 1, self.size)):
                            result[square_index] = front_squares[index]

                        for (index, square_index) in enumerate(xrange(front_first_square, front_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                        back_squares = list(reversed(back_squares))
                        for (index, square_index) in enumerate(xrange(down_first_square, down_last_square + 1, self.size)):
                            result[square_index] = back_squares[index]

                        top_squares = list(reversed(top_squares))
                        for (index, square_index) in enumerate(xrange(back_first_square, back_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                self.state = result[:]

        elif side_name == "B":

            for turn in xrange(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in xrange(rows_to_rotate):
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
                    for square_index in xrange(top_first_square, top_last_square + 1):
                        top_squares.append(self.state[square_index])

                    left_squares = []
                    for square_index in xrange(left_first_square, left_last_square + 1, self.size):
                        left_squares.append(self.state[square_index])

                    down_squares = []
                    for square_index in xrange(down_first_square, down_last_square + 1):
                        down_squares.append(self.state[square_index])

                    right_squares = []
                    for square_index in xrange(right_first_square, right_last_square + 1, self.size):
                        right_squares.append(self.state[square_index])

                    if reverse:
                        left_squares = list(reversed(left_squares))
                        for (index, square_index) in enumerate(xrange(top_first_square, top_last_square + 1)):
                            result[square_index] = left_squares[index]

                        for (index, square_index) in enumerate(xrange(left_first_square, left_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                        right_squares = list(reversed(right_squares))
                        for (index, square_index) in enumerate(xrange(down_first_square, down_last_square + 1)):
                            result[square_index] = right_squares[index]

                        for (index, square_index) in enumerate(xrange(right_first_square, right_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                    else:
                        for (index, square_index) in enumerate(xrange(top_first_square, top_last_square + 1)):
                            result[square_index] = right_squares[index]

                        top_squares = list(reversed(top_squares))
                        for (index, square_index) in enumerate(xrange(left_first_square, left_last_square + 1, self.size)):
                            result[square_index] = top_squares[index]

                        for (index, square_index) in enumerate(xrange(down_first_square, down_last_square + 1)):
                            result[square_index] = left_squares[index]

                        down_squares = list(reversed(down_squares))
                        for (index, square_index) in enumerate(xrange(right_first_square, right_last_square + 1, self.size)):
                            result[square_index] = down_squares[index]

                self.state = result[:]

        elif side_name == "D":

            for turn in xrange(quarter_turns):

                # rotate the connecting row(s) of the surrounding sides
                for row in xrange(rows_to_rotate):
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
                        for square_index in xrange(left_first_square, left_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in xrange(front_first_square, front_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in xrange(right_first_square, right_last_square + 1):
                            result[square_index] = self.state[square_index + self.squares_per_side]

                        for square_index in xrange(back_first_square, back_last_square + 1):
                            result[square_index] = self.state[square_index - (3 * self.squares_per_side)]

                    else:
                        for square_index in xrange(left_first_square, left_last_square + 1):
                            result[square_index] = self.state[square_index + (3 * self.squares_per_side)]

                        for square_index in xrange(front_first_square, front_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                        for square_index in xrange(right_first_square, right_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                        for square_index in xrange(back_first_square, back_last_square + 1):
                            result[square_index] = self.state[square_index - self.squares_per_side]

                self.state = result[:]

        else:
            raise Exception("Unsupported action %s" % action)

    def print_cube_layout(self):
        print(get_cube_layout(self.size) + '\n')

    def print_cube(self):
        side_names = ('U', 'L', 'F', 'R', 'B', 'D')
        side_name_index = 0
        rows = []
        row_index = 0
        printing_numbers = False

        for x in xrange(self.size * 3):
            rows.append([])

        for (square_index, square_state) in enumerate(self.state):

            # ignore the placeholder
            if square_index == 0:
                continue

            side_name = side_names[side_name_index]
            color = self.color_map.get(square_state, None)

            if color:
                # end of the row
                if square_index % self.size == 0:
                    rows[row_index].append("\033[%dm%s\033[0m " % (color, square_state))
                    row_index += 1
                else:
                    rows[row_index].append("\033[%dm%s\033[0m" % (color, square_state))
            else:
                if square_state.isdigit():
                    printing_numbers = True

                # end of the row
                if square_index % self.size == 0:
                    if square_state.endswith('x'):
                        rows[row_index].append("%s " % square_state)
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
        print("    } else if (strcmp(step, \"%s\") == 0) {" % case)
        for (key, value) in enumerate(self.state[1:]):
            key += 1

            if str(key) != str(value):
                print("        cube[%s] = cube_tmp[%s];" % (key, value))
        print("")

    def print_case_statement_python(self, case):
        """
        This is called via --rotate-printer, it is used to print the
        if/elif statements used by rotate.py
        """
        new_cube_string = "cube[0]"
        for (key, value) in enumerate(self.state[1:]):
            new_cube_string += ", cube[%s]" % value
        print("    return [%s]" % new_cube_string)

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

        for x in xrange(count):
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
        raise SolveError("We should not be here, square_index %s" % pformat(square_index))

    def get_edge_colors(self, square_index):
        side = self.get_side_for_index(square_index)
        edge_indexes = None

        if square_index in side.edge_north_pos:
            edge_indexes = side.edge_north_pos
        elif square_index in side.edge_west_pos:
            edge_indexes = side.edge_west_pos
        elif square_index in side.edge_south_pos:
            edge_indexes = side.edge_south_pos
        elif square_index in side.edge_east_pos:
            edge_indexes = side.edge_east_pos

        colors = []

        for edge_index in edge_indexes:
            partner_index = side.get_wing_partner(edge_index)
            colors.append(tuple(sorted((self.state[edge_index], self.state[partner_index]))))

        colors = sorted(list(set(colors)))
        #log.info("%s colors %s" % (square_index, pformat(colors)))
        return colors

    def get_non_paired_wings(self):
        return (self.sideU.non_paired_wings(True, True, True, True) +
                self.sideF.non_paired_wings(False, True, False, True) +
                self.sideB.non_paired_wings(False, True, False, True) +
                self.sideD.non_paired_wings(True, True, True, True))

    def get_non_paired_wings_count(self):
        return len(self.get_non_paired_wings())

    def get_paired_wings(self):
        return (self.sideU.paired_wings(True, True, True, True) +
                self.sideF.paired_wings(False, True, False, True) +
                self.sideB.paired_wings(False, True, False, True) +
                self.sideD.paired_wings(True, True, True, True))

    def get_paired_wings_count(self):
        return len(self.get_paired_wings())

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

    def get_wing_in_middle_of_edge(self, pos1, remove_if_in_same_edge=False):
        wings = self.get_wings(pos1, remove_if_in_same_edge)

        for wing in wings:
            wing_side = self.get_side_for_index(wing[0])
            if wing_side.wing_is_middle_of_edge(wing[0]):
                return wing
        return None

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

    def make_U_west_have_unpaired_edge(self):
        if not self.sideU.west_edge_paired():
            return

        if self.sideU.all_edges_paired():
            self.make_B_north_have_unpaired_edge()

        # U until a non-paired edge is in on the West side of U
        while self.sideU.west_edge_paired():
            self.rotate_U()

    def make_U_south_have_unpaired_edge(self):
        """
        5x5x5 edge pairing is the only place this is used
        """

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

    def rotate_B(self):
        self.rotate("B")

    def rotate_U(self):
        self.rotate("U")

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

    def get_center_corner_state(self):
        return ''.join([self.state[square_index] for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD) for square_index in side.center_corner_pos])

    def centers_solved(self):
        for side in self.sides.values():
            prev_pos = None
            for pos in side.center_pos:
                if prev_pos is not None:
                    if self.state[prev_pos] != self.state[pos]:
                        return False
                prev_pos = pos
        return True

    def UD_centers_staged(self):
        for side in (self.sideU, self.sideD):
            for pos in side.center_pos:
                if self.state[pos] not in ('U', 'D'):
                    return False
        return True

    def LR_centers_staged(self):
        for side in (self.sideL, self.sideR):
            for pos in side.center_pos:
                if self.state[pos] not in ('L', 'R'):
                    return False
        return True

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
            # Use the top-right inner x-center
            offset = ((self.size/2) * self.size) - (self.size/2)

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

                for square_index in xrange(side.min_pos, side.max_pos + 1):
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
                        offset = ((self.size/2) * self.size) - (self.size/2)
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
        orbits_with_oll_parity = self.center_solution_leads_to_oll_parity()
        steps = None

        if not orbits_with_oll_parity:
            return True

        if self.size == 4:
            if orbits_with_oll_parity == [0]:
                steps = "Rw U2 Rw U2 Rw U2 Rw U2 Rw U2"
            else:
                raise SolveError("prevent_OLL for %sx%sx%s, orbits %s have parity issues" %
                                    (self.size, self.size, self.size, pformat(orbits_with_oll_parity)))

        elif self.size == 6:
            # 10 steps
            if orbits_with_oll_parity == [0,1]:
                steps = "3Rw U2 3Rw U2 3Rw U2 3Rw U2 3Rw U2"

            # 10 steps
            elif orbits_with_oll_parity == [0]:
                steps = "Rw U2 Rw U2 Rw U2 Rw U2 Rw U2"

            # 15 steps for an inside orbit
            elif orbits_with_oll_parity == [1]:
                steps = "3Rw Rw' U2 3Rw Rw' U2 3Rw Rw' U2 3Rw Rw' U2 3Rw Rw' U2"

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
                # We should no longer hit OLL for 4x4x4 or 6x6x6
                if self.size == 4 or self.size == 6:
                    raise SolveError("prevent_OLL failed")

                # 26 moves :(
                oll_solution = "%dRw2 R2 U2 %dRw2 R2 U2 %dRw R' U2 %dRw R' U2 %dRw' R' U2 B2 U %dRw' R U' B2 U %dRw R' U R2" % (self.size/2, self.size/2, self.size/2, self.size/2, self.size/2, self.size/2, self.size/2)
                log.warning("Solving OLL %s" % oll_solution)
                self.print_cube()

                for step in oll_solution.split():
                    self.rotate(step)
            else:
                break

    def solve_PLL(self):
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
            raise ImplementThis()
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
            raise ImplementThis()
        elif self.state[self.sideF.edge_south_pos[0]] != 'F':
            self.rotate_x()
        elif self.state[self.sideF.edge_east_pos[0]] != 'F':
            self.rotate_z_reverse()
        elif self.state[self.sideF.edge_west_pos[0]] != 'F':
            raise ImplementThis()
        elif self.state[self.sideR.edge_north_pos[0]] != 'R':
            raise ImplementThis()
        elif self.state[self.sideR.edge_south_pos[0]] != 'R':
            self.rotate_y()
            self.rotate_x()
        elif self.state[self.sideR.edge_east_pos[0]] != 'R':
            self.rotate_y()
            self.rotate_z_reverse()
        elif self.state[self.sideR.edge_west_pos[0]] != 'R':
            raise ImplementThis()
        elif self.state[self.sideB.edge_north_pos[0]] != 'B':
            raise ImplementThis()
        elif self.state[self.sideB.edge_south_pos[0]] != 'B':
            self.rotate_x()
            self.rotate_x()
        elif self.state[self.sideB.edge_east_pos[0]] != 'B':
            raise ImplementThis()
        elif self.state[self.sideB.edge_west_pos[0]] != 'B':
            raise ImplementThis()
        elif self.state[self.sideD.edge_north_pos[0]] != 'D':
            raise ImplementThis()
        elif self.state[self.sideD.edge_south_pos[0]] != 'D':
            raise ImplementThis()
        elif self.state[self.sideD.edge_east_pos[0]] != 'D':
            raise ImplementThis()
        elif self.state[self.sideD.edge_west_pos[0]] != 'D':
            raise ImplementThis()
        else:
            self.print_cube()
            raise Exception("we should not be here")

        if self.state[self.sideF.edge_north_pos[0]] == 'F':
            raise SolveError("F-north should have PLL edge")

        # rotate the other hosed edges to U-west
        if self.state[self.sideU.edge_south_pos[0]] != self.state[self.sideU.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideU.edge_north_pos[0]] != self.state[self.sideU.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideU.edge_west_pos[0]] != self.state[self.sideU.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideU.edge_east_pos[0]] != self.state[self.sideU.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideL.edge_north_pos[0]] != self.state[self.sideL.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideL.edge_south_pos[0]] != self.state[self.sideL.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideL.edge_east_pos[0]] != self.state[self.sideL.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideL.edge_west_pos[0]] != self.state[self.sideL.corner_pos[0]]:
            self.rotate_y()
            pll_id = 2
        elif self.state[self.sideF.edge_south_pos[0]] != self.state[self.sideF.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideF.edge_east_pos[0]] != self.state[self.sideF.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideF.edge_west_pos[0]] != self.state[self.sideF.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideR.edge_north_pos[0]] != self.state[self.sideR.corner_pos[0]]:
            self.rotate_y()
            pll_id = 2
        elif self.state[self.sideR.edge_south_pos[0]] != self.state[self.sideR.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideR.edge_east_pos[0]] != self.state[self.sideR.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideR.edge_west_pos[0]] != self.state[self.sideR.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideB.edge_north_pos[0]] != self.state[self.sideB.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideB.edge_south_pos[0]] != self.state[self.sideB.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideB.edge_east_pos[0]] != self.state[self.sideB.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideB.edge_west_pos[0]] != self.state[self.sideB.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideD.edge_north_pos[0]] != self.state[self.sideD.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideD.edge_south_pos[0]] != self.state[self.sideD.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideD.edge_east_pos[0]] != self.state[self.sideD.corner_pos[0]]:
            raise ImplementThis()
        elif self.state[self.sideD.edge_west_pos[0]] != self.state[self.sideD.corner_pos[0]]:
            raise ImplementThis()
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
            #edge_swap_count = self.get_edge_swap_count(edges_paired=True, debug=True)
            #corner_swap_count = self.get_corner_swap_count(debug=True)
            #raise SolveError("parity error made kociemba barf, edge parity %d, corner parity %d, kociemba %s" %
            #    (edge_swap_count, corner_swap_count, kociemba_string))
            raise SolveError("parity error made kociemba barf,  kociemba %s" % kociemba_string)

        log.debug("kociemba       : %s" % kociemba_string)
        log.debug("kociemba steps : %s" % ', '.join(steps))

        for step in steps:
            step = str(step)
            self.rotate(step)

        if not self.solved():
            self.solve_OLL()

            if not self.solved():
                self.solve_PLL()

                if not self.solved():
                    print("We hit either OLL or PLL parity and could not solve it")
                    sys.exit(1)

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

        for (edge_index, square_index) in enumerate(self.sideU.edge_south_pos):
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

        for (edge_index, square_index) in enumerate(self.sideD.edge_south_pos):
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

                self.state = original_state[:]
                self.solution = original_solution[:]

            current_edges.append(wing_str)

        if debug:
            log.info("current edges: %s" % ' '.join(current_edges))
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
        self.rotate_U_to_U()
        self.rotate_F_to_F()

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
        self.rotate_U_to_U()
        self.rotate_F_to_F()
        orbits_with_oll_parity = []

        orbits = (self.size - 2) / 2

        for orbit in xrange(orbits):
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
            for square_index in xrange(side.min_pos, side.max_pos + 1):
                result.append(self.state[square_index])

        return ''.join(result)

    def group_centers_guts(self):
        raise ImplementThis("Child class must implement group_centers_guts")

    def group_centers(self):

        if self.centers_solved():
            log.info("group center solution: centers are already solved")
            self.solution.append('CENTERS_SOLVED')
            return

        min_solution_length = None
        min_solution_leads_to_oll = False
        min_solution_non_paired_wings_count = None
        min_solution_state = None
        min_solution = None

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        # You could set this to False for 4x4x4, for 5x5x5 and larger IDA is used to solve
        # the centers so it takes much longer...you really don't want to sit there and crank
        # through all of the upper_side_name/front_side_name/opening_move combinations.
        #
        # Even for 4x4x4 it isn't worth it, it only shaves 1 move off of center
        # solving across our 50 test cubes.
        break_out_asap = True

        if self.size == 6:
            opening_moves = (None,
                             "3Uw", "Uw",
                             "3Lw", "Lw",
                             "3Fw", "Fw",
                             "3Rw", "Rw",
                             "3Bw", "Bw",
                             "3Dw", "Dw",
                             "3Uw'", "Uw'",
                             "3Lw'", "Lw'",
                             "3Fw'", "Fw'",
                             "3Rw'", "Rw'",
                             "3Bw'", "Bw'",
                             "3Dw'", "Dw'")
        else:
            opening_moves = (None,
                             "Uw", "Dw", "Lw", "Fw", "Rw", "Bw",
                             "Uw'", "Dw'", "Lw'", "Fw'", "Rw'", "Bw'")

        for upper_side_name in ('U', 'D', 'L', 'F', 'R', 'B'):
            for front_side_name in ('F', 'R', 'B', 'L', 'U', 'D'):
                for opening_move in opening_moves:

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

                    if opening_move:
                        self.rotate(opening_move)

                    log.info("")
                    log.info("")
                    log.info("")
                    self.group_centers_guts()

                    if not self.centers_solved():
                        raise SolveError("centers should be solved but they are not")

                    # Prefer solutions that do not lead to OLL parity. Note that we do not do this
                    # for anything larger than 4x4x4 because it takes too long to compute multiple
                    # solutions for solving the centers.
                    if self.is_even():
                        orbits_with_oll_parity = self.center_solution_leads_to_oll_parity()

                        if orbits_with_oll_parity:
                            if self.size == 4:
                                log.info("%s on top, %s in front, opening move %4s: creates OLL parity" % (upper_side_name, front_side_name, opening_move))
                                solution_leads_to_oll = True
                            else:
                                #log.info("%s on top, %s in front, opening move %4s: creates OLL parity" % (upper_side_name, front_side_name, opening_move))
                                #solution_leads_to_oll = True
                                log.info("%s on top, %s in front, opening move %4s: creates OLL parity but we will avoid it" % (upper_side_name, front_side_name, opening_move))
                                if self.prevent_OLL():
                                    solution_leads_to_oll = False
                                else:
                                    solution_leads_to_oll = True
                        else:
                            log.info("%s on top, %s in front, opening move %4s: free of OLL parity" % (upper_side_name, front_side_name, opening_move))
                            solution_leads_to_oll = False
                    else:
                        solution_leads_to_oll = False

                    center_solution_length = self.get_solution_len_minus_rotates(self.solution)
                    non_paired_wings_count = self.get_non_paired_wings_count()

                    if min_solution_length is None:
                        update_min = True
                    elif min_solution_leads_to_oll and not solution_leads_to_oll:
                        update_min = True
                    elif not min_solution_leads_to_oll and solution_leads_to_oll:
                        update_min = False
                    elif center_solution_length < min_solution_length:
                        update_min = True
                    elif center_solution_length == min_solution_length and non_paired_wings_count < min_solution_non_paired_wings_count:
                        update_min = True
                    else:
                        update_min = False

                    if update_min:
                        min_solution_leads_to_oll = solution_leads_to_oll
                        min_solution = self.solution[:]
                        min_solution_state = self.state[:]
                        min_solution_length = copy(center_solution_length)
                        min_solution_non_paired_wings_count = non_paired_wings_count

                        log.warning("%s on top, %s in front, opening move %4s: solution length %d, min solution length %s, non paired wings %d (NEW MIN)" %\
                            (upper_side_name, front_side_name, opening_move, center_solution_length, min_solution_length, min_solution_non_paired_wings_count))
                    else:
                        log.info("%s on top, %s in front, opening move %4s: solution length %d, min solution length %s, non paired wings %d" %\
                            (upper_side_name, front_side_name, opening_move, center_solution_length, min_solution_length, min_solution_non_paired_wings_count))

                    # We can compute solutions for 4x4x4 centers without using IDA so
                    # those are very fast, keep exploring 4x4x4 solutions until we find
                    # one that is free of OLL.
                    if min_solution_length is not None:
                        if min_solution_leads_to_oll:
                            if self.size == 4:
                                min_solution_length = None
                            else:
                                break
                        else:
                            break

                if min_solution_length is not None:
                    break

            if min_solution_length is not None:
                break

        if min_solution_length is None:
            raise SolveError("Could not find parity free solution for centers")

        log.info("group center solution (%d steps): %s" % (min_solution_length, ' '.join(min_solution)))
        self.state = min_solution_state[:]
        self.solution = min_solution[:]
        self.solution.append('CENTERS_SOLVED')

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

    def get_solution_len_minus_rotates(self, solution):
        count = 0
        size_str = str(self.size)

        for step in solution:
            if step in ('CENTERS_SOLVED', 'EDGES_GROUPED'):
                continue
            if not step.startswith(size_str):
                count += 1

        return count

    def compress_solution(self):
        solution_string = ' '.join(self.solution)
        moves = set(self.solution)

        while True:
            original_solution_string = solution_string[:]

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
                rotations.append(apply_rotations(self.size, step, rotations))
            else:
                final_steps.append(apply_rotations(self.size, step, rotations))
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
        The RubiksCube222 and RubiksCube333 child classes will override
        this since they don't need to group centers or edges
        """
        solved_string = 'U' * self.squares_per_side +\
                        'L' * self.squares_per_side +\
                        'F' * self.squares_per_side +\
                        'R' * self.squares_per_side +\
                        'B' * self.squares_per_side +\
                        'D' * self.squares_per_side

        if self.get_state_all() != solved_string:
            self.group_centers()
            self.group_edges()
            self.rotate_U_to_U()
            self.rotate_F_to_F()
            self.solve_333()
            self.compress_solution()

    def print_solution(self):
        print("\nSolution: %s" % ' '.join(self.solution))

        if self.steps_to_rotate_cube:
            print("%d steps to rotate entire cube" % self.steps_to_rotate_cube)

        if self.steps_to_solve_centers:
            print("%d steps to solve centers" % self.steps_to_solve_centers)

        if self.steps_to_group_edges:
            print("%d steps to group edges" % self.steps_to_group_edges)

        if self.steps_to_solve_3x3x3:
            print("%d steps to solve 3x3x3" % self.steps_to_solve_3x3x3)

        print("%d steps total" % len(self.solution))

    def edge_string_to_find(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = []
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in sorted(side.edge_pos):
                if square_index == target_wing[0]:
                    state.append('A')

                elif square_index == target_wing[1]:
                    state.append('B')

                elif square_index == sister_wing1[0]:
                    state.append('C')

                elif square_index == sister_wing1[1]:
                    state.append('D')

                elif square_index == sister_wing2[0]:
                    state.append('E')

                elif square_index == sister_wing2[1]:
                    state.append('F')

                elif square_index == sister_wing3[0]:
                    state.append('G')

                elif square_index == sister_wing3[1]:
                    state.append('H')

                else:
                    state.append('x')

        return ''.join(state)

    def www_header(self):
        """
        Write the <head> including css
        """
        side_margin = 10
        square_size = 40
        size = self.size # 3 for 3x3x3, etc
        shutil.copy('www/solution.js', '/tmp/')
        shutil.copy('www/Arrow-Next.png', '/tmp/')
        shutil.copy('www/Arrow-Prev.png', '/tmp/')

        with open('/tmp/solution.html', 'w') as fh:
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

    def www_write_cube(self, desc):
        """
        'cube' is a list of (R,G,B) tuples
        """
        cube = ['dummy',]
        for square in self.state[1:]:
            cube.append(self.color_map_html[square])

        col = 1
        squares_per_side = self.size * self.size
        min_square = 1
        max_square = squares_per_side * 6

        sides = ('upper', 'left', 'front', 'right', 'back', 'down')
        side_index = -1
        (first_squares, last_squares, last_UBD_squares) = get_important_square_indexes(self.size)

        with open('/tmp/solution.html', 'a') as fh:
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
        with open('/tmp/solution.html', 'a') as fh:
            # dwalton
            fh.write("""
<div id="sets-browse-controls">
<a class="prev_page" style="display: block;"><img src="Arrow-Prev.png" class="clickable" width="128"></a>
<a class="next_page" style="display: block;"><img src="Arrow-Next.png" class="clickable" width="128"></a>
</div>
</div>
</body>
</html>
""")
