# standard libraries
import logging
import random
import sys
from pprint import pformat

# rubiks cube libraries
from rubikscubennnsolver import wing_str_map
from rubikscubennnsolver.RubiksCube333 import RubiksCube333, moves_333
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, moves_444
from rubikscubennnsolver.RubiksCube555 import RubiksCube555, midge_indexes, moves_555
from rubikscubennnsolver.RubiksCube666 import RubiksCube666
from rubikscubennnsolver.RubiksCube666 import edge_orbit_0 as edge_orbit_0_666
from rubikscubennnsolver.RubiksCube666 import edge_orbit_1 as edge_orbit_1_666
from rubikscubennnsolver.RubiksCube666 import moves_666

log = logging.getLogger(__name__)
random.seed(1234)


class RubiksCubeHighLow333(RubiksCube333):
    def high_low_state(self, x, y, state_x, state_y, wing_str):
        """
        Return U if this is a high edge, D if it is a low edge
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Nuke everything except the one wing we are interested in
        self.nuke_corners()
        self.nuke_centers()
        self.nuke_edges()

        self.state[x] = state_x
        self.state[y] = state_y

        # Now move that wing to its home edge
        if wing_str.startswith("U"):

            if wing_str == "UB":
                self.move_wing_to_U_north(x)
                high_edge_index = 2
                low_edge_index = 38

            elif wing_str == "UL":
                self.move_wing_to_U_west(x)
                high_edge_index = 4
                low_edge_index = 11

            elif wing_str == "UR":
                self.move_wing_to_U_east(x)
                high_edge_index = 6
                low_edge_index = 29

            elif wing_str == "UF":
                self.move_wing_to_U_south(x)
                high_edge_index = 8
                low_edge_index = 20

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "U":
                result = "U"
            elif self.state[low_edge_index] == "U":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "U edge something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("L"):

            if wing_str == "LB":
                self.move_wing_to_L_west(x)
                high_edge_index = 13
                low_edge_index = 42

            elif wing_str == "LF":
                self.move_wing_to_L_east(x)
                high_edge_index = 15
                low_edge_index = 22

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "L":
                result = "U"
            elif self.state[low_edge_index] == "L":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "L edge something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("R"):

            if wing_str == "RB":
                self.move_wing_to_R_east(x)
                high_edge_index = 33
                low_edge_index = 40

            elif wing_str == "RF":
                self.move_wing_to_R_west(x)
                high_edge_index = 31
                low_edge_index = 24

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "R":
                result = "U"
            elif self.state[low_edge_index] == "R":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "R edge something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("D"):
            if wing_str == "DB":
                self.move_wing_to_D_south(x)
                high_edge_index = 53
                low_edge_index = 44

            elif wing_str == "DL":
                self.move_wing_to_D_west(x)
                high_edge_index = 49
                low_edge_index = 17

            elif wing_str == "DR":
                self.move_wing_to_D_east(x)
                high_edge_index = 51
                low_edge_index = 35

            elif wing_str == "DF":
                self.move_wing_to_D_north(x)
                high_edge_index = 47
                low_edge_index = 26

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "D":
                result = "U"
            elif self.state[low_edge_index] == "D":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "D edge something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )
        else:
            raise Exception("invalid wing_str %s" % wing_str)

        self.state = original_state[:]
        self.solution = original_solution[:]

        assert result in ("U", "D")
        return result

    def build_highlow_edge_values(self):
        new_highlow_edge_values = {}

        for x in range(1000000):

            # make random moves
            step = moves_333[random.randint(0, len(moves_333) - 1)]

            if "w" in step:
                continue

            self.rotate(step)

            for (x, y) in self.reduce333_orient_edges_tuples:
                state_x = self.state[x]
                state_y = self.state[y]
                wing_str = wing_str_map[state_x + state_y]
                wing_tuple = (x, y, state_x, state_y)

                if wing_tuple not in new_highlow_edge_values:
                    new_highlow_edge_values[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str)

        print("new highlow_edge_values\n\n%s\n\n" % pformat(new_highlow_edge_values))
        log.info("new_highlow_edge_values has %d entries" % len(new_highlow_edge_values))
        sys.exit(0)


class RubiksCubeHighLow444(RubiksCube444):
    def high_low_state(self, x, y, state_x, state_y, wing_str):
        """
        Return U if this is a high edge, D if it is a low edge
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Nuke everything except the one wing we are interested in
        self.nuke_corners()
        self.nuke_centers()
        self.nuke_edges()

        self.state[x] = state_x
        self.state[y] = state_y

        # Now move that wing to its home edge
        if wing_str.startswith("U"):

            if wing_str == "UB":
                self.move_wing_to_U_north(x)
                high_edge_index = 2
                low_edge_index = 3

            elif wing_str == "UL":
                self.move_wing_to_U_west(x)
                high_edge_index = 9
                low_edge_index = 5

            elif wing_str == "UR":
                self.move_wing_to_U_east(x)
                high_edge_index = 8
                low_edge_index = 12

            elif wing_str == "UF":
                self.move_wing_to_U_south(x)
                high_edge_index = 15
                low_edge_index = 14

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "U":
                result = "U"
            elif self.state[low_edge_index] == "U":
                result = "D"
            elif self.state[high_edge_index] == ".":
                result = "U"
            elif self.state[low_edge_index] == ".":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "U something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("L"):

            if wing_str == "LB":
                self.move_wing_to_L_west(x)
                high_edge_index = 25
                low_edge_index = 21

            elif wing_str == "LF":
                self.move_wing_to_L_east(x)
                high_edge_index = 24
                low_edge_index = 28

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "L":
                result = "U"
            elif self.state[low_edge_index] == "L":
                result = "D"
            elif self.state[high_edge_index] == ".":
                result = "U"
            elif self.state[low_edge_index] == ".":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "L something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("R"):

            if wing_str == "RB":
                self.move_wing_to_R_east(x)
                high_edge_index = 56
                low_edge_index = 60

            elif wing_str == "RF":
                self.move_wing_to_R_west(x)
                high_edge_index = 57
                low_edge_index = 53

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "R":
                result = "U"
            elif self.state[low_edge_index] == "R":
                result = "D"
            elif self.state[high_edge_index] == ".":
                result = "U"
            elif self.state[low_edge_index] == ".":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "R something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("D"):
            if wing_str == "DB":
                self.move_wing_to_D_south(x)
                high_edge_index = 95
                low_edge_index = 94

            elif wing_str == "DL":
                self.move_wing_to_D_west(x)
                high_edge_index = 89
                low_edge_index = 85

            elif wing_str == "DR":
                self.move_wing_to_D_east(x)
                high_edge_index = 88
                low_edge_index = 92

            elif wing_str == "DF":
                self.move_wing_to_D_north(x)
                high_edge_index = 82
                low_edge_index = 83

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "D":
                result = "U"
            elif self.state[low_edge_index] == "D":
                result = "D"
            elif self.state[high_edge_index] == ".":
                result = "U"
            elif self.state[low_edge_index] == ".":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "D something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        else:
            raise Exception("invalid wing_str %s" % wing_str)

        self.state = original_state[:]
        self.solution = original_solution[:]

        assert result in ("U", "D")
        return result

    def build_highlow_edge_values(self):
        new_highlow_edge_values = {}

        for x in range(100000):

            # make random moves
            step = moves_444[random.randint(0, len(moves_444) - 1)]
            self.rotate(step)

            for (x, y) in self.reduce333_orient_edges_tuples:
                state_x = self.state[x]
                state_y = self.state[y]
                wing_str = wing_str_map[state_x + state_y]
                wing_tuple = (x, y, state_x, state_y)

                if wing_tuple not in new_highlow_edge_values:
                    new_highlow_edge_values[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str)

        print("new highlow_edge_values\n\n%s\n\n" % pformat(new_highlow_edge_values))
        log.info("new_highlow_edge_values has %d entries" % len(new_highlow_edge_values))
        sys.exit(0)


