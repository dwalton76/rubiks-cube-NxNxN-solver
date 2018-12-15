#!/usr/bin/env python3

from rubikscubennnsolver import wing_strs_all, wing_str_map
from rubikscubennnsolver.RubiksSide import SolveError
from rubikscubennnsolver.misc import pre_steps_to_try
from rubikscubennnsolver.RubiksCube555 import (
    centers_555,
    edges_555,
    edges_partner_555,
    edges_recolor_pattern_555,
    l4e_wings_555,
    moves_555,
    wings_for_edges_pattern_555,
    LFRB_centers_555,
    RubiksCube555,
    LookupTableIDA555UDCentersStage,
    LookupTableIDA555LRCentersStage,
    LookupTableIDA555ULFRBDCentersSolve,
    LookupTable555UDTCenterStage,
    LookupTable555LRTCenterStageOdd,
    LookupTable555LRTCenterStageEven,
    LookupTable555TCenterSolve,
    LookupTable555XPlaneYPlaneEdgesOrientPairOneEdge,
    LookupTable555LRCenterStage432PairOneEdge,
)
from rubikscubennnsolver.LookupTable import (
    LookupTable,
    LookupTableIDA,
    LookupTableHashCostOnly,
)
from pprint import pformat
import itertools
import logging
import sys

log = logging.getLogger(__name__)


class LookupTable555CycleEdges(LookupTable):
    """
    0-deep
    lookup-table-555-step810-edges.txt
    ==================================
    3 steps has 1 entries (0 percent, 0.00x previous step)
    5 steps has 894 entries (0 percent, 894.00x previous step)
    6 steps has 2,295 entries (0 percent, 2.57x previous step)
    7 steps has 17,562 entries (1 percent, 7.65x previous step)
    8 steps has 145,519 entries (12 percent, 8.29x previous step)
    9 steps has 964,432 entries (85 percent, 6.63x previous step)

    Total: 1,130,703 entries


    1-deep
    lookup-table-555-step810-edges.txt
    ==================================
    3 steps has 1 entries (0 percent, 0.00x previous step)
    5 steps has 894 entries (0 percent, 894.00x previous step)
    6 steps has 4,265 entries (0 percent, 4.77x previous step)
    7 steps has 36,300 entries (0 percent, 8.51x previous step)
    8 steps has 269,023 entries (2 percent, 7.41x previous step)
    9 steps has 2,083,100 entries (18 percent, 7.74x previous step)
    10 steps has 8,786,611 entries (78 percent, 4.22x previous step)

    Total: 11,180,194 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-555-step810-edges.txt',
            'TBD',

            # 0-deep
            #linecount=1130703,
            #filesize=81410616,

            # 1-deep
            linecount=11180194,
            filesize=838514550,
        )

    def state(self):
        state = edges_recolor_pattern_555(self.parent.state[:], uppercase_paired_edges=False)
        state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        return state

    def ida_heuristic(self):
        state = edges_recolor_pattern_555(self.parent.state[:])
        state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)



class LookupTable555StageFirstFourEdges(LookupTable):
    """
    lookup-table-5x5x5-step100-stage-first-four-edges.txt
    =====================================================
    1 steps has 9 entries (0 percent, 0.00x previous step)
    2 steps has 72 entries (0 percent, 8.00x previous step)
    3 steps has 330 entries (0 percent, 4.58x previous step)
    4 steps has 84 entries (0 percent, 0.25x previous step)
    5 steps has 1,152 entries (0 percent, 13.71x previous step)
    6 steps has 10,200 entries (0 percent, 8.85x previous step)
    7 steps has 53,040 entries (0 percent, 5.20x previous step)
    8 steps has 187,296 entries (2 percent, 3.53x previous step)
    9 steps has 1,357,482 entries (18 percent, 7.25x previous step)
    10 steps has 5,779,878 entries (78 percent, 4.26x previous step)

    Total: 7,389,543 entries

    There is no need to build this any deeper...building it to 10-deep
    takes about 2 days on a 12-core machine.
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step100-stage-first-four-edges.txt',
            'TBD',
            linecount=7389543,
            filesize=421203951,
        )

    def state(self, wing_strs_to_stage):
        state = self.parent.state[:]

        for square_index in l4e_wings_555:
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in wing_strs_to_stage:
                state[square_index] = '1'
                state[partner_index] = '1'
            else:
                state[square_index] = '0'
                state[partner_index] = '0'

        edges_state = ''.join([state[square_index] for square_index in edges_555])
        edges_state = int(edges_state, 2)
        edges_state = self.hex_format % edges_state
        return edges_state


