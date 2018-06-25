#!/usr/bin/env python3

from rubikscubennnsolver import reverse_steps
from rubikscubennnsolver.combinatorial import state_to_rank
from rubikscubennnsolver.RubiksCube666 import RubiksCube666, solved_666
from math import sqrt
from pprint import pformat
import datetime as dt
import json
import logging
import os
import resource
import sys


def convert_lookup_table_to_graph(filename, NUMBER_COMBOS, state_is_hex, bits_to_fill):
    graph = [None] * NUMBER_COMBOS
    moves = []
    state_target = ()

    if '6x6x6' in filename:
        cube = RubiksCube666(solved_666, 'URFDLB')
        cube.lt_init()

        if (filename == 'lookup-table-6x6x6-step01-UD-oblique-edges-stage-left-only.txt' or
            filename == 'lookup-table-6x6x6-step02-UD-oblique-edges-stage-right-only.txt'):
            state_target = ('UUUUxxxxxxxxxxxxxxxxUUUU', )
            moves = cube.lt_UD_oblique_edge_stage.moves_all
        else:
            raise Exception("What moves/state_target for %s?" % filename)

    else:
        raise Exception("What size cube is for %s?" % filename)

    log.info("%s: %d moves, %s" % (filename, len(moves), ' '.join(moves)))

    for state in state_target:
        state_rank = state_to_rank(state)
        log.info("%s: state %s has rank %s" % (filename, state, state_rank))
        edges = []

        for move in moves:
            cube.rotate(move)
            next_state = cube.lt_UD_oblique_edge_stage_left_only.state()
            next_state_rank = state_to_rank(next_state)

            # 730673
            if next_state_rank == state_rank:
                edges.append(None)
            else:
                edges.append(next_state_rank)

            cube.re_init()
        graph[state_rank] = (0, tuple(edges))

    with open(filename, 'r') as fh:
        for (line_number, line) in enumerate(fh):
            (state, steps_to_solve) = line.rstrip().split(':')
            steps_to_solve = steps_to_solve.split()
            cost = len(steps_to_solve)


            if state_is_hex:
                state = str(bin(int(state, 16))[2:]).zfill(bits_to_fill)
                state = state.replace('0', 'x').replace('1', 'U')
            state_rank = state_to_rank(state)
            steps_to_scramble = reverse_steps(steps_to_solve)
            #log.info("%s: state %s has rank %s" % (filename, state, state_rank))

            edges = []

            for move in moves:
                for setup_move in steps_to_scramble:
                    cube.rotate(setup_move)
                cube.rotate(move)

                next_state = cube.lt_UD_oblique_edge_stage_left_only.state()
                next_state_rank = state_to_rank(next_state)

                if next_state_rank == state_rank:
                    edges.append(None)
                else:
                    edges.append(next_state_rank)

                cube.re_init()

            graph[state_rank] = (cost, tuple(edges))
            #if line_number == 3:
            #    log.info("graph:\n%s\n" % pformat(graph))
            #    sys.exit(0)

            if line_number % 1000 == 0:
                log.info("%s %d: state %s has rank %s" % (filename, line_number, state, state_rank))

                #if line_number == 1000:
                #    break

    with open(filename.replace('.txt', '.graph.txt'), 'w') as fh:
        json.dump(graph, fh, indent=4)

    none_count = 0
    for x in range(NUMBER_COMBOS):
        if graph[x] is None:
            none_count += 1

    log.info("%s: has %d entries, %d have content, %d are empty" %
        (filename, len(graph), NUMBER_COMBOS - none_count, none_count))

    return graph


if __name__ == '__main__':
    start_time = dt.datetime.now()

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    convert_lookup_table_to_graph('lookup-table-6x6x6-step01-UD-oblique-edges-stage-left-only.txt', 735741, True, 24)
    convert_lookup_table_to_graph('lookup-table-6x6x6-step02-UD-oblique-edges-stage-right-only.txt', 735741, True, 24)

    end_time = dt.datetime.now()
    print("\nMemory : {:,} bytes".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    print("Time   : %s" % (end_time - start_time))
    print("")
