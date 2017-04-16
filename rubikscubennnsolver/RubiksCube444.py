
from collections import OrderedDict
from copy import copy
from pprint import pformat
from rubikscubennnsolver.pts_line_bisect import get_line_startswith
from rubikscubennnsolver.RubiksSide import Side, SolveError
from rubikscubennnsolver import RubiksCube
import logging
import math
import os
import random
import re
import subprocess
import sys

log = logging.getLogger(__name__)

moves_4x4x4 = ("U", "U'", "U2", "Uw", "Uw'", "Uw2",
               "L", "L'", "L2", "Lw", "Lw'", "Lw2",
               "F" , "F'", "F2", "Fw", "Fw'", "Fw2",
               "R" , "R'", "R2", "Rw", "Rw'", "Rw2",
               "B" , "B'", "B2", "Bw", "Bw'", "Bw2",
               "D" , "D'", "D2", "Dw", "Dw'", "Dw2")

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

class RubiksCube444(RubiksCube):

    def lookup_table_444_UD_centers_solve(self):
        filename = 'lookup-table-4x4x4-step10-UD-centers-solve.txt'
        state = self.get_center_corner_state()
        state = state.replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x')

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                log.info("Found UD centers solve %s in lookup table, %d steps in, %s" %\
                    (state, len(self.solution), ' '.join(steps)))

                for step in steps:
                    self.rotate(step)
            else:
                print("ERROR: Could not find UD solve %s in %s" % (state, filename))
                sys.exit(1)

    def lookup_table_444_LFRB_centers_solve(self):
        filename = 'lookup-table-4x4x4-step20-LFRB-centers-solve.txt'
        state = self.get_center_corner_state()

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                log.info("Found LFRB centers stage %s in lookup table, %d steps in, %s" %\
                    (state, len(self.solution), ' '.join(steps)))

                for step in steps:
                    self.rotate(step)
            else:
                print("ERROR: Could not find LFRB state %s in %s" % (state, filename))
                sys.exit(1)

        '''
    def lookup_table_444_UD_centers_stage(self):
        filename = 'lookup-table-4x4x4-step10-UD-centers-stage.txt'
        state = self.get_center_corner_state()
        state = state.replace('U', 'U').replace('L', 'x').replace('F', 'x').replace('R', 'x').replace('B', 'x').replace('D', 'U')

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                log.info("Found UD centers stage %s in lookup table, %d steps in, %s" %\
                    (state, len(self.solution), ' '.join(steps)))

                for step in steps:
                    self.rotate(step)
            else:
                print("ERROR: Could not find UD state %s in %s" % (state, filename))
                sys.exit(1)

    def lookup_table_444_LR_centers_stage(self):
        filename = 'lookup-table-4x4x4-step20-LR-centers-stage.txt'
        state = self.get_center_corner_state()
        state = state.replace('U', 'U').replace('L', 'L').replace('F', 'F').replace('R', 'L').replace('B', 'F').replace('D', 'U')

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                log.info("Found LR centers stage %s in lookup table, %d steps in, %s" %\
                    (state, len(self.solution), ' '.join(steps)))

                for step in steps:
                    self.rotate(step)
            else:
                raise SolveError("Could not find LFRB state %s in %s" % (state, filename))

    def lookup_table_444_ULFRBD_centers_solve(self):
        # TODO find a way to pair some edges in the process
        filename = 'lookup-table-4x4x4-step30-ULFRBD-centers-solve.txt'
        state = self.get_center_corner_state()

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, state + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()

                log.info("Found ULFRDB centers solve %s in lookup table, %d steps in, %s" %\
                    (state, len(self.solution), ' '.join(steps)))

                for step in steps:
                    self.rotate(step)

                self.rotate_U_to_U()
                self.rotate_F_to_F()
            else:
                raise SolveError("Did not find %s in %s" % (state, filename))
        '''

    def group_centers_guts(self):
        # old way
        #self.lookup_table_444_UD_centers_stage()
        #self.lookup_table_444_LR_centers_stage()
        #self.lookup_table_444_ULFRBD_centers_solve()

        # new way
        self.lookup_table_444_UD_centers_solve()
        self.lookup_table_444_LFRB_centers_solve()

    def find_moves_to_stage_slice_forward_444(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        # target_wing must go in spot 41
        # sister_wing1 must go in spot (40, 53)
        # sister_wing2 must go in spot (56, 69)
        # sister_wing3 must go in spot (72, 21)
        foo = []
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in sorted(side.edge_pos):

                if square_index in (target_wing[0], target_wing[1]):
                    foo.append('A')

                elif square_index in (sister_wing1[0], sister_wing1[1]):
                    foo.append('B')

                elif square_index in (sister_wing2[0], sister_wing2[1]):
                    foo.append('C')

                elif square_index in (sister_wing3[0], sister_wing3[1]):
                    foo.append('D')

                else:
                    foo.append('x')

        edge_string_to_find = ''.join(foo)
        filename = 'lookup-table-4x4x4-step40-edges-slice-forward.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, edge_string_to_find + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                return steps

        log.debug("find_moves_to_stage_slice_forward_444 could not find %s" % edge_string_to_find)
        return None

    def find_moves_to_stage_slice_backward_444(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        # target_wing must go in spot (44, 57)
        # sister_wing1 must go in spot (24, 37)
        # sister_wing2 must go in spot (72, 21))
        # sister_wing3 must go in spot (56, 69)
        foo = []
        for side in (self.sideU, self.sideL, self.sideF, self.sideR, self.sideB, self.sideD):
            for square_index in sorted(side.edge_pos):

                if square_index in (target_wing[0], target_wing[1]):
                    foo.append('A')

                elif square_index in (sister_wing1[0], sister_wing1[1]):
                    foo.append('B')

                elif square_index in (sister_wing2[0], sister_wing2[1]):
                    foo.append('C')

                elif square_index in (sister_wing3[0], sister_wing3[1]):
                    foo.append('D')

                else:
                    foo.append('x')

        edge_string_to_find = ''.join(foo)
        filename = 'lookup-table-4x4x4-step50-edges-slice-backward.txt'

        with open(filename, 'r') as fh:
            line = get_line_startswith(fh, edge_string_to_find + ':')

            if line:
                (key, steps) = line.split(':')
                steps = steps.strip().split()
                return steps

        log.debug("find_moves_to_stage_slice_backward_444 could not find %s" % edge_string_to_find)
        return None

        '''
    def find_moves_to_reach_state(self, wing_to_move, target_face_side):
        """
        This was used to build the lookup_table_444_last_two_edges_place_F_east, etc lookup tables
        """
        original_state = copy(self.state)
        original_solution = copy(self.solution)

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

                self.state = copy(original_state)
                self.solution = copy(original_solution)

                if found_solution:
                    log.warning("solution to move %s to %s is %s" % (wing_to_move, target_face_side, ' '.join(steps)))
                    sys.exit(1)

            log.warning("Explored %d moves in %s but did not find a solution" % (count, filename))
            sys.exit(1)
        '''

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
            raise SolveError("Did not find an unpaired edge")

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
        original_state = copy(self.state)
        original_solution = copy(self.solution)
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
            self.state = copy(original_state)
            self.solution = copy(original_solution)
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
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

        if not self.prep_for_slice_back_444():
            #raise SolveError("cannot slice back")
            self.state = copy(original_state)
            self.solution = copy(original_solution)
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
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()
        original_non_paired_edges = self.get_non_paired_edges()

        min_solution_len = None
        min_solution_state = None
        min_solution = None

        for wing_to_pair in original_non_paired_edges:
            self.state = copy(original_state)
            self.solution = copy(original_solution)
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
                for x in range(3):
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
                min_solution_state = copy(self.state)
                min_solution = copy(self.solution)
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
            self.state = copy(original_state)
            self.solution = copy(original_solution)
            return False

    def pair_four_edges_444(self, edge):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
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
            self.state = copy(original_state)
            self.solution = copy(original_solution)
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

    def pair_two_edges_444(self, edge, pair_multiple_edges_at_once):
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

        # Now that that two edges on F are in place, put an unpaired edge at U-west
        if pair_multiple_edges_at_once:

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
        else:
            self.make_U_west_have_unpaired_edge()

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
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        # Put one unpaired edge on F west
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

    def group_edges(self):

        # save cube state
        original_state = copy(self.state)
        original_solution = copy(self.solution)
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)

        # There are 12 edges, cycle through all 12 in terms of which edge we try to pair first.
        # Remember the one that results in the shortest solution that is free of PLL parity.
        original_non_paired_edges = self.get_non_paired_edges()
        min_solution_length = None
        min_solution_state = None
        min_solution = None

        # There are some cubes where I always hit PLL parity when I pair multiple
        # edges at a time, so try with this capability first and if we fail to find
        # a PLL free solution then turn it off.
        for pair_multiple_edges_at_once in (True, False):
            for init_wing_to_pair in original_non_paired_edges:
                log.info("init_wing_to_pair %20s" % pformat(init_wing_to_pair))

                while True:
                    non_paired_edges = self.get_non_paired_edges()
                    len_non_paired_edges = len(non_paired_edges)

                    if len_non_paired_edges > 6:
                        if init_wing_to_pair:
                            wing_to_pair = init_wing_to_pair[0]
                            init_wing_to_pair = None
                        else:
                            wing_to_pair = non_paired_edges[0][0]

                        if not self.pair_six_edges_444(wing_to_pair):
                            log.info("pair_six_edges_444()    returned False")
                            self.pair_two_edges_444(wing_to_pair, pair_multiple_edges_at_once)

                    elif len_non_paired_edges == 6 and pair_multiple_edges_at_once:
                        # When there are 6 pairs left you can pair 2 on the slice forward
                        # and the final 4 on the slice back. When you pair the 2 on the slice
                        # forward the edge on the back left side must be unpaired (if it is
                        # paired we will unpair it)
                        if init_wing_to_pair:
                            wing_to_pair = init_wing_to_pair[0]
                            init_wing_to_pair = None
                        else:
                            wing_to_pair = non_paired_edges[0][0]

                        if not self.pair_last_six_edges_444():
                            log.info("pair_last_six_edges_444() returned False")

                            if not self.pair_four_edges_444(wing_to_pair):
                                log.info("pair_four_edges_444() returned False")
                                self.pair_two_edges_444(wing_to_pair, pair_multiple_edges_at_once)

                    elif len_non_paired_edges > 2:
                        if init_wing_to_pair:
                            wing_to_pair = init_wing_to_pair[0]
                            init_wing_to_pair = None
                        else:
                            wing_to_pair = non_paired_edges[0][0]

                        self.pair_two_edges_444(wing_to_pair, pair_multiple_edges_at_once)

                    elif len_non_paired_edges == 2:
                        wing_to_pair = non_paired_edges[0][0]
                        self.pair_last_two_edges_444(wing_to_pair)

                    else:
                        break

                solution_len_minus_rotates = self.get_solution_len_minus_rotates(self.solution)

                if self.edge_solution_leads_to_pll_parity():
                    log.info("edges solution length %d, leads to PLL parity" % (solution_len_minus_rotates - original_solution_len))
                else:
                    if min_solution_length is None or solution_len_minus_rotates < min_solution_length:
                        min_solution_length = solution_len_minus_rotates
                        min_solution_state = copy(self.state)
                        min_solution = copy(self.solution)
                        log.warning("edges solution length %d (NEW MIN)" % (solution_len_minus_rotates - original_solution_len))
                    else:
                        log.info("edges solution length %d" % (solution_len_minus_rotates - original_solution_len))
                log.info('')

                # Restore to original state
                self.state = copy(original_state)
                self.solution = copy(original_solution)

            # If we were able to find a PLL free solution when pair_multiple_edges_at_once
            # was True then break, there is not point trying with pair_multiple_edges_at_once
            # False since those solutions will all be longer
            if min_solution_length:
                break
            else:
                log.warning("Could not find PLL free edge solution with pair_multiple_edges_at_once True")

        if min_solution_length:
            self.state = copy(min_solution_state)
            self.solution = copy(min_solution)

            if self.get_non_paired_edges_count():
                raise SolveError("All edges should be resolved")

            self.solution.append('EDGES_GROUPED')
        else:
            raise SolveError("Could not find a PLL free edge solution")