class RubiksCubeHighLow555(RubiksCube555):
    def high_low_state(self, x, y, state_x, state_y, wing_str):
        """
        Return U if this is a high edge, D if it is a low edge
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Nuke everything except the one wing we are interested in
        self.nuke_corners()
        self.nuke_centers()
        self.nuke_edges()

        self.state[x] = state_x
        self.state[y] = state_y

        if x in midge_indexes or y in midge_indexes:
            is_midge = True
        else:
            is_midge = False

        # Now move that wing to its home edge
        if wing_str.startswith("U"):

            if wing_str == "UB":
                self.move_wing_to_U_north(x)

                if is_midge:
                    high_edge_index = 3
                    low_edge_index = 103
                else:
                    high_edge_index = 2
                    low_edge_index = 4

            elif wing_str == "UL":
                self.move_wing_to_U_west(x)

                if is_midge:
                    high_edge_index = 11
                    low_edge_index = 28
                else:
                    high_edge_index = 16
                    low_edge_index = 6

            elif wing_str == "UR":
                self.move_wing_to_U_east(x)

                if is_midge:
                    high_edge_index = 15
                    low_edge_index = 78
                else:
                    high_edge_index = 10
                    low_edge_index = 20

            elif wing_str == "UF":
                self.move_wing_to_U_south(x)

                if is_midge:
                    high_edge_index = 23
                    low_edge_index = 53
                else:
                    high_edge_index = 24
                    low_edge_index = 22

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if is_midge:
                if self.state[high_edge_index] == "U":
                    result = "U"
                elif self.state[low_edge_index] == "U":
                    result = "D"
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception(
                        "U midge something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s"
                        % (
                            x,
                            y,
                            state_x,
                            state_y,
                            wing_str,
                            high_edge_index,
                            self.state[high_edge_index],
                            low_edge_index,
                            self.state[low_edge_index],
                            is_midge,
                        )
                    )
            else:
                if self.state[high_edge_index] == "U":
                    result = "U"
                elif self.state[low_edge_index] == "U":
                    result = "D"
                elif self.state[high_edge_index] == ".":
                    result = "U"
                elif self.state[low_edge_index] == ".":
                    result = "D"
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception(
                        "U something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s"
                        % (
                            x,
                            y,
                            state_x,
                            state_y,
                            wing_str,
                            high_edge_index,
                            self.state[high_edge_index],
                            low_edge_index,
                            self.state[low_edge_index],
                            is_midge,
                        )
                    )

        elif wing_str.startswith("L"):

            if wing_str == "LB":
                self.move_wing_to_L_west(x)

                if is_midge:
                    high_edge_index = 36
                    low_edge_index = 115
                else:
                    high_edge_index = 41
                    low_edge_index = 31

            elif wing_str == "LF":
                self.move_wing_to_L_east(x)

                if is_midge:
                    high_edge_index = 40
                    low_edge_index = 61
                else:
                    high_edge_index = 35
                    low_edge_index = 45

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if is_midge:
                if self.state[high_edge_index] == "L":
                    result = "U"
                elif self.state[low_edge_index] == "L":
                    result = "D"
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception(
                        "L midge something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s"
                        % (
                            x,
                            y,
                            state_x,
                            state_y,
                            wing_str,
                            high_edge_index,
                            self.state[high_edge_index],
                            low_edge_index,
                            self.state[low_edge_index],
                            is_midge,
                        )
                    )
            else:
                if self.state[high_edge_index] == "L":
                    result = "U"
                elif self.state[low_edge_index] == "L":
                    result = "D"
                elif self.state[high_edge_index] == ".":
                    result = "U"
                elif self.state[low_edge_index] == ".":
                    result = "D"
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception(
                        "L something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                        % (
                            x,
                            y,
                            state_x,
                            state_y,
                            wing_str,
                            high_edge_index,
                            self.state[high_edge_index],
                            low_edge_index,
                            self.state[low_edge_index],
                        )
                    )

        elif wing_str.startswith("R"):

            if wing_str == "RB":
                self.move_wing_to_R_east(x)

                if is_midge:
                    high_edge_index = 90
                    low_edge_index = 111
                else:
                    high_edge_index = 85
                    low_edge_index = 95

            elif wing_str == "RF":
                self.move_wing_to_R_west(x)

                if is_midge:
                    high_edge_index = 86
                    low_edge_index = 65
                else:
                    high_edge_index = 91
                    low_edge_index = 81

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if is_midge:
                if self.state[high_edge_index] == "R":
                    result = "U"
                elif self.state[low_edge_index] == "R":
                    result = "D"
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception(
                        "R midge something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s"
                        % (
                            x,
                            y,
                            state_x,
                            state_y,
                            wing_str,
                            high_edge_index,
                            self.state[high_edge_index],
                            low_edge_index,
                            self.state[low_edge_index],
                            is_midge,
                        )
                    )
            else:
                if self.state[high_edge_index] == "R":
                    result = "U"
                elif self.state[low_edge_index] == "R":
                    result = "D"
                elif self.state[high_edge_index] == ".":
                    result = "U"
                elif self.state[low_edge_index] == ".":
                    result = "D"
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception(
                        "R something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                        % (
                            x,
                            y,
                            state_x,
                            state_y,
                            wing_str,
                            high_edge_index,
                            self.state[high_edge_index],
                            low_edge_index,
                            self.state[low_edge_index],
                        )
                    )

        elif wing_str.startswith("D"):
            if wing_str == "DB":
                self.move_wing_to_D_south(x)

                if is_midge:
                    high_edge_index = 148
                    low_edge_index = 123
                else:
                    high_edge_index = 149
                    low_edge_index = 147

            elif wing_str == "DL":
                self.move_wing_to_D_west(x)

                if is_midge:
                    high_edge_index = 136
                    low_edge_index = 48
                else:
                    high_edge_index = 141
                    low_edge_index = 131

            elif wing_str == "DR":
                self.move_wing_to_D_east(x)

                if is_midge:
                    high_edge_index = 140
                    low_edge_index = 98
                else:
                    high_edge_index = 135
                    low_edge_index = 145

            elif wing_str == "DF":
                self.move_wing_to_D_north(x)

                if is_midge:
                    high_edge_index = 128
                    low_edge_index = 73
                else:
                    high_edge_index = 127
                    low_edge_index = 129

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if is_midge:
                if self.state[high_edge_index] == "D":
                    result = "U"
                elif self.state[low_edge_index] == "D":
                    result = "D"
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception(
                        "D midge something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s, is_midge %s"
                        % (
                            x,
                            y,
                            state_x,
                            state_y,
                            wing_str,
                            high_edge_index,
                            self.state[high_edge_index],
                            low_edge_index,
                            self.state[low_edge_index],
                            is_midge,
                        )
                    )
            else:
                if self.state[high_edge_index] == "D":
                    result = "U"
                elif self.state[low_edge_index] == "D":
                    result = "D"
                elif self.state[high_edge_index] == ".":
                    result = "U"
                elif self.state[low_edge_index] == ".":
                    result = "D"
                else:
                    self.print_cube()
                    self.print_cube_layout()
                    raise Exception(
                        "D something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                        % (
                            x,
                            y,
                            state_x,
                            state_y,
                            wing_str,
                            high_edge_index,
                            self.state[high_edge_index],
                            low_edge_index,
                            self.state[low_edge_index],
                        )
                    )

        else:
            raise Exception("invalid wing_str %s" % wing_str)

        self.state = original_state[:]
        self.solution = original_solution[:]

        assert result in ("U", "D")
        return result

    def build_highlow_edge_values(self):
        new_highlow_edge_values = {}

        for x in range(1000000):

            # make random moves
            step = moves_555[random.randint(0, len(moves_555) - 1)]

            if "w" in step:
                continue

            self.rotate(step)

            for (x, y) in self.reduce333_orient_edges_tuples:
                state_x = self.state[x]
                state_y = self.state[y]
                wing_str = wing_str_map[state_x + state_y]
                wing_tuple = (x, y, state_x, state_y)

                if wing_tuple not in new_highlow_edge_values:
                    new_highlow_edge_values[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str)

        print("new highlow_edge_values\n\n%s\n\n" % pformat(new_highlow_edge_values))
        log.info("new_highlow_edge_values has %d entries" % len(new_highlow_edge_values))
        sys.exit(0)


class RubiksCubeHighLow666(RubiksCube666):
    def high_low_state(self, x, y, state_x, state_y, wing_str, orbit):
        """
        Return U if this is a high edge, D if it is a low edge
        """
        assert orbit in (0, 1), f"invalid orbit {orbit}"
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Nuke everything except the one wing we are interested in
        self.nuke_corners()
        self.nuke_centers()
        self.nuke_edges()

        self.state[x] = state_x
        self.state[y] = state_y

        # Now move that wing to its home edge
        if wing_str.startswith("U"):

            if wing_str == "UB":
                self.move_wing_to_U_north(x)

                if orbit == 0:
                    high_edge_index = 2
                    low_edge_index = 5
                elif orbit == 1:
                    high_edge_index = 3
                    low_edge_index = 4

            elif wing_str == "UL":
                self.move_wing_to_U_west(x)

                if orbit == 0:
                    high_edge_index = 25
                    low_edge_index = 7
                elif orbit == 1:
                    high_edge_index = 19
                    low_edge_index = 13

            elif wing_str == "UR":
                self.move_wing_to_U_east(x)

                if orbit == 0:
                    high_edge_index = 12
                    low_edge_index = 30
                elif orbit == 1:
                    high_edge_index = 18
                    low_edge_index = 24

            elif wing_str == "UF":
                self.move_wing_to_U_south(x)

                if orbit == 0:
                    high_edge_index = 35
                    low_edge_index = 32
                elif orbit == 1:
                    high_edge_index = 34
                    low_edge_index = 33

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "U":
                result = "U"
            elif self.state[low_edge_index] == "U":
                result = "D"
            elif self.state[high_edge_index] == ".":
                result = "U"
            elif self.state[low_edge_index] == ".":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "U something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("L"):

            if wing_str == "LB":
                self.move_wing_to_L_west(x)

                if orbit == 0:
                    high_edge_index = 61
                    low_edge_index = 43
                elif orbit == 1:
                    high_edge_index = 55
                    low_edge_index = 49

            elif wing_str == "LF":
                self.move_wing_to_L_east(x)

                if orbit == 0:
                    high_edge_index = 48
                    low_edge_index = 66
                elif orbit == 1:
                    high_edge_index = 54
                    low_edge_index = 60

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "L":
                result = "U"
            elif self.state[low_edge_index] == "L":
                result = "D"
            elif self.state[high_edge_index] == ".":
                result = "U"
            elif self.state[low_edge_index] == ".":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "L something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("R"):

            if wing_str == "RB":
                self.move_wing_to_R_east(x)

                if orbit == 0:
                    high_edge_index = 120
                    low_edge_index = 138
                elif orbit == 1:
                    high_edge_index = 126
                    low_edge_index = 132

            elif wing_str == "RF":
                self.move_wing_to_R_west(x)

                if orbit == 0:
                    high_edge_index = 133
                    low_edge_index = 115
                elif orbit == 1:
                    high_edge_index = 127
                    low_edge_index = 121

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "R":
                result = "U"
            elif self.state[low_edge_index] == "R":
                result = "D"
            elif self.state[high_edge_index] == ".":
                result = "U"
            elif self.state[low_edge_index] == ".":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "R something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        elif wing_str.startswith("D"):
            if wing_str == "DB":
                self.move_wing_to_D_south(x)

                if orbit == 0:
                    high_edge_index = 215
                    low_edge_index = 212
                elif orbit == 1:
                    high_edge_index = 214
                    low_edge_index = 213

            elif wing_str == "DL":
                self.move_wing_to_D_west(x)

                if orbit == 0:
                    high_edge_index = 205
                    low_edge_index = 187
                elif orbit == 1:
                    high_edge_index = 199
                    low_edge_index = 193

            elif wing_str == "DR":
                self.move_wing_to_D_east(x)

                if orbit == 0:
                    high_edge_index = 192
                    low_edge_index = 210
                elif orbit == 1:
                    high_edge_index = 198
                    low_edge_index = 204

            elif wing_str == "DF":
                self.move_wing_to_D_north(x)

                if orbit == 0:
                    high_edge_index = 182
                    low_edge_index = 185
                elif orbit == 1:
                    high_edge_index = 183
                    low_edge_index = 184

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == "D":
                result = "U"
            elif self.state[low_edge_index] == "D":
                result = "D"
            elif self.state[high_edge_index] == ".":
                result = "U"
            elif self.state[low_edge_index] == ".":
                result = "D"
            else:
                self.print_cube()
                self.print_cube_layout()
                raise Exception(
                    "D something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s"
                    % (
                        x,
                        y,
                        state_x,
                        state_y,
                        wing_str,
                        high_edge_index,
                        self.state[high_edge_index],
                        low_edge_index,
                        self.state[low_edge_index],
                    )
                )

        else:
            raise Exception("invalid wing_str %s" % wing_str)

        if orbit == 0:
            assert high_edge_index in edge_orbit_0_666, f"{high_edge_index} is not in edge_orbit_0_666"
            assert low_edge_index in edge_orbit_0_666, f"{low_edge_index} is not in edge_orbit_0_666"
        elif orbit == 1:
            assert high_edge_index in edge_orbit_1_666, f"{high_edge_index} is not in edge_orbit_1_666"
            assert low_edge_index in edge_orbit_1_666, f"{low_edge_index} is not in edge_orbit_1_666"

        self.state = original_state[:]
        self.solution = original_solution[:]

        assert result in ("U", "D")
        return result

    def build_highlow_edge_values(self):
        new_highlow_edge_values = {}

        for x in range(100000):

            # make random moves
            step = moves_666[random.randint(0, len(moves_666) - 1)]
            self.rotate(step)

            for (x, y) in self.reduce333_orient_edges_tuples:
                state_x = self.state[x]
                state_y = self.state[y]
                wing_str = wing_str_map[state_x + state_y]
                wing_tuple = (x, y, state_x, state_y)

                if x in edge_orbit_0_666 and y in edge_orbit_0_666:
                    orbit = 0
                elif x in edge_orbit_1_666 and y in edge_orbit_1_666:
                    orbit = 1
                else:
                    raise Exception(f"What orbit for ({x}, {y})?")

                if wing_tuple not in new_highlow_edge_values:
                    new_highlow_edge_values[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str, orbit)

        print("new highlow_edge_values\n\n%s\n\n" % pformat(new_highlow_edge_values))
        log.info("new_highlow_edge_values has %d entries" % len(new_highlow_edge_values))
