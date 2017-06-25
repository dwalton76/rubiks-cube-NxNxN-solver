#!/usr/bin/env python2

from rubikscubennnsolver import ImplementThis, SolveError, StuckInALoop
from rubikscubennnsolver.LookupTable import NoSteps, steps_cancel_out
from rubikscubennnsolver.RubiksCube777 import RubiksCube777, moves_7x7x7
import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

parser = argparse.ArgumentParser()
parser.add_argument('--print-steps', default=False, action='store_true')
parser.add_argument('--debug', default=False, action='store_true')

# 7x7x7
parser.add_argument('--state', type=str, help='Cube state in URFDLB order',
#    default='DBDBDDFBDDLUBDLFRFRBRLLDUFFDUFRBRDFDRUFDFDRDBDBULDBDBDBUFBUFFFULLFLDURRBBRRBRLFUUUDUURBRDUUURFFFLRFLRLDLBUFRLDLDFLLFBDFUFRFFUUUFURDRFULBRFURRBUDDRBDLLRLDLLDLUURFRFBUBURBRUDBDDLRBULBULUBDBBUDRBLFFBLRBURRUFULBRLFDUFDDBULBRLBUFULUDDLLDFRDRDBBFBUBBFLFFRRUFFRLRRDRULLLFRLFULBLLBBBLDFDBRBFDULLULRFDBR',
    default='UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB' # solved
)

args = parser.parse_args()
cube = RubiksCube777(args.state, args.debug)

cube.state[61] = 'R'
cube.state[65] = 'L'
cube.state[69] = 'L'
cube.state[79] = 'R'
cube.state[82] = 'L'
cube.state[87] = 'R'
cube.state[89] = 'R'

cube.state[108] = 'B'
cube.state[110] = 'B'
cube.state[114] = 'F'
cube.state[118] = 'F'
cube.state[128] = 'F'
cube.state[132] = 'F'
cube.state[136] = 'B'
cube.state[138] = 'F'

cube.state[157] = 'R'
cube.state[159] = 'R'
cube.state[163] = 'R'
cube.state[167] = 'R'
cube.state[177] = 'L'
cube.state[181] = 'L'
cube.state[185] = 'L'
cube.state[187] = 'L'

cube.state[206] = 'B'
cube.state[208] = 'B'
cube.state[212] = 'F'
cube.state[216] = 'B'
cube.state[226] = 'F'
cube.state[230] = 'F'
cube.state[234] = 'B'
cube.state[236] = 'B'

#cube.print_cube()
cube.lt_init()
#cube.solve()
original_cube = cube.state[:]
original_solution = cube.solution[:]
states_to_check = {}
count = 0

illegal_moves = ("3Rw", "3Rw'", "3Lw", "3Lw'", "3Fw", "3Fw'", "3Bw", "3Bw'", "3Uw", "3Uw'", "3Dw", "3Dw'", # do not mess up staged centers
                 "Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'",             # do not mess up staged centers
                 "3Rw2", "3Lw2", "3Fw2", "3Bw2", "Rw2", "Lw2", "Fw2", "Bw2"),                              # do not mess up solved UD

log.info("rotate begin: rotated %d" % count)
with open('find_777_4900.states', 'w') as fh:
    for step1 in moves_7x7x7:

        if step1 in illegal_moves:
            continue

        cube.state = original_cube[:]
        cube.solution = original_solution[:]

        log.info("step1 %s" % step1)
        cube.rotate(step1)
        lt_state = cube.lt_LFRB_solve_inner_centers_and_oblique_edges.state()

        if lt_state in states_to_check:
            continue

        solution_pretty = ' '.join(cube.solution)
        states_to_check[lt_state] = solution_pretty
        #fh.write("%s:%s\n" % (lt_state, solution_pretty))
        count += 1

        end_step1_state = cube.state[:]
        end_step1_solution = cube.solution[:]

        for step2 in moves_7x7x7:

            if step2 in illegal_moves:
                continue

            if steps_cancel_out(step1, step2):
                continue

            cube.state = end_step1_state[:]
            cube.solution = end_step1_solution[:]

            cube.rotate(step2)
            lt_state = cube.lt_LFRB_solve_inner_centers_and_oblique_edges.state()

            if lt_state in states_to_check:
                continue

            solution_pretty = ' '.join(cube.solution)
            states_to_check[lt_state] = solution_pretty
            #fh.write("%s:%s\n" % (lt_state, solution_pretty))
            count += 1

            end_step2_state = cube.state[:]
            end_step2_solution = cube.solution[:]


            for step3 in moves_7x7x7:

                if step3 in illegal_moves:
                    continue

                if steps_cancel_out(step2, step3):
                    continue

                cube.state = end_step2_state[:]
                cube.solution = end_step2_solution[:]

                cube.rotate(step3)
                lt_state = cube.lt_LFRB_solve_inner_centers_and_oblique_edges.state()

                if lt_state in states_to_check:
                    continue

                solution_pretty = ' '.join(cube.solution)
                states_to_check[lt_state] = solution_pretty
                #fh.write("%s:%s\n" % (lt_state, solution_pretty))
                count += 1

                end_step3_state = cube.state[:]
                end_step3_solution = cube.solution[:]


                for step4 in moves_7x7x7:

                    if step4 in illegal_moves:
                        continue

                    if steps_cancel_out(step3, step4):
                        continue

                    cube.state = end_step3_state[:]
                    cube.solution = end_step3_solution[:]

                    cube.rotate(step4)
                    lt_state = cube.lt_LFRB_solve_inner_centers_and_oblique_edges.state()

                    if lt_state in states_to_check:
                        continue

                    solution_pretty = ' '.join(cube.solution)
                    states_to_check[lt_state] = solution_pretty
                    #fh.write("%s:%s\n" % (lt_state, solution_pretty))
                    count += 1

                    end_step4_state = cube.state[:]
                    end_step4_solution = cube.solution[:]


                    for step5 in moves_7x7x7:

                        if step5 in illegal_moves:
                            continue

                        if steps_cancel_out(step4, step5):
                            continue

                        cube.state = end_step4_state[:]
                        cube.solution = end_step4_solution[:]

                        cube.rotate(step5)
                        lt_state = cube.lt_LFRB_solve_inner_centers_and_oblique_edges.state()

                        if lt_state in states_to_check:
                            continue

                        solution_pretty = ' '.join(cube.solution)
                        states_to_check[lt_state] = solution_pretty
                        #fh.write("%s:%s\n" % (lt_state, solution_pretty))
                        count += 1

                        end_step5_state = cube.state[:]
                        end_step5_solution = cube.solution[:]


                        for step6 in moves_7x7x7:

                            if step6 in illegal_moves:
                                continue

                            if steps_cancel_out(step5, step6):
                                continue

                            cube.state = end_step5_state[:]
                            cube.solution = end_step5_solution[:]

                            cube.rotate(step6)
                            lt_state = cube.lt_LFRB_solve_inner_centers_and_oblique_edges.state()

                            if lt_state in states_to_check:
                                continue

                            solution_pretty = ' '.join(cube.solution)
                            states_to_check[lt_state] = solution_pretty
                            #fh.write("%s:%s\n" % (lt_state, solution_pretty))
                            count += 1

                            end_step6_state = cube.state[:]
                            end_step6_solution = cube.solution[:]


                            for step7 in moves_7x7x7:

                                if step7 in illegal_moves:
                                    continue

                                if steps_cancel_out(step6, step7):
                                    continue

                                cube.state = end_step6_state[:]
                                cube.solution = end_step6_solution[:]

                                cube.rotate(step7)
                                lt_state = cube.lt_LFRB_solve_inner_centers_and_oblique_edges.state()

                                if lt_state in states_to_check:
                                    continue

                                solution_pretty = ' '.join(cube.solution)
                                states_to_check[lt_state] = solution_pretty
                                #fh.write("%s:%s\n" % (lt_state, solution_pretty))
                                count += 1

                                end_step7_state = cube.state[:]
                                end_step7_solution = cube.solution[:]


