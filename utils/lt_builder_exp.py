#!/usr/bin/env python3

"""
experiment to see how long it takes to build the 4x4x4 centers staging
lookup tables for a scrambled cube. If you only go 4-deep it takes about
20s.  Going deeper than that chews through too much memory on the workq.
The workq needs to be stored in a file.

We need to build 6 or 7 deep.
"""

from collections import deque
import logging
import os
import sys
from rubikscubennnsolver import reverse_steps
from rubikscubennnsolver.rotate_xxx import rotate_444
from rubikscubennnsolver.RubiksCube444 import (
    moves_4x4x4,
    solved_4x4x4,
    RubiksCube444,
    LookupTableIDA444ULFRBDCentersStage,
    LookupTable444UDCentersStage,
    LookupTable444LRCentersStage,
    LookupTable444FBCentersStage,
)


def build_state_table():
    cube = RubiksCube444('DRFDFRUFDURDDLLUFLDLLBLULFBUUFRBLBFLLUDDUFRBURBBRBDLLDURFFBBRUFUFDRFURBUDLDBDUFFBUDRRLDRBLFBRRLB', 'URFDLB')
    cube.nuke_corners()
    cube.nuke_edges()
    original_state = cube.state[:]

    log.info("cache start")
    for side in (cube.sideU, cube.sideL, cube.sideF, cube.sideR, cube.sideB, cube.sideD):
        for pos in side.center_pos:
            if cube.state[pos] in ('U', 'D'):
                cube.state[pos] = 'U'
            elif cube.state[pos] in ('L', 'R'):
                cube.state[pos] = 'L'
            elif cube.state[pos] in ('F', 'B'):
                cube.state[pos] = 'F'

    cube.lt_UD_centers_stage = LookupTable444UDCentersStage(cube)
    cube.lt_LR_centers_stage = LookupTable444LRCentersStage(cube)
    cube.lt_FB_centers_stage = LookupTable444FBCentersStage(cube)
    lt_ULFRBD_centers_stage = LookupTableIDA444ULFRBDCentersStage(cube)

    workq = deque()
    explored = set()
    UD_explored = {}
    LR_explored = {}
    FB_explored = {}
    count = 0

    for step in moves_4x4x4:
        workq.append(([step,], cube.state[:]))

    while workq:
        (steps, prev_state) = workq.popleft()
        cube.state = rotate_444(prev_state, steps[-1])

        state = lt_ULFRBD_centers_stage.state()
        UD_state = cube.lt_UD_centers_stage.state()
        LR_state = cube.lt_LR_centers_stage.state()
        FB_state = cube.lt_FB_centers_stage.state()

        count += 1

        if count % 100000 == 0:
            UD_count = len(UD_explored)
            LR_count = len(LR_explored)
            FB_count = len(FB_explored)

            log.info("%d UD states, %d LR state, %d FB states, %d on workq" % (UD_count, LR_count, FB_count, len(workq)))

            if UD_count == 735471 and LR_count == 735471 and FB_count == 735471:
                break

        if state in explored:
            continue
        else:
            explored.add(state)
            keep_going = False

            if UD_state not in UD_explored:
                UD_explored[UD_state] = ' '.join(reverse_steps(steps))
                keep_going = True

            if LR_state not in LR_explored:
                LR_explored[LR_state] = ' '.join(reverse_steps(steps))
                keep_going = True

            if FB_state not in FB_explored:
                FB_explored[FB_state] = ' '.join(reverse_steps(steps))
                keep_going = True

            if not keep_going:
                continue

            # Only build the table 4-deep for now
            if len(steps) == 4:
                continue

            prev_step = steps[-1]

            for step in moves_4x4x4:

                # U2 followed by U2 is a no-op
                if step == prev_step and step.endswith("2"):
                    continue

                # U' followed by U is a no-op
                if prev_step.endswith("'") and not step.endswith("'") and step == prev_step[0:-1]:
                    continue

                # U followed by U' is a no-op
                if not prev_step.endswith("'") and step.endswith("'") and step[0:-1] == prev_step:
                    continue

                workq.append((steps + [step,], cube.state[:]))

    log.info("cache end")

    log.info("write start")

    with open('UD_state.txt', 'w') as fh:
        for key in sorted(UD_explored.keys()):
            value = UD_explored[key]
            fh.write("%s:%s\n" % (key, value))

    with open('LR_state.txt', 'w') as fh:
        for key in sorted(LR_explored.keys()):
            value = LR_explored[key]
            fh.write("%s:%s\n" % (key, value))

    with open('FB_state.txt', 'w') as fh:
        for key in sorted(FB_explored.keys()):
            value = FB_explored[key]
            fh.write("%s:%s\n" % (key, value))

    log.info("write end")


if __name__ == '__main__':

    # setup logging
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    build_state_table()