class LookupTable555StageSecondFourEdges(LookupTable):
    """
    lookup-table-5x5x5-step101-stage-second-four-edges.txt
    ======================================================
    5 steps has 32 entries (0 percent, 0.00x previous step)
    6 steps has 304 entries (0 percent, 9.50x previous step)
    7 steps has 1,208 entries (0 percent, 3.97x previous step)
    8 steps has 3,612 entries (1 percent, 2.99x previous step)
    9 steps has 12,856 entries (3 percent, 3.56x previous step)
    10 steps has 42,688 entries (12 percent, 3.32x previous step)
    11 steps has 89,194 entries (26 percent, 2.09x previous step)
    12 steps has 113,508 entries (33 percent, 1.27x previous step)
    13 steps has 74,720 entries (22 percent, 0.66x previous step)

    Total: 338,122 entries

    This should have (16!/(8!*8!)) * (8!/(4!*4!)) or 900,900 entries
    if you built it out the entire way. We do not need to build it that deep
    though, we can try enough edge color combinations to find a hit
    in 13-deep.
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step101-stage-second-four-edges.txt',
            'TBD',
            linecount=338122,
            filesize=28740370)

    def state(self, wing_strs_to_stage):
        state = self.parent.state[:]

        for square_index in l4e_wings_555:
            partner_index = edges_partner_555[square_index]
            square_value = state[square_index]
            partner_value = state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]

            if wing_str in wing_strs_to_stage:
                state[square_index] = 'U'
                state[partner_index] = 'U'
            else:
                state[square_index] = 'x'
                state[partner_index] = 'x'

        edges_state = ''.join([state[square_index] for square_index in l4e_wings_555])
        #log.info("FOO: %s" % edges_state)
        return edges_state


class LookupTable555EdgesXPlaneEdgesOnly(LookupTable):
    """
    lookup-table-5x5x5-step301-edges-x-plane-edges-only.txt
    =======================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 21 entries (0 percent, 3.00x previous step)
    3 steps has 90 entries (0 percent, 4.29x previous step)
    4 steps has 358 entries (0 percent, 3.98x previous step)
    5 steps has 1,204 entries (2 percent, 3.36x previous step)
    6 steps has 2,656 entries (6 percent, 2.21x previous step)
    7 steps has 6,084 entries (15 percent, 2.29x previous step)
    8 steps has 6,652 entries (16 percent, 1.09x previous step)
    9 steps has 9,016 entries (22 percent, 1.36x previous step)
    10 steps has 7,576 entries (18 percent, 0.84x previous step)
    11 steps has 5,480 entries (13 percent, 0.72x previous step)
    12 steps has 984 entries (2 percent, 0.18x previous step)
    13 steps has 192 entries (0 percent, 0.20x previous step)

    Total: 40,320 entries
    Average: 8.71 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step301-edges-x-plane-edges-only.txt',
            '------------sSSTTtuUUVVv------------',
            linecount=40320,
            max_depth=13,
            filesize=3346560)

    def ida_heuristic(self):
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        state = edges_recolor_pattern_555(self.parent.state[:], self.only_colors)
        edges_state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(edges_state)
        return (edges_state, cost_to_goal)


