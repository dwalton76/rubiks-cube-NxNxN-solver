from pprint import pformat
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.LookupTable import LookupTable, LookupTableIDA, NoSteps
from subprocess import check_output
import logging
import sys

log = logging.getLogger(__name__)


moves_4x4x4 = ("U", "U'", "U2", "Uw", "Uw'", "Uw2",
               "L", "L'", "L2", "Lw", "Lw'", "Lw2",
               "F" , "F'", "F2", "Fw", "Fw'", "Fw2",
               "R" , "R'", "R2", "Rw", "Rw'", "Rw2",
               "B" , "B'", "B2", "Bw", "Bw'", "Bw2",
               "D" , "D'", "D2", "Dw", "Dw'", "Dw2")
solved_4x4x4 = 'UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB'


class RubiksCube444(RubiksCube):
    """
    4x4x4 strategy
    - stage UD centers to sides U or D
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers
    - pair edges
    - solve as 3x3x3
    """

    def __init__(self, kociemba_string, avoid_pll=True, debug=False):
        RubiksCube.__init__(self, kociemba_string, debug)
        self.avoid_pll = avoid_pll

        if debug:
            log.setLevel(logging.DEBUG)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        """
        lookup-tables init
        """

        '''
        24!/(16! * 8!) is 735,471

        lookup-table-4x4x4-step01-UD-centers-stage.txt
        ==============================================
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
        self.lt_UD_centers_stage = LookupTable(self,
                                               'lookup-table-4x4x4-step01-UD-centers-stage.txt',
                                               '444-UD-centers-stage',
                                               'f0000f',
                                                True,  # state hex
                                                False) # prune table


        '''
        16!/(8! * 8!) is 12,870

        lookup-table-4x4x4-step02-LR-centers-stage.txt
        ==============================================
        1 steps has 3 entries (0 percent)
        2 steps has 29 entries (0 percent)
        3 steps has 234 entries (1 percent)
        4 steps has 1,246 entries (9 percent)
        5 steps has 4,466 entries (34 percent)
        6 steps has 6,236 entries (48 percent)
        7 steps has 656 entries (5 percent)

        Total: 12,870 entries
        '''
        self.lt_LR_centers_stage = LookupTable(self,
                                               'lookup-table-4x4x4-step02-LR-centers-stage.txt',
                                               '444-LR-centers-stage',
                                               'f0f0',
                                                True,  # state hex
                                                False) # prune table


        '''
        (8!/(4! * 4!))^3 is 343,000

        lookup-table-4x4x4-step03-ULFRBD-centers-solve.txt
        ==================================================
        1 steps has 7 entries (0 percent)
        2 steps has 99 entries (0 percent)
        3 steps has 996 entries (0 percent)
        4 steps has 6,477 entries (1 percent)
        5 steps has 23,540 entries (6 percent)
        6 steps has 53,537 entries (15 percent)
        7 steps has 86,464 entries (25 percent)
        8 steps has 83,240 entries (24 percent)
        9 steps has 54,592 entries (15 percent)
        10 steps has 29,568 entries (8 percent)
        11 steps has 4,480 entries (1 percent)

        Total: 343,000 entries
        '''
        self.lt_ULFRBD_centers_solve = LookupTable(self,
                                                   'lookup-table-4x4x4-step03-ULFRBD-centers-solve.txt',
                                                   '444-ULFRBD-centers-solve',
                                                   'UUUULLLLFFFFRRRRBBBBDDDD',
                                                   False, # state hex
                                                   False) # prune table

        '''
        22*20*18 is 7920

        lookup-table-4x4x4-step40-edges-slice-forward.txt
        =================================================
        1 steps has 7 entries (0 percent)
        2 steps has 42 entries (0 percent)
        3 steps has 299 entries (3 percent)
        4 steps has 1,306 entries (16 percent)
        5 steps has 3,449 entries (43 percent)
        6 steps has 2,617 entries (33 percent)
        7 steps has 200 entries (2 percent)

        Total: 7,920 entries
        '''
        self.lt_edge_slice_forward = LookupTable(self,
                                                 'lookup-table-4x4x4-step40-edges-slice-forward.txt',
                                                 '444-edges-slice-forward',
                                                 'TBD',
                                                 False, # state hex
                                                 False) # prune table

        '''
        22*20*18 is 7920
        No idea why I am one entry short (should be 7920 total)...oh well

        lookup-table-4x4x4-step50-edges-slice-backward.txt
        ==================================================
        1 steps has 1 entries (0 percent)
        3 steps has 36 entries (0 percent)
        4 steps has 66 entries (0 percent)
        5 steps has 334 entries (4 percent)
        6 steps has 1,369 entries (17 percent)
        7 steps has 3,505 entries (44 percent)
        8 steps has 2,539 entries (32 percent)
        9 steps has 69 entries (0 percent)

        Total: 7,919 entries
        '''
        self.lt_edge_slice_backward = LookupTable(self,
                                                  'lookup-table-4x4x4-step50-edges-slice-backward.txt',
                                                  '444-edges-slice-backward',
                                                  'TBD',
                                                  False, # state hex
                                                  False) # prune table

        self.lt_edges = LookupTable(self,
                                    'lookup-table-4x4x4-step101-edges.txt',
                                    '444-edges',
                                    'TBD',
                                    False, # state_hex
                                    False) # prune table

    def phase(self):
        if self._phase is None:
            self._phase = 'Stage UD centers'
            return self._phase

        if self._phase == 'Stage UD centers':
            if self.UD_centers_staged():
                self._phase = 'Stage LR centers'
            return self._phase

        if self._phase == 'Stage LR centers':
            if self.LR_centers_staged():
                self._phase = 'Solve Centers'

        if self._phase == 'Solve Centers':
            if self.centers_solved():
                self._phase = 'Pair Edges'

        if self._phase == 'Pair Edges':
            if not self.get_non_paired_edges():
                self._phase = 'Solve 3x3x3'

        return self._phase

    def group_centers_guts(self):
        self.lt_init()

        # The UD solve -> LFRB solve approach is only ~1 move shorter on average
        # than doing UD stage, LR stage, ULFRBD solve.  The UD solve -> LFRB
        # lookup tables are 5.6G where the UD stage, LR stage, ULFRBD solve
        # lookup tables are only 49M...we use the 49M tables so we can check
        # them into the github repo.
        self.lt_UD_centers_stage.solve()
        self.lt_LR_centers_stage.solve()
        self.lt_ULFRBD_centers_solve.solve()

    def edge_string_to_find(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = []
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in sorted(side.edge_pos):

                if square_index in (target_wing[0], target_wing[1]):
                    state.append('A')

                elif square_index in (sister_wing1[0], sister_wing1[1]):
                    state.append('B')

                elif square_index in (sister_wing2[0], sister_wing2[1]):
                    state.append('C')

                elif square_index in (sister_wing3[0], sister_wing3[1]):
                    state.append('D')

                else:
                    state.append('x')

        return ''.join(state)

    def find_moves_to_stage_slice_forward_444(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        """
        target_wing must go in spot 41
        sister_wing1 must go in spot (40, 53)
        sister_wing2 must go in spot (56, 69)
        sister_wing3 must go in spot (72, 21)
        """
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_forward.steps(state)

    def find_moves_to_stage_slice_backward_444(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        """
        target_wing must go in spot (44, 57)
        sister_wing1 must go in spot (24, 37)
        sister_wing2 must go in spot (72, 21))
        sister_wing3 must go in spot (56, 69)
        """
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edge_slice_backward.steps(state)

    def prep_for_slice_back_444(self):

        # Now set things up so that when we slice back we pair another 3 edges.
        # Work with the wing on the bottom of F-east
        target_wing = self.sideF.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        target_wing_partner_index = 57
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]
        steps = self.find_moves_to_stage_slice_backward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True

        # If we are here it means the unpaired edge on F-east needs to be swapped with
        # its sister_wing1. In other words F-east and sister-wing1 have the same two
        # sets of colors and the two of them together would create two paired edges if
        # we swapped their wings.
        #
        # As a work-around, move some other unpaired edge into F-east. There are no
        # guarantees we won't hit the exact same problem with that edge but that doesn't
        # happen too often.

        if not self.sideU.north_edge_paired() and self.sideU.has_wing(sister_wing1) != 'north':
            self.rotate("F'")
            self.rotate("U2")
            self.rotate("F")
        elif not self.sideU.east_edge_paired() and self.sideU.has_wing(sister_wing1) != 'east':
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
        elif not self.sideU.west_edge_paired() and self.sideU.has_wing(sister_wing1) != 'west':
            self.rotate("F'")
            self.rotate("U'")
            self.rotate("F")
        elif not self.sideD.south_edge_paired() and self.sideD.has_wing(sister_wing1) != 'south':
            self.rotate("F")
            self.rotate("D2")
            self.rotate("F'")
        elif not self.sideD.east_edge_paired() and self.sideD.has_wing(sister_wing1) != 'east':
            self.rotate("F")
            self.rotate("D'")
            self.rotate("F'")
        elif not self.sideD.west_edge_paired() and self.sideD.has_wing(sister_wing1) != 'west':
            self.rotate("F")
            self.rotate("D")
            self.rotate("F'")
        # Look for these last since they take 4 steps instead of 3
        elif not self.sideU.south_edge_paired() and self.sideU.has_wing(sister_wing1) != 'south':
            self.rotate("U'")
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
        elif not self.sideD.north_edge_paired() and self.sideD.has_wing(sister_wing1) != 'north':
            self.rotate("D")
            self.rotate("F")
            self.rotate("D'")
            self.rotate("F'")
        else:
            # If we are here we are down to two unpaired wings
            return False

        if self.sideF.east_edge_paired():
            raise SolveError("F-east should not be paired")

        target_wing = self.sideF.edge_east_pos[-1]
        sister_wing = self.get_wings(target_wing)[0]
        target_wing_partner_index = 57
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]
        steps = self.find_moves_to_stage_slice_backward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True
        else:
            return False

    def pair_six_edges_444(self, wing_to_pair):
        """
        Sections are:
        - PREP-FOR-Uw-SLICE
        - Uw
        - PREP-FOR-REVERSE-Uw-SLICE
        - Uw'
        """

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        self.rotate_edge_to_F_west(wing_to_pair)
        #log.info("PREP-FOR-Uw-SLICE (begin)")
        #self.print_cube()

        # Work with the wing at the bottom of the F-west edge
        # Move the sister wing to the top of F-east
        target_wing = self.sideF.edge_west_pos[-1]
        target_wing_partner_index = 28
        sister_wing1 = self.get_wings(target_wing)[0]
        sister_wing1_side = self.get_side_for_index(sister_wing1[0])
        sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
        sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
        sister_wing2_side = self.get_side_for_index(sister_wing2[0])
        sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
        sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]

        steps = self.find_moves_to_stage_slice_forward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, sister_wing3)

        if not steps:
            log.info("pair_six_edges_444()    could not find steps to slice forward")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        #log.info("PREP-FOR-Uw-SLICE (end)....SLICE (begin)")
        #self.print_cube()
        self.rotate("Uw")
        #log.info("SLICE (end)")
        #self.print_cube()

        post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_edges_444()    paired %d wings in %d moves on slice forward (%d left to pair)" %
            (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_wings_count))

        if self.sideL.west_edge_paired():

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
                raise SolveError("Did not find an unpaired edge")

        else:
            self.rotate_y()
            self.rotate_y()

        if self.sideF.east_edge_paired():
            log.warning("F-east should not be paired")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        if not self.prep_for_slice_back_444():
            #raise SolveError("cannot slice back")
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        #log.info("PREP-FOR-Uw'-SLICE-BACK (end)...SLICE BACK (begin)")
        #self.print_cube()
        self.rotate("Uw'")
        #log.info("SLICE BACK (end)")
        #self.print_cube()
        #self.verify_all_centers_solved()

        post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_six_edges_444()    paired %d wings in %d moves on slice back (%d left to pair)" %
            (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len - post_slice_forward_solution_len,
             post_slice_back_non_paired_wings_count))

        return True

    def pair_last_six_edges_444(self):
        """
        Sections are:
        - PREP-FOR-Uw-SLICE
        - Uw
        - PREP-FOR-REVERSE-Uw-SLICE
        - Uw'
        """
        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_non_paired_edges = self.get_non_paired_edges()

        min_solution_len = None
        min_solution_state = None
        min_solution = None

        for wing_to_pair in original_non_paired_edges:
            self.state = original_state[:]
            self.solution = original_solution[:]
            self.rotate_edge_to_F_west(wing_to_pair[0])

            # Work with the wing at the bottom of the F-west edge
            # Move the sister wing to the top of F-east
            target_wing = self.sideF.edge_west_pos[-1]
            target_wing_partner_index = 28
            sister_wing1 = self.get_wings(target_wing)[0]
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])
            sister_wing1_neighbor = sister_wing1_side.get_wing_neighbors(sister_wing1[0])[0]
            sister_wing2 = self.get_wings(sister_wing1_neighbor)[0]
            sister_wing2_side = self.get_side_for_index(sister_wing2[0])
            sister_wing2_neighbor = sister_wing2_side.get_wing_neighbors(sister_wing2[0])[0]
            sister_wing3 = self.get_wings(sister_wing2_neighbor)[0]

            #log.info("target_wing: %s" % target_wing)
            #log.info("sister_wing1 %s on %s, neighbor %s" % (sister_wing1, sister_wing1_side, sister_wing1_neighbor))
            #log.info("sister_wing2 %s on %s, neighbor %s" % (sister_wing2, sister_wing2_side, sister_wing2_neighbor))
            #log.info("sister_wing3 %s" % pformat(sister_wing3))

            sister_wing3_candidates = []

            # We need sister_wing3 to be any unpaired edge that allows us
            # to only pair 2 on the slice forward
            for wing in self.get_non_paired_wings():
                if (wing[0] not in (target_wing, sister_wing1, sister_wing2, sister_wing3) and
                    wing[1] not in (target_wing, sister_wing1, sister_wing2, sister_wing3)):
                    sister_wing3_candidates.append(wing[1])

            min_sister_wing3_steps_len = None
            min_sister_wing3_steps = None
            min_sister_wing3 = None

            for x in sister_wing3_candidates:
                steps = self.find_moves_to_stage_slice_forward_444((target_wing, target_wing_partner_index), sister_wing1, sister_wing2, x)

                if steps:
                    steps_len = len(steps)

                    if min_sister_wing3_steps_len is None or steps_len < min_sister_wing3_steps_len:
                        min_sister_wing3_steps_len = steps_len
                        min_sister_wing3_steps = steps
                        min_sister_wing3 = x

            sister_wing3 = min_sister_wing3
            steps = min_sister_wing3_steps
            #log.info("sister_wing3 %s" % pformat(sister_wing3))

            if not steps:
                log.info("pair_last_six_edges_444() cannot slice back (no steps found)")
                continue

            for step in steps:
                self.rotate(step)

            # At this point we are setup to slice forward and pair 2 edges
            #log.info("PREP-FOR-Uw-SLICE (end)....SLICE (begin)")
            #self.print_cube()
            self.rotate("Uw")
            #log.info("SLICE (end)")
            #self.print_cube()

            post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
            post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

            log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice forward (%d left to pair)" %
                (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
                 post_slice_forward_solution_len - original_solution_len,
                 post_slice_forward_non_paired_wings_count))

            if self.sideF.east_edge_paired():
                for x in xrange(3):
                    self.rotate_y()
                    if not self.sideF.east_edge_paired():
                        break

            if self.sideF.east_edge_paired():
                log.info("pair_last_six_edges_444() cannot slice back (F-east paired)")
                continue

            if not self.prep_for_slice_back_444():
                log.info("pair_last_six_edges_444() cannot slice back (prep failed)")
                continue

            self.rotate("Uw'")

            post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
            post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)

            if min_solution_len is None or post_slice_back_solution_len < min_solution_len:
                min_solution_len = post_slice_back_solution_len
                min_solution_state = self.state[:]
                min_solution = self.solution[:]
                log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice back (%d left to pair) (NEW MIN %d)" %
                    (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - post_slice_forward_solution_len,
                    post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - original_solution_len))
            else:
                log.info("pair_last_six_edges_444() paired %d wings in %d moves on slice back (%d left to pair)" %
                    (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
                    post_slice_back_solution_len - post_slice_forward_solution_len,
                    post_slice_back_non_paired_wings_count))

        if min_solution_len:
            self.state = min_solution_state
            self.solution = min_solution
            return True
        else:
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

    def pair_four_edges_444(self, edge):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        if original_non_paired_wings_count < 4:
            raise SolveError("pair_four_edges_444() requires at least 4 unpaired edges")

        self.rotate_edge_to_F_west(edge)

        # Work with the wing at the bottom of the F-west edge
        target_wing = self.sideF.edge_west_pos[-1]

        # Move the sister wing to F east
        sister_wing = self.get_wings(target_wing)[0]
        steps = lookup_table_444_sister_wing_to_F_east[sister_wing]

        for step in steps.split():
            self.rotate(step)

        self.rotate("Uw")

        if not self.sideR.west_edge_paired():
            pass
        elif not self.sideB.west_edge_paired():
            self.rotate_y()
        elif not self.sideL.west_edge_paired():
            self.rotate_y()
            self.rotate_y()

        if not self.prep_for_slice_back_444():
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

        self.rotate("Uw'")

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_four_edges_444()    paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count >= original_non_paired_wings_count:
            raise SolveError("Went from %d to %d non_paired_edges" %
                (original_non_paired_wings_count, current_non_paired_wings_count))

        return True

    def pair_two_edges_444(self, edge):
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        if original_non_paired_wings_count == 2:
            raise SolveError("pair_last_two_edges_444() should be used when there are only 2 edges left")

        self.rotate_edge_to_F_west(edge)

        # Work with the wing at the bottom of the F-west edge
        target_wing = self.sideF.edge_west_pos[-1]

        # Move the sister wing to F east...this uses a small lookup table
        # that I built manually. This puts the sister wing at F-east in the correct
        # orientation (it will not need to be flipped). We used to just move the
        # sister wing to F-east but then sometimes we would need to "R U' B' R2"
        # to flip it around.
        sister_wing = self.get_wings(target_wing)[0]
        '''
        if sister_wing not in lookup_table_444_sister_wing_to_F_east:
            log.warning("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
            self.find_moves_to_reach_state(sister_wing, 'F-east')
            raise ImplementThis("lookup_table_444_sister_wing_to_F_east needs %s" % pformat(sister_wing))
        '''
        steps = lookup_table_444_sister_wing_to_F_east[sister_wing]

        for step in steps.split():
            self.rotate(step)

        # Now that that two edges on F are in place, put an unpaired edge at U-west.
        # The unpaired edge that we place at U-west should contain the
        # sister wing of the wing that is at the bottom of F-east. This
        # will allow us to pair two wings at once.
        wing_bottom_F_east = self.sideF.edge_east_pos[-1]
        sister_wing_bottom_F_east = self.get_wings(wing_bottom_F_east)[0]

        if sister_wing_bottom_F_east not in lookup_table_444_sister_wing_to_U_west:
            raise ImplementThis("sister_wing_bottom_F_east %s" % pformat(sister_wing_bottom_F_east))

        steps = lookup_table_444_sister_wing_to_U_west[sister_wing_bottom_F_east]

        # If steps is None it means sister_wing_bottom_F_east is at (37, 24)
        # which is the top wing on F-west. If that is the case we can't pair
        # two edges at once so just put some random unpaired edge at U-west
        if steps == None:
            self.make_U_west_have_unpaired_edge()
        else:
            for step in steps.split():
                self.rotate(step)

        for step in ("Uw", "L'", "U'", "L", "Uw'"):
            self.rotate(step)

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_two_edges_444()    paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count < original_non_paired_wings_count:
            return True

        raise SolveError("Went from %d to %d non_paired_edges" %
            (original_non_paired_wings_count, current_non_paired_wings_count))

    def pair_last_two_edges_444(self, edge):
        """
        At one point I looked into using two lookup tables to do this:
        - the first to stage edges to F-west and F-east
        - the second to solve the two staged edges

        The first stage took 1 or steps and the 2nd stage took either 7 or 10, it
        was 10 if the wing at F-east was turned the wrong way and needed to be
        rotated around. It wasn't worth it...what I have below works just find and
        takes between 7 to 11 steps total.
        """
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        # rotate unpaired edge to F-west
        self.rotate_edge_to_F_west(edge)

        pos1 = self.sideF.edge_west_pos[-1]

        # Put the other unpaired edge on F east...this uses a small lookup table
        # that I built manually. This puts the sister wing at F-east in the correct
        # orientation (it will not need to be flipped). We used to just move the
        # sister wing to F-east but then sometimes we would need to "R F' U R' F"
        # to flip it around.
        sister_wing = self.get_wings(pos1)[0]

        steps = lookup_table_444_last_two_edges_place_F_east[sister_wing]
        for step in steps.split():
            self.rotate(step)

        # "Solving the last 4 edge blocks" in
        # http://www.rubiksplace.com/cubes/4x4/
        for step in ("Dw", "R", "F'", "U", "R'", "F", "Dw'"):
            self.rotate(step)

        current_non_paired_wings_count = self.get_non_paired_wings_count()
        current_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_last_two_edges_444() paired %d wings in %d moves (%d left to pair)" %
            (original_non_paired_wings_count - current_non_paired_wings_count,
             current_solution_len - original_solution_len,
             current_non_paired_wings_count))

        if current_non_paired_wings_count:
            raise SolveError("Failed to pair last two edges")

    def pair_edge(self, edge_to_pair):
        """
        Pair a specific edge
        """
        pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
        pre_non_paired_edges_count = self.get_non_paired_edges_count()
        log.info("pair_edge() for %s (%d wings left to pair)" % (pformat(edge_to_pair), pre_non_paired_edges_count))

        if pre_non_paired_edges_count > 6:
            if not self.pair_six_edges_444(edge_to_pair[0]):
                log.info("pair_six_edges_444()    returned False")

                if not self.pair_four_edges_444(edge_to_pair[0]):
                    log.info("pair_four_edges_444() returned False")
                    self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count == 6:
            if not self.pair_last_six_edges_444():
                log.info("pair_last_six_edges_444() returned False")

                if not self.pair_four_edges_444(edge_to_pair[0]):
                    log.info("pair_four_edges_444() returned False")
                    self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count >= 4:
            if not self.pair_four_edges_444(edge_to_pair[0]):
                log.info("pair_four_edges_444() returned False")
                self.pair_two_edges_444(edge_to_pair[0])

        elif pre_non_paired_edges_count == 2:
            self.pair_last_two_edges_444(edge_to_pair[0])

        # The scenario where you have 3 unpaired edges
        elif pre_non_paired_edges_count > 2:
            self.pair_two_edges_444(edge_to_pair[0])

        post_non_paired_edges_count = self.get_non_paired_edges_count()
        edges_paired = pre_non_paired_edges_count - post_non_paired_edges_count

        if edges_paired < 1:
            raise SolveError("Paired %d edges" % edges_paired)

        return True

        '''
    def get_best_edge_to_pair(self, non_paired_edges):
        """
        Loop over all of the non-paired-edges and return the one that will allow us to pair the most edges
        """
        max_edges_paired_has_pll = False
        max_edges_paired = None
        max_edges_paired_edge = None
        max_edges_paired_solution_len = None

        pre_non_paired_edges_count = len(self.get_non_paired_edges())
        original_state = self.state[:]
        original_solution = self.solution[:]

        for edge in non_paired_edges:

            log.info('')
            pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
            self.pair_edge(edge)

            post_non_paired_edges_count = len(self.get_non_paired_edges())
            post_solution_len = self.get_solution_len_minus_rotates(self.solution)
            solution_len = post_solution_len - pre_solution_len
            edges_paired = pre_non_paired_edges_count - post_non_paired_edges_count

            if post_non_paired_edges_count:
                leads_to_pll = None
            else:
                leads_to_pll = self.edge_solution_leads_to_pll_parity()

            new_min = False

            if max_edges_paired is None:
                new_min = True

            elif max_edges_paired_has_pll:
                if leads_to_pll is True:
                    if edges_paired > max_edges_paired or (edges_paired == max_edges_paired and solution_len < max_edges_paired_solution_len):
                        new_min = True
                elif leads_to_pll is False:
                    new_min = True
                # Not all edges were paired so leads_to_pll is None..you can
                # only calculate PLL once all edges are paired
                else:
                    if edges_paired > max_edges_paired or (edges_paired == max_edges_paired and solution_len < max_edges_paired_solution_len):
                        new_min = True

            elif leads_to_pll is None or leads_to_pll is False:
                if edges_paired > max_edges_paired or (edges_paired == max_edges_paired and solution_len < max_edges_paired_solution_len):
                    new_min = True

            if new_min:
                max_edges_paired_has_pll = leads_to_pll
                max_edges_paired = edges_paired
                max_edges_paired_edge = edge
                max_edges_paired_solution_len = solution_len

            self.state = original_state[:]
            self.solution = original_solution[:]

        log.warning("%s will pair %d edges in %d steps, leads to PLL %s" % (max_edges_paired_edge, max_edges_paired, max_edges_paired_solution_len, max_edges_paired_has_pll))
        return max_edges_paired_edge
        '''

    def group_edges_recursive(self, depth, edge_to_pair):
        """
        """
        pre_non_paired_wings_count = len(self.get_non_paired_wings())
        pre_non_paired_edges_count = len(self.get_non_paired_edges())
        edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len
        tmp_state = self.state[:]
        tmp_solution = self.solution[:]

        log.info("")
        log.info("group_edges_recursive(%d) called with edge_to_pair %s (%d edges and %d wings left to pair, min solution len %s, current solution len %d)" %
                (depth,
                 pformat(edge_to_pair),
                 pre_non_paired_edges_count,
                 pre_non_paired_wings_count,
                 self.min_edge_solution_len,
                 edge_solution_len))

        # Is the current state in the lookup table? The lookup table was built with U at U
        # and F at F so we must rotate those in place.
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        try:
            self.lt_edges.solve()
            non_paired_edges = []
            # dwalton
            raise SolveError("holy crap that worked")

        except NoSteps:
            # No entry in the lookup table so restore to tmp_state/tmp_solution to undo the rotate UF to UF
            self.state = tmp_state[:]
            self.solution = tmp_solution[:]

            # Should we continue down this branch or should we prune it? An estimate
            # of 2 moves to pair an edge is a low estimate so if the current number of
            # steps plus 2 * pre_non_paired_wings_count is greater than our current minimum
            # there isn't any point in continuing down this branch so prune it and save
            # some CPU cycles.
            estimated_solution_len = edge_solution_len + (2 * pre_non_paired_wings_count)

            if estimated_solution_len >= self.min_edge_solution_len:
                #log.warning("PRUNE: %s + (2 * %d) > %s" % (edge_solution_len, non_paired_wings_count, self.min_edge_solution_len))
                return False

            # The only time this will be None is on the initial call to group_edges_recursive()
            if edge_to_pair:
                self.pair_edge(edge_to_pair)

            non_paired_edges = self.get_non_paired_edges()

        if non_paired_edges:
            original_state = self.state[:]
            original_solution = self.solution[:]

            # call group_edges_recursive() for each non-paired edge
            for edge in non_paired_edges:
                self.group_edges_recursive(depth+1, edge)
                self.state = original_state[:]
                self.solution = original_solution[:]

        else:
            # There are no edges left to pair, note how many steps it took pair them all
            edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len

            # It takes 12 steps to solve PLL parity so add that to the solution length.
            # If we are pairing the outside edges of a 5x5x5 self.avoid_pll will be False.
            if self.avoid_pll and self.edge_solution_leads_to_pll_parity():
                edge_solution_len += 12

            # I tried this once for grins but it takes about 20x longer to run and the
            # avg solution over 50 cubes wasn't any shorter. I think it is because the
            # cubes are basically always scambled to the point where the 3x3x3 phase
            # takes ~20 steps.
            #
            #kociemba_string = self.get_kociemba_string(False)
            #steps_333 = check_output(['kociemba', kociemba_string]).decode('ascii').splitlines()[-1].strip().split()
            #edge_solution_len += len(steps_333)

            # Remember the solution that pairs all edges in the least number of moves
            if edge_solution_len < self.min_edge_solution_len:
                self.min_edge_solution_len = edge_solution_len
                self.min_edge_solution = self.solution[:]
                self.min_edge_solution_state = self.state[:]
                log.warning("NEW MIN: edges paired in %d steps" % self.min_edge_solution_len)

            return True

    def group_edges(self):
        if not self.get_non_paired_edges():
            self.solution.append('EDGES_GROUPED')
            return

        depth = 0
        self.lt_init()
        self.center_solution_len = self.get_solution_len_minus_rotates(self.solution)
        self.min_edge_solution_len = 9999
        self.min_edge_solution = None
        self.min_edge_solution_state = None

        # group_edges_recursive() is where the magic happens
        self.group_edges_recursive(depth, None)
        self.state = self.min_edge_solution_state[:]
        self.solution = self.min_edge_solution[:]
        self.solution.append('EDGES_GROUPED')

        # This is the non-recursive approach...will leave this as a reference
        '''
        original_state = self.state[:]
        original_solution = self.solution[:]
        pll_blacklist = []
        first_edge = None

        while True:

            if not self.get_non_paired_edges():
                if self.edge_solution_leads_to_pll_parity():
                    log.warning('*' * 80)
                    log.warning("Pairing %s first leads to PLL" % pformat(first_edge))
                    log.warning('*' * 80)
                    pll_blacklist.append(first_edge)
                    first_edge = None
                    self.state = original_state[:]
                    self.solution = original_solution[:]
                else:
                    self.solution.append('EDGES_GROUPED')
                    break

            self.rotate_U_to_U()
            self.rotate_F_to_F()

            try:
                tmp_state = self.state[:]
                tmp_solution = self.solution[:]
                self.lt_edges.solve()

                if self.edge_solution_leads_to_pll_parity():
                    self.state = tmp_state[:]
                    self.solution = tmp_solution[:]
                else:
                    self.solution.append('EDGES_GROUPED')
                    break
            except NoSteps:
                pass

            if first_edge is None:
                non_paired_edges = [edge for edge in self.get_non_paired_edges() if edge not in pll_blacklist]
            else:
                non_paired_edges = self.get_non_paired_edges()

            edge_to_pair = self.get_best_edge_to_pair(non_paired_edges)

            if first_edge is None:
                first_edge = edge_to_pair

            pre_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len
            self.pair_edge(edge_to_pair)

            post_non_paired_edges_count = len(self.get_non_paired_edges())
            log.info('%d edges left to pair, %d steps in' %
                (post_non_paired_edges_count,
                 self.get_solution_len_minus_rotates(self.solution) - pre_solution_len))
            log.info('')
            log.info('')
            log.info('')
        '''

# Move a wing to (44, 57)
lookup_table_444_last_two_edges_place_F_east = {
    (2, 67)  : "B' R2",
    (3, 66)  : "U R'",
    (5, 18)  : "U2 R'",
    (9, 19)  : "U B' R2",
    (14, 34) : "U' R'",
    (15, 35) : "U F' U' F",
    (8, 51)  : "F' U F",
    (12, 50) : "R'",
    (21, 72) : "B' U R'",
    (25, 76) : "B2 R2",
    (30, 89) : "F D F'",
    (31, 85) : "D2 R",
    (40, 53) : "R U' B' R2",
    (44, 57) : "",
    (46, 82) : "D F D' F'",
    (47, 83) : "D R",
    (56, 69) : "R2",
    (60, 73) : "B U R'",
    (62, 88) : "F D' F'",
    (63, 92) : "R",
    (78, 95) : "B R2",
    (79, 94) : "D' R",
}

# Move a wing to (40, 53)
lookup_table_444_sister_wing_to_F_east = {
    (2, 67)  : "U R'",
    (3, 66)  : "B' R2",
    (5, 18)  : "U B' R2",
    (9, 19)  : "U2 R'",
    (14, 34) : "L F L'",
    (15, 35) : "U' R'",
    (8, 51)  : "R'",
    (12, 50) : "F' U F",
    (21, 72) : "B2 R2",
    (25, 76) : "B D' R",
    (30, 89) : "D2 R",
    (31, 85) : "F D F'",
    (40, 53) : "",
    (44, 57) : "F D F' R",
    (46, 82) : "D R",
    (47, 83) : "D2 B R2",
    (56, 69) : "B U R'",
    (60, 73) : "R2",
    (62, 88) : "R",
    (63, 92) : "F D' F'",
    (78, 95) : "D' R",
    (79, 94) : "B R2",
}

# Move a wing to (5, 18)
lookup_table_444_sister_wing_to_U_west = {
    (2, 67)  : "L' B L",
    (3, 66)  : "U'",
    (5, 18)  : "",
    (9, 19)  : "L' B' L U'",
    (14, 34) : "U",
    (15, 35) : "F' L' F",
    (8, 51)  : "U' B F L F'",
    (12, 50) : "U2",
    (21, 72) : "B' U'",
    (25, 76) : "L U L' U'",
    (30, 89) : "L B' L' U'",
    (31, 85) : "D' B2 U'",
    (37, 24) : None,
    #(40, 53) : "",
    #(44, 57) : "",
    (46, 82) : "F L' F'",
    (47, 83) : "D2 B2 U'",
    (56, 69) : "R' U2 R",
    (60, 73) : "B U'",
    (62, 88) : "R' B R U'",
    (63, 92) : "D B2 U'",
    (78, 95) : "B2 U'",
    (79, 94) : "B2 U'",
}


# Code below here is no longer...maybe I am saving it for a rainy day
'''
    def find_moves_to_reach_state(self, wing_to_move, target_face_side):
        """
        This was used to build the lookup_table_444_last_two_edges_place_F_east, etc lookup tables
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        orig_f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
        orig_f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
        orig_f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
        orig_f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])

        orig_r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
        orig_r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])
        orig_r_east_top = self.get_wing_value(self.sideR.edge_east_pos[0])
        orig_r_east_bottom = self.get_wing_value(self.sideR.edge_east_pos[1])

        orig_b_west_top = self.get_wing_value(self.sideB.edge_west_pos[0])
        orig_b_west_bottom = self.get_wing_value(self.sideB.edge_west_pos[1])
        orig_b_east_top = self.get_wing_value(self.sideB.edge_east_pos[0])
        orig_b_east_bottom = self.get_wing_value(self.sideB.edge_east_pos[1])

        orig_l_west_top = self.get_wing_value(self.sideL.edge_west_pos[0])
        orig_l_west_bottom = self.get_wing_value(self.sideL.edge_west_pos[1])
        orig_l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
        orig_l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])

        orig_center_corner_state = self.get_center_corner_state()
        wing_to_move_value = sorted(self.get_wing_value(wing_to_move))

        filename = 'utils/all_3x3x3_moves_6_deep.txt'
        with open(filename, 'r') as fh:
            self.print_cube()
            count = 0
            for line in fh:
                count += 1
                steps = line.strip().split()

                for step in steps:
                    self.rotate(step)

                if count % 10000 == 0:
                    log.info("count %d, step len %d" % (count, len(steps)))

                # For SLICE-FORWARD
                if target_face_side == 'F-east':
                    # Find sequence that moves wing_to_move to (40, 53)
                    # F-west must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])

                    f_east_top = sorted(self.get_wing_value(self.sideF.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        f_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'R-east':
                    # Find sequence that moves wing_to_move to (56, 69)
                    # F-west and R-west must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
                    r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
                    r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])

                    r_east_top = sorted(self.get_wing_value(self.sideR.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        r_west_top == orig_r_west_top and
                        r_west_bottom == orig_r_west_bottom and
                        r_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'B-east':
                    # Find sequence that moves wing_to_move to (21, 72)
                    # F-west, R-west, and B-west edges must not change
                    f_west_top = self.get_wing_value(self.sideF.edge_west_pos[0])
                    f_west_bottom = self.get_wing_value(self.sideF.edge_west_pos[1])
                    r_west_top = self.get_wing_value(self.sideR.edge_west_pos[0])
                    r_west_bottom = self.get_wing_value(self.sideR.edge_west_pos[1])
                    b_west_top = self.get_wing_value(self.sideB.edge_west_pos[0])
                    b_west_bottom = self.get_wing_value(self.sideB.edge_west_pos[1])

                    b_east_top = sorted(self.get_wing_value(self.sideB.edge_east_pos[0]))

                    if (f_west_top == orig_f_west_top and
                        f_west_bottom == orig_f_west_bottom and
                        r_west_top == orig_r_west_top and
                        r_west_bottom == orig_r_west_bottom and
                        b_west_top == orig_b_west_top and
                        b_west_bottom == orig_b_west_bottom and
                        b_east_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                # For SLICE-BACK
                elif target_face_side == 'F-west':
                    # Find sequence that moves wing_to_move to (24, 37)
                    # F-east must not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    f_west_top = sorted(self.get_wing_value(self.sideF.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        f_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'L-west':
                    # Find sequence that moves wing_to_move to (21, 72)
                    # F-east and L-east ust not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])
                    l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
                    l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    l_west_top = sorted(self.get_wing_value(self.sideL.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        l_east_top == orig_l_east_top and
                        l_east_bottom == orig_l_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        l_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                elif target_face_side == 'B-west':
                    # Find sequence that moves wing_to_move to (56, 69)
                    # F-east, L-east and B-east must not change
                    f_east_top = self.get_wing_value(self.sideF.edge_east_pos[0])
                    f_east_bottom = self.get_wing_value(self.sideF.edge_east_pos[1])
                    l_east_top = self.get_wing_value(self.sideL.edge_east_pos[0])
                    l_east_bottom = self.get_wing_value(self.sideL.edge_east_pos[1])
                    b_east_top = self.get_wing_value(self.sideB.edge_east_pos[0])
                    b_east_bottom = self.get_wing_value(self.sideB.edge_east_pos[1])

                    center_corner_state = self.get_center_corner_state()
                    b_west_top = sorted(self.get_wing_value(self.sideB.edge_west_pos[0]))

                    if (f_east_top == orig_f_east_top and
                        f_east_bottom == orig_f_east_bottom and
                        l_east_top == orig_l_east_top and
                        l_east_bottom == orig_l_east_bottom and
                        b_east_top == orig_b_east_top and
                        b_east_bottom == orig_b_east_bottom and
                        center_corner_state == orig_center_corner_state and
                        b_west_top == wing_to_move_value):
                        found_solution = True
                    else:
                        found_solution = False

                else:
                    raise ImplementThis("target_face_side %s" % target_face_side)

                self.state = original_state[:]
                self.solution = original_solution[:]

                if found_solution:
                    log.warning("solution to move %s to %s is %s" % (wing_to_move, target_face_side, ' '.join(steps)))
                    sys.exit(1)

            log.warning("Explored %d moves in %s but did not find a solution" % (count, filename))
            sys.exit(1)

lookup_table_444_sister_wing_to_R_east = {
    (2, 67)  : "B'", # U-north
    (3, 66)  : "R' U R", # U-north
    (5, 18)  : "L' B2 L", # U-west
    (9, 19)  : "U B'", # U-west
    (14, 34) : "R' U' R", # U-south
    (15, 35) : "U2 B'", # U-south
    (8, 51)  : "U' B'", # U-east
    (12, 50) : "F R F'", # U-east
    (21, 72) : "B R D' R'", # L-west
    (25, 76) : "B2", # L-west
    (37, 24) : None, # L-east
    #(41, 28) : "", # L-east
    #(40, 53) : "", # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "D", # R-east
    (60, 73) : "B R' U R", # R-east
    (46, 82) : "D2 B", # D-north
    (47, 83) : "R D R'", # D-north
    (30, 89) : "D' B", # D-west
    (31, 85) : "L B2 L'", # D-west
    (78, 95) : "B", # D-south
    (79, 94) : "R D' R'", # D-south
    (62, 88) : "D B", # D-east
    (63, 92) : "D B", # D-east
}

lookup_table_444_sister_wing_to_B_east = {
    (2, 67)  : "L U' L'", # U-north
    (3, 66)  : "R B R'", # U-north
    (5, 18)  : "B' U B", # U-west
    (9, 19)  : "F L' F'", # U-west
    (14, 34) : "B' U2 B", # U-south
    (15, 35) : "L U L'", # U-south
    (8, 51)  : "L U2 L'", # U-east
    (12, 50) : "B' U' B", # U-east
    (21, 72) : "D", # L-west
    (25, 76) : "B L' D B' L", # L-west
    (37, 24) : None, # L-east
    #(41, 28) : "", # L-east
    #(40, 53) : "", # R-west
    (44, 57) : None, # R-west
    #(56, 69) : "", # R-east
    #(60, 73) : "", # R-east
    (46, 82) : "L' D' L", # D-north
    (47, 83) : "B D2 B'", # D-north
    (30, 89) : "F L F'", # D-west
    (31, 85) : "B D' B'", # D-west
    (78, 95) : "L' D L", # D-south
    (79, 94) : "R B' R'", # D-south
    (62, 88) : "L' D2 L", # D-east
    (63, 92) : "B D B'", # D-east
}

lookup_table_444_sister_wing_to_F_west = {
    (2, 67)  : "F U2 F'", # U-north
    (3, 66)  : "L' U' L", # U-north
    (5, 18)  : "L F L' F'", # U-west
    (9, 19)  : "F U' F'", # U-west
    (14, 34) : "L' U L", # U-south
    (15, 35) : "F' L F L'", # U-south
    (8, 51)  : "F U F'", # U-east
    (12, 50) : "L' U2 L", # U-east
    (21, 72) : "B L D B' L'", # L-west
    (25, 76) : "B L2 B' L2", # L-west
    (37, 24) : "D", # L-east
    (41, 28) : "F L' U F' L", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "L2 B2 L2 B2", # R-east
    (60, 73) : "B L' U' B' L", # R-east
    (46, 82) : "D F' D' F", # D-north
    (47, 83) : "L D' L'", # D-north
    (30, 89) : "F' D F", # D-west
    (31, 85) : "D L D' L'", # D-west
    (78, 95) : "F' D2 F", # D-south
    (79, 94) : "L D L'", # D-south
    (62, 88) : "F' D' F", # D-east
    (63, 92) : "L D2 L'", # D-east
}

lookup_table_444_sister_wing_to_L_west = {
    (2, 67)  : "L U' L'", # U-north
    (3, 66)  : "B L B' L'", # U-north
    (5, 18)  : "B' U B", # U-west
    (9, 19)  : "L' B L B'", # U-west
    (14, 34) : "B' U2 B", # U-south
    (15, 35) : "L U L'", # U-south
    (8, 51)  : "L U2 L'", # U-east
    (12, 50) : "B' U' B", # U-east
    (21, 72) : "D", # L-west
    (25, 76) : "B L' D B' L", # L-west
    #(37, 24) : "", # L-east
    #(41, 28) : "", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "B L U' B' L'", # R-east
    (60, 73) : "B2 L B2 L'", # R-east
    (46, 82) : "L' D' L", # D-north
    (47, 83) : "B D2 B'", # D-north
    (30, 89) : "D L' D' L", # D-west
    (31, 85) : "B D' B'", # D-west
    (78, 95) : "L' D L", # D-south
    (79, 94) : "B' L B L'", # D-south
    (62, 88) : "L' D2 L", # D-east
    (63, 92) : "B D B'", # D-east
}

lookup_table_444_sister_wing_to_B_west = {
    (2, 67)  : "B' R B R'", # U-north
    (3, 66)  : "R' U R", # U-north
    (5, 18)  : "R' U2 R", # U-west
    (9, 19)  : "B U B'", # U-west
    (14, 34) : "R' U' R", # U-south
    (15, 35) : "B U2 B'", # U-south
    (8, 51)  : "B U' B'", # U-east
    (12, 50) : "R B R' B'", # U-east
    #(21, 72) : "", # L-west
    #(25, 76) : "", # L-west
    #(37, 24) : "", # L-east
    #(41, 28) : "", # L-east
    (40, 53) : None, # R-west
    #(44, 57) : "", # R-west
    (56, 69) : "D", # R-east
    (60, 73) : "B R' U B' R", # R-east
    (46, 82) : "B' D2 B", # D-north
    (47, 83) : "R D R'", # D-north
    (30, 89) : "B' D' B", # D-west
    (31, 85) : "R D2 R'", # D-west
    (78, 95) : "B R B' R'", # D-south
    (79, 94) : "R D' R'", # D-south
    (62, 88) : "B' D B", # D-east
    (63, 92) : "D R D' R'", # D-east
}
'''
