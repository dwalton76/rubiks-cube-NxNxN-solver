#!/usr/bin/env python3

from rubikscubennnsolver import reverse_steps
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, rotate_444, solved_444
from pprint import pformat
import logging
import sys
import logging


def do_the_needfull():
    cube = RubiksCube444(solved_444, 'URFDLB')
    to_write = []
    to_write_count = 0
    BATCH_SIZE = 100000

    with open("kociemba_strings.txt", "w") as fh_kociemba:
        with open("lookup-table-4x4x4-step31-reduce333-edges.txt.sym", "r") as fh:
            for (line_number, line) in enumerate(fh):
                (state, steps_to_solve) = line.strip().split(":")
                steps_to_solve = steps_to_solve.split()
                steps_to_scramble = reverse_steps(steps_to_solve)

                cube.re_init()
                #if line_number == 100:
                #    cube.print_cube()

                for step in steps_to_scramble:
                    cube.rotate(step)

                # Put the centers back to solved
                for side in list(cube.sides.values()):
                    for pos in side.center_pos:
                        cube.state[pos] = side.name

                ks = cube.get_kociemba_string(True)
                to_write.append(ks)
                to_write_count += 1

                if to_write_count == BATCH_SIZE:
                    fh_kociemba.write("\n".join(to_write) + "\n")
                    to_write = []
                    to_write_count = 0
                    #print(steps_to_scramble)
                    #cube.print_cube()
                    #break
                    log.info(line_number)

            if to_write_count:
                fh_kociemba.write("\n".join(to_write) + "\n")
                to_write = []
                to_write_count = 0


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    do_the_needfull()
