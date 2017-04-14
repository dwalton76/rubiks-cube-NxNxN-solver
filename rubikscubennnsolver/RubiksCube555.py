#!/usr/bin/env python3

from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver import RubiksCube, ImplementThis, steps_cancel_out
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

    def get_state_t_centers(self):
        """
        This is currently hard coded for 5x5x5
        """
        result = []

        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):

            # [7, 8, 9, 12, 13, 14, 17, 18, 19]
            #  X  T  X   T  TX   T   X   T   X
            #  0  1  2   3   4   5   6   7   8
            result.append('x')
            result.append(self.state[side.center_pos[1]])
            result.append('x')
            result.append(self.state[side.center_pos[3]])
            result.append(self.state[side.center_pos[4]])
            result.append(self.state[side.center_pos[5]])
            result.append('x')
            result.append(self.state[side.center_pos[7]])
            result.append('x')

        return ''.join(result)

    def get_state_x_centers(self):
        """
        This is currently hard coded for 5x5x5
        """
        result = []

        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):

            # [7, 8, 9, 12, 13, 14, 17, 18, 19]
            #  X  T  X   T  TX   T   X   T   X
            #  0  1  2   3   4   5   6   7   8
            result.append(self.state[side.center_pos[0]])
            result.append('x')
            result.append(self.state[side.center_pos[2]])
            result.append('x')
            result.append(self.state[side.center_pos[4]])
            result.append('x')
            result.append(self.state[side.center_pos[6]])
            result.append('x')
            result.append(self.state[side.center_pos[8]])

        return ''.join(result)

    def get_t_centers_solution(self, t_centers_state):
        filename = 'lookup-table-5x5x5-step11-stage-UD-T-centers.txt'

        if not os.path.exists(filename):
            print("ERROR: Could not find %s" % filename)
            sys.exit(1)

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, t_centers_state + ':')

            if line:
                (key, steps) = line.split(':')
                return steps.strip().split()
            else:
                print("ERROR: Could not find T-center %s in %s" % (t_centers_state, filename))
                sys.exit(1)

    def get_x_centers_solution(self, x_centers_state):
        filename = 'lookup-table-5x5x5-step12-stage-UD-X-centers.txt'

        if not os.path.exists(filename):
            print("ERROR: Could not find %s" % filename)
            sys.exit(1)

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, x_centers_state + ':')

            if line:
                (key, steps) = line.split(':')
                return steps.strip().split()
            else:
                print("ERROR: Could not find X-center %s in %s" % (x_centers_state, filename))
                sys.exit(1)

    def lookup_table_555_UD_centers_stage(self):
        filename = 'lookup-table-5x5x5-step10-stage-UD-centers.txt'

        if not os.path.exists(filename):
            print("ERROR: Could not find %s" % filename)
            sys.exit(1)

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)

        with open(filename, 'r') as fh:

            # rotate_y() 4x to see if any of these states are in the lookup table
            for rotate_y_count in range(4):

                self.state = copy(original_state)
                self.solution = copy(original_solution)

                for x in range(rotate_y_count):
                    self.rotate_y()

                state = ''.join([self.state[square_index] for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD) for square_index in side.center_pos])
                state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

                line = get_line_startswith(fh, state + ':')

                if line:
                    (key, steps) = line.split(':')
                    steps = steps.strip().split()

                    log.warning("UD centers-stage %s: FOUND entry %d steps in (%s), %s" %\
                        (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))
                    for step in steps:
                        self.rotate(step)
                    return True

        self.state = copy(original_state)
        self.solution = copy(original_solution)
        return False

    def get_xt_centers_solution_length_555(self):
        t_centers = self.get_state_t_centers()
        t_centers = t_centers.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')
        x_centers = self.get_state_x_centers()
        x_centers = x_centers.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        t_centers_solution = self.get_t_centers_solution(t_centers)
        x_centers_solution = self.get_x_centers_solution(x_centers)

        t_centers_solution_len = len(t_centers_solution)
        x_centers_solution_len = len(x_centers_solution)

        #log.info("T-centers %s solution is %s, length %d" % (t_centers, ' '.join(t_centers_solution), t_centers_solution_len))
        #log.info("X-centers %s solution is %s, length %d" % (x_centers, ' '.join(x_centers_solution), x_centers_solution_len))

        return max(t_centers_solution_len, x_centers_solution_len)

    def ida_UD_centers_stage(self, cost_to_here, threshold, prev_step, prev_state, prev_solution):
        log.info("ida_UD_centers_stage: cost_to_here %d, threshold %d" % (cost_to_here, threshold))

        for step in moves_5x5x5:

            # If this step cancels out the previous step then don't bother with this branch
            if steps_cancel_out(prev_step, step):
                continue

            self.state = copy(prev_state)
            self.solution = copy(prev_solution)
            self.rotate(step)

            # Do we have the cube in a state where there is a match in the lookup table?
            if self.lookup_table_555_UD_centers_stage():
                return True

            cost_to_goal = self.get_xt_centers_solution_length_555()

            if (cost_to_here + cost_to_goal) > threshold:
                #log.info("prune IDA branch at %s, cost_to_here %d, cost_to_goal %d, threshold %d" %
                #    (step1, cost_to_here, cost_to_goal, threshold))
                continue

            state_end_of_this_step = copy(self.state)
            solution_end_of_this_step = copy(self.solution)

            if self.ida_UD_centers_stage(cost_to_here+1, threshold, step, state_end_of_this_step, solution_end_of_this_step):
                return True

        return False

    def lookup_table_555_LR_centers_stage(self):
        filename = 'lookup-table-5x5x5-step20-stage-LR-centers.txt'

        original_state = copy(self.state)
        original_solution = copy(self.solution)

        with open(filename, 'r') as fh:

            # rotate_y() to see if any of these states are in the lookup table
            for rotate_y_count in (0, 2):

                self.state = copy(original_state)
                self.solution = copy(original_solution)

                for x in range(rotate_y_count):
                    self.rotate_y()

                state = ''.join([self.state[square_index] for side in (self.sideL, self.sideF, self.sideR, self.sideB) for square_index in side.center_pos])
                state = state.replace('U', 'x').replace('F', 'x').replace('D', 'x').replace('B', 'x').replace('R', 'L')

                line = get_line_startswith(fh, state + ':')

                if line:
                    (key, steps) = line.split(':')
                    steps = steps.strip().split()

                    log.warning("LR centers-stage %s: FOUND entry %d steps in, %s" %\
                        (state, len(self.solution), ' '.join(steps)))
                    for step in steps:
                        self.rotate(step)
                    return True

        raise SolveError("LR centers-stage FAILED")

    def lookup_table_555_UD_centers_solve(self):
        filename = 'lookup-table-5x5x5-step30-solve-UD-centers.txt'

        if not os.path.exists(filename):
            print("ERROR: Could not find %s" % filename)
            sys.exit(1)

        with open(filename, 'r') as fh:
            state = ''.join([self.state[square_index] for side in (self.sideU, self.sideD) for square_index in side.center_pos])

            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()

                log.info("UD centers-solve %s: FOUND entry %d steps in, %s" %\
                    (state, len(self.solution), ' '.join(steps)))
                for step in steps:
                    self.rotate(step)
            else:
                raise SolveError("UD centers-solve %s: FAILED to find entry" % state)

    def lookup_table_555_LFRB_centers_solve(self):
        filename = 'lookup-table-5x5x5-step40-solve-LFRB-centers.txt'

        if not os.path.exists(filename):
            print("ERROR: Could not find %s" % filename)
            sys.exit(1)

        with open(filename, 'r') as fh:
            state = ''.join([self.state[square_index] for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD) for square_index in side.center_pos])

            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()

                log.info("LFRB centers-solve %s: FOUND entry %d steps in, %s" %\
                    (state, len(self.solution), ' '.join(steps)))
                for step in steps:
                    self.rotate(step)
            else:
                raise SolveError("LFRB centers-solve %s: FAILED to find entry" % state)

    def lookup_table_555_ULFRBD_centers_solve(self):
        filename = 'lookup-table-5x5x5-step25-ULFRBD-centers-solve.txt'

        if not os.path.exists(filename):
            print("ERROR: Could not find %s" % filename)
            sys.exit(1)

        with open(filename, 'r') as fh:
            state = ''.join([self.state[square_index] for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD) for square_index in side.center_pos])
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()

                log.warning("ULFRBD-centers-solve %s: FOUND entry %d steps in (%s), %s" %\
                        (state, len(self.solution), ' '.join(self.solution), ' '.join(steps)))
                for step in steps:
                    self.rotate(step)
                return True
        return False

    def get_555_UDLR_centers_solve_len(self):
        filename = 'lookup-table-5x5x5-step26-UDLR-centers-solve.txt'

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
        log.info("ida_ULFRBD_centers_solve: cost_to_here %d, threshold %d" % (cost_to_here, threshold))

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

            if (cost_to_here + cost_to_goal) > threshold:
                #log.info("prune IDA branch at %s, cost_to_here %d, cost_to_goal %d, threshold %d" %
                #    (step1, cost_to_here, cost_to_goal, threshold))
                continue

            state_end_of_this_step = copy(self.state)
            solution_end_of_this_step = copy(self.solution)

            if self.ida_ULFRBD_centers_solve(cost_to_here+1, threshold, step, state_end_of_this_step, solution_end_of_this_step):
                return True

        return False

    def group_centers_guts(self):
        self.rotate_U_to_U()

        if not self.lookup_table_555_UD_centers_stage():

            # If we are here (odds are very high we will be) it means that the current
            # cube state was not in the lookup table.  We must now perform an IDA search
            # until we find a sequence of moves that takes us to a state that IS in the
            # lookup table.

            # save cube state
            original_state = copy(self.state)
            original_solution = copy(self.solution)

            for threshold in range(1, 10):
                if self.ida_UD_centers_stage(1, threshold, None, original_state, original_solution):
                    break
            else:
                raise SolveError("UD centers-stage FAILED")

        # TODO I'm in the process of rebuilding the LR-centers-stage table...it was 8 million short
        self.lookup_table_555_LR_centers_stage()
        log.info("Took %d steps to stage ULFRBD centers" % len(self.solution))

        # old way
        #self.lookup_table_555_UD_centers_solve()
        #self.lookup_table_555_LFRB_centers_solve()

        # new way using IDA
        if not self.lookup_table_555_ULFRBD_centers_solve():

            # save cube state
            original_state = copy(self.state)
            original_solution = copy(self.solution)

            for threshold in range(1, 10):
                if self.ida_ULFRBD_centers_solve(1, threshold, None, original_state, original_solution):
                    break
            else:
                raise SolveError("UD centers-stage FAILED")

        log.info("Took %d steps to solve ULFRBD centers" % len(self.solution))
        #self.print_cube()
        #sys.exit(0)

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
                                self.rotate("3U'")
                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # How many will pair on slice back?
                                will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count

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

    def get_sister_wings_slice_forward_555(self, last_six):
        results = (None, None, None, None, None)
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
                            if last_six:

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

                                pre_non_paired_wings_count = self.get_non_paired_wings_count()
                                for step in steps:
                                    self.rotate(step)
                                self.rotate("3U")
                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # How many will pair on slice forward?
                                will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                bonus = None

                                if not last_six:
                                    # How many "bonus" wings can we pair by doing a Uw, Uw' or Uw2?
                                    tmp_state = copy(self.state)
                                    tmp_solution = copy(self.solution)

                                    self.rotate("Uw")
                                    bonus_Uw = post_non_paired_wings_count - self.get_non_paired_wings_count()
                                    self.state = copy(tmp_state)
                                    self.solution = copy(tmp_solution)

                                    self.rotate("Uw'")
                                    bonus_Uw_prime = post_non_paired_wings_count - self.get_non_paired_wings_count()
                                    self.state = copy(tmp_state)
                                    self.solution = copy(tmp_solution)

                                    self.rotate("Uw2")
                                    bonus_Uw2 = post_non_paired_wings_count - self.get_non_paired_wings_count()
                                    self.state = copy(tmp_state)
                                    self.solution = copy(tmp_solution)

                                    if bonus_Uw > 0 or bonus_Uw_prime > 0 or bonus_Uw2 > 0:

                                        if bonus_Uw >= bonus_Uw_prime and bonus_Uw >= bonus_Uw2:
                                            bonus = "Uw"
                                            will_pair_on_slice_count += bonus_Uw

                                        elif bonus_Uw_prime >= bonus_Uw and bonus_Uw_prime >= bonus_Uw2:
                                            bonus = "Uw'"
                                            will_pair_on_slice_count += bonus_Uw_prime

                                        elif bonus_Uw2 >= bonus_Uw and bonus_Uw2 >= bonus_Uw_prime:
                                            bonus = "Uw2"
                                            will_pair_on_slice_count += bonus_Uw2

                                # restore cube state
                                self.state = copy(original_state)
                                self.solution = copy(original_solution)

                                if will_pair_on_slice_count > max_pair_on_slice_forward:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3, bonus)
                                    max_pair_on_slice_forward = will_pair_on_slice_count

        #log.info("max_pair_on_slice_forward is %d" % max_pair_on_slice_forward)
        #if max_pair_on_slice_forward != 3:
        #    raise SolveError("Could not find sister wings for 5x5x5 slice forward (max_pair_on_slice_forward %d)" % max_pair_on_slice_forward)
        return results

    def pair_six_edges_555(self, wing_to_pair, last_six):
        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        log.info("")
        log.info("pair_six_edges_555() with wing_to_pair %s (%d left to pair, %d steps in)" % (pformat(wing_to_pair), original_non_paired_wings_count, original_solution_len))

        self.rotate_edge_to_F_west(wing_to_pair)

        # We need the unpaired wing to be at the bottom
        if self.state[61] == self.state[66] and self.state[45] == self.state[40]:
            self.rotate_z()
            self.rotate_z()
            self.rotate_y()

        # log.info("PREP-FOR-3U-SLICE (begin)")
        # self.print_cube()

        (target_wing, sister_wing1, sister_wing2, sister_wing3, bonus) = self.get_sister_wings_slice_forward_555(last_six)

        if target_wing is None:
            log.info("pair_six_edges_555() failed...get_sister_wings_slice_forward_555")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        steps = self.find_moves_to_stage_slice_forward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if not steps:
            raise SolveError("pair_six_edges_555() failed (no steps for slice forward)")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        #log.info("PREP-FOR-3U-SLICE (end)....SLICE (begin)")
        #self.print_cube()
        self.rotate("3U")
        #log.info("SLICE (end)")
        #self.print_cube()

        if bonus:
            self.rotate(bonus)

        post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_edges_555()    paired %d wings in %d moves on slice forward (%d left to pair, %d steps in)" %
            (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len))

        if self.sideL.west_edge_paired():

            # The stars aligned and we paired 4 at once so we have to move those
            # four out of the way via this six step sequence
            for step in "L R' D U L' R".split():
                self.rotate(step)

            if self.sideF.east_edge_paired():
                for x in range(3):
                    self.rotate_y()
                    if not self.sideF.east_edge_paired():
                        break
        else:
            self.rotate_y()
            self.rotate_y()

        if self.sideF.east_edge_paired():
            log.info("pair_six_edges_555() failed (F-east should not be paired)")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        if not self.prep_for_slice_back_555():
            log.info("pair_six_edges_555() failed (no prep for slice back)")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        if self.state[70] == self.state[65] and self.state[91] == self.state[86]:
            raise SolveError("Need to rotate this around...but then we may need to Uw' instead of 3U'")

        #log.info("PREP-FOR-3U'-SLICE-BACK (end)...SLICE BACK (begin)")
        #self.print_cube()
        self.rotate("3U'")
        #log.info("SLICE BACK (end)")
        #self.print_cube()

        if bonus:
            if bonus == "Uw":
                self.rotate("Uw'")
            elif bonus == "Uw'":
                self.rotate("Uw")
            elif bonus == "Uw2":
                self.rotate("Uw2")

        self.verify_all_centers_solved()

        post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_edges_555()    paired %d wings in %d moves on slice back (%d left to pair, %d steps in)" %
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

    def pair_two_edges_555(self, edge):
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        self.move_wing_to_F_west(edge)
        log.info("pair_two_edges_555() called (%d left to pair, %d steps in)" % (original_non_paired_wings_count, original_solution_len))

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

            log.info("pair_two_edges_555() added %d steps" % (self.get_solution_len_minus_rotates(self.solution) - original_solution_len))
            return True

        # Move sister wing to F-east
        sister_wing = sister_wings[0]
        self.move_wing_to_F_east(sister_wing)

        # The sister wing is in the right location but does it need to be flipped?
        sister_wing = self.get_wings_on_edge(target_wing, 'F', 'R')[0]
        sister_wing_value = self.get_wing_value(sister_wing)

        if target_wing_value != sister_wing_value:

            for step in ("R", "U'", "B'", "R2"):
                self.rotate(step)
            sister_wing = self.get_wings_on_edge(target_wing, 'F', 'R')[0]
            sister_wing_value = self.get_wing_value(sister_wing)


        # If there are no unpaired wings on U,B or D then we cannot pair this wing
        # without breaking some other already paired wing. I originally returned False
        # here but there are scenarios where you have to pair the wing even though
        # it means unpairing some other wing, else you get yourself in a situation
        # where you cannot solve the edges.
        if (self.sideU.all_wings_paired() and
            self.sideB.all_wings_paired() and
            self.sideD.all_wings_paired()):

            # Now that that two edges on F are in place, put an unpaired edge at U-west
            self.make_U_west_have_unpaired_edge()

        else:
            # Now that that two edges on F are in place, put an unpaired wing at U-west
            self.make_U_west_have_unpaired_wing()

        if sister_wing[0] == 60:

            # The U F' steps are not needed but makes troubleshooting easier
            # as it puts the side you paired back at the front
            #for step in ("Uw", "L'", "U'", "L", "Uw'", "U", "F'"):
            for step in ("Uw", "L'", "U'", "L", "Uw'"):
                self.rotate(step)

        elif sister_wing[0] == 70:

            # Move the unpaired wing at U-west to U-east
            self.rotate("U2")

            # The U F' steps are not needed but makes troubleshooting easier
            # as it puts the side you paired back at the front
            #for step in ("3U'", "R", "U", "R'", "3U", "U", "F'"):
            for step in ("3U'", "R", "U", "R'", "3U"):
                self.rotate(step)

        else:
            raise SolveError("sister_wing %s is in the wrong position" % str(sister_wing))

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        log.info("pair_two_edges_555() added %d steps" % (self.get_solution_len_minus_rotates(self.solution) - original_solution_len))

        if current_non_paired_wings_count < original_non_paired_wings_count:
            return True

        return False

    def group_edges(self):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_edges = self.get_non_paired_edges()

        min_solution_length = None
        min_solution_state = None
        min_solution = None

        for init_wing_to_pair in original_non_paired_edges:

            while True:
                non_paired_edges = self.get_non_paired_edges()
                len_non_paired_edges = len(non_paired_edges)

                if len_non_paired_edges == 0:
                    break

                if len_non_paired_edges == 6:
                    last_six = True
                else:
                    last_six = False

                pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
                pre_non_paired_wings_count = self.get_non_paired_wings_count()
                attempt_to_pair_six = False
                log.info("\n\n\n\n")
                log.warning("%d steps in, %d wings left to pair over %d edges" % (pre_solution_len, pre_non_paired_wings_count, len_non_paired_edges))

                if init_wing_to_pair:
                    wing_to_pair = init_wing_to_pair[0]
                    init_wing_to_pair = None
                    attempt_to_pair_six = True

                elif len_non_paired_edges >= 6:

                    # cycle through and find one where pair_six_edges_555 works
                    tmp_state = copy(self.state)
                    tmp_solution = copy(self.solution)

                    max_wings_paired = None
                    max_wings_paired_wing_to_pair = None
                    max_wing_solution_len = None

                    for foo in non_paired_edges:
                        wing_to_pair = foo[0]

                        if self.pair_six_edges_555(wing_to_pair, last_six):
                            attempt_to_pair_six = True
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

                        # Restore state
                        self.state = copy(tmp_state)
                        self.solution = copy(tmp_solution)

                    if max_wings_paired is None:
                        wing_to_pair = non_paired_edges[0][0]
                        log.warning("There are no wings where pair_six_edges_555 will return True (last_six %s)" % last_six)
                    else:
                        wing_to_pair = max_wings_paired_wing_to_pair
                        log.warning("Using %s as next wing_to_pair will pair %d wings in %d moves" % (wing_to_pair, max_wings_paired, max_wing_solution_len))

                    # Restore state
                    self.state = copy(tmp_state)
                    self.solution = copy(tmp_solution)

                else:
                    wing_to_pair = non_paired_edges[0][0]

                if attempt_to_pair_six:
                    if not self.pair_six_edges_555(wing_to_pair, last_six):
                        self.pair_two_edges_555(wing_to_pair)

                elif len_non_paired_edges > 2:
                    self.pair_two_edges_555(wing_to_pair)

                elif len_non_paired_edges >= 1:
                    self.pair_last_two_edges_555()

                else:
                    break

            solution_len = self.get_solution_len_minus_rotates(self.solution)

            if min_solution_length is None or solution_len < min_solution_length:
                min_solution_length = solution_len
                min_solution_state = copy(self.state)
                min_solution = copy(self.solution)
                log.warning("edges solution length %d (NEW MIN)" % min_solution_length)
            else:
                log.info("edges solution length %d" % min_solution_length)

            # Restore to original state
            self.state = copy(original_state)
            self.solution = copy(original_solution)

            # remove me...break out of the 'for init_wing_to_pair' loop
            #break

        if min_solution_length:
            self.state = copy(min_solution_state)
            self.solution = copy(min_solution)

            if self.get_non_paired_edges_count():
                raise SolveError("All edges should be resolved")

            self.solution.append('EDGES_GROUPED')
        else:
            raise SolveError("Could not find a PLL free edge solution")
