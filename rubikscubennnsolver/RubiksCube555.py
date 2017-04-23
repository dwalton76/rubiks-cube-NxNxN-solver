
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis, steps_cancel_out, convert_state_to_hex, LookupTable, LookupTableIDA
from rubikscubennnsolver.RubiksSide import Side, SolveError
from rubikscubennnsolver.RubiksCube444 import moves_4x4x4
import logging
import math
import os
import random
import re
import subprocess
import sys

log = logging.getLogger(__name__)

moves_5x5x5 = moves_4x4x4


class RubiksCube555(RubiksCube):
    """
    5x5x5 strategy
    - IDA stage UD centers to sides U or D
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - IDA solve all centers
    - pair edges
    - solve as 3x3x3
    """

    def __init__(self, kociemba_string):
        RubiksCube.__init__(self, kociemba_string)

        '''
        There are 4 T-centers and 4 X-centers so (24!/(8! * 16!))^2 is 540,917,591,841
        We cannot build a table this large so we will build it to 7 moves deep and use
        IDA with T-centers and X-centers as our prune tables. Both the T-centers and
        X-centers prune tables will have 735,471 entries so 735,471/540,917,591,841
        is 0.0000013596729171 which is a decent percentage for IDA.

        1 steps has 5 entries (0 percent)
        2 steps has 98 entries (0 percent)
        3 steps has 2,036 entries (0 percent)
        4 steps has 41,096 entries (0 percent)
        5 steps has 824,950 entries (0 percent)
        6 steps has 16,300,291 entries (4 percent)
        7 steps has 311,709,304 entries (94 percent)

        Total: 328,877,780 entries


        T-centers - 24!/(16! * 8!) is 735,471

        1 steps has 5 entries (0 percent)
        2 steps has 66 entries (0 percent)
        3 steps has 900 entries (0 percent)
        4 steps has 9,626 entries (1 percent)
        5 steps has 80,202 entries (10 percent)
        6 steps has 329,202 entries (44 percent)
        7 steps has 302,146 entries (41 percent)
        8 steps has 13,324 entries (1 percent)

        Total: 735,471 entries


        X-centers - 24!/(16! * 8!) is 735,471

        1 steps has 5 entries (0 percent)
        2 steps has 82 entries (0 percent)
        3 steps has 1,206 entries (0 percent)
        4 steps has 14,116 entries (1 percent)
        5 steps has 123,404 entries (16 percent)
        6 steps has 422,508 entries (57 percent)
        7 steps has 173,254 entries (23 percent)
        8 steps has 896 entries (0 percent)

        Total: 735,471 entries
        '''
        self.lt_UD_T_centers_stage = LookupTable(self,
                                                 'lookup-table-5x5x5-step11-UD-T-centers-stage.txt',
                                                 'UD-T-centers-stage',
                                                 None,
                                                 False) # state_hex

        self.lt_UD_X_centers_stage = LookupTable(self,
                                                 'lookup-table-5x5x5-step12-UD-X-centers-stage.txt',
                                                 'UD-X-centers-stage',
                                                 None,
                                                 False) # state_hex

        self.lt_UD_centers_stage = LookupTableIDA(self,
                                                 'lookup-table-5x5x5-step10-UD-centers-state.txt',
                                                 'UD-centers-stage',
                                                 '3fe000000001ff',
                                                 True, # state_hex
                                                 moves_5x5x5,
                                                 (), # illegal_moves
                                                 (self.lt_UD_T_centers_stage, self.lt_UD_X_centers_stage)) # prune tables

    def group_centers_guts(self):
        self.rotate_U_to_U()
        self.lt_UD_centers_stage.solve()
        # dwalton remove this
        #self.print_cube()
        #sys.exit(0)

        self.lookup_table_555_LR_centers_stage()
        log.info("Took %d steps to stage ULFRBD centers" % len(self.solution))

        if not self.lookup_table_555_ULFRBD_centers_solve():

            # save cube state
            original_state = copy(self.state)
            original_solution = copy(self.solution)

            for threshold in range(1, 15):
                log.info("ida_ULFRBD_centers_solve: threshold %d" % threshold)
                if self.ida_ULFRBD_centers_solve(0, threshold, None, original_state, original_solution):
                    break
            else:
                raise SolveError("UD centers-solve FAILED")

        log.info("Took %d steps to solve ULFRBD centers" % len(self.solution))

    def lookup_table_555_LR_centers_stage(self):
        filename = 'lookup-table-5x5x5-step20-LR-centers-stage.txt'

        with open(filename, 'r') as fh:
            while True:
                state = ''.join([self.state[square_index] for side in (self.sideL, self.sideF, self.sideR, self.sideB) for square_index in side.center_pos])
                state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

                if state == 'LLLLLLLLLxxxxxxxxxLLLLLLLLLxxxxxxxxx':
                    break

                hex_state = convert_state_to_hex(state)
                line = get_line_startswith(fh, hex_state + ':')

                if line:
                    (key, step) = line.strip().split(':')
                    self.rotate(step)

                    log.warning("LR centers-stage: FOUND entry %d steps in, %s" % (len(self.solution), step))
                else:
                    raise SolveError("LR centers-stage FAILED state %s, hex_state %s" % (state, hex_state))

    def lookup_table_555_ULFRBD_centers_solve(self):
        filename = 'lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt'

        with open(filename, 'r') as fh:
            while True:
                state = ''.join([self.state[square_index] for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD) for square_index in side.center_pos])

                if state == 'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD':
                    return True

                line = get_line_startswith(fh, state + ':')

                if line:
                    (key, step) = line.strip().split(':')
                    self.rotate(step)

                    log.warning("ULFRBD-centers-solve %s: FOUND entry %d steps in (%s), %s" %\
                        (state, len(self.solution), ' '.join(self.solution), step))
                else:
                    return False
        return False

    def get_555_UDLR_centers_solve_len(self):
        filename = 'lookup-table-5x5x5-step31-UDLR-centers-solve.txt'

        if not os.path.exists(filename):
            print("ERROR: Could not find %s" % filename)
            sys.exit(1)

        with open(filename, 'r') as fh:
            state = ''.join([self.state[square_index] for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD) for square_index in side.center_pos])
            state = state.replace('F','x').replace('B','x')
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                return len(steps)
        raise SolveError("UDLR-centers-solve could not find state %s" % state)

    def ida_ULFRBD_centers_solve(self, cost_to_here, threshold, prev_step, prev_state, prev_solution):

        for step in moves_5x5x5:

            # These moves would destroy the staged centers
            if step in ("Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'"):
                continue

            # If this step cancels out the previous step then don't bother with this branch
            if steps_cancel_out(prev_step, step):
                continue

            self.state = copy(prev_state)
            self.solution = copy(prev_solution)
            self.rotate(step)

            # Do we have the cube in a state where there is a match in the lookup table?
            if self.lookup_table_555_ULFRBD_centers_solve():
                return True

            cost_to_goal = self.get_555_UDLR_centers_solve_len()

            if (cost_to_here + 1 + cost_to_goal) > threshold:
                #log.info("prune IDA branch at %s, cost_to_here %d, cost_to_goal %d, threshold %d" %
                #    (step1, cost_to_here, cost_to_goal, threshold))
                continue

            state_end_of_this_step = copy(self.state)
            solution_end_of_this_step = copy(self.solution)

            if self.ida_ULFRBD_centers_solve(cost_to_here + 1, threshold, step, state_end_of_this_step, solution_end_of_this_step):
                return True

        return False

    def find_moves_to_stage_slice_forward_555(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        log.debug("find_moves_to_stage_slice_forward_555 called with target_wing %s, sister_wing1 %s, sister_wing2 %s, sister_wing3 %s" %
            (pformat(target_wing), pformat(sister_wing1), pformat(sister_wing2), pformat(sister_wing3)))

        foo = []
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in sorted(side.edge_pos):
                if square_index == target_wing[0]:
                    foo.append('A')

                elif square_index == target_wing[1]:
                    foo.append('B')

                elif square_index == sister_wing1[0]:
                    foo.append('C')

                elif square_index == sister_wing1[1]:
                    foo.append('D')

                elif square_index == sister_wing2[0]:
                    foo.append('E')

                elif square_index == sister_wing2[1]:
                    foo.append('F')

                elif square_index == sister_wing3[0]:
                    foo.append('G')

                elif square_index == sister_wing3[1]:
                    foo.append('H')

                else:
                    foo.append('x')

        edge_string_to_find = ''.join(foo)
        filename = 'lookup-table-5x5x5-step60-edges-slice-forward.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, edge_string_to_find + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                log.debug("find_moves_to_stage_slice_forward_555 found %s" % ' '.join(steps))
                return steps

        log.debug("find_moves_to_stage_slice_forward_555 could not find %s" % edge_string_to_find)
        return None

    def find_moves_to_stage_slice_backward_555(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        foo = []
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in sorted(side.edge_pos):
                if square_index == target_wing[0]:
                    foo.append('A')

                elif square_index == target_wing[1]:
                    foo.append('B')

                elif square_index == sister_wing1[0]:
                    foo.append('C')

                elif square_index == sister_wing1[1]:
                    foo.append('D')

                elif square_index == sister_wing2[0]:
                    foo.append('E')

                elif square_index == sister_wing2[1]:
                    foo.append('F')

                elif square_index == sister_wing3[0]:
                    foo.append('G')

                elif square_index == sister_wing3[1]:
                    foo.append('H')

                else:
                    foo.append('x')

        edge_string_to_find = ''.join(foo)
        filename = 'lookup-table-5x5x5-step70-edges-slice-backward.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, edge_string_to_find + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                log.debug("find_moves_to_stage_slice_backward_555 found %s" % ' '.join(steps))
                return steps

        log.debug("find_moves_to_stage_slice_backward_555 could not find %s" % edge_string_to_find)
        return None

    def get_sister_wings_slice_backward_555(self):
        results = (None, None, None, None)
        max_pair_on_slice_back = 0

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        # Work with the wing at the bottom of the F-east edge
        # Move the sister wing to F-west
        target_wing = (self.sideF.edge_east_pos[-1], self.sideR.edge_west_pos[-1])
        target_wing_side = self.get_side_for_index(target_wing[0])

        # Do we need to reverse sister_wing1?
        for sister_wing1_reverse in (True, False):
            sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0])

            if sister_wing1_reverse:
                sister_wing1 = tuple(list(reversed(sister_wing1)))
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])

            sister_wing2 = None
            sister_wing3 = None
            #log.info("target_wing %s on %s" % (pformat(target_wing), target_wing_side))
            #log.info("sister_wing1 %s on %s" % (pformat(sister_wing1), sister_wing1_side))

            for sister_wing1_use_first_neighbor in (True, False):
                neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])

                if sister_wing1_use_first_neighbor:
                    sister_wing1_neighbor = neighbors[0]
                else:
                    sister_wing1_neighbor = neighbors[1]

                for sister_wing2_reverse in (True, False):
                    sister_wing2 = self.get_wing_in_middle_of_edge(sister_wing1_neighbor)

                    if sister_wing2_reverse:
                        sister_wing2 = tuple(list(reversed(sister_wing2)))
                    sister_wing2_side = self.get_side_for_index(sister_wing2[0])

                    # log.info("sister_wing1_use_first_neighbor %s, sister_wing2 %s on %s" %
                    #     (sister_wing1_use_first_neighbor, pformat(sister_wing2), sister_wing2_side))

                    for sister_wing2_use_first_neighbor in (True, False):
                        neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])

                        if sister_wing2_use_first_neighbor:
                            sister_wing2_neighbor = neighbors[0]
                        else:
                            sister_wing2_neighbor = neighbors[1]

                        for sister_wing3_reverse in (True, False):
                            sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor)

                            if sister_wing3_reverse:
                                sister_wing3 = tuple(list(reversed(sister_wing3)))
                            sister_wing3_side = self.get_side_for_index(sister_wing3[0])

                            # log.info("sister_wing2_use_first_neighbor %s, sister_wing3 %s on %s" %
                            #    (sister_wing2_use_first_neighbor, pformat(sister_wing3), sister_wing3_side))

                            steps = self.find_moves_to_stage_slice_backward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

                            if steps:
                                pre_non_paired_wings_count = self.get_non_paired_wings_count()
                                for step in steps:
                                    self.rotate(step)
                                self.rotate("3Uw'")
                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # F-east must pair
                                if self.state[70] == self.state[65] and self.state[91] == self.state[86]:
                                    will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                else:
                                    will_pair_on_slice_count = 0

                                # log.info("get_sister_wings_slice_backward_555() will_pair_on_slice_count %d via %s" %
                                #    (will_pair_on_slice_count, ' '.join(steps)))

                                # restore cube state
                                self.state = copy(original_state)
                                self.solution = copy(original_solution)

                                if will_pair_on_slice_count > max_pair_on_slice_back:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3)
                                    max_pair_on_slice_back = will_pair_on_slice_count

        # log.info("max_pair_on_slice_back is %d" % max_pair_on_slice_back)
        return results

    def prep_for_slice_back_555(self):

        (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

        if target_wing is None:
            log.info("prep_for_slice_back_555() failed...get_sister_wings_slice_backward_555")
            return False

        steps = self.find_moves_to_stage_slice_backward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True
        else:
            log.info("prep_for_slice_back_555() failed...no steps")
            return False

    def get_sister_wings_slice_forward_555(self, pre_non_paired_wings_count):
        results = (None, None, None, None)
        max_pair_on_slice_forward = 0

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        # Work with the wing at the bottom of the F-west edge
        # Move the sister wing to F-east
        target_wing = (self.sideL.edge_east_pos[-1], self.sideF.edge_west_pos[-1])
        target_wing_side = self.get_side_for_index(target_wing[0])

        for sister_wing1_reverse in (True, False):
            sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0])

            if sister_wing1_reverse:
                sister_wing1 = tuple(list(reversed(sister_wing1)))
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])

            sister_wing2 = None
            sister_wing3 = None
            #log.info("target_wing %s on %s" % (pformat(target_wing), target_wing_side))
            #log.info("sister_wing1 %s, reverse %s, %s" % (pformat(sister_wing1), sister_wing1_reverse, sister_wing1_side))

            for sister_wing1_use_first_neighbor in (True, False):
                neighbors = sister_wing1_side.get_wing_neighbors(sister_wing1[0])

                if sister_wing1_use_first_neighbor:
                    sister_wing1_neighbor = neighbors[0]
                else:
                    sister_wing1_neighbor = neighbors[1]

                for sister_wing2_reverse in (True, False):
                    sister_wing2 = self.get_wing_in_middle_of_edge(sister_wing1_neighbor)

                    if sister_wing2_reverse:
                        sister_wing2 = tuple(list(reversed(sister_wing2)))
                    sister_wing2_side = self.get_side_for_index(sister_wing2[0])

                    # log.info("sister_wing1_use_first_neighbor %s, sister_wing2 %s, reverse %s, %s" %
                    #   (sister_wing1_use_first_neighbor, pformat(sister_wing2), sister_wing2_reverse, sister_wing2_side))

                    for sister_wing2_use_first_neighbor in (True, False):
                        neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])

                        if sister_wing2_use_first_neighbor:
                            sister_wing2_neighbor = neighbors[0]
                        else:
                            sister_wing2_neighbor = neighbors[1]

                        for sister_wing3_reverse in (True, False):

                            # If we are pairing the last six wings then we need sister_wing3 to
                            # be any unpaired edge that allows us to only pair 2 on the slice forward
                            if pre_non_paired_wings_count == 6:

                                # We need sister_wing3 to be any unpaired edge that allows us
                                # to only pair 2 on the slice forward
                                for wing in self.get_non_paired_wings():
                                    if (wing[0] not in (target_wing, sister_wing1, sister_wing2, sister_wing3) and
                                        wing[1] not in (target_wing, sister_wing1, sister_wing2, sister_wing3)):
                                        sister_wing3 = wing[1]
                                        break
                            else:
                                sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor)

                            if sister_wing3_reverse:
                                sister_wing3 = tuple(list(reversed(sister_wing3)))
                            sister_wing3_side = self.get_side_for_index(sister_wing3[0])

                            # log.info("sister_wing2_use_first_neighbor %s, sister_wing3 %s, reverse %s, %s" %
                            #    (sister_wing2_use_first_neighbor, pformat(sister_wing3), sister_wing3_reverse, sister_wing3_side))
                            steps = self.find_moves_to_stage_slice_forward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

                            if steps:
                                #log.info("target_wing %s, sister_wing1 %s, sister_wing2 %s, sister_wing3 %s" %
                                #    (pformat(target_wing), pformat(sister_wing1), pformat(sister_wing2), pformat(sister_wing3)))

                                # pre_non_paired_wings_count = self.get_non_paired_wings_count()
                                for step in steps:
                                    self.rotate(step)
                                self.rotate("3Uw")
                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # F-west must pair
                                if self.state[66] == self.state[61] and self.state[45] == self.state[40]:
                                    will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                else:
                                    will_pair_on_slice_count = 0

                                # restore cube state
                                self.state = copy(original_state)
                                self.solution = copy(original_solution)

                                if will_pair_on_slice_count > max_pair_on_slice_forward:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3)
                                    max_pair_on_slice_forward = will_pair_on_slice_count

        #log.info("max_pair_on_slice_forward is %d" % max_pair_on_slice_forward)
        #if max_pair_on_slice_forward != 3:
        #    raise SolveError("Could not find sister wings for 5x5x5 slice forward (max_pair_on_slice_forward %d)" % max_pair_on_slice_forward)
        return results

    def rotate_unpaired_wing_to_bottom_of_F_east(self):
        """
        Rotate an unpaired wing to the bottom of F-east (one that can be sliced back)
        """
        for flip in (False, True):

            if flip:
                self.rotate_x()
                self.rotate_x()

            for x in range(3):
                if self.state[70] == self.state[65] and self.state[91] == self.state[86]:
                    self.rotate_y()
                else:
                    if self.prep_for_slice_back_555():
                        return (True, flip)

        self.rotate_x()
        self.rotate_x()
        return (False, flip)

    def pair_six_wings_555(self, wing_to_pair, pre_non_paired_wings_count, flip):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        self.rotate_edge_to_F_west(wing_to_pair)

        if flip:
            self.rotate_z()
            self.rotate_z()
            self.rotate_y()

        # We need the unpaired wing to be at the bottom, if it isn't don't worry
        # it will be when pair_six_wings_555 is called for the same wing but with
        # the opposite 'flip' value.
        if self.state[61] == self.state[66] and self.state[45] == self.state[40]:
            return False

        log.info("")
        log.info("pair_six_wings_555() with wing_to_pair %s, flip %s (%d left to pair, %d steps in)" % (pformat(wing_to_pair), flip, original_non_paired_wings_count, original_solution_len))
        # log.info("PREP-FOR-3Uw-SLICE (begin)")
        # self.print_cube()

        (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_forward_555(pre_non_paired_wings_count)

        if target_wing is None:
            log.info("pair_six_wings_555() failed...get_sister_wings_slice_forward_555")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        steps = self.find_moves_to_stage_slice_forward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if not steps:
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        #log.info("PREP-FOR-3Uw-SLICE (end)....SLICE (begin), %d left to pair" % self.get_non_paired_wings_count())
        #self.print_cube()
        self.rotate("3Uw")
        #log.info("SLICE (end), %d left to pair" % self.get_non_paired_wings_count())
        #self.print_cube()

        post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_wings_555()    paired %d wings in %d moves on slice forward (%d left to pair, %d steps in)" %
            (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len))

        (placed_unpaired_wing, flip) = self.rotate_unpaired_wing_to_bottom_of_F_east()

        if not placed_unpaired_wing:

            # TODO there are some steps to save here...we only need to move one wing
            # The stars aligned and we paired 4 at once so we have to move those
            # four out of the way via this six step sequence
            for step in "L R' D U L' R".split():
                self.rotate(step)

            '''
            # The stars aligned and we paired 4 at once so we cannot rotate L-west around
            # to F-east, move an unpaired edge to F-east. This preserves the LFRB centers
            # for the slice back.
            if not self.sideU.north_edge_paired():
                self.rotate("F'")
                self.rotate("U2")
                self.rotate("F")
            elif not self.sideU.east_edge_paired():
                self.rotate("F'")
                self.rotate("U")
                self.rotate("F")
            elif not self.sideU.west_edge_paired():
                self.rotate("F'")
                self.rotate("U'")
                self.rotate("F")
            elif not self.sideD.south_edge_paired():
                self.rotate("F")
                self.rotate("D2")
                self.rotate("F'")
            elif not self.sideD.east_edge_paired():
                self.rotate("F")
                self.rotate("D'")
                self.rotate("F'")
            elif not self.sideD.west_edge_paired():
                self.rotate("F")
                self.rotate("D")
                self.rotate("F'")
            # Look for these last since they take 4 steps instead of 3
            elif not self.sideU.south_edge_paired():
                self.rotate("U'")
                self.rotate("F'")
                self.rotate("U")
                self.rotate("F")
            elif not self.sideD.north_edge_paired():
                self.rotate("D")
                self.rotate("F")
                self.rotate("D'")
                self.rotate("F'")
            else:
                # This can happen if we pair the final four wings on the slice forward
                log.info("Did not find an unpaired edge")
                self.state = copy(original_state)
                self.solution = copy(original_solution)
                return False
            '''

            (placed_unpaired_wing, flip) = self.rotate_unpaired_wing_to_bottom_of_F_east()
            if not placed_unpaired_wing:
                self.state = copy(original_state)
                self.solution = copy(original_solution)
                return False

        # TODO remove these two checks after running the 50 test cubes
        if self.sideF.east_edge_paired():
            raise SolveError("pair_six_wings_555() failed (F-east should not be paired)")

        if self.state[70] == self.state[65] and self.state[91] == self.state[86]:
            raise SolveError("Need to rotate this around...but then we may need to 2Uw' instead of 3Uw'")

        #log.info("PREP-FOR-3Uw'-SLICE-BACK (end)...SLICE BACK (begin), %d left to pair" % self.get_non_paired_wings_count())
        #self.print_cube()

        if flip:
            self.rotate("2Uw'")
        else:
            self.rotate("3Uw'")

        #log.info("SLICE BACK (end), %d left to pair" % self.get_non_paired_wings_count())
        #self.print_cube()
        self.verify_all_centers_solved()

        post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_wings_555()    paired %d wings in %d moves on slice back (%d left to pair, %d steps in)" %
            (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len - post_slice_forward_solution_len,
             post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len))

        return True

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

            # log.info("edges_of_interest_state: rotate_double_y %s,  %s" % (rotate_double_y, edges_of_interest_state))

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

    def pair_last_two_edges_555(self):
        attempt = 0
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        log.info("pair_last_two_edges_555() called (%d left to pair, %d steps in)" % (self.get_non_paired_wings_count(), original_solution_len))

        while True:
            count = self.get_non_paired_edges_count()

            if not count:
                log.info("pair_last_two_edges_555() added %d steps" % (self.get_solution_len_minus_rotates(self.solution) - original_solution_len))
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
                for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                    self.rotate(step)

            # No 2 on https://imgur.com/r/all/wsTqj or the "Two edge crossover" on http://www.rubik.rthost.org/5x5x5_edges.htm
            elif pattern_id == 2 or pattern_id == 11:
                for step in "Lw' U2 Lw' U2 F2 Lw' F2 Rw U2 Rw' U2 Lw2".split():
                    self.rotate(step)

            # No 3 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 3:
                for step in "Dw R F' U R' F Dw'".split():
                    self.rotate(step)

            # No 4 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 4:
                for step in "Dw' L' U' L F' L F L' Dw".split():
                    self.rotate(step)

            # No 5 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 5:
                for step in "Dw Uw' R F' U R' F Dw' Uw".split():
                    self.rotate(step)

            # No 6 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 6:
                for step in "Uw2 Rw2 F2 Uw2 U2 F2 Rw2 Uw2".split():
                    self.rotate(step)

            # No 7 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 7:
                for step in "F2 Rw D2 Rw' F2 U2 F2 Lw B2 Lw'".split():
                    self.rotate(step)

            # No 8 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 8:
                for step in "Rw2 B2 Rw' U2 Rw' U2 B2 Rw' B2 Rw B2 Rw' B2 Rw2".split():
                    self.rotate(step)

            # No 9 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 9:
                for step in "Lw U2 Lw2 U2 Lw' U2 Lw U2 Lw' U2 Lw2 U2 Lw".split():
                    self.rotate(step)

            # No 10 on https://imgur.com/r/all/wsTqj
            elif pattern_id == 10:
                for step in "Rw' U2 Rw2 U2 Rw U2 Rw' U2 Rw U2 Rw2 U2 Rw'".split():
                    self.rotate(step)

            # "Two edge crossover" on http://www.rubik.rthost.org/5x5x5_edges.htm
            elif pattern_id == 11 or pattern_id == 2:
                for step in "Lw' U2 Lw' U2 F2 Lw' F2 Rw U2 Rw' U2 Lw2".split():
                    self.rotate(step)

            # "Flip one edge element" on http://www.rubik.rthost.org/5x5x5_edges.htm
            # The south middle edge needs to be flipped
            elif pattern_id == 12:
                for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                    self.rotate(step)

            # "Flip two edge elements" (the 2nd one) on http://www.rubik.rthost.org/5x5x5_edges.htm
            elif pattern_id == 14:
                # This doesn't work like it claims to on the website

                self.rotate_x_reverse()
                self.rotate("Lw'")
                self.rotate("Rw")

                for step in "F R F' U F' U' F".split():
                    self.rotate(step)

                self.rotate_x()
                self.rotate("Lw")
                self.rotate("Rw'")

            # playground
            elif pattern_id == 15:
                self.print_cube()

                # 1
                for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                    self.rotate(step)

                log.info('\n\n\n')
                self.print_cube()
                sys.exit(0)
            else:
                raise ImplementThis("Add support for 5x5x5 pattern_id %d" % pattern_id)

    def pair_one_wing_555(self, edge, flip):
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        self.move_wing_to_F_west(edge)

        if flip:
            self.rotate_z()
            self.rotate_z()
            self.rotate_y()

        log.info("pair_one_wing_555() called (%d left to pair, %d steps in)" % (original_non_paired_wings_count, original_solution_len))

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

            for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                self.rotate(step)

            current_non_paired_wings_count = self.get_non_paired_wings_count()
            wings_paired = original_non_paired_wings_count - current_non_paired_wings_count
            log.info("pair_one_wing_555() (same edge) paired %d wings, added %d steps" % (wings_paired, self.get_solution_len_minus_rotates(self.solution) - original_solution_len))
            return True

        # Move sister wing to F-east
        sister_wing = sister_wings[0]
        self.move_wing_to_F_east(sister_wing)
        #self.print_cube()

        # The sister wing is in the right location but does it need to be flipped?
        sister_wing = self.get_wings_on_edge(target_wing, 'F', 'R')[0]
        sister_wing_value = self.get_wing_value(sister_wing)

        if target_wing_value != sister_wing_value:

            for step in ("R", "U'", "B'", "R2"):
                self.rotate(step)
            sister_wing = self.get_wings_on_edge(target_wing, 'F', 'R')[0]
            sister_wing_value = self.get_wing_value(sister_wing)

            #log.info("flipped sister wing")
            #self.print_cube()

        # If there are no unpaired wings on U,B or D then we cannot pair this wing
        # without breaking some other already paired wing. I originally returned False
        # here but there are scenarios where you have to pair the wing even though
        # it means unpairing some other wing, else you get yourself in a situation
        # where you cannot solve the edges.
        if (self.sideU.all_wings_paired() and
            self.sideB.all_wings_paired() and
            self.sideD.all_wings_paired()):
            log.info("No unpaired wings in U B or D")

            # Now that that two edges on F are in place, put an unpaired edge at U-west
            self.make_U_west_have_unpaired_edge()

        else:
            # Now that that two edges on F are in place, put an unpaired wing at U-west
            self.make_U_west_have_unpaired_wing()

        if sister_wing[0] == 60:
            #log.info("U-west has unpaired edge, sister_wing %s" % pformat(sister_wing))
            #self.print_cube()

            # The U F' steps are not needed but makes troubleshooting easier
            # as it puts the side you paired back at the front
            #for step in ("Uw", "L'", "U'", "L", "Uw'", "U", "F'"):
            for step in ("Uw", "L'", "U'", "L", "Uw'"):
                self.rotate(step)

        elif sister_wing[0] == 70:

            # Move the unpaired wing at U-west to U-east
            self.rotate("U2")

            #log.info("U-east has unpaired edge, sister_wing %s" % pformat(sister_wing))
            #self.print_cube()

            # The U F' steps are not needed but makes troubleshooting easier
            # as it puts the side you paired back at the front
            #for step in ("3Uw'", "R", "U", "R'", "3Uw", "U", "F'"):
            for step in ("3Uw'", "R", "U", "R'", "3Uw"):
                self.rotate(step)

        else:
            raise SolveError("sister_wing %s is in the wrong position" % str(sister_wing))

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        wings_paired = original_non_paired_wings_count - current_non_paired_wings_count
        log.info("pair_one_wing_555() paired %d wings, added %d steps" % (wings_paired, self.get_solution_len_minus_rotates(self.solution) - original_solution_len))

        if current_non_paired_wings_count < original_non_paired_wings_count:
            return True

        return False

    def group_edges(self):

        while True:
            non_paired_edges = self.get_non_paired_edges()
            len_non_paired_edges = len(non_paired_edges)
            pre_non_paired_wings_count = self.get_non_paired_wings_count()
            pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
            log.info("")
            log.info("")
            log.info("")
            log.warning("%d steps in, %d wings left to pair over %d edges" % (pre_solution_len, pre_non_paired_wings_count, len_non_paired_edges))

            if pre_non_paired_wings_count == 0:
                break

            # cycle through the unpaired wings and find the wing where pair_six_wings_555
            # pairs the most in the least number of moves
            tmp_state = copy(self.state)
            tmp_solution = copy(self.solution)

            min_moves_per_paired_wing = None
            max_wings_paired = None
            max_wings_paired_wing_to_pair = None
            max_wing_solution_len = None
            max_wings_flip = False

            if len_non_paired_edges >= 4 and pre_non_paired_wings_count > 4:
                for flip in (False, True):
                    for foo in non_paired_edges:
                        wing_to_pair = foo[0]

                        if self.pair_six_wings_555(wing_to_pair, pre_non_paired_wings_count, flip):
                            post_non_paired_wings_count = self.get_non_paired_wings_count()
                            wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count
                            post_solution_len = self.get_solution_len_minus_rotates(self.solution)
                            wing_solution_len = post_solution_len - pre_solution_len

                            if wings_paired > 0:
                                moves_per_paired_wing = float(wing_solution_len/wings_paired)

                                if (min_moves_per_paired_wing is None or
                                    moves_per_paired_wing < min_moves_per_paired_wing or
                                    (moves_per_paired_wing == min_moves_per_paired_wing and wings_paired > max_wings_paired)):
                                    max_wings_paired = wings_paired
                                    max_wings_paired_wing_to_pair = wing_to_pair
                                    max_wing_solution_len = wing_solution_len
                                    max_wings_flip = flip
                                    min_moves_per_paired_wing = moves_per_paired_wing

                        # Restore state
                        self.state = copy(tmp_state)
                        self.solution = copy(tmp_solution)

            if max_wings_paired:
                wing_to_pair = max_wings_paired_wing_to_pair
                log.info("Using %s as next wing_to_pair will pair %d wings in %d moves" % (wing_to_pair, max_wings_paired, max_wing_solution_len))
                self.pair_six_wings_555(wing_to_pair, pre_non_paired_wings_count, max_wings_flip)

            # see which wing we can pair two at a time with the least moves
            else:
                if len_non_paired_edges >= 4:
                    log.warning("There are no wings where pair_six_wings_555 will return True")

                if len_non_paired_edges > 2:
                    # TODO - this scenario needs work, we spend a ton of moves here

                    for flip in (False, True):
                        for foo in non_paired_edges:
                            wing_to_pair = foo[0]

                            if self.pair_one_wing_555(wing_to_pair, flip):
                                post_non_paired_wings_count = self.get_non_paired_wings_count()
                                wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count
                                post_solution_len = self.get_solution_len_minus_rotates(self.solution)
                                wing_solution_len = post_solution_len - pre_solution_len

                                if (max_wings_paired is None or
                                    wings_paired > max_wings_paired or
                                    (wings_paired == max_wings_paired and wing_solution_len < max_wing_solution_len)):
                                    max_wings_paired = wings_paired
                                    max_wings_paired_wing_to_pair = wing_to_pair
                                    max_wing_solution_len = wing_solution_len
                                    max_wing_flip = flip

                            # Restore state
                            self.state = copy(tmp_state)
                            self.solution = copy(tmp_solution)

                    if max_wings_paired_wing_to_pair is None:
                        raise SolveError("FOO")

                    wing_to_pair = max_wings_paired_wing_to_pair
                    log.info("Using %s as next wing_to_pair will pair %s wings in %s moves" % (wing_to_pair, max_wings_paired, max_wing_solution_len))
                    self.pair_one_wing_555(wing_to_pair, max_wing_flip)

                else:
                    self.pair_last_two_edges_555()

        self.solution.append('EDGES_GROUPED')