log.info("rotate end  : rotated %d" % count)
log.info("cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps() begin")
steps_for_states = cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps(states_to_check.keys(), exit_on_first_match=False)
log.info("cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps() end")

for (state, steps_to_ida) in steps_for_states.items():
    if steps_to_ida:
        steps_to_here = states_to_check[state]
        print("%s: steps_to_here %s" % (state, steps_to_here))
        print("%s: steps_to_ida  %s\n" % (state, steps_to_ida))
log.info("Finished")

'''
init guts cache of first and last line only....avg left->right range here was about 12 million
2017-06-25 08:07:42,110 find_777_4900.py     INFO: rotate begin: rotated 0
2017-06-25 08:07:54,305 find_777_4900.py     INFO: rotate end  : rotated 155244
2017-06-25 08:07:54,306 find_777_4900.py     INFO: cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps() begin
2017-06-25 08:15:51,421   LookupTable.py     INFO: 7x7x7-step60-LFRB-solve-inner-center-and-oblique-edges: found 69357 states (another 0 were cached, cache has 69357 entries) in 0:07:57.037766
2017-06-25 08:15:51,423 find_777_4900.py     INFO: cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps() end
2017-06-25 08:15:51,455 find_777_4900.py     INFO: Finished


init guts cache of every 1 million lines
2017-06-25 08:46:15,222 find_777_4900.py     INFO: rotate begin: rotated 0
2017-06-25 08:46:28,082 find_777_4900.py     INFO: rotate end  : rotated 155244
2017-06-25 08:46:28,082 find_777_4900.py     INFO: cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps() begin
2017-06-25 08:46:28,165   LookupTable.py     INFO: 7x7x7-step60-LFRB-solve-inner-center-and-oblique-edges find 69357 states, 69357 are not cached
2017-06-25 08:49:17,126   LookupTable.py     INFO: 7x7x7-step60-LFRB-solve-inner-center-and-oblique-edges: found 69357 states (another 0 were cached) in 0:02:48.961506, 41071 guts calls, 14659 avg left->right range, guts_cache has 34 entries
2017-06-25 08:49:17,128 find_777_4900.py     INFO: cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps() end
2017-06-25 08:49:17,168 find_777_4900.py     INFO: Finished


init guts cache of every 64k lines
2017-06-25 09:41:46,975 find_777_4900.py     INFO: rotate begin: rotated 0
2017-06-25 09:41:59,834 find_777_4900.py     INFO: rotate end  : rotated 155244
2017-06-25 09:41:59,834 find_777_4900.py     INFO: cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps() begin
2017-06-25 09:41:59,908   LookupTable.py     INFO: 7x7x7-step60-LFRB-solve-inner-center-and-oblique-edges find 69357 states, 69357 are not cached
2017-06-25 09:43:57,916   LookupTable.py     INFO: 7x7x7-step60-LFRB-solve-inner-center-and-oblique-edges: found 69357 states (another 0 were cached) in 0:01:58.007438, 41071 guts calls, 1612 avg left->right range, guts_cache has 292 entries
2017-06-25 09:43:57,918 find_777_4900.py     INFO: cube.lt_LFRB_solve_inner_centers_and_oblique_edges.steps() end
2017-06-25 09:43:57,947 find_777_4900.py     INFO: Finished


'''

#print("Final Cube")
#cube.print_cube()
#cube.print_solution()