class LookupTable555EdgesXPlaneCentersOnly(LookupTable):
    """
    lookup-table-5x5x5-step302-edges-x-plane-centers-only.txt
    =========================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 33 entries (1 percent, 4.71x previous step)
    3 steps has 162 entries (6 percent, 4.91x previous step)
    4 steps has 504 entries (20 percent, 3.11x previous step)
    5 steps has 1,182 entries (46 percent, 2.35x previous step)
    6 steps has 632 entries (25 percent, 0.53x previous step)

    Total: 2,520 entries
    Average: 4.87 moves
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step302-edges-x-plane-centers-only.txt',
            'LLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBB',
            linecount=2520,
            max_depth=6,
            filesize=146160)

    def ida_heuristic(self):
        parent_state = self.parent.state
        state = ''.join([parent_state[x] for x in LFRB_centers_555])
        cost_to_goal = self.heuristic(state)
        return (state, cost_to_goal)


class LookupTableIDA555EdgesXPlane(LookupTableIDA):
    """
    lookup-table-5x5x5-step300-edges-x-plane.txt
    ============================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 33 entries (0 percent, 4.71x previous step)
    3 steps has 230 entries (0 percent, 6.97x previous step)
    4 steps has 1,414 entries (0 percent, 6.15x previous step)
    5 steps has 8,768 entries (2 percent, 6.20x previous step)
    6 steps has 50,346 entries (14 percent, 5.74x previous step)
    7 steps has 280,506 entries (82 percent, 5.57x previous step)

    Total: 341,304 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step300-edges-x-plane.txt',
            ('LLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBB------------sSSTTtuUUVVv------------', ),
            moves_555,
            # illegal moves
            (),

            linecount=341304,
            max_depth=7,
            filesize=35154312,

            legal_moves = (
                "L2", "F2", "R2", "B2",
                "Uw", "Uw'", "Uw2",
                "Dw", "Dw'", "Dw2",
            )
        )

    def ida_heuristic(self):
        parent_state = self.parent.state
        (edges_state, edges_cost) = self.parent.lt_edges_x_plane_edges_only.ida_heuristic()
        (centers_state, centers_cost) = self.parent.lt_edges_x_plane_centers_only.ida_heuristic()

        lt_state = centers_state + edges_state
        cost_to_goal = max(edges_cost, centers_cost)

        if cost_to_goal > 0:
            steps = self.steps(lt_state)

            if steps:
                cost_to_goal = len(steps)
            else:
                cost_to_goal = max(cost_to_goal, self.max_depth + 1)

        return (lt_state, cost_to_goal)


