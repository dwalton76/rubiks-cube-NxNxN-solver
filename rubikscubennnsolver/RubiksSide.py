#!/usr/bin/env python3

from pprint import pformat
import logging
import math

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


class Side(object):

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.squares_per_side = self.parent.squares_per_side
        self.size = int(math.sqrt(self.squares_per_side))
        self.wing_partner = {}

        if self.name == 'U':
            index = 0
        elif self.name == 'L':
            index = 1
        elif self.name == 'F':
            index = 2
        elif self.name == 'R':
            index = 3
        elif self.name == 'B':
            index = 4
        elif self.name == 'D':
            index = 5

        self.min_pos = (index * self.squares_per_side) + 1
        self.max_pos = (index * self.squares_per_side) + self.squares_per_side

        # If this is a cube of odd size (3x3x3) then define a mid_pos
        if self.size % 2 == 0:
            self.mid_pos = None
        else:
            self.mid_pos = int((self.min_pos + self.max_pos) / 2)


        # Corners
        self.corner_pos = (self.min_pos,
                           self.min_pos + self.size - 1,
                           self.max_pos - self.size + 1,
                           self.max_pos)

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

        self.center_corner_pos = [self.min_pos + self.size + 1,
                               self.min_pos + (self.size * 2) - 2,
                               self.max_pos - (self.size * 2) + 2,
                               self.max_pos - self.size - 1]

        if self.size >= 5:
            self.center_edge_pos = [self.center_corner_pos[0] + 1,
                                    self.center_corner_pos[0] + self.size,
                                    self.center_corner_pos[1] + self.size,
                                    self.center_corner_pos[2] + 1]
        else:
            self.center_edge_pos = []

        log.debug("\nSide %s\n\tmin/max %d/%d\n\tedges %s\n\tcorners %s\n\tcenters %s\n\tcenter corners %s\n\tcenter edges %s\n" %
            (self.name, self.min_pos, self.max_pos,
             pformat(self.edge_pos),
             pformat(self.corner_pos),
             pformat(self.center_pos),
             pformat(self.center_corner_pos),
             pformat(self.center_edge_pos)))

    def __str__(self):
        return 'side %s' % self.name

    def is_even(self):
        if self.size % 2 == 0:
            return True
        return False

    def is_odd(self):
        if self.size % 2 == 0:
            return False
        return True

    # TODO rename these center_corner_is...
    def corner_is_top_left(self, square_index):
        return bool(self.center_corner_pos[0] == square_index)

    def corner_is_top_right(self, square_index):
        return bool(self.center_corner_pos[1] == square_index)

    def corner_is_bottom_left(self, square_index):
        return bool(self.center_corner_pos[2] == square_index)

    def corner_is_bottom_right(self, square_index):
        return bool(self.center_corner_pos[3] == square_index)

    # TODO rename these center_edge_is...
    def edge_is_top(self, square_index):
        return bool(self.center_edge_pos[0] == square_index)

    def edge_is_left(self, square_index):
        return bool(self.center_edge_pos[1] == square_index)

    def edge_is_right(self, square_index):
        return bool(self.center_edge_pos[2] == square_index)

    def edge_is_bottom(self, square_index):
        return bool(self.center_edge_pos[3] == square_index)

    def get_face_as_2d_list(self):
        """
        Used by RubiksCube rotate()
        """
        return build_2d_list([self.parent.state[square_index] for square_index in range(self.min_pos, self.max_pos + 1)])

    def center_corners_solved(self):
        if self.mid_pos:
            mid_pos_value = self.parent.state[self.mid_pos]
        else:
            mid_pos_value = None

        prev_value = None

        for square_index in self.center_corner_pos:
            square_value = self.parent.state[square_index]

            if mid_pos_value:
                if square_value != mid_pos_value:
                    return False

            if prev_value is not None:
                if prev_value != square_value:
                    return False
            prev_value = square_value

        return True

    def center_edges_solved(self):
        if not self.mid_pos:
            return True

        target = self.parent.state[self.mid_pos]

        for square_index in self.center_edge_pos:
            square_value = self.parent.state[square_index]
            if square_value != target:
                return False
        return True

    def center_solved(self):
        if self.center_corners_solved() and self.center_edges_solved():
            return True
        return False

    def verify_center_corners_solved(self):
        if not self.center_corners_solved():
            raise SolveError("%s center corners are not solved" % self)

    def verify_center_edges_solved(self):
        if not self.center_edges_solved():
            raise SolveError("%s center edges are not solved" % self)

    def verify_center_solved(self):
        if not self.center_solved():
            raise SolveError("%s center not solved" % self)

    def get_wing_partner(self, wing_index):
        try:
            return self.wing_partner[wing_index]
        except KeyError:
            log.info("wing_partner\n%s\n" % pformat(self.wing_partner))
            raise

    def get_wing_neighbors(self, target_wing_index):

        if target_wing_index in self.edge_north_pos:
            edges_to_check = self.edge_north_pos

        elif target_wing_index in self.edge_west_pos:
            edges_to_check = self.edge_west_pos

        elif target_wing_index in self.edge_south_pos:
            edges_to_check = self.edge_south_pos

        elif target_wing_index in self.edge_east_pos:
            edges_to_check = self.edge_east_pos

        else:
            raise SolveError("%s does not have wing %d" % (self, target_wing_index))

        neighbors = []
        prev_wing = None

        for wing in edges_to_check:
            if wing == target_wing_index:
                if prev_wing is not None:
                    neighbors.append(prev_wing)
            elif prev_wing == target_wing_index:
                neighbors.append(wing)
            prev_wing = wing

        return neighbors

    def paired_wings(self, check_north, check_west, check_south, check_east):
        paired_wings = []

        # north edge
        if check_north:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_north_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if self.parent.state[prev_pos1] == self.parent.state[pos1] and self.parent.state[prev_pos2] == self.parent.state[pos2]:
                        paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        # west edge
        if check_west:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_west_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if self.parent.state[prev_pos1] == self.parent.state[pos1] and self.parent.state[prev_pos2] == self.parent.state[pos2]:
                        paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        # south edge
        if check_south:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_south_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if self.parent.state[prev_pos1] == self.parent.state[pos1] and self.parent.state[prev_pos2] == self.parent.state[pos2]:
                        paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        # east edge
        if check_east:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_east_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if self.parent.state[prev_pos1] == self.parent.state[pos1] and self.parent.state[prev_pos2] == self.parent.state[pos2]:
                        paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        return paired_wings

    def non_paired_wings(self, check_north, check_west, check_south, check_east):
        """
        TODO there is a lot of cut-n-paste code in here to clean up
        """
        non_paired_wings = []

        # north edge
        if check_north:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_north_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if self.parent.state[prev_pos1] != self.parent.state[pos1] or self.parent.state[prev_pos2] != self.parent.state[pos2]:
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
                    if self.parent.state[prev_pos1] != self.parent.state[pos1] or self.parent.state[prev_pos2] != self.parent.state[pos2]:
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
                    if self.parent.state[prev_pos1] != self.parent.state[pos1] or self.parent.state[prev_pos2] != self.parent.state[pos2]:
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
                    if self.parent.state[prev_pos1] != self.parent.state[pos1] or self.parent.state[prev_pos2] != self.parent.state[pos2]:
                        non_paired_wings.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                prev_pos1 = pos1
                prev_pos2 = pos2

        return non_paired_wings

    def non_paired_edges(self, check_north, check_west, check_south, check_east):
        """
        TODO there is a lot of cut-n-paste code in here to clean up
        """
        non_paired_edges = []

        # north edge
        if check_north:
            prev_pos1 = None
            prev_pos2 = None

            for pos1 in self.edge_north_pos:
                pos2 = self.get_wing_partner(pos1)
                if prev_pos1 is not None:
                    if self.parent.state[prev_pos1] != self.parent.state[pos1] or self.parent.state[prev_pos2] != self.parent.state[pos2]:
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
                    if self.parent.state[prev_pos1] != self.parent.state[pos1] or self.parent.state[prev_pos2] != self.parent.state[pos2]:
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
                    if self.parent.state[prev_pos1] != self.parent.state[pos1] or self.parent.state[prev_pos2] != self.parent.state[pos2]:
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
                    if self.parent.state[prev_pos1] != self.parent.state[pos1] or self.parent.state[prev_pos2] != self.parent.state[pos2]:
                        non_paired_edges.append(((pos1, pos2), (prev_pos1, prev_pos2)))
                        break
                prev_pos1 = pos1
                prev_pos2 = pos2

        #log.info("%s; non_paired_edges %s for check_north %s, check_west %s, check_south %s, check_east %s" %
        #    (self, check_north, check_west, check_south, check_east, non_paired_edges))
        return non_paired_edges

    def all_edges_paired(self):
        if self.non_paired_edges(True, True, True, True):
            return False
        return True

    def all_wings_paired(self):
        north_pairs = self.paired_wings(True, False, False, False)
        west_pairs = self.paired_wings(False, True, False, False)
        south_pairs = self.paired_wings(False, False, True, False)
        east_pairs = self.paired_wings(False, False, False, True)

        if north_pairs and west_pairs and south_pairs and east_pairs:
            return True

        return False

    def north_edge_non_paired(self):
        """
        TODO lots of cut-n-paste code here
        """
        non_paired_edges = self.non_paired_wings(True, False, False, False)

        for ((pos1, pos2), (pos3, pos4)) in non_paired_edges:
            if pos1 in self.edge_north_pos:
                return True
            if pos3 in self.edge_north_pos:
                return True
        return False

    def north_edge_paired(self):
        return not self.north_edge_non_paired()

    def north_wing_paired(self):
        if self.paired_wings(True, False, False, False):
            return True
        return False

    def south_edge_non_paired(self):
        non_paired_edges = self.non_paired_wings(False, False, True, False)

        for ((pos1, pos2), (pos3, pos4)) in non_paired_edges:
            if pos1 in self.edge_south_pos:
                return True
            if pos3 in self.edge_south_pos:
                return True
        return False

    def south_edge_paired(self):
        return not self.south_edge_non_paired()

    def south_wing_paired(self):
        if self.paired_wings(False, False, True, False):
            return True
        return False

    def east_edge_non_paired(self):
        non_paired_edges = self.non_paired_wings(False, False, False, True)

        for ((pos1, pos2), (pos3, pos4)) in non_paired_edges:
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
            if pos1 in self.edge_west_pos:
                return True
            if pos3 in self.edge_west_pos:
                return True
        return False

    def west_edge_paired(self):
        return not self.west_edge_non_paired()

    def west_wing_paired(self):
        if self.paired_wings(False, True, False, False):
            return True
        return False

    def is_solved(self):
        """
        Return True if all squares on this side are the same color
        """
        prev = None

        for pos in range(self.min_pos, self.max_pos+1):
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

    def has_wing(self, wing_to_find):
        wing_to_find_value = (self.parent.state[wing_to_find[0]], self.parent.state[wing_to_find[1]])

        for square_index in self.edge_pos:
            home_value = self.parent.state[square_index]
            partner_index = self.get_wing_partner(square_index)
            partner_value = self.parent.state[partner_index]

            if wing_to_find_value == (home_value, partner_value) or wing_to_find_value == (partner_value, home_value):
                if square_index in self.edge_north_pos:
                    return 'north'

                if square_index in self.edge_west_pos:
                    return 'west'

                if square_index in self.edge_south_pos:
                    return 'south'

                if square_index in self.edge_east_pos:
                    return 'east'

                raise Exception("We should not be here")

        return None

    def wing_is_middle_of_edge(self, square_index):
        squares_per_edge = len(self.edge_north_pos)

        if squares_per_edge % 2 == 0:
            raise Exception("Cannot call wing_is_middle_of_edge() for an even cube")
        mid_index = int((squares_per_edge/2.0) - 0.5)

        if (self.edge_north_pos[mid_index] == square_index or
            self.edge_west_pos[mid_index] == square_index or
            self.edge_south_pos[mid_index] == square_index or
            self.edge_east_pos[mid_index] == square_index):
            return True

        return False
