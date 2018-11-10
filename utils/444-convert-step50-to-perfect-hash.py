#!/usr/bin/env python3

from rubikscubennnsolver.RubiksCube444 import moves_444
from rubikscubennnsolver.RubiksCube444Misc import (
    high_edges_444,
    low_edges_444,
    highlow_edge_mapping_combinations,
    highlow_edge_values,
    step51_index,
    step52_index,
)
import sys


moves_444_abbrv = {
    "U" : '0',
    "U'" : '1',
    "U2" : '2',
    "Uw" : '3',
    "Uw'" : '4',
    "Uw2" : '5',

    "L"  : '6',
    "L'" : '7',
    "L2" : '8',
    "Lw" : '9',
    "Lw'" : 'a',
    "Lw2" : 'b',

    "F"  : 'c',
    "F'" : 'd',
    "F2" : 'e',
    "Fw" : 'f',
    "Fw'" : 'g',
    "Fw2" : 'h',

    "R"  : 'i',
    "R'" : 'j',
    "R2" : 'k',
    "Rw" : 'l',
    "Rw'" : 'm',
    "Rw2" : 'n',

    "B"  : 'o',
    "B'" : 'p',
    "B2" : 'q',
    "Bw" : 'r',
    "Bw'" : 's',
    "Bw2" : 't',

    "D"  : 'u',
    "D'" : 'v',
    "D2" : 'w',
    "Dw" : 'x',
    "Dw'" : 'y',
    "Dw2" : 'z',
}

for (move, abbr) in moves_444_abbrv.items():
    print('        "{}" : "{}",'.format(abbr, move))

# dwalton
sys.exit(0)

data = [0] * 50803200
with open("lookup-table-4x4x4-step50.txt", "r") as fh:
    for (index, line) in enumerate(fh):
        (state, steps) = line.strip().split(":")
        centers_state = state[0:24]
        edges_state = state[24:]

        centers_index = step52_index[centers_state]
        edges_index = step51_index[edges_state]
        line_number = (centers_index * 20160) + edges_index
        first_step = steps.split()[0]
        data[line_number] = moves_444_abbrv[first_step]

        if index % 1000000 == 0:
            print(index)

with open("lookup-table-4x4x4-step50-perfect-hash.txt", "w") as fh:
    fh.write("".join(data))