class LookupTable555EdgesXPlaneCentersSolved(LookupTable):
    """
    lookup-table-5x5x5-step310-edges-x-plane-with-solved-centers.txt
    ================================================================
    1 steps has 1 entries (0 percent, 0.00x previous step)
    5 steps has 10 entries (0 percent, 10.00x previous step)
    6 steps has 45 entries (0 percent, 4.50x previous step)
    7 steps has 196 entries (0 percent, 4.36x previous step)
    8 steps has 452 entries (1 percent, 2.31x previous step)
    9 steps has 1,556 entries (3 percent, 3.44x previous step)
    10 steps has 3,740 entries (9 percent, 2.40x previous step)
    11 steps has 10,188 entries (25 percent, 2.72x previous step)
    12 steps has 16,778 entries (41 percent, 1.65x previous step)
    13 steps has 6,866 entries (17 percent, 0.41x previous step)
    14 steps has 488 entries (1 percent, 0.07x previous step)

    Total: 40,320 entries
    Average: 11.56 moves
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step310-edges-x-plane-with-solved-centers.txt',
            '------------sSSTTtuUUVVv------------',
            linecount=40320,
            max_depth=14,
            filesize=3427200)

    def ida_heuristic(self):
        assert self.only_colors and len(self.only_colors) == 4, "You must specify which 4-edges"
        state = edges_recolor_pattern_555(self.parent.state[:], self.only_colors)
        edges_state = ''.join([state[index] for index in wings_for_edges_pattern_555])
        cost_to_goal = self.heuristic(edges_state)
        #log.info("%s: edges_state %s" % (self, edges_state))
        return (edges_state, cost_to_goal)



class RubiksCube555ForNNN(RubiksCube555):
    """
    5x5x5 strategy
    - stage UD centers to sides U or D (use IDA)
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3
    """

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        self.lt_UD_centers_stage = LookupTableIDA555UDCentersStage(self)
        self.lt_LR_centers_stage = LookupTableIDA555LRCentersStage(self)
        self.lt_ULFRBD_centers_solve = LookupTableIDA555ULFRBDCentersSolve(self)
        self.lt_UD_T_centers_stage = LookupTable555UDTCenterStage(self)
        self.lt_LR_T_centers_stage_odd = LookupTable555LRTCenterStageOdd(self)
        self.lt_LR_T_centers_stage_even = LookupTable555LRTCenterStageEven(self)
        self.lt_ULFRBD_t_centers_solve = LookupTable555TCenterSolve(self)

        # No need to preload this one, we use binary_seach_multiple
        self.lt_edges_stage_first_four = LookupTable555StageFirstFourEdges(self)
        self.lt_edges_stage_second_four = LookupTable555StageSecondFourEdges(self)
        self.lt_edges_stage_second_four.preload_cache_string()

        self.lt_edges_x_plane_centers_solved = LookupTable555EdgesXPlaneCentersSolved(self)
        #self.lt_cycle_edges = LookupTable555CycleEdges(self)
        #self.lt_LR_432_pair_one_edge = LookupTable555LRCenterStage432PairOneEdge(self)

    def stage_first_four_edges_555(self):
        """
        There are 495 different permutations of 4-edges out of 12-edges, use the one
        that gives us the shortest solution for getting 4-edges staged to LB, LF, RF, RB
        """

        # return if they are already staged
        if self.x_plane_edges_are_l4e():
            log.info("%s: first L4E group in x-plane" % self)
            return

        if self.y_plane_edges_are_l4e():
            log.info("%s: first L4E group in y-plane, moving to x-plane" % self)
            self.rotate("z")
            return

        if self.z_plane_edges_are_l4e():
            log.info("%s: first L4E group in z-plane, moving to x-plane" % self)
            self.rotate("x")
            return

        min_solution_len = None
        min_solution_steps = None

        # The table for staging the 1st 4-edges would have 364,058,145 if built to completion.
        # Building that table the entire way is difficult though because this is a table where
        # the centers must be kept solved...so this involves building out a HUGE table and only
        # keeping the entries where the centers are solved.  To build one deep enough to find
        # all 364,058,145 entries needed that also have solved centers would probably take a
        # few months and more drive space than I have access to.
        #
        # To avoid building such a massive table we only build the table out 10-deep which gives
        # us a few million entries.  We then try all 495 permutations of 4-edges out of 12-edges
        # looking for one that does have a hit.  Most of the time this is all that is needed and
        # we can find a hit.  On the off chance that we cannot though we need a way to find a solution
        # so what we do is try all outer layer moves up to 3 moves deep and see if any of those
        # sequences put the cube in a state such that one of the 495 edge permutations does find
        # a hit. I have yet to find a cube that cannot be solved with this approach but if I did
        # the pre_steps_to_try could be expanded to 4-deep.

        # Ran this once to generate pre_steps_to_try
        '''
        outer_layer_moves = (
            "U", "U'", "U2",
            "L", "L'", "L2",
            "F", "F'", "F2",
            "R", "R'", "R2",
            "B", "B'", "B2",
            "D", "D'", "D2",
        )
        pre_steps_to_try = []
        pre_steps_to_try.append([])

        for step in outer_layer_moves:
            pre_steps_to_try.append((step,))

        for step1 in outer_layer_moves:
            for step2 in outer_layer_moves:
                if not steps_on_same_face_and_layer(step1, step2):
                    pre_steps_to_try.append((step1, step2))

        for step1 in outer_layer_moves:
            for step2 in outer_layer_moves:
                if not steps_on_same_face_and_layer(step1, step2):

                    for step3 in outer_layer_moves:
                        if not steps_on_same_face_and_layer(step2, step3):
                            pre_steps_to_try.append((step1, step2, step3))

        from pprint import pformat
        log.info("pre_steps_to_try: %d" % len(pre_steps_to_try))
        log.info("pre_steps_to_try:\n%s\n" % pformat(pre_steps_to_try))

        # uncomment this if we ever find a cube that raises the
        # "Could not find 4-edges to stage" NoEdgeSolution exception below
        for step1 in outer_layer_moves:
            for step2 in outer_layer_moves:
                if not steps_on_same_face_and_layer(step1, step2):
                    for step3 in outer_layer_moves:
                        if not steps_on_same_face_and_layer(step2, step3):
                            for step4 in outer_layer_moves:
                                if not steps_on_same_face_and_layer(step3, step4):
                                    pre_steps_to_try.append([step1, step2, step3, step4])
        '''

        # Remember what things looked like
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)

        min_solution_len = None
        min_solution_steps = None

        for pre_steps in pre_steps_to_try:
            self.state = original_state[:]
            self.solution = original_solution[:]

            #log.info("")
            #log.info("")
            #log.info("%s: pre_steps %s" % (self, " ".join(pre_steps)))
            for step in pre_steps:
                self.rotate(step)

            post_pre_steps_state = self.state[:]
            post_pre_steps_solution = self.solution[:]
            states_to_find = []

            for wing_strs in itertools.combinations(wing_strs_all, 4):
                states_to_find.append(self.lt_edges_stage_first_four.state(wing_strs))

            results = self.lt_edges_stage_first_four.binary_search_multiple(states_to_find)
            len_results = len(results)
            log.info("%s: %d states_to_find, found %d matches" % (self, len(states_to_find), len(results)))

            for (line_number, (_, steps)) in enumerate(results.items()):
                self.state = post_pre_steps_state[:]
                self.solution = post_pre_steps_solution[:]

                for step in steps.split():
                    self.rotate(step)

                self.stage_final_four_edges_in_x_plane()
                solution_steps = self.solution[original_solution_len:]
                solution_len = self.get_solution_len_minus_rotates(solution_steps)

                # Technically we only need 4 edges to be pairable for the next phase but 5 is nice because it gives
                # the next phase some wiggle room...it can choose the best 4-edge tuple.
                if min_solution_len is None or solution_len < min_solution_len:
                    log.info("%s: %d/%d 1st 4-edges can be staged in %d steps %s (NEW MIN)" % (
                        self, line_number, len_results, solution_len, ' '.join(solution_steps)))
                    min_solution_len = solution_len
                    min_solution_steps = solution_steps
                else:
                    log.info("%s: %d/%d 1st 4-edges can be staged in %d steps" % (
                        self, line_number, len_results, solution_len))

            if min_solution_len is not None:
                #if pre_steps:
                #    log.info("pre-steps %s required to find a hit" % ' '.join(pre_steps))
                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in min_solution_steps:
                    self.rotate(step)

                break

        if not self.x_plane_edges_are_l4e():
            raise SolveError("There should be an L4E group in x-plane but there is not")

        self.print_cube()
        self.solution.append("COMMENT_%d_steps_555_first_L4E_edges_staged" % self.get_solution_len_minus_rotates(self.solution[original_solution_len:]))
        log.info("%s: 1st 4-edges staged to x-plane, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def place_first_four_paired_edges_in_x_plane(self):

        if self.x_plane_edges_paired():
            log.info("%s: 4 paired edges in x-plane" % (self))
            return

        if self.y_plane_edges_paired():
            log.info("%s: 4 paired edges in y-plane, moving to x-plane" % (self))
            self.rotate("z")
            return

        if self.z_plane_edges_paired():
            log.info("%s: 4 paired edges in z-plane, moving to x-plane" % (self))
            self.rotate("x")
            return

        original_state = self.state[:]
        original_solution = self.solution[:]

        # Traverse a table of moves that place L4E in one of three planes
        for pre_steps in pre_steps_to_try:
            self.state = original_state[:]
            self.solution = original_solution[:]

            for step in pre_steps:
                self.rotate(step)

            if self.x_plane_edges_paired():
                log.info("%s: %s puts 4 paired edges in x-plane" % (self, "".join(pre_steps)))
                break

            elif self.y_plane_edges_paired():
                log.info("%s: %s puts 4 paired edges in y-plane" % (self, "".join(pre_steps)))
                self.rotate("z")
                break

            elif self.z_plane_edges_paired():
                log.info("%s: %s puts 4 paired edges in z-plane" % (self, "".join(pre_steps)))
                self.rotate("x")
                break
        else:
            raise SolveError("Could not place 4 paired edges in x-plane")

    def pair_first_four_edges_via_l4e(self):
        paired_edges_count = self.get_paired_edges_count()

        # If there are already 4 paired edges all we need to do is put them in the x-plane
        if paired_edges_count >= 4:
            self.place_first_four_paired_edges_in_x_plane()
            log.info("%s: 1st 4-edges already paired, moved to x-plane, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        # We do not have 4 paired edges, stage a L4E group to the x-plane and pair them via the L4E table
        else:
            self.stage_first_four_edges_555()
            self.pair_x_plane_edges_in_l4e()

    def stage_second_four_edges_555(self):
        """
        The 1st 4-edges have been staged to LB, LF, RF, RB. Stage the next four
        edges to UB, UF, DF, DB (this in turn stages the final four edges).

        Since there are 8-edges there are 70 different combinations of edges we can
        choose to stage to UB, UF, DF, DB. Walk through all 70 combinations and see
        which one leads to the shortest solution.
        """

        # return if they are already staged
        if self.y_plane_edges_are_l4e() and self.z_plane_edges_are_l4e():
            return

        first_four_wing_strs = list(self.get_x_plane_wing_strs())
        wing_strs_for_second_four = []

        log.info("first_four_wing_strs %s" % pformat(first_four_wing_strs))

        for wing_str in wing_strs_all:
            if wing_str not in first_four_wing_strs:
                wing_strs_for_second_four.append(wing_str)

        log.info("wing_strs_for_second_four %s" % pformat(wing_strs_for_second_four))
        assert len(wing_strs_for_second_four) == 8
        min_solution_len = None
        min_solution_steps = None

        # Remember what things looked like
        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)

        for pre_steps in pre_steps_to_try:

            for wing_strs in itertools.combinations(wing_strs_for_second_four, 4):
                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in pre_steps:
                    self.rotate(step)

                state = self.lt_edges_stage_second_four.state(wing_strs)
                steps = self.lt_edges_stage_second_four.steps(state)
                #log.info("%s: pre_steps %s, wing_strs %s, state %s, steps %s" % (
                #    self, pformat(pre_steps), wing_strs, state, pformat(steps)))

                if steps:

                    for step in steps:
                        self.rotate(step)

                    solution_steps = self.solution[original_solution_len:]
                    solution_len = self.get_solution_len_minus_rotates(solution_steps)

                    if min_solution_len is None or solution_len < min_solution_len:
                        min_solution_len = solution_len
                        min_solution_steps = solution_steps
                        log.info("%s: y-plane edges %s can be staged in %d steps (NEW MIN)" % (self, wing_strs, solution_len))
                    else:
                        log.info("%s: y-plane edges %s can be staged in %d steps" % (self, wing_strs, solution_len))

                    self.state = original_state[:]
                    self.solution = original_solution[:]

            if min_solution_len is not None:
                if pre_steps:
                    log.info("pre-steps %s required to find a hit" % ' '.join(pre_steps))

                self.state = original_state[:]
                self.solution = original_solution[:]

                for step in min_solution_steps:
                    self.rotate(step)

                break

        self.state = original_state[:]
        self.solution = original_solution[:]

        if min_solution_len is None:
            raise SolveError("Could not find 4-edges to stage")
        else:
            for step in min_solution_steps:
                self.rotate(step)

    def pair_second_four_edges_via_l4e(self):
        self.stage_second_four_edges_555()
        self.rotate("x")
        log.info("%s: 2nd 4-edges staged, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.pair_x_plane_edges_in_l4e()
        self.print_cube()
        #log.info("kociemba: %s" % self.get_kociemba_string(True))
        log.info("%s: 2nd 4-edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def stage_final_four_edges_in_x_plane(self):
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Traverse a table of moves that place L4E in one of three planes
        # and then rotate that plane to the x-plane
        for pre_steps in pre_steps_to_try:
            self.state = original_state[:]
            self.solution = original_solution[:]
            steps = None

            for step in pre_steps:
                self.rotate(step)

            if self.x_plane_edges_are_l4e() and self.x_plane_edges_unpaired_count() > 0:
                #if pre_steps:
                #    log.info("%s: %s puts L4E group in x-plane" % (self, "".join(pre_steps)))
                #else:
                #    log.info("%s: L4E group in x-plane" % self)
                break

            elif self.y_plane_edges_are_l4e() and self.y_plane_edges_unpaired_count() > 0:
                #if pre_steps:
                #    log.info("%s: %s puts L4E group in y-plane, moving to x-plane" % (self, "".join(pre_steps)))
                #else:
                #    log.info("%s: L4E group in y-plane, moving to x-plane" % self)
                self.rotate("z")
                break

            elif self.z_plane_edges_are_l4e() and self.z_plane_edges_unpaired_count() > 0:
                #if pre_steps:
                #    log.info("%s: %s puts L4E group in z-plane" % (self, "".join(pre_steps)))
                #else:
                #    log.info("%s: L4E group in z-plane, moving to x-plane" % self)
                self.rotate("x")
                break
        else:
            raise SolveError("Could not stage L4E in x-plane")

        #log.info("%s: final four edges placed in x-plane, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

    def pair_x_plane_edges_in_l4e(self):

        if not self.x_plane_edges_are_l4e():
            raise SolveError("There must be a L4E group of edges in the x-plane")

        if self.x_plane_edges_paired():
            log.info("%s: x-plane edges already paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            return

        original_state = self.state[:]
        original_solution = self.solution[:]
        original_solution_len = len(self.solution)
        original_paired_edges_count = self.get_paired_edges_count()

        # The 4 paired edges are in the x-plane
        only_colors = []
        for square_index in (36, 40, 86, 90):
            partner_index = edges_partner_555[square_index]
            square_value = self.state[square_index]
            partner_value = self.state[partner_index]
            wing_str = wing_str_map[square_value + partner_value]
            only_colors.append(wing_str)

        # Old way where we would IDA
        '''
        self.lt_edges_x_plane_edges_only.only_colors = only_colors
        self.lt_edges_x_plane.only_colors = only_colors

        # Recolor the centers in the x-plane to LFRB since LFRB was used to build our tables
        centers_recolor = {
            self.state[38] : "L",
            self.state[63] : "F",
            self.state[88] : "R",
            self.state[113] : "B",
        }

        for x in LFRB_centers_555:
            self.state[x] = centers_recolor[self.state[x]]

        # Recolor the edges to they are all oriented using their original orientation.
        # We do this because our tables were built will all edges at their original orientation.
        self.edges_flip_to_original_orientation()

        # Now we can solve
        self.lt_edges_x_plane.solve()
        '''

        # Recolor the edges to they are all oriented using their original orientation.
        # We do this because our tables were built will all edges at their original orientation.
        self.edges_flip_to_original_orientation()

        # Now we can solve
        self.lt_edges_x_plane_centers_solved.only_colors = only_colors
        self.lt_edges_x_plane_centers_solved.solve()

        # Put the cube back the way it was (to undo all of the recoloring we did) and apply the solution
        l4e_solution = self.solution[original_solution_len:]
        self.state = original_state[:]
        self.solution = original_solution[:]

        for step in l4e_solution:
            self.rotate(step)

        self.print_cube()
        assert self.x_plane_edges_paired(), "4-edges in x-plane should have paired"
        self.solution.append("COMMENT_%d_steps_555_L4E_paired" % self.get_solution_len_minus_rotates(self.solution[original_solution_len:]))
        log.info("%s: x-plane edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        '''
    def get_final_edges_steps(self):
        log.info("%s: get_final_edges_steps begin (%d pre_steps_to_try)" % (self, len(pre_steps_to_try)))
        tmp_state = self.state[:]
        tmp_solution = self.solution[:]
        states_to_find = []
        pre_steps_for_state = {}

        for pre_steps in pre_steps_to_try:
            self.state = tmp_state[:]
            self.solution = tmp_solution[:]
    
            for step in pre_steps:
                self.rotate(step)

            self.edges_flip_to_original_orientation()
            state = self.lt_cycle_edges.state()
            states_to_find.append(state)

            pre_steps_for_state[state] = pre_steps

        self.state = tmp_state[:]
        self.solution = tmp_solution[:]
        results = self.lt_cycle_edges.binary_search_multiple(states_to_find)
        min_steps = None

        for (state, steps) in results.items():
            steps = list(pre_steps_for_state[state]) + steps.split()

            # dwalton here now
            if min_steps is None or len(steps) < len(min_steps):
                min_steps = steps
                log.info("%s: get_final_edges_steps %s (NEW MIN %d)" % (self, " ".join(steps), len(steps)))
            else:
                log.info("%s: get_final_edges_steps %s (%d)" % (self, " ".join(steps), len(steps)))

        log.info("%s: get_final_edges_steps end" % self)
        return min_steps
        '''

    def reduce_333(self):
        """
        This is used to pair the inside orbit of edges for 7x7x7
        """
        self.lt_init()

        if not self.centers_staged():
            self.group_centers_stage_UD()
            self.group_centers_stage_LR()

        if not self.centers_solved():
            tmp_solution_len = len(self.solution)
            self.lt_ULFRBD_centers_solve.solve()
            self.print_cube()
            self.solution.append("COMMENT_%d_steps_555_centers_solved" % self.get_solution_len_minus_rotates(self.solution[tmp_solution_len:]))
            log.info("%s: centers solved, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        log.info("%s: kociemba %s" % (self, self.get_kociemba_string(True)))
        self.solution.append('CENTERS_SOLVED')

        # algorithms table approach is WIP
        '''
        LR_pairable = self.edges_pairable_without_LR()
        log.info("%s: %d pairable without LR (%s)" %
            (self, len(LR_pairable), " ".join(LR_pairable)))

        tmp_state = self.state[:]
        tmp_solution = self.solution[:]

        while not self.edges_paired():
            pre_wing_count = 24 - self.get_non_paired_wings_count()
            pre_edges_count = self.get_paired_edges_count()

            if pre_edges_count >= 8:
                self.stage_final_four_edges_in_x_plane()
                self.pair_x_plane_edges_in_l4e()
                break

            steps = self.get_final_edges_steps()

            if steps:
                log.warning("FOUND STEPS!!! %s" % " ".join(steps))
                for step in steps:
                    self.rotate(step)
                break

            else:
                self.edges_flip_to_original_orientation()
                state = self.lt_cycle_edges.state()
                line = self.lt_cycle_edges.best_match(state, pre_wing_count)
                (_state, steps) = line.strip().split(":")

                for step in steps.split():
                    self.rotate(step)
                self.print_cube()
                post_wing_count = 24 - self.get_non_paired_wings_count()
                wing_delta = post_wing_count - pre_wing_count

                if not wing_delta:
                    raise SolveError("Could not pair any more wings")

                post_edges_count = self.get_paired_edges_count()
                edges_delta = post_edges_count - pre_edges_count
                log.info("%s: %d steps in, %d wings paired (%d -> %d), %d edges paired (%d -> %d)" %
                    (self, self.get_solution_len_minus_rotates(self.solution),
                    wing_delta, pre_wing_count, post_wing_count,
                    edges_delta, pre_edges_count, post_edges_count,
                    ))

                LR_pairable = self.edges_pairable_without_LR()

                log.info("%s: %d pairable without LR (%s)" %
                    (self, len(LR_pairable), " ".join(LR_pairable)))
                log.info("%s: kociemba %s" % (self, self.get_kociemba_string(True)))
                log.info("\n\n\n")

        steps = self.solution[len(tmp_solution):]
        self.state = tmp_state[:]
        self.solution = tmp_solution[:]

        for step in steps:
            if step.startswith("COMMENT"):
                self.solution.append(step)
            else:
                self.rotate(step)

        self.rotate_U_to_U()
        self.rotate_F_to_F()
        self.print_cube()
        log.info("%s: edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        '''

        if not self.edges_paired():
            self.pair_first_four_edges_via_l4e()
            self.pair_second_four_edges_via_l4e()
            self.stage_final_four_edges_in_x_plane()
            self.pair_x_plane_edges_in_l4e()

        self.solution.append('EDGES_GROUPED')
