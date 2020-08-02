# standard libraries
import logging
import math
from pprint import pformat

log = logging.getLogger(__name__)


def build_2d_list(squares_list):
    """
    Convert 1d list to a 2d list
    squares_list is for a single side
    """
    result = []
    row = []

    squares_per_side = len(squares_list)
    size = int(math.sqrt(squares_per_side))

    for (square_index, x) in enumerate(squares_list):
        row.append(x)

        if (square_index + 1) % size == 0:
            result.append(row)
            row = []

    return result


class SolveError(Exception):
    pass


class NotSolving(Exception):
    pass


class StuckInALoop(Exception):
    pass


class ImplementThis(Exception):
    pass


class Side(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.squares_per_side = self.parent.squares_per_side
        self.size = int(math.sqrt(self.squares_per_side))
        self.wing_partner = {}

        if self.name == "U":
            index = 0
        elif self.name == "L":
            index = 1
        elif self.name == "F":
            index = 2
        elif self.name == "R":
            index = 3
        elif self.name == "B":
            index = 4
        elif self.name == "D":
            index = 5

        self.min_pos = (index * self.squares_per_side) + 1
        self.max_pos = (index * self.squares_per_side) + self.squares_per_side

        # If this is a cube of odd size (3x3x3) then define a mid_pos
        if self.size % 2 == 0:
            self.mid_pos = None
        else:
            self.mid_pos = int((self.min_pos + self.max_pos) / 2)

        # Corners
        self.corner_pos = (self.min_pos, self.min_pos + self.size - 1, self.max_pos - self.size + 1, self.max_pos)

        # Edges
        self.edge_pos = []
        self.edge_north_pos = []
        self.edge_west_pos = []
        self.edge_south_pos = []
        self.edge_east_pos = []
        self.center_pos = []

        for position in range(self.min_pos, self.max_pos):
            if position in self.corner_pos:
                pass

            # Edges at the north
            elif position > self.corner_pos[0] and position < self.corner_pos[1]:
                self.edge_pos.append(position)
                self.edge_north_pos.append(position)

            # Edges at the south
            elif position > self.corner_pos[2] and position < self.corner_pos[3]:
                self.edge_pos.append(position)
                self.edge_south_pos.append(position)

            elif (position - 1) % self.size == 0:
                west_edge = position
                east_edge = west_edge + self.size - 1

                # Edges on the west
                self.edge_pos.append(west_edge)
                self.edge_west_pos.append(west_edge)

                # Edges on the east
                self.edge_pos.append(east_edge)
                self.edge_east_pos.append(east_edge)

                # Center squares
                for x in range(west_edge + 1, east_edge):
                    self.center_pos.append(x)

        self.center_corner_pos = [
            self.min_pos + self.size + 1,
            self.min_pos + (self.size * 2) - 2,
            self.max_pos - (self.size * 2) + 2,
            self.max_pos - self.size - 1,
        ]

        if self.size >= 5:
            self.center_edge_pos = [
                self.center_corner_pos[0] + 1,
                self.center_corner_pos[0] + self.size,
                self.center_corner_pos[1] + self.size,
                self.center_corner_pos[2] + 1,
            ]
        else:
            self.center_edge_pos = []

        log.debug(
            "\nSide %s\n\tmin/max %d/%d\n\tedges %s\n\tcorners %s\n\tcenters %s\n\tcenter corners %s\n\tcenter edges %s\n"
            % (
                self.name,
                self.min_pos,
                self.max_pos,
                pformat(self.edge_pos),
                pformat(self.corner_pos),
                pformat(self.center_pos),
                pformat(self.center_corner_pos),
                pformat(self.center_edge_pos),
            )
        )

    def __str__(self):
        return "side %s" % self.name

    def get_face_as_2d_list(self):
        """
        Used by RubiksCube rotate()
        """
        return build_2d_list(
            [self.parent.state[square_index] for square_index in range(self.min_pos, self.max_pos + 1)]
        )

    def get_wing_partner(self, wing_index):
        try:
            return self.wing_partner[wing_index]
        except KeyError:
            log.info("wing_partner\n%s\n" % pformat(self.wing_partner))
            raise

    def non_paired_wings(self, check_north, check_west, check_south, check_east):
        non_paired_wings = []

        # north edge
        if check_north:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_north_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if (
                        self.parent.state[prev_pos1] != self.parent.state[pos1]
                        or self.parent.state[prev_pos2] != self.parent.state[pos2]
                    ):
                        non_paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        # west edge
        if check_west:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_west_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if (
                        self.parent.state[prev_pos1] != self.parent.state[pos1]
                        or self.parent.state[prev_pos2] != self.parent.state[pos2]
                    ):
                        non_paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        # south edge
        if check_south:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_south_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if (
                        self.parent.state[prev_pos1] != self.parent.state[pos1]
                        or self.parent.state[prev_pos2] != self.parent.state[pos2]
                    ):
                        non_paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        # east edge
        if check_east:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_east_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if (
                        self.parent.state[prev_pos1] != self.parent.state[pos1]
                        or self.parent.state[prev_pos2] != self.parent.state[pos2]
                    ):
                        non_paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        return non_paired_wings

    def non_paired_edges(self, check_north, check_west, check_south, check_east):
        non_paired_edges = []

        # north edge
        if check_north:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_north_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if (
                        self.parent.state[prev_pos1] != self.parent.state[pos1]
                        or self.parent.state[prev_pos2] != self.parent.state[pos2]
                    ):
                        non_paired_edges.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                        break
                prev_pos1 = pos1
                prev_pos2 = pos2

        # west edge
        if check_west:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_west_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if (
                        self.parent.state[prev_pos1] != self.parent.state[pos1]
                        or self.parent.state[prev_pos2] != self.parent.state[pos2]
                    ):
                        non_paired_edges.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                        break
                prev_pos1 = pos1
                prev_pos2 = pos2

        # south edge
        if check_south:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_south_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if (
                        self.parent.state[prev_pos1] != self.parent.state[pos1]
                        or self.parent.state[prev_pos2] != self.parent.state[pos2]
                    ):
                        non_paired_edges.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                        break
                prev_pos1 = pos1
                prev_pos2 = pos2

        # east edge
        if check_east:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_east_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if (
                        self.parent.state[prev_pos1] != self.parent.state[pos1]
                        or self.parent.state[prev_pos2] != self.parent.state[pos2]
                    ):
                        non_paired_edges.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                        break
                prev_pos1 = pos1
                prev_pos2 = pos2

        # log.info("%s; non_paired_edges %s for check_north %s, check_west %s, check_south %s, check_east %s" %
        #    (self, check_north, check_west, check_south, check_east, non_paired_edges))
        return non_paired_edges

    def north_edge_non_paired(self):
        non_paired_edges = self.non_paired_wings(True, False, False, False)

        for ((pos1, pos2), (pos3, pos4)) in non_paired_edges:
            if (
                self.parent.state[pos1] == "-"
                and self.parent.state[pos2] == "-"
                and self.parent.state[pos3] == "-"
                and self.parent.state[pos4] == "-"
            ):
                continue
            if pos1 in self.edge_north_pos:
                return True
            if pos3 in self.edge_north_pos:
                return True

        return False

    def north_edge_paired(self):
        return not self.north_edge_non_paired()

    def south_edge_non_paired(self):
        non_paired_edges = self.non_paired_wings(False, False, True, False)

        for ((pos1, pos2), (pos3, pos4)) in non_paired_edges:
            if (
                self.parent.state[pos1] == "-"
                and self.parent.state[pos2] == "-"
                and self.parent.state[pos3] == "-"
                and self.parent.state[pos4] == "-"
            ):
                continue
            if pos1 in self.edge_south_pos:
                return True
            if pos3 in self.edge_south_pos:
                return True
        return False

    def south_edge_paired(self):
        return not self.south_edge_non_paired()

    def east_edge_non_paired(self):
        non_paired_edges = self.non_paired_wings(False, False, False, True)

        for ((pos1, pos2), (pos3, pos4)) in non_paired_edges:
            if (
                self.parent.state[pos1] == "-"
                and self.parent.state[pos2] == "-"
                and self.parent.state[pos3] == "-"
                and self.parent.state[pos4] == "-"
            ):
                continue
            if pos1 in self.edge_east_pos:
                return True
            if pos3 in self.edge_east_pos:
                return True
        return False

    def east_edge_paired(self):
        return not self.east_edge_non_paired()

    def west_edge_non_paired(self):
        non_paired_edges = self.non_paired_wings(False, True, False, False)

        for ((pos1, pos2), (pos3, pos4)) in non_paired_edges:
            if (
                self.parent.state[pos1] == "-"
                and self.parent.state[pos2] == "-"
                and self.parent.state[pos3] == "-"
                and self.parent.state[pos4] == "-"
            ):
                continue
            if pos1 in self.edge_west_pos:
                return True
            if pos3 in self.edge_west_pos:
                return True
        return False

    def west_edge_paired(self):
        return not self.west_edge_non_paired()

    def solved(self):
        """
        Return True if all squares on this side are the same color
        """
        prev = None

        for pos in range(self.min_pos, self.max_pos + 1):
            current = self.parent.state[pos]
            if prev is not None and current != prev:
                return False
            prev = current
        return True

    def calculate_wing_partners(self):
        for (pos1, pos2) in self.parent.all_edge_positions:
            if pos1 >= self.min_pos and pos1 <= self.max_pos:
                self.wing_partner[pos1] = pos2
            elif pos2 >= self.min_pos and pos2 <= self.max_pos:
                self.wing_partner[pos2] = pos1

    def centers_solved(self):
        prev_pos = None
        for pos in self.center_pos:
            if prev_pos is not None:
                if self.parent.state[prev_pos] != self.parent.state[pos]:
                    return False
            prev_pos = pos

        return True

    def edges_paired(self):
        if self.non_paired_edges(True, True, True, True):
            return False
        return True
