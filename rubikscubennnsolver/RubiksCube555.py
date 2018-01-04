#!/usr/bin/env python3

from collections import deque
from pprint import pformat
from random import randint
from rubikscubennnsolver import RubiksCube, ImplementThis
from rubikscubennnsolver.RubiksSide import Side, SolveError
from rubikscubennnsolver.RubiksCube333 import moves_3x3x3
from rubikscubennnsolver.RubiksCube444 import RubiksCube444, moves_4x4x4, solved_4x4x4
from rubikscubennnsolver.RubiksCube444Misc import tsai_edge_mapping_combinations
from rubikscubennnsolver.LookupTable import (
    get_best_entry,
    get_characters_common_count,
    LookupTable,
    LookupTableIDA,
    LookupTableAStar
)

from rubikscubennnsolver.rotate_xxx import rotate_555
import datetime as dt
import logging
import math
import os
import random
import re
import subprocess
import sys

log = logging.getLogger(__name__)
'''
baseline

35 steps to solve centers
71 steps to group edges
21 steps to solve 3x3x3
127 steps total

'''

moves_5x5x5 = moves_4x4x4
solved_5x5x5 = 'UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB'

centers_555 = (
    7, 8, 9, 12, 13, 14, 17, 18, 19,
    32, 33, 34, 37, 38, 39, 42, 43, 44,
    57, 58, 59, 62, 63, 64, 67, 68, 69,
    82, 83, 84, 87, 88, 89, 92, 93, 94,
    107, 108, 109, 112, 113, 114, 117, 118, 119,
    132, 133, 134, 137, 138, 139, 142, 143, 144
)

LFRB_centers_555 = (
    32, 33, 34, 37, 38, 39, 42, 43, 44,
    57, 58, 59, 62, 63, 64, 67, 68, 69,
    82, 83, 84, 87, 88, 89, 92, 93, 94,
    107, 108, 109, 112, 113, 114, 117, 118, 119
)

wings_555 = (
    2, 3, 4, 6, 10, 11, 15, 16, 20, 22, 23, 24,                # Upper
    31, 35, 36, 40, 41, 45,                                    # Left
    81, 85, 86, 90, 91, 95,                                    # Right
    127, 128, 129, 131, 135, 136, 140, 141, 145, 147, 148, 149 # Down
)

wings_555 = (
    2, 3, 4,       # Upper
    6, 11, 16,
    10, 15, 20,
    22, 23, 24,
    31, 36, 41,    # Left
    35, 40, 45,
    81, 86, 91,    # Right
    85, 90, 95,
    127, 128, 129, # Down
    131, 136, 141,
    135, 140, 145,
    147, 148, 149
)


wing_str_map = {
    'UB' : 'UB',
    'BU' : 'UB',
    'UL' : 'UL',
    'LU' : 'UL',
    'UR' : 'UR',
    'RU' : 'UR',
    'UF' : 'UF',
    'FU' : 'UF',
    'LB' : 'LB',
    'BL' : 'LB',
    'LF' : 'LF',
    'FL' : 'LF',
    'RB' : 'RB',
    'BR' : 'RB',
    'RF' : 'RF',
    'FR' : 'RF',
    'DB' : 'DB',
    'BD' : 'DB',
    'DL' : 'DL',
    'LD' : 'DL',
    'DR' : 'DR',
    'RD' : 'DR',
    'DF' : 'DF',
    'FD' : 'DF',
}


def get_edges_paired_binary_signature(state):
    """
    The facelets are numbered:
                         --- 002 003 004 ---
                         006 --- --- --- 010
                         011 --- --- --- 015
                         016 --- --- --- 020
                         --- 022 023 024 ---

    --- 027 028 029 ---  --- 052 053 054 ---  --- 077 078 079 ---  --- 102 103 104 ---
    031 --- --- --- 035  056 --- --- --- 060  081 --- --- --- 085  106 --- --- --- 110
    036 --- --- --- 040  061 --- --- --- 065  086 --- --- --- 090  111 --- --- --- 115
    041 --- --- --- 045  066 --- --- --- 070  091 --- --- --- 095  116 --- --- --- 120
    --- 047 048 049 ---  --- 072 073 074 ---  --- 097 098 099 ---  --- 122 123 124 ---

                         --- 127 128 129 ---
                         131 --- --- --- 135
                         136 --- --- --- 140
                         141 --- --- --- 145
                         --- 147 148 149 ---


                           ---  0   o   1  ---
                            2  --- --- ---  3
                            p  --- --- ---  q
                            4  --- --- ---  5
                           ---  6   r   7  ---

    ---  2   p   4  ---    ---  6   r   7  ---    ---  5   q   3  ---    ---  1   o   0  ---
     8  --- --- ---  9      9  --- --- ---  c      c  --- --- ---  d      d  --- --- ---  8
     s  --- --- ---  t      t  --- --- ---  u      u  --- --- ---  v      v  --- --- ---  s
     a  --- --- ---  b      b  --- --- ---  e      e  --- --- ---  f      f  --- --- ---  a
    ---  k   x   i  ---    ---  g   w   h  ---    ---  j   y   l  ---    ---  n   z   m  ---

                           ---  g   w   h  ---
                            i  --- --- ---  j
                            x  --- --- ---  y
                            k  --- --- ---  l
                           ---  m   z   n  ---

    'state' is the relationship of the outside wings to their midge.  For the "high" wings
    the uppercase format of the midge location is used to represent the state for that "high"
    wing.  For "low" wings the lowercase format of the midge location is used to represent
    the state of that "low" wing.

    So if the (2,3,4) edge is paired the state string for those three wings would be OOo.

    state: OOopPPQQqrRRsSSTTtuUUVVvWWwxXXYYyzZZ
    index: 000000000011111111112222222222333333
           012345678901234567890123456789012345

    All are paired
    >>> get_edges_paired_binary_signature('OOopPPQQqrRRsSSTTtuUUVVvWWwxXXYYyzZZ')
    '111111111111111111111111'

    None are paired
    >>> get_edges_paired_binary_signature('UoTqpQZqsxRzRsWSTurupoVYXWVvxtPYOyZw')
    '000000000000000000000000'
    """
    result = []

    # state: OOopPPQQqrRRsSSTTtuUUVVvWWwxXXYYyzZZ
    # index: 000000000011111111112222222222333333
    #        012345678901234567890123456789012345

    # Upper/Back high wing
    if ((state[0] == 'O' and state[1] == 'O') or
        (state[0] == 'o' and state[1] == 'o')):
        result.append('1')
    else:
        result.append('0')

    # Upper/Back low wing
    if ((state[2] == 'o' and state[1] == 'O') or
        (state[2] == 'O' and state[1] == 'o')):
        result.append('1')
    else:
        result.append('0')


    # Upper/Left low wing
    if ((state[3] == 'p' and state[4] == 'P') or
        (state[3] == 'P' and state[4] == 'p')):
        result.append('1')
    else:
        result.append('0')

    # Upper/Left high wing
    if ((state[5] == 'P' and state[4] == 'P') or
        (state[5] == 'p' and state[4] == 'p')):
        result.append('1')
    else:
        result.append('0')


    # Upper/Right high wing
    if ((state[6] == 'Q' and state[7] == 'Q') or
        (state[6] == 'q' and state[7] == 'q')):
        result.append('1')
    else:
        result.append('0')

    # Upper/Right low wing
    if ((state[8] == 'q' and state[7] == 'Q') or
        (state[8] == 'Q' and state[7] == 'q')):
        result.append('1')
    else:
        result.append('0')


    # Upper/Down low wing
    if ((state[9] == 'r' and state[10] == 'R') or
        (state[9] == 'R' and state[10] == 'r')):
        result.append('1')
    else:
        result.append('0')

    # Upper/Down high wing
    if ((state[11] == 'R' and state[10] == 'R') or
        (state[11] == 'r' and state[10] == 'r')):
        result.append('1')
    else:
        result.append('0')


    # Left/Back low wing
    if ((state[12] == 's' and state[13] == 'S') or
        (state[12] == 'S' and state[13] == 's')):
        result.append('1')
    else:
        result.append('0')

    # Left/Back high wing
    if ((state[14] == 'S' and state[13] == 'S') or
        (state[14] == 's' and state[13] == 's')):
        result.append('1')
    else:
        result.append('0')


    # Left/Right high wing
    if ((state[15] == 'T' and state[16] == 'T') or
        (state[15] == 't' and state[16] == 't')):
        result.append('1')
    else:
        result.append('0')

    # Left/Right low wing
    if ((state[17] == 't' and state[16] == 'T') or
        (state[17] == 'T' and state[16] == 't')):
        result.append('1')
    else:
        result.append('0')


    # Right/Front low wing
    if ((state[18] == 'u' and state[19] == 'U') or
        (state[18] == 'U' and state[19] == 'u')):
        result.append('1')
    else:
        result.append('0')

    # Right/Front high wing
    if ((state[20] == 'U' and state[19] == 'U') or
        (state[20] == 'u' and state[19] == 'u')):
        result.append('1')
    else:
        result.append('0')


    # Right/Back high wing
    if ((state[21] == 'V' and state[22] == 'V') or
        (state[21] == 'v' and state[22] == 'v')):
        result.append('1')
    else:
        result.append('0')

    # Right/Back low wing
    if ((state[23] == 'v' and state[22] == 'V') or
        (state[23] == 'V' and state[22] == 'v')):
        result.append('1')
    else:
        result.append('0')


    # Down/Front high wing
    if ((state[24] == 'W' and state[25] == 'W') or
        (state[24] == 'w' and state[25] == 'w')):
        result.append('1')
    else:
        result.append('0')

    # Down/Front low wing
    if ((state[26] == 'w' and state[25] == 'W') or
        (state[26] == 'W' and state[25] == 'w')):
        result.append('1')
    else:
        result.append('0')


    # Down/Left low wing
    if ((state[27] == 'x' and state[28] == 'X') or
        (state[27] == 'X' and state[28] == 'x')):
        result.append('1')
    else:
        result.append('0')

    # Down/Left high wing
    if ((state[29] == 'X' and state[28] == 'X') or
        (state[29] == 'x' and state[28] == 'x')):
        result.append('1')
    else:
        result.append('0')


    # Down/Right high wing
    if ((state[30] == 'Y' and state[31] == 'Y') or
        (state[30] == 'y' and state[31] == 'y')):
        result.append('1')
    else:
        result.append('0')

    # Down/Right low wing
    if ((state[32] == 'y' and state[31] == 'Y') or
        (state[32] == 'Y' and state[31] == 'y')):
        result.append('1')
    else:
        result.append('0')


    # Down/Back low wing
    if ((state[33] == 'z' and state[34] == 'Z') or
        (state[33] == 'Z' and state[34] == 'z')):
        result.append('1')
    else:
        result.append('0')

    # Down/Back high wing
    if ((state[35] == 'Z' and state[34] == 'Z') or
        (state[35] == 'z' and state[34] == 'z')):
        result.append('1')
    else:
        result.append('0')

    return ''.join(result)



class LookupTable555UDTCenterStage(LookupTable):
    """
    There are 4 T-centers and 4 X-centers so (24!/(8! * 16!))^2 is 540,917,591,841
    We cannot build a table that large so we will build it 7 moves deep and use
    IDA with T-centers and X-centers as our prune tables. Both the T-centers and
    X-centers prune tables will have 735,471 entries, 735,471/540,917,591,841
    is 0.000 001 3596729171 which is a decent percentage for IDA.

    lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.txt
    ============================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 66 entries (0 percent, 13.20x previous step)
    3 steps has 900 entries (0 percent, 13.64x previous step)
    4 steps has 9,626 entries (1 percent, 10.70x previous step)
    5 steps has 80,202 entries (10 percent, 8.33x previous step)
    6 steps has 329,202 entries (44 percent, 4.10x previous step)
    7 steps has 302,146 entries (41 percent, 0.92x previous step)
    8 steps has 13,324 entries (1 percent, 0.04x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step11-UD-centers-stage-t-center-only.txt',
            '174000000000ba',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            'x', parent_state[8], 'x',
            parent_state[12], parent_state[13], parent_state[14],
            'x', parent_state[18], 'x',

            # Left
            'x', parent_state[33], 'x',
            parent_state[37], parent_state[38], parent_state[39],
            'x', parent_state[43], 'x',

            # Front
            'x', parent_state[58], 'x',
            parent_state[62], parent_state[63], parent_state[64],
            'x', parent_state[68], 'x',

            # Right
            'x', parent_state[83], 'x',
            parent_state[87], parent_state[88], parent_state[89],
            'x', parent_state[93], 'x',

            # Back
            'x', parent_state[108], 'x',
            parent_state[112], parent_state[113], parent_state[114],
            'x', parent_state[118], 'x',

            # Down
            'x', parent_state[133], 'x',
            parent_state[137], parent_state[138], parent_state[139],
            'x', parent_state[143], 'x'
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable555UDXCenterStage(LookupTable):
    """
    lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.txt
    ============================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 82 entries (0 percent, 16.40x previous step)
    3 steps has 1,206 entries (0 percent, 14.71x previous step)
    4 steps has 14,116 entries (1 percent, 11.70x previous step)
    5 steps has 123,404 entries (16 percent, 8.74x previous step)
    6 steps has 422,508 entries (57 percent, 3.42x previous step)
    7 steps has 173,254 entries (23 percent, 0.41x previous step)
    8 steps has 896 entries (0 percent, 0.01x previous step)

    Total: 735,471 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step12-UD-centers-stage-x-center-only.txt',
            '2aa00000000155',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            parent_state[7], 'x', parent_state[9],
            'x', parent_state[13], 'x',
            parent_state[17], 'x', parent_state[19],

            # Left
            parent_state[32], 'x', parent_state[34],
            'x', parent_state[38], 'x',
            parent_state[42], 'x', parent_state[44],

            # Front
            parent_state[57], 'x', parent_state[59],
            'x', parent_state[63], 'x',
            parent_state[67], 'x', parent_state[69],

            # Right
            parent_state[82], 'x', parent_state[84],
            'x', parent_state[88], 'x',
            parent_state[92], 'x', parent_state[94],

            # Back
            parent_state[107], 'x', parent_state[109],
            'x', parent_state[113], 'x',
            parent_state[117], 'x', parent_state[119],

            # Down
            parent_state[132], 'x', parent_state[134],
            'x', parent_state[138], 'x',
            parent_state[142], 'x', parent_state[144]
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA555UDCentersStage(LookupTableIDA):
    """
    lookup-table-5x5x5-step10-UD-centers-stage.txt
    ==============================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 98 entries (0 percent, 19.60x previous step)
    3 steps has 2,036 entries (0 percent, 20.78x previous step)
    4 steps has 41,096 entries (0 percent, 20.18x previous step)
    5 steps has 824,950 entries (4 percent, 20.07x previous step)
    6 steps has 16,300,291 entries (94 percent, 19.76x previous step)

    Total: 17,168,476 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step10-UD-centers-stage.txt',
            '3fe000000001ff', # UUUUUUUUUxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxUUUUUUUUU
            moves_5x5x5,
            (), # illegal_moves

            # prune tables
            (parent.lt_UD_T_centers_stage,
             parent.lt_UD_X_centers_stage),
            linecount=17168476)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Upper
            parent_state[7], parent_state[8], parent_state[9],
            parent_state[12], parent_state[13], parent_state[14],
            parent_state[17], parent_state[18], parent_state[19],

            # Left
            parent_state[32], parent_state[33], parent_state[34],
            parent_state[37], parent_state[38], parent_state[39],
            parent_state[42], parent_state[43], parent_state[44],

            # Front
            parent_state[57], parent_state[58], parent_state[59],
            parent_state[62], parent_state[63], parent_state[64],
            parent_state[67], parent_state[68], parent_state[69],

            # Right
            parent_state[82], parent_state[83], parent_state[84],
            parent_state[87], parent_state[88], parent_state[89],
            parent_state[92], parent_state[93], parent_state[94],

            # Back
            parent_state[107], parent_state[108], parent_state[109],
            parent_state[112], parent_state[113], parent_state[114],
            parent_state[117], parent_state[118], parent_state[119],

            # Down
            parent_state[132], parent_state[133], parent_state[134],
            parent_state[137], parent_state[138], parent_state[139],
            parent_state[142], parent_state[143], parent_state[144]
        ]

        result = ['1' if x in ('U', 'D') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable555LRTCenterStage(LookupTable):

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step103-LR-centers-stage-t-center-only.txt',
            '000ba002e80000',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            'x', parent_state[8], 'x',
            parent_state[12], parent_state[13], parent_state[14],
            'x', parent_state[18], 'x',

            # Left
            'x', parent_state[33], 'x',
            parent_state[37], parent_state[38], parent_state[39],
            'x', parent_state[43], 'x',

            # Front
            'x', parent_state[58], 'x',
            parent_state[62], parent_state[63], parent_state[64],
            'x', parent_state[68], 'x',

            # Right
            'x', parent_state[83], 'x',
            parent_state[87], parent_state[88], parent_state[89],
            'x', parent_state[93], 'x',

            # Back
            'x', parent_state[108], 'x',
            parent_state[112], parent_state[113], parent_state[114],
            'x', parent_state[118], 'x',

            # Down
            'x', parent_state[133], 'x',
            parent_state[137], parent_state[138], parent_state[139],
            'x', parent_state[143], 'x'
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable555LRXCenterStage(LookupTable):
    """
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step104-LR-centers-stage-x-center-only.txt',
            '00155005540000',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            parent_state[7], 'x', parent_state[9],
            'x', parent_state[13], 'x',
            parent_state[17], 'x', parent_state[19],

            # Left
            parent_state[32], 'x', parent_state[34],
            'x', parent_state[38], 'x',
            parent_state[42], 'x', parent_state[44],

            # Front
            parent_state[57], 'x', parent_state[59],
            'x', parent_state[63], 'x',
            parent_state[67], 'x', parent_state[69],

            # Right
            parent_state[82], 'x', parent_state[84],
            'x', parent_state[88], 'x',
            parent_state[92], 'x', parent_state[94],

            # Back
            parent_state[107], 'x', parent_state[109],
            'x', parent_state[113], 'x',
            parent_state[117], 'x', parent_state[119],

            # Down
            parent_state[132], 'x', parent_state[134],
            'x', parent_state[138], 'x',
            parent_state[142], 'x', parent_state[144]
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable555FBTCenterStage(LookupTable):

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step105-FB-centers-stage-t-center-only.txt',
            '000005d0017400',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            'x', parent_state[8], 'x',
            parent_state[12], parent_state[13], parent_state[14],
            'x', parent_state[18], 'x',

            # Left
            'x', parent_state[33], 'x',
            parent_state[37], parent_state[38], parent_state[39],
            'x', parent_state[43], 'x',

            # Front
            'x', parent_state[58], 'x',
            parent_state[62], parent_state[63], parent_state[64],
            'x', parent_state[68], 'x',

            # Right
            'x', parent_state[83], 'x',
            parent_state[87], parent_state[88], parent_state[89],
            'x', parent_state[93], 'x',

            # Back
            'x', parent_state[108], 'x',
            parent_state[112], parent_state[113], parent_state[114],
            'x', parent_state[118], 'x',

            # Down
            'x', parent_state[133], 'x',
            parent_state[137], parent_state[138], parent_state[139],
            'x', parent_state[143], 'x'
        ]

        result = ['1' if x in ('F', 'B') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable555FBXCenterStage(LookupTable):
    """
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step106-FB-centers-stage-x-center-only.txt',
            '00000aa802aa00',
            linecount=735471)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            parent_state[7], 'x', parent_state[9],
            'x', parent_state[13], 'x',
            parent_state[17], 'x', parent_state[19],

            # Left
            parent_state[32], 'x', parent_state[34],
            'x', parent_state[38], 'x',
            parent_state[42], 'x', parent_state[44],

            # Front
            parent_state[57], 'x', parent_state[59],
            'x', parent_state[63], 'x',
            parent_state[67], 'x', parent_state[69],

            # Right
            parent_state[82], 'x', parent_state[84],
            'x', parent_state[88], 'x',
            parent_state[92], 'x', parent_state[94],

            # Back
            parent_state[107], 'x', parent_state[109],
            'x', parent_state[113], 'x',
            parent_state[117], 'x', parent_state[119],

            # Down
            parent_state[132], 'x', parent_state[134],
            'x', parent_state[138], 'x',
            parent_state[142], 'x', parent_state[144]
        ]

        result = ['1' if x in ('F', 'B') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA555AllCenterStage(LookupTableIDA):
    """
    lookup-table-5x5x5-step100-ALL-centers-stage.txt
    ================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 147 entries (0 percent, 21.00x previous step)
    3 steps has 3,054 entries (0 percent, 20.78x previous step)
    4 steps has 65,520 entries (4 percent, 21.45x previous step)
    5 steps has 1,467,630 entries (95 percent, 22.40x previous step)

    Total: 1,536,358 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step100-ALL-centers-stage.txt',
            'UUUUUUUUULLLLLLLLLFFFFFFFFFLLLLLLLLLFFFFFFFFFUUUUUUUUU',
            moves_5x5x5,
            (), # illegal_moves

            # prune tables
            (parent.lt_UD_T_centers_stage,
             parent.lt_UD_X_centers_stage,
             parent.lt_LR_T_centers_stage,
             parent.lt_LR_X_centers_stage,
             parent.lt_FB_T_centers_stage,
             parent.lt_FB_X_centers_stage),
            linecount=1536358)

    def state(self):
        parent_state = self.parent.state

        tmp_result = [
            # Upper
            parent_state[7], parent_state[8], parent_state[9],
            parent_state[12], parent_state[13], parent_state[14],
            parent_state[17], parent_state[18], parent_state[19],

            # Left
            parent_state[32], parent_state[33], parent_state[34],
            parent_state[37], parent_state[38], parent_state[39],
            parent_state[42], parent_state[43], parent_state[44],

            # Front
            parent_state[57], parent_state[58], parent_state[59],
            parent_state[62], parent_state[63], parent_state[64],
            parent_state[67], parent_state[68], parent_state[69],

            # Right
            parent_state[82], parent_state[83], parent_state[84],
            parent_state[87], parent_state[88], parent_state[89],
            parent_state[92], parent_state[93], parent_state[94],

            # Back
            parent_state[107], parent_state[108], parent_state[109],
            parent_state[112], parent_state[113], parent_state[114],
            parent_state[117], parent_state[118], parent_state[119],

            # Down
            parent_state[132], parent_state[133], parent_state[134],
            parent_state[137], parent_state[138], parent_state[139],
            parent_state[142], parent_state[143], parent_state[144]
        ]

        result = []

        for x in tmp_result:
            if x in ('U', 'D'):
                result.append('U')
            elif x in ('L', 'R'):
                result.append('L')
            elif x in ('F', 'B'):
                result.append('F')

        return ''.join(result)


class LookupTable555LRXCentersStage(LookupTable):
    """
    lookup-table-5x5x5-step21-LR-centers-stage-x-center-only.txt
    ============================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
    3 steps has 234 entries (1 percent, 8.07x previous step)
    4 steps has 1,246 entries (9 percent, 5.32x previous step)
    5 steps has 4,466 entries (34 percent, 3.58x previous step)
    6 steps has 6,236 entries (48 percent, 1.40x previous step)
    7 steps has 656 entries (5 percent, 0.11x previous step)

    Total: 12,870 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step21-LR-centers-stage-x-center-only.txt',
            'aa802aa00',
            linecount=12870)

    def state(self):
        parent_state = self.parent.state

        result = [
            # Left
            parent_state[32], 'x', parent_state[34],
            'x', parent_state[38], 'x',
            parent_state[42], 'x', parent_state[44],

            # Front
            parent_state[57], 'x', parent_state[59],
            'x', parent_state[63], 'x',
            parent_state[67], 'x', parent_state[69],

            # Right
            parent_state[82], 'x', parent_state[84],
            'x', parent_state[88], 'x',
            parent_state[92], 'x', parent_state[94],

            # Back
            parent_state[107], 'x', parent_state[109],
            'x', parent_state[113], 'x',
            parent_state[117], 'x', parent_state[119]]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable555LRTCentersStage(LookupTable):
    """
    lookup-table-5x5x5-step22-LR-centers-stage-t-center-only.txt
    ============================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 25 entries (0 percent, 8.33x previous step)
    3 steps has 210 entries (1 percent, 8.40x previous step)
    4 steps has 722 entries (5 percent, 3.44x previous step)
    5 steps has 1,752 entries (13 percent, 2.43x previous step)
    6 steps has 4,033 entries (31 percent, 2.30x previous step)
    7 steps has 4,014 entries (31 percent, 1.00x previous step)
    8 steps has 1,977 entries (15 percent, 0.49x previous step)
    9 steps has 134 entries (1 percent, 0.07x previous step)

    Total: 12,870 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step22-LR-centers-stage-t-center-only.txt',
            '5d0017400',
            linecount=12870)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Left
            'x', parent_state[33], 'x',
            parent_state[37], parent_state[38], parent_state[39],
            'x', parent_state[43], 'x',

            # Front
            'x', parent_state[58], 'x',
            parent_state[62], parent_state[63], parent_state[64],
            'x', parent_state[68], 'x',

            # Right
            'x', parent_state[83], 'x',
            parent_state[87], parent_state[88], parent_state[89],
            'x', parent_state[93], 'x',

            # Back
            'x', parent_state[108], 'x',
            parent_state[112], parent_state[113], parent_state[114],
            'x', parent_state[118], 'x']

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA555LRCentersStage(LookupTableIDA):
    """
    Stage LR centers to sides L or R, this will automagically stage
    the F and B centers to sides F or B. 4 T-centers and 4 X-centers
    on 4 sides (ignore U and D since they are solved) but we treat
    L and R as one color so 8! on the bottom.
    (16!/(8! * 8!)))^2 is 165,636,900

    The copy of this table that is checked in to the repo only goes to 7-deep thus the need for IDA.
    If you build the table out the entire way we'll never use the prune tables and you will get
    a hit on the first lookup.

    12,870/165,636,900 is 0.000 0777 so this will be a fast IDA search

    lookup-table-5x5x5-step20-LR-centers-stage.txt
    ==============================================
    1 steps has 3 entries (0 percent)
    2 steps has 33 entries (0 percent)
    3 steps has 374 entries (0 percent)
    4 steps has 3,838 entries (0 percent)
    5 steps has 39,254 entries (0 percent)
    6 steps has 387,357 entries (0 percent)
    7 steps has 3,374,380 entries (2 percent)
    8 steps has 20,851,334 entries (12 percent)
    9 steps has 65,556,972 entries (39 percent)
    10 steps has 66,986,957 entries (40 percent)
    11 steps has 8,423,610 entries (5 percent)
    12 steps has 12,788 entries (0 percent)

    Total: 165,636,900 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step20-LR-centers-stage.txt',
            'ff803fe00', # LLLLLLLLLxxxxxxxxxLLLLLLLLLxxxxxxxxx
            moves_5x5x5,
            ("Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'"), # illegal moves

            # prune tables
            (parent.lt_LR_centers_stage_x_center_only,
             parent.lt_LR_centers_stage_t_center_only),
            linecount=3805239)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Left
            parent_state[32], parent_state[33], parent_state[34],
            parent_state[37], parent_state[38], parent_state[39],
            parent_state[42], parent_state[43], parent_state[44],

            # Front
            parent_state[57], parent_state[58], parent_state[59],
            parent_state[62], parent_state[63], parent_state[64],
            parent_state[67], parent_state[68], parent_state[69],

            # Right
            parent_state[82], parent_state[83], parent_state[84],
            parent_state[87], parent_state[88], parent_state[89],
            parent_state[92], parent_state[93], parent_state[94],

            # Back
            parent_state[107], parent_state[108], parent_state[109],
            parent_state[112], parent_state[113], parent_state[114],
            parent_state[117], parent_state[118], parent_state[119]
        ]

        result = ['1' if x in ('L', 'R') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable555TsaiPhase2EdgesOrient(LookupTable):
    """
    lookup-table-5x5x5-step41-tsai-phase2-edges-orient.txt
    ======================================================
    1 steps has 3 entries (0 percent, 0.00x previous step)
    2 steps has 29 entries (0 percent, 9.67x previous step)
    3 steps has 278 entries (0 percent, 9.59x previous step)
    4 steps has 1,934 entries (0 percent, 6.96x previous step)
    5 steps has 15,640 entries (0 percent, 8.09x previous step)
    6 steps has 124,249 entries (4 percent, 7.94x previous step)
    7 steps has 609,241 entries (22 percent, 4.90x previous step)
    8 steps has 1,224,098 entries (45 percent, 2.01x previous step)
    9 steps has 688,124 entries (25 percent, 0.56x previous step)
    10 steps has 40,560 entries (1 percent, 0.06x previous step)

    Total: 2,704,156 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step41-tsai-phase2-edges-orient.txt',
            '995a665a6699',
            linecount=2704156)

    def state(self):
        return self.parent.tsai_phase2_orient_edges_state([], return_hex=True)


class LookupTable555TsaiPhase2LRCenters(LookupTable):
    """
    lookup-table-5x5x5-step42-tsai-phase2-L-centers-solve.txt
    =========================================================
    1 steps has 5 entries (0 percent, 0.00x previous step)
    2 steps has 22 entries (0 percent, 4.40x previous step)
    3 steps has 82 entries (1 percent, 3.73x previous step)
    4 steps has 292 entries (5 percent, 3.56x previous step)
    5 steps has 986 entries (20 percent, 3.38x previous step)
    6 steps has 2,001 entries (40 percent, 2.03x previous step)
    7 steps has 1,312 entries (26 percent, 0.66x previous step)
    8 steps has 200 entries (4 percent, 0.15x previous step)

    Total: 4,900 entries
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step42-tsai-phase2-L-centers-solve.txt',
            '001ff000000000',
            linecount=4900)

    def state(self):
        parent_state = self.parent.state
        result = ''.join(['1' if parent_state[x] == 'L' else '0' for x in centers_555])

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTable555TsaiPhase2(LookupTableIDA):
    """
    Stage LR centers and do EO

    lookup-table-5x5x5-step40-tsai-phase2.txt
    =========================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 63 entries (0 percent, 9.00x previous step)
    3 steps has 706 entries (0 percent, 11.21x previous step)
    4 steps has 7,338 entries (0 percent, 10.39x previous step)
    5 steps has 78,620 entries (0 percent, 10.71x previous step)
    6 steps has 880,024 entries (8 percent, 11.19x previous step)
    7 steps has 9,578,439 entries (90 percent, 10.88x previous step)

    Total: 10,545,197 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step40-tsai-phase2.txt',
            'UxxUUxxUxUxLLLULLLULLLxUxxUUxxUUxxUxRRRURRRURRRxUxxUUxxUUxUxxUUxxU',
            moves_5x5x5,

            # illegal moves
            ("Rw", "Rw'", "Lw", "Lw'",
             "Fw", "Fw'", "Bw", "Bw'",
             "Uw", "Uw'", "Dw", "Dw'"),

            # prune tables
            (parent.lt_tsai_phase2_edges_orient,
             parent.lt_tsai_phase2_LR_centers),

            linecount=966758)

    def state(self):
        self.edge_mapping = {}
        parent_state = self.parent.state
        orient_edge_state = self.parent.tsai_phase2_orient_edges_state(self.edge_mapping, return_hex=False)

        # tsai_phase2_orient_edges_staten returns high edges as U and
        # low edges as D so we can print them but for the lookup table
        # low edges are x.  This was done so the lookup-table-5x5x5-step41-tsai-phase2-edges-orient.txt
        # table could be stored in hex.
        orient_edge_state = orient_edge_state.replace('D', 'x')

        # Return the state of the edges plus the LR centers
        result = []
        result.append(orient_edge_state[0:11]) # takes us up to square 31 (inclusive)

        # L centers start here
        result.append(parent_state[32])
        result.append(parent_state[33])
        result.append(parent_state[34])
        result.append(orient_edge_state[11]) # 35
        result.append(parent_state[37])
        result.append(parent_state[38])
        result.append(parent_state[39])
        result.append(orient_edge_state[12]) # 41
        result.append(parent_state[42])
        result.append(parent_state[43])
        result.append(parent_state[44])

        result.append(orient_edge_state[13:27]) # 81
        result.append(parent_state[82])
        result.append(parent_state[83])
        result.append(parent_state[84])
        result.append(orient_edge_state[27]) # 85
        result.append(parent_state[87])
        result.append(parent_state[88])
        result.append(parent_state[89])
        result.append(orient_edge_state[28]) # 91
        result.append(parent_state[92])
        result.append(parent_state[93])
        result.append(parent_state[94])
        result.append(orient_edge_state[29:]) # 95
        result = ''.join(result)
        return result


class LookupTable555TsaiPhase3LFCenters(LookupTable):
    """
    lookup-table-5x5x5-step51-tsai-phase3-LF-centers-solve.txt
    ==========================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 55 entries (0 percent, 7.86x previous step)
    3 steps has 400 entries (0 percent, 7.27x previous step)
    4 steps has 2538 entries (0 percent, 6.34x previous step)
    5 steps has 14184 entries (0 percent, 5.59x previous step)
    6 steps has 69225 entries (3 percent, 4.88x previous step)
    7 steps has 252240 entries (11 percent, 3.64x previous step)
    8 steps has 604827 entries (28 percent, 2.40x previous step)
    9 steps has 693234 entries (32 percent, 1.15x previous step)
    10 steps has 390310 entries (18 percent, 0.56x previous step)
    11 steps has 87692 entries (4 percent, 0.22x previous step)
    12 steps has 2088 entries (0 percent, 0.02x previous step)

    Total: 2116800 entries
    """
    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step51-tsai-phase3-LF-centers-solve.txt',
            'LLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBB',
            linecount=2116800)

    def state(self):
        parent_state = self.parent.state
        result = ''.join([parent_state[x] for x in LFRB_centers_555])
        return result


class LookupTable555TsaiPhase3LFCenters(LookupTable):
    """
    lookup-table-5x5x5-step52-tsai-phase3-pair-four-edges-outside.txt
    =================================================================
    1 steps has 4 entries (0 percent, 0.00x previous step)
    2 steps has 27 entries (0 percent, 6.75x previous step)
    3 steps has 216 entries (0 percent, 8.00x previous step)
    4 steps has 1,418 entries (0 percent, 6.56x previous step)
    5 steps has 9,623 entries (0 percent, 6.79x previous step)
    6 steps has 63,448 entries (1 percent, 6.59x previous step)
    7 steps has 365,270 entries (6 percent, 5.76x previous step)
    8 steps has 1,548,382 entries (26 percent, 4.24x previous step)
    9 steps has 3,061,324 entries (52 percent, 1.98x previous step)
    10 steps has 830,336 entries (14 percent, 0.27x previous step)
    11 steps has 552 entries (0 percent, 0.00x previous step)

    Total: 5,880,600 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step52-tsai-phase3-pair-four-edges-outside.txt',
            'TBD',
            linecount=5880600)

    # stopped here on tsai phase3
    def state(self):
        parent_state = self.parent.state
        return result


class LookupTableULCentersSolve(LookupTable):
    """
    This tables solves sides U and L which in turn also solve D and R.  When
    the table was built the Ls were replaced with Us so that we were left with
    only 'U' and 'x' squares so that we could save the states in hex which
    makes the table take up much less disk space.

    lookup-table-5x5x5-step31-UL-centers-solve.txt
    ==============================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 71 entries (0 percent, 10.14x previous step)
    3 steps has 630 entries (0 percent, 8.87x previous step)
    4 steps has 4,639 entries (0 percent, 7.36x previous step)
    5 steps has 32,060 entries (0 percent, 6.91x previous step)
    6 steps has 198,779 entries (0 percent, 6.20x previous step)
    7 steps has 1,011,284 entries (4 percent, 5.09x previous step)
    8 steps has 3,826,966 entries (15 percent, 3.78x previous step)
    9 steps has 8,611,512 entries (35 percent, 2.25x previous step)
    10 steps has 8,194,244 entries (34 percent, 0.95x previous step)
    11 steps has 2,062,640 entries (8 percent, 0.25x previous step)
    12 steps has 67,152 entries (0 percent, 0.03x previous step)
    13 steps has 16 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step31-UL-centers-solve.txt',
            '3ffff000000000',
            linecount=24010000)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            parent_state[7], parent_state[8], parent_state[9],
            parent_state[12], parent_state[13], parent_state[14],
            parent_state[17], parent_state[18], parent_state[19],

            # Left
            parent_state[32], parent_state[33], parent_state[34],
            parent_state[37], parent_state[38], parent_state[39],
            parent_state[42], parent_state[43], parent_state[44],

            # Front
            parent_state[57], parent_state[58], parent_state[59],
            parent_state[62], parent_state[63], parent_state[64],
            parent_state[67], parent_state[68], parent_state[69],

            # Right
            parent_state[82], parent_state[83], parent_state[84],
            parent_state[87], parent_state[88], parent_state[89],
            parent_state[92], parent_state[93], parent_state[94],

            # Back
            parent_state[107], parent_state[108], parent_state[109],
            parent_state[112], parent_state[113], parent_state[114],
            parent_state[117], parent_state[118], parent_state[119],

            # Down
            parent_state[132], parent_state[133], parent_state[134],
            parent_state[137], parent_state[138], parent_state[139],
            parent_state[142], parent_state[143], parent_state[144]
        ]

        result = ['1' if x in ('U', 'L') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableUFCentersSolve(LookupTable):
    """
    This tables solves sides U and F which in turn also solve D and B.  When
    the table was built the Fs were replaced with Us so that we were left with
    only 'U' and 'x' squares so that we could save the states in hex which
    makes the table take up much less disk space.

    lookup-table-5x5x5-step33-UF-centers-solve.txt
    ==============================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 71 entries (0 percent, 10.14x previous step)
    3 steps has 630 entries (0 percent, 8.87x previous step)
    4 steps has 4,639 entries (0 percent, 7.36x previous step)
    5 steps has 32,060 entries (0 percent, 6.91x previous step)
    6 steps has 198,779 entries (0 percent, 6.20x previous step)
    7 steps has 1,011,284 entries (4 percent, 5.09x previous step)
    8 steps has 3,826,966 entries (15 percent, 3.78x previous step)
    9 steps has 8,611,512 entries (35 percent, 2.25x previous step)
    10 steps has 8,194,244 entries (34 percent, 0.95x previous step)
    11 steps has 2,062,640 entries (8 percent, 0.25x previous step)
    12 steps has 67,152 entries (0 percent, 0.03x previous step)
    13 steps has 16 entries (0 percent, 0.00x previous step)

    Total: 24,010,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step33-UF-centers-solve.txt',
            '3fe00ff8000000',
            linecount=24010000)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            parent_state[7], parent_state[8], parent_state[9],
            parent_state[12], parent_state[13], parent_state[14],
            parent_state[17], parent_state[18], parent_state[19],

            # Left
            parent_state[32], parent_state[33], parent_state[34],
            parent_state[37], parent_state[38], parent_state[39],
            parent_state[42], parent_state[43], parent_state[44],

            # Front
            parent_state[57], parent_state[58], parent_state[59],
            parent_state[62], parent_state[63], parent_state[64],
            parent_state[67], parent_state[68], parent_state[69],

            # Right
            parent_state[82], parent_state[83], parent_state[84],
            parent_state[87], parent_state[88], parent_state[89],
            parent_state[92], parent_state[93], parent_state[94],

            # Back
            parent_state[107], parent_state[108], parent_state[109],
            parent_state[112], parent_state[113], parent_state[114],
            parent_state[117], parent_state[118], parent_state[119],

            # Down
            parent_state[132], parent_state[133], parent_state[134],
            parent_state[137], parent_state[138], parent_state[139],
            parent_state[142], parent_state[143], parent_state[144]
        ]

        result = ['1' if x in ('U', 'F') else '0' for x in result]
        result = ''.join(result)

        # Convert to hex
        return self.hex_format % int(result, 2)


class LookupTableIDA555ULFRBDCentersSolve(LookupTableIDA):
    """
    Would be 117,649,000,000...I built it 7-deep.
    24,010,000/117,649,000,000 is 0.000204082 so this will be a fast IDA search

    lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt
    ==================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 99 entries (0 percent, 14.14x previous step)
    3 steps has 1,134 entries (0 percent, 11.45x previous step)
    4 steps has 12,183 entries (0 percent, 10.74x previous step)
    5 steps has 128,730 entries (0 percent, 10.57x previous step)
    6 steps has 1,291,295 entries (9 percent, 10.03x previous step)
    7 steps has 12,250,688 entries (89 percent, 9.49x previous step)

    Total: 13,684,136 entries
    """

    def __init__(self, parent):
        LookupTableIDA.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step30-ULFRBD-centers-solve.txt',
            'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD',
            moves_5x5x5,

            # These moves would destroy the staged centers
            ("Rw", "Rw'", "Lw", "Lw'", "Fw", "Fw'", "Bw", "Bw'", "Uw", "Uw'", "Dw", "Dw'"),

            # prune tables
            (parent.lt_UL_centers_solve,
             parent.lt_UF_centers_solve),
            linecount=13684136)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            parent_state[7], parent_state[8], parent_state[9],
            parent_state[12], parent_state[13], parent_state[14],
            parent_state[17], parent_state[18], parent_state[19],

            # Left
            parent_state[32], parent_state[33], parent_state[34],
            parent_state[37], parent_state[38], parent_state[39],
            parent_state[42], parent_state[43], parent_state[44],

            # Front
            parent_state[57], parent_state[58], parent_state[59],
            parent_state[62], parent_state[63], parent_state[64],
            parent_state[67], parent_state[68], parent_state[69],

            # Right
            parent_state[82], parent_state[83], parent_state[84],
            parent_state[87], parent_state[88], parent_state[89],
            parent_state[92], parent_state[93], parent_state[94],

            # Back
            parent_state[107], parent_state[108], parent_state[109],
            parent_state[112], parent_state[113], parent_state[114],
            parent_state[117], parent_state[118], parent_state[119],

            # Down
            parent_state[132], parent_state[133], parent_state[134],
            parent_state[137], parent_state[138], parent_state[139],
            parent_state[142], parent_state[143], parent_state[144]
        ]

        result = ''.join(result)
        return result


class LookupTable555EdgeSliceForward(LookupTable):
    """
    lookup-table-5x5x5-step90-edges-slice-forward.txt
    =================================================
    1 steps has 7 entries (0 percent)
    2 steps has 42 entries (0 percent)
    3 steps has 299 entries (3 percent)
    4 steps has 1,306 entries (16 percent)
    5 steps has 3,449 entries (43 percent)
    6 steps has 2,617 entries (33 percent)
    7 steps has 200 entries (2 percent)

    Total: 7920 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step90-edges-slice-forward.txt',
            'EDGES',
            linecount=7920)

    def state(self):
        raise Exception("This should never be called")


class LookupTable555EdgeSliceBackward(LookupTable):
    """
    lookup-table-5x5x5-step91-edges-slice-backward.txt
    ==================================================
    1 steps has 1 entries (0 percent)
    3 steps has 36 entries (0 percent)
    4 steps has 66 entries (0 percent)
    5 steps has 334 entries (4 percent)
    6 steps has 1,369 entries (17 percent)
    7 steps has 3,505 entries (44 percent)
    8 steps has 2,539 entries (32 percent)
    9 steps has 69 entries (0 percent)

    Total: 7919 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step91-edges-slice-backward.txt',
            'EDGES',
            linecount=7919)

    def state(self):
        raise Exception("This should never be called")


edges_recolor_tuples_555 = (
    ('0', 2, 104), # upper
    ('1', 4, 102),
    ('2', 6, 27),
    ('3', 10, 79),
    ('4', 16, 29),
    ('5', 20, 77),
    ('6', 22, 52),
    ('7', 24, 54),

    ('8', 31, 110), # left
    ('9', 35, 56),
    ('a', 41, 120),
    ('b', 45, 66),

    ('c', 81, 60), # right
    ('d', 85, 106),
    ('e', 91, 70),
    ('f', 95, 116),

    ('g', 127, 72), # down
    ('h', 129, 74),
    ('i', 131, 49),
    ('j', 135, 97),
    ('k', 141, 47),
    ('l', 145, 99),
    ('m', 147, 124),
    ('n', 149, 122)
)

midges_recolor_tuples_555 = (
    ('o', 3, 103), # upper
    ('p', 11, 28),
    ('q', 15, 78),
    ('r', 23, 53),

    ('s', 36, 115), # left
    ('t', 40, 61),

    ('u', 86, 65),  # right
    ('v', 90, 111),

    ('w', 128, 73), # down
    ('x', 136, 48),
    ('y', 140, 98),
    ('z', 148, 123)
)

def edges_recolor_pattern_555(state):
    midges_map = {
        'BD': None,
        'BL': None,
        'BR': None,
        'BU': None,
        'DF': None,
        'DL': None,
        'DR': None,
        'FL': None,
        'FR': None,
        'FU': None,
        'LU': None,
        'RU': None
    }

    for (edge_index, square_index, partner_index) in midges_recolor_tuples_555:
        square_value = state[square_index]
        partner_value = state[partner_index]
        wing_str = ''.join(sorted([square_value, partner_value]))
        midges_map[wing_str] = edge_index

        # We need to indicate which way the midge is rotated.  If the square_index contains
        # U, D, L, or R use the uppercase of the edge_index, if not use the lowercase of the
        # edge_index.
        if square_value == 'U':
            state[square_index] = edge_index.upper()
            state[partner_index] = edge_index.upper()
        elif partner_value == 'U':
            state[square_index] = edge_index
            state[partner_index] = edge_index
        elif square_value == 'D':
            state[square_index] = edge_index.upper()
            state[partner_index] = edge_index.upper()
        elif partner_value == 'D':
            state[square_index] = edge_index
            state[partner_index] = edge_index
        elif square_value == 'L':
            state[square_index] = edge_index.upper()
            state[partner_index] = edge_index.upper()
        elif partner_value == 'L':
            state[square_index] = edge_index
            state[partner_index] = edge_index
        elif square_value == 'R':
            state[square_index] = edge_index.upper()
            state[partner_index] = edge_index.upper()
        elif partner_value == 'R':
            state[square_index] = edge_index
            state[partner_index] = edge_index
        else:
            raise Exception("We should not be here")

    # Where is the midge for each high/low wing?
    for (edge_index, square_index, partner_index) in edges_recolor_tuples_555:
        square_value = state[square_index]
        partner_value = state[partner_index]

        high_low = tsai_phase2_orient_edges_555[(square_index, partner_index, square_value, partner_value)]
        wing_str = ''.join(sorted([square_value, partner_value]))

        # If this is a high wing use the uppercase of the midge edge_index
        if high_low == 'U':
            state[square_index] = midges_map[wing_str].upper()
            state[partner_index] = midges_map[wing_str].upper()

        # If this is a low wing use the lowercase of the midge edge_index
        elif high_low == 'D':
            state[square_index] = midges_map[wing_str]
            state[partner_index] = midges_map[wing_str]

        else:
            raise Exception("(%s, %s, %s, %) high_low is %s" % (square_index, partner_index, square_value, partner_value, high_low))

    return ''.join(state)


class LookupTable555Edges(LookupTable):
    """
    lookup-table-5x5x5-step100-edges.txt
    ====================================
    5 steps has 97856 entries (1 percent, 0.00x previous step)
    6 steps has 375995 entries (5 percent, 3.84x previous step)
    7 steps has 892869 entries (12 percent, 2.37x previous step)
    8 steps has 1438416 entries (19 percent, 1.61x previous step)
    9 steps has 4588466 entries (62 percent, 3.19x previous step)

    Total: 7393602 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step100-edges.txt',
            '111111111111111111111111_OOopPPQQqrRRsSSTTtuUUVVvWWwxXXYYyzZZ',
            linecount=7393602)

    def state(self):
        """
        Normally the state() for a LookupTable is a straightforward thing where
        you look at certain squares on the cube, build the state from the squares
        and you are done.  With LookupTable555Edges though things are a little
        different because lookup-table-5x5x5-step100-edges.txt does not contain
        all possible edge states (there are gazillions of them), it only contains
        all of the edges states possible up to 9-deep.

        So what we do is find the current state of edges and look through
        lookup-table-5x5x5-step100-edges.txt for the line whose state is the closest
        match to our own. The LookupTable.solve() code will then execute the set of
        steps for that state which will pair several of our edges.
        """
        state = edges_recolor_pattern_555(self.parent.state[:])

        edges_state = ''.join([state[square_index] for square_index in wings_555])
        signature = get_edges_paired_binary_signature(edges_state)
        signature_width = len(signature) + 1
        edges_state = signature + '_' + edges_state

        pre_non_paired_wings_count = self.parent.get_non_paired_wings_count()
        log.info("%s: signature %s, %d unpaired wings, %d steps in" %
            (self, signature, pre_non_paired_wings_count, self.parent.get_solution_len_minus_rotates(self.parent.solution)))
        self.parent.print_cube()

        # This is a sanity check to make sure we calculate the signature correctly...delete this at some point
        if pre_non_paired_wings_count != signature.count('0'):
            raise SolveError("pre_non_paired_wings_count is %d but there are %s 0s in signature %s, edges_state %s" %
                (pre_non_paired_wings_count, signature.count('0'), signature, edges_state))


        # If all edges are paired return our actual state
        if self.parent.edges_paired():
            return edges_state


        # If our state is in lookup-table-5x5x5-step100-edges.txt, return our actual state.
        # When this happens we will pair all of the remaining edges.
        steps = self.steps(edges_state)

        if steps is not None:
            return edges_state


        # If we are here then we need to look through lookup-table-5x5x5-step100-edges.txt
        # to find the line whose state is the closest match to our own. This allows us to
        # pair some of our unpaired edges and make some progress even though our current
        # state isn't in the lookup table.
        MAX_WING_PAIRS = 24

        # How many wings are paired?
        pre_paired_wings_count = MAX_WING_PAIRS - pre_non_paired_wings_count

        # Find all of the 'loose' matching entries in our lookup table. 'loose' means the
        # entry will not unpair any of our already paired wings.
        loose_matching_entry = []
        max_wing_pair_count = None

        for line in self.find_edge_entries_with_loose_signature(signature):
            (phase1_state, phase1_steps) = line.split(':')

            common_count = get_characters_common_count(edges_state[signature_width:],
                                                       phase1_state[signature_width:],
                                                       self.state_width - signature_width)
            wing_pair_count = int(common_count/2)

            # Only bother with this entry if it will pair more wings than are currently paired
            if wing_pair_count > pre_paired_wings_count:

                if max_wing_pair_count is None:
                    loose_matching_entry.append((wing_pair_count, line))
                    max_wing_pair_count = wing_pair_count

                elif wing_pair_count > max_wing_pair_count:
                    loose_matching_entry = []
                    loose_matching_entry.append((wing_pair_count, line))
                    max_wing_pair_count = wing_pair_count

                elif wing_pair_count == max_wing_pair_count:
                    loose_matching_entry.append((wing_pair_count, line))

        if not loose_matching_entry:
            raise SolveError("could not find any edge solutions to apply to move forward")

        #log.warning("pre_paired_wings_count %d, loose_matching_entry(%d):\n%s" % (pre_paired_wings_count, len(loose_matching_entry), str(loose_matching_entry)))
        log.warning("pre_paired_wings_count %d, loose_matching_entry(%d)" % (pre_paired_wings_count, len(loose_matching_entry)))
        original_state = self.parent.state[:]
        original_solution = self.parent.solution[:]
        best_score_states = []

        # Now run through each state:steps in loose_matching_entry
        for (wing_pair_count, line) in loose_matching_entry:
            (phase1_edges_state_fake, phase1_steps) = line.split(':')
            phase1_steps = phase1_steps.split()

            # Apply the phase1 steps
            for step in phase1_steps:
                self.parent.rotate(step)

            phase1_state = edges_recolor_pattern_555(self.parent.state[:])
            phase1_edges_state = ''.join([phase1_state[square_index] for square_index in wings_555])
            phase1_signature = get_edges_paired_binary_signature(phase1_edges_state)
            phase1_edges_state = phase1_signature + '_' + phase1_edges_state

            # If that got us to our state_target then phase1 alone paired all
            # of the edges...this is unlikely
            if phase1_edges_state in self.state_target:
                best_score_states.append((MAX_WING_PAIRS, len(phase1_steps), phase1_edges_state_fake))

            else:
                # phase1_steps did not pair all edges so do another lookup and execute those steps
                phase2_steps = self.steps(phase1_edges_state)

                if phase2_steps is not None:
                    for step in phase2_steps:
                        self.parent.rotate(step)

                    phase2_state = edges_recolor_pattern_555(self.parent.state[:])
                    phase2_edges_state = ''.join([phase2_state[square_index] for square_index in wings_555])
                    phase2_signature = get_edges_paired_binary_signature(phase2_edges_state)
                    phase2_edges_state = phase2_signature + '_' + phase2_edges_state

                    if phase2_edges_state in self.state_target:
                        best_score_states.append((MAX_WING_PAIRS, len(phase1_steps) + len(phase2_steps), phase1_edges_state_fake))
                    else:
                        post_non_paired_wings_count = self.parent.get_non_paired_wings_count()
                        paired_wings_count = MAX_WING_PAIRS - post_non_paired_wings_count

                        best_score_states.append((paired_wings_count, len(phase1_steps) + len(phase2_steps), phase1_edges_state_fake))
                else:
                    post_non_paired_wings_count = self.parent.get_non_paired_wings_count()
                    paired_wings_count = MAX_WING_PAIRS - post_non_paired_wings_count

                    best_score_states.append((paired_wings_count, len(phase1_steps), phase1_edges_state_fake))

            self.parent.state = original_state[:]
            self.parent.solution = original_solution[:]

        #log.info("best_score_states: %s" % pformat(best_score_states))
        best_entry = get_best_entry(best_score_states)
        log.info("best_entry: %s" % pformat(best_entry))
        log.info("\n\n\n\n\n\n")

        return best_entry[2]


class LookupTable555TCenterSolve(LookupTable):
    """
    This is only used when a cube larger than 7x7x7 is being solved

    lookup-table-5x5x5-step32-ULFRBD-t-centers-solve.txt
    ====================================================
    1 steps has 7 entries (0 percent, 0.00x previous step)
    2 steps has 99 entries (0 percent, 14.14x previous step)
    3 steps has 1,038 entries (0 percent, 10.48x previous step)
    4 steps has 8,463 entries (2 percent, 8.15x previous step)
    5 steps has 47,986 entries (13 percent, 5.67x previous step)
    6 steps has 146,658 entries (42 percent, 3.06x previous step)
    7 steps has 128,914 entries (37 percent, 0.88x previous step)
    8 steps has 9,835 entries (2 percent, 0.08x previous step)

    Total: 343,000 entries
    """

    def __init__(self, parent):
        LookupTable.__init__(
            self,
            parent,
            'lookup-table-5x5x5-step32-ULFRBD-t-centers-solve.txt',
            'xUxUUUxUxxLxLLLxLxxFxFFFxFxxRxRRRxRxxBxBBBxBxxDxDDDxDx',
            linecount=343000)

    def state(self):
        parent_state = self.parent.state
        result = [
            # Upper
            'x', parent_state[8], 'x',
            parent_state[12], parent_state[13], parent_state[14],
            'x', parent_state[18], 'x',

            # Left
            'x', parent_state[33], 'x',
            parent_state[37], parent_state[38], parent_state[39],
            'x', parent_state[43], 'x',

            # Front
            'x', parent_state[58], 'x',
            parent_state[62], parent_state[63], parent_state[64],
            'x', parent_state[68], 'x',

            # Right
            'x', parent_state[83], 'x',
            parent_state[87], parent_state[88], parent_state[89],
            'x', parent_state[93], 'x',

            # Back
            'x', parent_state[108], 'x',
            parent_state[112], parent_state[113], parent_state[114],
            'x', parent_state[118], 'x',

            # Down
            'x', parent_state[133], 'x',
            parent_state[137], parent_state[138], parent_state[139],
            'x', parent_state[143], 'x'
        ]

        result = ''.join(result)
        return result


class RubiksCube555(RubiksCube):
    """
    5x5x5 strategy
    - stage UD centers to sides U or D (use IDA)
    - stage LR centers to sides L or R...this in turn stages FB centers to sides F or B
    - solve all centers (use IDA)
    - pair edges
    - solve as 3x3x3
    """

    def __init__(self, state, order, colormap=None, debug=False):
        RubiksCube.__init__(self, state, order, colormap)
        self.use_pair_outside_edges = False

        # This will be True when an even cube is using the 555 edge solver
        # to pair an orbit of edges
        self.avoid_pll = False

        if debug:
            log.setLevel(logging.DEBUG)

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

    def sanity_check(self):
        edge_orbit_0 = (2, 4, 10, 20, 24, 22, 16, 6,
                        27, 29, 35, 45, 49, 47, 41, 31,
                        52, 54, 60, 70, 74, 72, 66, 56,
                        77, 79, 85, 95, 99, 97, 91, 81,
                        102, 104, 110, 120, 124, 122, 116, 106,
                        127, 129, 135, 145, 149, 147, 141, 131)

        edge_orbit_1 = (3, 15, 23, 11,
                        28, 40, 48, 36,
                        53, 65, 73, 61,
                        78, 90, 98, 86,
                        103, 115, 123, 111,
                        128, 140, 148, 136)

        corners = (1, 5, 21, 25,
                   26, 30, 46, 50,
                   51, 55, 71, 75,
                   76, 80, 96, 100,
                   101, 105, 121, 125,
                   126, 130, 146, 150)

        x_centers = (7, 9, 17, 19,
                     32, 34, 42, 44,
                     57, 59, 67, 69,
                     82, 84, 92, 94,
                     107, 109, 117, 119,
                     132, 134, 142, 144)

        t_centers = (8, 12, 14, 18,
                     33, 37, 39, 43,
                     58, 62, 64, 68,
                     83, 87, 89, 93,
                     108, 112, 114, 118,
                     133, 137, 139, 143)

        centers = (13, 38, 63, 88, 113, 138)

        self._sanity_check('edge-orbit-0', edge_orbit_0, 8)
        self._sanity_check('edge-orbit-1', edge_orbit_1, 4)
        self._sanity_check('corners', corners, 4)
        self._sanity_check('x-centers', x_centers, 4)
        self._sanity_check('t-centers', t_centers, 4)
        self._sanity_check('centers', centers, 1)

    def rotate(self, step):
        """
        The 5x5x5 solver calls rotate() much more than other solvers, this is
        due to the edge-pairing code.  In order to speed up edge-pairing use
        the faster rotate_555() instead of RubiksCube.rotate()
        """
        self.state = rotate_555(self.state[:], step)
        self.solution.append(step)

    def lt_init(self):
        if self.lt_init_called:
            return
        self.lt_init_called = True

        # experiment
        '''
        self.lt_UD_T_centers_stage = LookupTable555UDTCenterStage(self)
        self.lt_UD_X_centers_stage = LookupTable555UDXCenterStage(self)
        self.lt_LR_T_centers_stage = LookupTable555LRTCenterStage(self)
        self.lt_LR_X_centers_stage = LookupTable555LRXCenterStage(self)
        self.lt_FB_T_centers_stage = LookupTable555FBTCenterStage(self)
        self.lt_FB_X_centers_stage = LookupTable555FBXCenterStage(self)
        self.lt_ALL_enters_stage = LookupTableIDA555AllCenterStage(self)
        '''

        self.lt_UD_T_centers_stage = LookupTable555UDTCenterStage(self)
        self.lt_UD_X_centers_stage = LookupTable555UDXCenterStage(self)
        self.lt_UD_centers_stage = LookupTableIDA555UDCentersStage(self)

        self.lt_LR_centers_stage_x_center_only = LookupTable555LRXCentersStage(self)
        self.lt_LR_centers_stage_t_center_only = LookupTable555LRTCentersStage(self)
        self.lt_LR_centers_stage = LookupTableIDA555LRCentersStage(self)

        #self.lt_tsai_phase2_edges_orient = LookupTable555TsaiPhase2EdgesOrient(self)
        #self.lt_tsai_phase2_LR_centers = LookupTable555TsaiPhase2LRCenters(self)
        #self.lt_tsai_phase2 = LookupTable555TsaiPhase2(self)

        #self.lt_tsai_phase3_LF_centers = LookupTable555TsaiPhase3LFCenters(self)

        self.lt_UL_centers_solve = LookupTableULCentersSolve(self)
        self.lt_UF_centers_solve = LookupTableUFCentersSolve(self)
        self.lt_ULFRB_centers_solve = LookupTableIDA555ULFRBDCentersSolve(self)

        self.lt_edges_slice_forward = LookupTable555EdgeSliceForward(self)
        self.lt_edges_slice_backward = LookupTable555EdgeSliceBackward(self)
        self.lt_edges = LookupTable555Edges(self)

        self.lt_ULFRBD_t_centers_solve = LookupTable555TCenterSolve(self)

    def high_low_state(self, x, y, state_x, state_y, wing_str):
        """
        Return U if this is a high edge, D if it is a low edge
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Nuke everything except the one wing we are interested in
        self.nuke_corners()
        self.nuke_centers()
        self.nuke_edges()

        self.state[x] = state_x
        self.state[y] = state_y

        # Now move that wing to its home edge
        if wing_str.startswith('U'):

            if wing_str == 'UB':
                self.move_wing_to_U_north(x)
                high_edge_index = 2
                low_edge_index = 4

            elif wing_str == 'UL':
                self.move_wing_to_U_west(x)
                high_edge_index = 16
                low_edge_index = 6

            elif wing_str == 'UR':
                self.move_wing_to_U_east(x)
                high_edge_index = 10
                low_edge_index = 20

            elif wing_str == 'UF':
                self.move_wing_to_U_south(x)
                high_edge_index = 24
                low_edge_index = 22

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == 'U':
                result = 'U'
            elif self.state[low_edge_index] == 'U':
                result = 'D'
            elif self.state[high_edge_index] == 'x':
                result = 'U'
            elif self.state[low_edge_index] == 'x':
                result = 'D'
            else:
                self.print_cube()
                raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                    (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        elif wing_str.startswith('L'):

            if wing_str == 'LB':
                self.move_wing_to_L_west(x)
                high_edge_index = 41
                low_edge_index = 31

            elif wing_str == 'LF':
                self.move_wing_to_L_east(x)
                high_edge_index = 35
                low_edge_index = 45

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == 'L':
                result = 'U'
            elif self.state[low_edge_index] == 'L':
                result = 'D'
            elif self.state[high_edge_index] == 'x':
                result = 'U'
            elif self.state[low_edge_index] == 'x':
                result = 'D'
            else:
                self.print_cube()
                raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                    (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        elif wing_str.startswith('R'):

            if wing_str == 'RB':
                self.move_wing_to_R_east(x)
                high_edge_index = 85
                low_edge_index = 95

            elif wing_str == 'RF':
                self.move_wing_to_R_west(x)
                high_edge_index = 91
                low_edge_index = 81

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == 'R':
                result = 'U'
            elif self.state[low_edge_index] == 'R':
                result = 'D'
            elif self.state[high_edge_index] == 'x':
                result = 'U'
            elif self.state[low_edge_index] == 'x':
                result = 'D'
            else:
                self.print_cube()
                raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                    (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        elif wing_str.startswith('D'):
            if wing_str == 'DB':
                self.move_wing_to_D_south(x)
                high_edge_index = 149
                low_edge_index = 147

            elif wing_str == 'DL':
                self.move_wing_to_D_west(x)
                high_edge_index = 141
                low_edge_index = 131

            elif wing_str == 'DR':
                self.move_wing_to_D_east(x)
                high_edge_index = 135
                low_edge_index = 145

            elif wing_str == 'DF':
                self.move_wing_to_D_north(x)
                high_edge_index = 127
                low_edge_index = 129

            else:
                raise Exception("invalid wing_str %s" % wing_str)

            if self.state[high_edge_index] == 'D':
                result = 'U'
            elif self.state[low_edge_index] == 'D':
                result = 'D'
            elif self.state[high_edge_index] == 'x':
                result = 'U'
            elif self.state[low_edge_index] == 'x':
                result = 'D'
            else:
                self.print_cube()
                raise Exception("something went wrong, (%s, %s) was originally (%s, %s), moved to %s, high_index state[%s] is %s, low_index state[%s] is %s" %
                    (x, y, state_x, state_y, wing_str, high_edge_index, self.state[high_edge_index], low_edge_index, self.state[low_edge_index]))

        else:
            raise Exception("invalid wing_str %s" % wing_str)

        self.state = original_state[:]
        self.solution = original_solution[:]

        assert result in ('U', 'D')
        return result

    def build_tsai_phase2_orient_edges_555(self):
        state = self.state

        for x in range(1000000):
            added_wing_tuple = False

            # make random moves
            step = moves_5x5x5[randint(0, len(moves_5x5x5)-1)]

            for (x, y) in (
                (2, 104), (4, 102), (6, 27), (10, 79), (16, 29), (20, 77), (22, 52), (24, 54),
                (27, 6), (29, 16), (31, 110), (35, 56), (41, 120), (45, 66), (47, 141), (49, 131),
                (52, 22), (54, 24), (56, 35), (60, 81), (66, 45), (70, 91), (72, 127), (74, 129),
                (77, 20), (79, 10), (81, 60), (85, 106), (91, 70), (95, 116), (97, 135), (99, 145),
                (102, 4), (104, 2), (106, 85), (110, 31), (116, 95), (120, 41), (122, 149), (124, 147),
                (127, 72), (129, 74), (131, 49), (135, 97), (141, 47), (145, 99), (147, 124), (149, 122)):

                state_x = self.state[x]
                state_y = self.state[y]
                wing_str = wing_str_map[''.join((state_x, state_y))]
                wing_tuple = (x, y, state_x, state_y)

                if wing_tuple not in tsai_phase2_orient_edges_555:
                    tsai_phase2_orient_edges_555[wing_tuple] = self.high_low_state(x, y, state_x, state_y, wing_str)
                    added_wing_tuple = True

        log.info("new tsai_phase2_orient_edges_555\n\n%s\n\n" % pformat(tsai_phase2_orient_edges_555))
        log.info("tsai_phase2_orient_edges_555 has %d entries" % len(tsai_phase2_orient_edges_555))
        sys.exit(0)

    def tsai_phase2_orient_edges_state(self, edges_to_flip, return_hex):
        state = self.state
        result = []

        for (x, y) in (
            (2, 104), (4, 102), (6, 27), (10, 79), (16, 29), (20, 77), (22, 52), (24, 54),
            (27, 6), (29, 16), (31, 110), (35, 56), (41, 120), (45, 66), (47, 141), (49, 131),
            (52, 22), (54, 24), (56, 35), (60, 81), (66, 45), (70, 91), (72, 127), (74, 129),
            (77, 20), (79, 10), (81, 60), (85, 106), (91, 70), (95, 116), (97, 135), (99, 145),
            (102, 4), (104, 2), (106, 85), (110, 31), (116, 95), (120, 41), (122, 149), (124, 147),
            (127, 72), (129, 74), (131, 49), (135, 97), (141, 47), (145, 99), (147, 124), (149, 122)):

            state_x = state[x]
            state_y = state[y]
            wing_str = wing_str_map[''.join((state_x, state_y))]
            high_low = tsai_phase2_orient_edges_555[(x, y, state_x, state_y)]

            if wing_str in edges_to_flip:
                if high_low == 'U':
                    high_low = 'D'
                else:
                    high_low = 'U'

            if return_hex:
                high_low = high_low.replace('D', '0').replace('U', '1')

            result.append(high_low)

        result = ''.join(result)

        if return_hex:
            return "%012x" % int(result, 2)
        else:
            return result

    def tsai_phase2_orient_edges_print(self):

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        self.nuke_corners()
        self.nuke_centers()
        self.edge_mapping = {}

        orient_edge_state = list(self.tsai_phase2_orient_edges_state(self.edge_mapping, return_hex=False))
        orient_edge_state_index = 0
        self.nuke_edges()

        for square_index in (
            2, 4, 6, 10, 16, 20, 22, 24,
            27, 29, 31, 35, 41, 45, 47, 49,
            52, 54, 56, 60, 66, 70, 72, 74,
            77, 79, 81, 85, 91, 95, 97, 99,
            102, 104, 106, 110, 116, 120, 122, 124,
            127, 129, 131, 135, 141, 145, 147, 149):
            self.state[square_index] = orient_edge_state[orient_edge_state_index]
            orient_edge_state_index += 1
        self.print_cube()

        self.state = original_state[:]
        self.solution = original_solution[:]

    def group_centers_stage_UD(self):
        """
        Stage UD centers.  The 7x7x7 uses this that is why it is in its own method.
        """
        self.rotate_U_to_U()
        self.rotate_F_to_F()
        self.lt_UD_centers_stage.solve()
        log.info("UD centers staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def group_centers_stage_LR(self):
        """
        Stage LR centers.  The 6x6x6 uses this that is why it is in its own method.
        """
        # Stage LR centers
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        self.lt_LR_centers_stage.solve()
        log.info("ULFRBD centers staged, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def group_centers_guts(self):
        self.lt_init()
        self.group_centers_stage_UD()
        self.group_centers_stage_LR()

        if self.cpu_mode == 'tsai':

            # Test prune tables
            #self.lt_tsai_phase2_edges_orient.solve()
            #self.lt_tsai_phase2_LR_centers.solve()
            #self.print_cube()
            #self.tsai_phase2_orient_edges_print()
            #log.info("%d steps in" % self.get_solution_len_minus_rotates(self.solution))
            #sys.exit(0)

            # All centers are staged, solve them and pair the edges
            log.info("%s: Start of tsai Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_tsai_phase2.solve()
            self.print_cube()
            self.tsai_phase2_orient_edges_print()
            log.info("%s: End of tsai Phase2, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

            # Test prune tables
            self.lt_tsai_phase3_LF_centers.solve()
            self.print_cube()
            log.info("%d steps in" % self.get_solution_len_minus_rotates(self.solution))
            sys.exit(0)

            log.info("%s: Start of tsai Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
            self.lt_tsai_phase3.solve()
            self.print_cube()
            log.info("%s: End of tsai Phase3, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))

        else:
            # All centers are staged, solve them
            self.lt_ULFRB_centers_solve.solve()
            log.info("ULFRBD centers solved, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def find_moves_to_stage_slice_backward_555(self, target_wing, sister_wing1, sister_wing2, sister_wing3):
        state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
        return self.lt_edges_slice_backward.steps(state)

    def get_sister_wings_slice_backward_555(self):
        results = (None, None, None, None)
        max_pair_on_slice_back = 0

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Work with the wing at the bottom of the F-east edge
        # Move the sister wing to F-west
        target_wing = (self.sideF.edge_east_pos[-1], self.sideR.edge_west_pos[-1])

        # Do we need to reverse sister_wing1?
        for sister_wing1_reverse in (True, False):
            sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0])

            if sister_wing1_reverse:
                sister_wing1 = tuple(list(reversed(sister_wing1)))
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])

            sister_wing2 = None
            sister_wing3 = None
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

                    #log.info("sister_wing1_use_first_neighbor %s, sister_wing2 %s on %s" %
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

                            #log.info("sister_wing2_use_first_neighbor %s, sister_wing3 %s" %
                            #    (sister_wing2_use_first_neighbor, pformat(sister_wing3)))

                            steps = self.find_moves_to_stage_slice_backward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

                            if steps:
                                pre_non_paired_wings_count = self.get_non_paired_wings_count()
                                for step in steps:
                                    self.rotate(step)

                                # 3Uw' Uw
                                if self.use_pair_outside_edges:
                                    self.rotate("Uw")
                                self.rotate("Dw'")
                                self.rotate_y_reverse()

                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # F-east must pair
                                if self.state[70] == self.state[65] and self.state[91] == self.state[86]:
                                    will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                else:
                                    will_pair_on_slice_count = 0

                                #log.info("get_sister_wings_slice_backward_555() will_pair_on_slice_count %d via %s" %
                                #    (will_pair_on_slice_count, ' '.join(steps)))

                                # restore cube state
                                self.state = original_state[:]
                                self.solution = original_solution[:]

                                if will_pair_on_slice_count > max_pair_on_slice_back:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3)
                                    max_pair_on_slice_back = will_pair_on_slice_count

        # log.info("max_pair_on_slice_back is %d" % max_pair_on_slice_back)
        return results

    def prep_for_slice_back_555(self):

        (target_wing, sister_wing1, sister_wing2, sister_wing3) = self.get_sister_wings_slice_backward_555()

        if target_wing is None:
            log.info("prep_for_slice_back_555() failed...get_sister_wings_slice_backward_555")
            #raise SolveError("prep_for_slice_back_555() failed...get_sister_wings_slice_backward_555")
            return False

        steps = self.find_moves_to_stage_slice_backward_555(target_wing, sister_wing1, sister_wing2, sister_wing3)

        if steps:
            for step in steps:
                self.rotate(step)
            return True
        else:
            log.info("prep_for_slice_back_555() failed...no steps")
            return False

    def get_sister_wings_slice_forward_555(self, pre_non_paired_edges_count, pre_non_paired_wings_count):
        results = (None, None, None, None, None)
        max_pair_on_slice_forward = 0

        # save cube state
        original_state = self.state[:]
        original_solution = self.solution[:]

        # Work with the wing at the bottom of the F-west edge
        # Move the sister wing to F-east
        target_wing = (self.sideL.edge_east_pos[-1], self.sideF.edge_west_pos[-1])

        for sister_wing1_reverse in (True, False):
            sister_wing1 = self.get_wing_in_middle_of_edge(target_wing[0])

            if sister_wing1_reverse:
                sister_wing1 = tuple(list(reversed(sister_wing1)))
            sister_wing1_side = self.get_side_for_index(sister_wing1[0])

            sister_wing2 = None
            sister_wing3 = None
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

                    #log.info("sister_wing1_use_first_neighbor %s, sister_wing2 %s, reverse %s, %s" %
                    #   (sister_wing1_use_first_neighbor, pformat(sister_wing2), sister_wing2_reverse, sister_wing2_side))

                    for sister_wing2_use_first_neighbor in (True, False):
                        neighbors = sister_wing2_side.get_wing_neighbors(sister_wing2[0])

                        if sister_wing2_use_first_neighbor:
                            sister_wing2_neighbor = neighbors[0]
                        else:
                            sister_wing2_neighbor = neighbors[1]

                        for sister_wing3_reverse in (True, False):

                            # If we are pairing the last 4, 5 or 6 edges then we need sister_wing3 to
                            # be any unpaired edge that allows us to only pair 2 edges on the slice forward
                            if pre_non_paired_edges_count in (4, 5, 6):

                                # We need sister_wing3 to be any unpaired edge that allows us
                                # to only pair 2 on the slice forward
                                for wing in self.get_non_paired_wings():
                                    if (wing[0] not in (target_wing, sister_wing1, sister_wing2, sister_wing3, (40, 61), (61, 40)) and
                                        wing[1] not in (target_wing, sister_wing1, sister_wing2, sister_wing3, (40, 61), (61, 40))):
                                        sister_wing3 = wing[1]
                                        break
                            else:
                                sister_wing3 = self.get_wing_in_middle_of_edge(sister_wing2_neighbor)

                            if sister_wing3_reverse:
                                sister_wing3 = tuple(list(reversed(sister_wing3)))

                            state = self.edge_string_to_find(target_wing, sister_wing1, sister_wing2, sister_wing3)
                            steps = self.lt_edges_slice_forward.steps(state)

                            #log.info("sister_wing2_use_first_neighbor %s, sister_wing3 %s, reverse %s, state %s, steps %s" %
                            #    (sister_wing2_use_first_neighbor, pformat(sister_wing3), sister_wing3_reverse, state, "True" if steps else "False"))

                            if steps:
                                #log.info("target_wing %s, sister_wing1 %s, sister_wing2 %s, sister_wing3 %s" %
                                #    (pformat(target_wing), pformat(sister_wing1), pformat(sister_wing2), pformat(sister_wing3)))

                                for step in steps:
                                    self.rotate(step)

                                # 3Uw Uw'
                                if self.use_pair_outside_edges:
                                    self.rotate("Uw'")

                                self.rotate("Dw")
                                self.rotate_y()
                                post_non_paired_wings_count = self.get_non_paired_wings_count()

                                # F-west must pair
                                if self.state[66] == self.state[61] and self.state[45] == self.state[40]:
                                    will_pair_on_slice_count = pre_non_paired_wings_count - post_non_paired_wings_count
                                else:
                                    will_pair_on_slice_count = 0

                                # restore cube state
                                self.state = original_state[:]
                                self.solution = original_solution[:]

                                if will_pair_on_slice_count > max_pair_on_slice_forward:
                                    results = (target_wing, sister_wing1, sister_wing2, sister_wing3, steps)
                                    max_pair_on_slice_forward = will_pair_on_slice_count

        #if pre_non_paired_edges_count in (4, 5, 6):
        #    if max_pair_on_slice_forward != 2:
        #        raise SolveError("Should pair 2 on slice forward but will pair %d" % max_pair_on_slice_forward)

        #log.info("max_pair_on_slice_forward is %d" % max_pair_on_slice_forward)
        #if max_pair_on_slice_forward != 3:
        #    raise SolveError("Could not find sister wings for 5x5x5 slice forward (max_pair_on_slice_forward %d)" % max_pair_on_slice_forward)
        return results

    def rotate_unpaired_wing_to_bottom_of_F_east(self):
        """
        Rotate an unpaired wing to the bottom of F-east (one that can be sliced back)
        """
        for x in range(3):
            if self.state[65] == self.state[70] and self.state[86] == self.state[91]:
                self.rotate_y()
            else:
                if self.prep_for_slice_back_555():
                    return True

        return False

    def pair_outside_edges(self):
        fake_444 = RubiksCube444(solved_4x4x4, 'URFDLB')
        fake_444.cpu_mode = self.cpu_mode
        fake_444.lt_init()

        # The corners don't matter but it does make troubleshooting easier if they match
        fake_444.state[1] = self.state[1]
        fake_444.state[4] = self.state[5]
        fake_444.state[13] = self.state[21]
        fake_444.state[16] = self.state[25]
        fake_444.state[17] = self.state[26]
        fake_444.state[20] = self.state[30]
        fake_444.state[29] = self.state[46]
        fake_444.state[32] = self.state[50]
        fake_444.state[33] = self.state[51]
        fake_444.state[36] = self.state[55]
        fake_444.state[45] = self.state[71]
        fake_444.state[48] = self.state[75]
        fake_444.state[49] = self.state[76]
        fake_444.state[52] = self.state[80]
        fake_444.state[61] = self.state[96]
        fake_444.state[64] = self.state[100]
        fake_444.state[65] = self.state[101]
        fake_444.state[68] = self.state[105]
        fake_444.state[77] = self.state[121]
        fake_444.state[80] = self.state[125]
        fake_444.state[81] = self.state[126]
        fake_444.state[84] = self.state[130]
        fake_444.state[93] = self.state[146]
        fake_444.state[96] = self.state[150]

        # Upper
        fake_444.state[2] = self.state[2]
        fake_444.state[3] = self.state[4]
        fake_444.state[5] = self.state[6]
        fake_444.state[8] = self.state[10]
        fake_444.state[9] = self.state[16]
        fake_444.state[12] = self.state[20]
        fake_444.state[14] = self.state[22]
        fake_444.state[15] = self.state[24]

        # Left
        fake_444.state[18] = self.state[27]
        fake_444.state[19] = self.state[29]
        fake_444.state[21] = self.state[31]
        fake_444.state[24] = self.state[35]
        fake_444.state[25] = self.state[41]
        fake_444.state[28] = self.state[45]
        fake_444.state[30] = self.state[47]
        fake_444.state[31] = self.state[49]

        # Front
        fake_444.state[34] = self.state[52]
        fake_444.state[35] = self.state[54]
        fake_444.state[37] = self.state[56]
        fake_444.state[40] = self.state[60]
        fake_444.state[41] = self.state[66]
        fake_444.state[44] = self.state[70]
        fake_444.state[46] = self.state[72]
        fake_444.state[47] = self.state[74]

        # Right
        fake_444.state[50] = self.state[77]
        fake_444.state[51] = self.state[79]
        fake_444.state[53] = self.state[81]
        fake_444.state[56] = self.state[85]
        fake_444.state[57] = self.state[91]
        fake_444.state[60] = self.state[95]
        fake_444.state[62] = self.state[97]
        fake_444.state[63] = self.state[99]

        # Back
        fake_444.state[66] = self.state[102]
        fake_444.state[67] = self.state[104]
        fake_444.state[69] = self.state[106]
        fake_444.state[72] = self.state[110]
        fake_444.state[73] = self.state[116]
        fake_444.state[76] = self.state[120]
        fake_444.state[78] = self.state[122]
        fake_444.state[79] = self.state[124]

        # Down
        fake_444.state[82] = self.state[127]
        fake_444.state[83] = self.state[129]
        fake_444.state[85] = self.state[131]
        fake_444.state[88] = self.state[135]
        fake_444.state[89] = self.state[141]
        fake_444.state[92] = self.state[145]
        fake_444.state[94] = self.state[147]
        fake_444.state[95] = self.state[149]
        fake_444.sanity_check()
        fake_444.group_edges()

        for step in fake_444.solution:
            if step == 'EDGES_GROUPED':
                continue

            if step.startswith('4'):
                step = '5' + step[1:]
            elif step.startswith('3'):
                raise ImplementThis('4x4x4 steps starts with 3')
            self.rotate(step)

        log.warning("Outside edges are paired, %d steps in" % self.get_solution_len_minus_rotates(self.solution))

    def get_two_edge_pattern_id(self):

        # Build a string that represents the pattern of colors for the U-south and U-north edges
        edges_of_interest = [52, 53, 54, 22, 23, 24, 2, 3, 4, 104, 103, 102]
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
        #log.info("edges_of_interest_state: %s" % edges_of_interest_state)

        # 1, 5, 6, 7, and 8 are the scenarios where the outsided wings are paired...so these are the only ones
        # you hit if you use the 4x4x4 edge solver to pair all of the outside wings first. 1 and 5 are handled
        # via pair_checkboard_edge_555() which has been called by now so we do not need to look for those two scenarios here.
        #
        # See https://i.imgur.com/wsTqj.png for these patterns

        # No 6 - Exchange places and flip both centers
        if edges_of_interest_state in ('010202020101', '010232323101', '010222222101', '000121212000', '010121212101'):
            pattern_id = 6
            self.rotate_x_reverse()
            self.rotate_z()

        # No 7 - Exchange places, no flipping
        elif edges_of_interest_state in ('010232101323', '010202101020', '010222101222', '010121101212', '000121000212'):
            pattern_id = 7

        # No 8 regular - Exchange places, flip one center
        # The one that has to flip is at U-south
        elif edges_of_interest_state in ('010232303121', '010121202111', '010222202121', '000121202010', '010202000121'):
            pattern_id = 8

        # No 8 - Exchange places, flip one center
        # The one that has to flip is at U-north, it needs to be at U-south
        elif edges_of_interest_state in ('010232121303', '000121010202', '010121111202', '010202121000', '010222121202'):
            self.rotate_y()
            self.rotate_y()
            pattern_id = 8

        # No 2 regular
        elif edges_of_interest_state in ('001222110222', '010222101222', '001220110002', '000112000221', '001112110221', '001223110332'):
            pattern_id = 2

        # No 2 but the one at U-south needs to flip around
        elif edges_of_interest_state in ('011122112001', '011233223001', '011200220001', '011222222001', '000122112000'):
            self.rotate("F")
            self.rotate("U'")
            self.rotate("R")
            self.rotate_y()
            pattern_id = 2

        # No 2 but the one at U-north needs to flip around
        elif edges_of_interest_state in ('001220200011', '001223233011', '001222222011', '001112122011', '000112122000'):
            self.rotate("U")
            self.rotate("R")
            self.rotate("U'")
            self.rotate("B")
            pattern_id = 2

        # No 2 that just needs to be rotated around 180 degrees
        elif edges_of_interest_state in ('011222100222', '011122100211', '011200100022', '011233100322', '000122000211'):
            self.rotate_y()
            self.rotate_y()
            pattern_id = 2

        # No 3 regular
        elif edges_of_interest_state in ('001223213031', '000112102020', '001222212021', '001220210001', '001112112021'):
            pattern_id = 3
            self.rotate_x_reverse()
            self.rotate_z()

        # No 3 where it just needs to be rotated down and counter clockwise
        elif edges_of_interest_state in ('010102122000', '011102122011', '012103133022', '012101111022', '012100100022'):
            self.rotate_x_reverse()
            self.rotate_z_reverse()
            pattern_id = 3

        # No 3 where it just needs to be rotated down, clockwise and the F-east edge needs to be flipped
        elif edges_of_interest_state in ('001220100012', '001223130312', '000112020201', '001112120211', '001222120212'):
            self.rotate_x_reverse()
            self.rotate_z()
            self.rotate("R")
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
            pattern_id = 3

        # No 3 where it just needs to be rotated down, counter clockwise and the F-east edge needs to be flipped
        elif edges_of_interest_state in ('012221200122', '012321200133', '012121200111', '001210100022', '010201000122'):
            self.rotate_x_reverse()
            self.rotate_z_reverse()
            self.rotate("R")
            self.rotate("F'")
            self.rotate("U")
            self.rotate("F")
            pattern_id = 3

        # No 4 regular, rotate down and counter clockwise
        elif edges_of_interest_state in ('011233203021', '000122102010', '011200200021', '011122102011', '011222202021'):
            pattern_id = 4
            self.rotate_x_reverse()
            self.rotate_z_reverse()

        # No 4 where it needs to be rotated down and clockwise
        elif edges_of_interest_state in ('010201221000', '001210220001', '012321331002', '012221221002', '012121111002'):
            self.rotate_x_reverse()
            self.rotate_z()
            pattern_id = 4

        # No 4 where it needs to be rotated down, clockwise and F-west needs to be flipped
        elif edges_of_interest_state in ('012103220331', '012100220001', '010102000221', '011102110221', '012101220111'):
            self.rotate_x_reverse()
            self.rotate_z()
            self.rotate("L'")
            self.rotate("F")
            self.rotate("U'")
            self.rotate("F'")
            pattern_id = 4

        # No 4 where it needs to be rotated down, counter clockwise and F-west needs to be flipped
        elif edges_of_interest_state in ('011233120302', '011122110201', '000122010201', '011222120202', '011200120002'):
            self.rotate_x_reverse()
            self.rotate_z_reverse()
            self.rotate("L'")
            self.rotate("F")
            self.rotate("U'")
            self.rotate("F'")
            pattern_id = 4

        # No 9 regular
        elif edges_of_interest_state in ('001210200021', '012221201022', '010201201020', '012121101012', '012321301032'):
            pattern_id = 9

        # No 9 where U-north needs to be flipped
        elif edges_of_interest_state in ('001210120002', '012221220102', '012121210101', '012321230103', '010201020102'):
            self.rotate("U")
            self.rotate("R")
            self.rotate("U'")
            self.rotate("B")
            pattern_id = 9

        # No 10 regular
        elif edges_of_interest_state in ('012103123032', '012100120002', '011102112021', '012101121012', '010102102020'):
            pattern_id = 10

        # No 10 where U-north needs to be flipped
        elif edges_of_interest_state in ('011102120211', '012100200021', '012103230321', '012101210121', '010102020201'):
            self.rotate("U")
            self.rotate("R")
            self.rotate("U'")
            self.rotate("B")
            pattern_id = 10

        else:
            self.print_cube()
            raise SolveError("Could not determine 5x5x5 last two edges pattern ID for %s" % edges_of_interest_state)

        return pattern_id

    def position_last_two_edges_555(self):
        """
        One unpaired edge is at F-west, position it and its sister edge to U-north and U-south
        """
        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        if not self.sideL.west_edge_paired():
            self.rotate_z()

        elif not self.sideB.south_edge_paired():
            self.rotate("B'")
            self.rotate_z()

        elif not self.sideR.south_edge_paired():
            self.rotate("D")
            self.rotate("B'")
            self.rotate_z()

        elif not self.sideU.north_edge_paired():
            self.rotate("F")

        elif not self.sideU.east_edge_paired():
            self.rotate("R'")
            self.rotate_x()
            self.rotate_y_reverse()

        elif not self.sideU.south_edge_paired():
            self.rotate("U2")
            self.rotate("F")

        elif not self.sideF.south_edge_paired():
            self.rotate("D2")
            self.rotate("B'")
            self.rotate_z()

        elif not self.sideL.south_edge_paired():
            self.rotate("D'")
            self.rotate("B'")
            self.rotate_z()

        elif not self.sideL.north_edge_paired():
            self.rotate("U")
            self.rotate("F")

        elif not self.sideR.west_edge_paired():
            self.rotate_z_reverse()
            self.rotate_x()

        elif not self.sideR.east_edge_paired():
            self.rotate("R2")
            self.rotate_z_reverse()
            self.rotate_x()

        else:
            raise ImplementThis("sister_wing1 %s" % pformat(sister_wing1))

        # Assert that U-north and U-south are not paired
        if self.sideU.north_edge_paired():
            raise SolveError("U-north should not be paired, sister_wing1 %s" % pformat(sister_wing1))

        if self.sideU.north_edge_paired():
            raise SolveError("U-south should not be paired, sister_wing1 %s" % pformat(sister_wing1))

    def position_sister_edges_555(self):
        """
        One unpaired edge is at F-west, position it and its sister edge to U-north and U-south
        """
        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        target_wing = self.sideF.edge_west_pos[1]
        sister_wing = self.get_wings(target_wing, remove_if_in_same_edge=True)[0]

        if sister_wing[0] in self.sideL.edge_west_pos or sister_wing[0] in self.sideB.edge_east_pos:
            self.rotate_z()

        elif sister_wing[0] in self.sideB.edge_south_pos or sister_wing[0] in self.sideD.edge_south_pos:
            self.rotate("B'")
            self.rotate_z()

        elif sister_wing[0] in self.sideR.edge_south_pos or sister_wing[0] in self.sideD.edge_east_pos:
            self.rotate("D")
            self.rotate("B'")
            self.rotate_z()

        elif sister_wing[0] in self.sideU.edge_north_pos or sister_wing[0] in self.sideB.edge_north_pos:
            self.rotate("F")

        elif sister_wing[0] in self.sideU.edge_east_pos or sister_wing[0] in self.sideL.edge_north_pos:
            self.rotate("R'")
            self.rotate_x()
            self.rotate_y_reverse()

        elif sister_wing[0] in self.sideU.edge_south_pos or sister_wing[0] in self.sideF.edge_north_pos:
            self.rotate("U2")
            self.rotate("F")

        elif sister_wing[0] in self.sideF.edge_south_pos or sister_wing[0] in self.sideD.edge_north_pos:
            self.rotate("D2")
            self.rotate("B'")
            self.rotate_z()

        elif sister_wing[0] in self.sideL.edge_south_pos or sister_wing[0] in self.sideD.edge_west_pos:
            self.rotate("D'")
            self.rotate("B'")
            self.rotate_z()

        elif sister_wing[0] in self.sideL.edge_north_pos or sister_wing[0] in self.sideU.edge_west_pos:
            self.rotate("U")
            self.rotate("F")

        elif sister_wing[0] in self.sideR.edge_west_pos or sister_wing[0] in self.sideF.edge_east_pos:
            self.rotate_z_reverse()
            self.rotate_x()

        elif sister_wing[0] in self.sideR.edge_east_pos or sister_wing[0] in self.sideB.edge_west_pos:
            self.rotate("R2")
            self.rotate_z_reverse()
            self.rotate_x()

        else:
            raise ImplementThis("sister_wing %s" % pformat(sister_wing))

        # Assert that U-north and U-south are not paired
        if self.sideU.north_edge_paired():
            raise SolveError("U-north should not be paired, sister_wing1 %s" % pformat(sister_wing1))

        if self.sideU.north_edge_paired():
            raise SolveError("U-south should not be paired, sister_wing1 %s" % pformat(sister_wing1))

    def all_colors_on_two_edges(self):
        target_wing = self.sideF.edge_west_pos[0]
        sister_wings = self.get_wings(target_wing, remove_if_in_same_edge=True)

        if not sister_wings:
            raise SolveError("We should not be here")

        if len(sister_wings) > 1:
            #log.info("F-west sister_wings %s" % pformat(sister_wings))
            return False

        sister_wing = sister_wings[0]
        target_edge_colors = self.get_edge_colors(target_wing)
        sister_wing_edge_colors = self.get_edge_colors(sister_wing[0])
        combined_edge_colors = list(set(target_edge_colors + sister_wing_edge_colors))
        #log.info("F-west combined_edge_colors %s" % pformat(combined_edge_colors))

        if len(combined_edge_colors) == 2:
            #log.info("all_colors_on_two_edges target %s" % pformat(target_wing))
            #log.info("all_colors_on_two_edges sister_wing %s" % pformat(sister_wing))
            #log.info("all_colors_on_two_edges target_edge_colors %s" % pformat(target_edge_colors))
            #log.info("all_colors_on_two_edges sister_wing_edge_colors %s" % pformat(sister_wing_edge_colors))
            #log.info("all_colors_on_two_edges combined %s" % pformat(combined_edge_colors))
            return True

        return False

    def pair_two_sister_edges_555(self, pre_solution_len, pre_non_paired_wings_count, pre_non_paired_edges_count):
        """
        This only works when there are only two colors of wings to work with. This
        is always the case for the last two edges but it can happen prior to that
        as well.
        """
        if pre_non_paired_edges_count == 2:
            self.position_last_two_edges_555()
            all_edges_should_pair = True
        else:
            if self.all_colors_on_two_edges():
                self.position_sister_edges_555()
                all_edges_should_pair = False
            else:
                return False

        pattern_id = self.get_two_edge_pattern_id()
        # log.info("pattern_id: %d" % pattern_id)

        # No 2 on https://imgur.com/r/all/wsTqj
        # 12 moves, pairs 2
        if pattern_id == 2:
            expected_pair_count = 2

            for step in "Lw' U2 Lw' U2 F2 Lw' F2 Rw U2 Rw' U2 Lw2".split():
                self.rotate(step)

        # No 3 on https://imgur.com/r/all/wsTqj
        # 7 moves, pairs 3
        elif pattern_id == 3:
            expected_pair_count = 3

            for step in "Dw R F' U R' F Dw'".split():
                self.rotate(step)

        # No 4 on https://imgur.com/r/all/wsTqj
        # 9 moves, pairs 4
        elif pattern_id == 4:
            expected_pair_count = 3

            for step in "Dw' L' U' L F' L F L' Dw".split():
                self.rotate(step)

        # 6, 7, and 8 are the scenarios where the outsided wings are paired...so these are
        # the only ones you hit if you use the 4x4x4 edge solver to pair all of the outside
        # wings first.
        #
        # No 6 on https://imgur.com/r/all/wsTqj
        # 8 moves, pairs 4
        elif pattern_id == 6:
            expected_pair_count = 4

            for step in "Uw2 Rw2 F2 Uw2 U2 F2 Rw2 Uw2".split():
                self.rotate(step)

        # No 7 on https://imgur.com/r/all/wsTqj
        # 10 moves, pairs 4
        elif pattern_id == 7:
            expected_pair_count = 4

            for step in "F2 Rw D2 Rw' F2 U2 F2 Lw B2 Lw'".split():
                self.rotate(step)

        # No 8 on https://imgur.com/r/all/wsTqj
        # 14 moves, pairs 4
        elif pattern_id == 8:
            expected_pair_count = 4

            for step in "Rw2 B2 Rw' U2 Rw' U2 B2 Rw' B2 Rw B2 Rw' B2 Rw2".split():
                self.rotate(step)

        # No 9 on https://imgur.com/r/all/wsTqj
        # 13 moves, pairs 4
        elif pattern_id == 9:
            expected_pair_count = 4

            for step in "Lw U2 Lw2 U2 Lw' U2 Lw U2 Lw' U2 Lw2 U2 Lw".split():
                self.rotate(step)

        # No 10 on https://imgur.com/r/all/wsTqj
        # 13 moves, pairs 4
        elif pattern_id == 10:
            expected_pair_count = 4

            for step in "Rw' U2 Rw2 U2 Rw U2 Rw' U2 Rw U2 Rw2 U2 Rw'".split():
                self.rotate(step)

        else:
            raise SolveError("unexpected pattern_id %d" % pattern_id)

        post_solution_len = self.get_solution_len_minus_rotates(self.solution)
        post_non_paired_edges_count = self.get_non_paired_edges_count()
        post_non_paired_wings_count = self.get_non_paired_wings_count()
        wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count

        log.info("pair_two_sister_edges_555() paired %d wings in %d moves (%d left to pair, %d steps in)" %
            (wings_paired,
             post_solution_len - pre_solution_len,
             post_non_paired_wings_count,
             post_solution_len))

        if wings_paired < expected_pair_count:
            raise SolveError("Paired %d wings, expected to pair %d, pattern_id %d" % (wings_paired, expected_pair_count, pattern_id))

        if all_edges_should_pair and post_non_paired_edges_count:
            raise SolveError("All edges should be paired")

        return True

    def pair_four_or_six_wings_555(self, wing_to_pair, pre_non_paired_edges_count):
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        log.info("pair_four_or_six_wings_555()")
        # log.info("PREP-FOR-3Uw-SLICE (begin)")

        (target_wing, sister_wing1, sister_wing2, sister_wing3, steps) = self.get_sister_wings_slice_forward_555(pre_non_paired_edges_count, original_non_paired_wings_count)

        if target_wing is None:
            log.info("pair_four_or_six_wings_555() failed...get_sister_wings_slice_forward_555")
            #raise SolveError("pair_four_or_six_wings_555() failed...get_sister_wings_slice_forward_555")
            return False

        for step in steps:
            self.rotate(step)

        # At this point we are setup to slice forward and pair 3 edges
        # log.info("PREP-FOR-3Uw-SLICE (end)....SLICE (begin), %d left to pair" % self.get_non_paired_wings_count())
        # 3Uw Uw'
        if self.use_pair_outside_edges:
            self.rotate("Uw'")
        self.rotate("Dw")
        self.rotate_y()

        #log.info("SLICE (end), %d left to pair" % self.get_non_paired_wings_count())
        post_slice_forward_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_forward_solution_len = self.get_solution_len_minus_rotates(self.solution)

        log.info("pair_four_or_six_wings_555() paired %d wings in %d moves on slice forward (%d left to pair, %d steps in)" %
            (original_non_paired_wings_count - post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len - original_solution_len,
             post_slice_forward_non_paired_wings_count,
             post_slice_forward_solution_len))

        # setup for slice back
        placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

        # We paired all 8 wings on the slice forward so rotate the edges from U and D onto L and F and check again
        if not placed_unpaired_wing:
            self.rotate("R")
            self.rotate("L'")
            self.rotate("U")
            self.rotate("D")
            self.rotate("R'")
            self.rotate("L")
            placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

            if not placed_unpaired_wing:
                log.info("pair_four_or_six_wings_555() failed...no unpaired wings to move to F-east")
                return False

        #log.info("PREP-FOR-3Uw'-SLICE-BACK (end)...SLICE BACK (begin), %d left to pair" % self.get_non_paired_wings_count())
        # 3Uw' Uw
        if self.use_pair_outside_edges:
            self.rotate("Uw")
        self.rotate("Dw'")
        self.rotate_y()
        #log.info("SLICE BACK (end), %d left to pair" % self.get_non_paired_wings_count())

        post_slice_back_non_paired_wings_count = self.get_non_paired_wings_count()
        post_slice_back_solution_len = self.get_solution_len_minus_rotates(self.solution)
        wings_paired = post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count

        log.info("pair_four_or_six_wings_555() paired %d wings in %d moves on slice back (%d left to pair, %d steps in)" %
            (post_slice_forward_non_paired_wings_count - post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len - post_slice_forward_solution_len,
             post_slice_back_non_paired_wings_count,
             post_slice_back_solution_len))

        if wings_paired < 1:
            raise SolveError("Paired %d wings" % wings_paired)

        return True

    def pair_checkboard_edge_555(self, pre_solution_len, pre_non_paired_wings_count):
        """
        We need to rotate the middle wing in place, this is needed when it is next to
        its two sister wings but is just rotated the wrong way

        No 1 is when there is only one edge like this, No 5 is when there are two. Ideally
        we want the No 5 scenario as it pairs two wings in 9 moves where No 1 pairs 1 wing
        in 15 moves.
        """

        if (self.state[35] == self.state[45] and
            self.state[56] == self.state[66] and
            self.state[56] == self.state[40] and
            self.state[35] == self.state[61]):
            is_checkerboard = True
        else:
            is_checkerboard = False

        if is_checkerboard:
            expected_pair_count = None

            # F-east
            if self.state[60] == self.state[86] and self.state[81] == self.state[65] and self.state[60] == self.state[70] and self.state[81] == self.state[91]:
                pattern_id = 5
                expected_pair_count = 4

            # L-east
            elif self.state[31] == self.state[115] and self.state[36] == self.state[110] and self.state[31] == self.state[41] and self.state[110] == self.state[120]:
                self.rotate_y_reverse()
                pattern_id = 5
                expected_pair_count = 4

            # U-east
            elif self.state[10] == self.state[78] and self.state[15] == self.state[79] and self.state[10] == self.state[20] and self.state[77] == self.state[79]:
                self.rotate("R'")
                pattern_id = 5
                expected_pair_count = 4

            # D-east
            elif self.state[135] == self.state[98] and self.state[140] == self.state[97] and self.state[135] == self.state[145] and self.state[97] == self.state[99]:
                self.rotate("R")
                pattern_id = 5
                expected_pair_count = 4

            # R-east
            elif self.state[85] == self.state[111] and self.state[90] == self.state[106] and self.state[85] == self.state[95] and self.state[106] == self.state[116]:
                self.rotate("R2")
                pattern_id = 5
                expected_pair_count = 4

            # U-north
            elif self.state[2] == self.state[103] and self.state[3] == self.state[104] and self.state[2] == self.state[4] and self.state[102] == self.state[104]:
                self.rotate("U")
                self.rotate("R'")
                pattern_id = 5
                expected_pair_count = 4

            # U-south
            elif self.state[52] == self.state[23] and self.state[22] == self.state[53] and self.state[52] == self.state[54] and self.state[22] == self.state[24]:
                self.rotate("U'")
                self.rotate("R'")
                pattern_id = 5
                expected_pair_count = 4

            # U-west
            elif self.state[6] == self.state[28] and self.state[11] == self.state[27] and self.state[6] == self.state[16] and self.state[27] == self.state[29]:
                self.rotate("U2")
                self.rotate("R'")
                pattern_id = 5
                expected_pair_count = 4

            # D-north
            elif self.state[72] == self.state[128] and self.state[73] == self.state[127] and self.state[72] == self.state[74] and self.state[127] == self.state[129]:
                self.rotate("D")
                self.rotate("R")
                pattern_id = 5
                expected_pair_count = 4

            # D-south
            elif self.state[147] == self.state[123] and self.state[148] == self.state[124] and self.state[147] == self.state[149] and self.state[122] == self.state[124]:
                self.rotate("D'")
                self.rotate("R")
                pattern_id = 5
                expected_pair_count = 4

            # D-west
            elif self.state[131] == self.state[48] and self.state[136] == self.state[49] and self.state[131] == self.state[141] and self.state[47] == self.state[49]:
                self.rotate("D2")
                self.rotate("R")
                pattern_id = 5
                expected_pair_count = 4

            else:
                expected_pair_count = 2

                # Move any unpaired edge to F-east so we can use pattern_id 5 instead and save ourselves 6 steps
                # It must be an edge without any paired wings.
                if self.sideR.west_edge_non_paired_wings_count() == 2:
                    pattern_id = 5

                elif self.sideL.west_edge_non_paired_wings_count() == 2:
                    self.rotate_y_reverse()
                    self.rotate_z()
                    self.rotate_z()
                    pattern_id = 5

                elif self.sideR.north_edge_non_paired_wings_count() == 2:
                    self.rotate("R'")
                    pattern_id = 5

                elif self.sideR.east_edge_non_paired_wings_count() == 2:
                    self.rotate("R2")
                    pattern_id = 5

                elif self.sideR.south_edge_non_paired_wings_count() == 2:
                    self.rotate("R")
                    pattern_id = 5

                elif self.sideD.north_edge_non_paired_wings_count() == 2:
                    self.rotate("D")
                    self.rotate("R")
                    pattern_id = 5

                elif self.sideD.south_edge_non_paired_wings_count() == 2:
                    self.rotate("D'")
                    self.rotate("R")
                    pattern_id = 5

                elif self.sideD.east_edge_non_paired_wings_count() == 2:
                    self.rotate("D2")
                    self.rotate("R")
                    pattern_id = 5

                elif self.sideU.north_edge_non_paired_wings_count() == 2:
                    self.rotate("U")
                    self.rotate("R'")
                    pattern_id = 5

                elif self.sideU.west_edge_non_paired_wings_count() == 2:
                    self.rotate("U2")
                    self.rotate("R'")
                    pattern_id = 5

                elif self.sideU.south_edge_non_paired_wings_count() == 2:
                    self.rotate("U'")
                    self.rotate("R'")
                    pattern_id = 5

                else:
                    pattern_id = 1

            # Flip one middle wing in place
            # No 1 at https://i.imgur.com/wsTqj.png
            if pattern_id == 1:
                self.rotate_x()
                self.rotate_y_reverse()

                for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                    self.rotate(step)

            # Flip two middle wings in place
            # No 5 at https://i.imgur.com/wsTqj.png
            elif pattern_id == 5:
                for step in "Dw Uw' R F' U R' F Dw' Uw".split():
                    self.rotate(step)

            post_solution_len = self.get_solution_len_minus_rotates(self.solution)
            post_non_paired_edges_count = self.get_non_paired_edges_count()
            post_non_paired_wings_count = self.get_non_paired_wings_count()
            wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count

            log.info("pair_checkboard_edge_555() paired %d wings in %d moves (%d left to pair, %d steps in)" %
                (wings_paired,
                 post_solution_len - pre_solution_len,
                 post_non_paired_wings_count,
                 post_solution_len))

            if not self.use_pair_outside_edges:
                expected_pair_count = int(expected_pair_count/2)

            if wings_paired < expected_pair_count:
                raise SolveError("Paired %d wings, expected to pair %d, pattern_id %d" % (wings_paired, expected_pair_count, pattern_id))

            return True

        return False

    def pair_one_wing_555(self):
        original_solution_len = self.get_solution_len_minus_rotates(self.solution)
        original_non_paired_wings_count = self.get_non_paired_wings_count()

        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        log.info("pair_one_wing_555() called (%d left to pair, %d steps in)" % (original_non_paired_wings_count, original_solution_len))

        # Work with the edge at the bottom of F-west
        target_wing = self.sideF.edge_west_pos[-1]
        target_wing_value = self.get_wing_value(target_wing)
        sister_wings = self.get_wings(target_wing)
        checkerboard = False

        # This is the scenario where the center edge is beside its two siblings it
        # just needs to be flipped in place.
        if not sister_wings:
            raise SolveError("We should not be here")


        # Is this a checkerboard?
        if (40, 61) in sister_wings:
            checkerboard = True
            sister_wing = (40, 61)

        elif (61, 40) in sister_wings:
            checkerboard = True
            sister_wing = (61, 40)

        else:
            # Pick the sister_wing that is in the middle of the edge
            for x in sister_wings:
                if x in ((3, 103), (103, 3),
                         (11, 28), (28, 11),
                         (15, 78), (78, 15),
                         (23, 53), (53, 23),
                         (36, 115), (115, 36),
                         (40, 61), (61, 40),
                         (65, 86), (86, 65),
                         (48, 136), (136, 48),
                         (73, 128), (128, 73),
                         (90, 111), (111, 90),
                         (98, 140), (140, 98),
                         (123, 148), (148, 123)):
                    sister_wing = x
                    break

            else:
                self.print_cube()
                raise SolveError("Could not find sister wing in the middle: %s" % pformat(sister_wings))

        if checkerboard:
            # Flip one middle wing in place
            # No 1 at https://i.imgur.com/wsTqj.png
            self.rotate_x()
            self.rotate_y_reverse()
            for step in "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2".split():
                self.rotate(step)
            return True

        else:

            # Move sister wing to F-east
            self.move_wing_to_F_east(sister_wing)

            # We must have a sister wing at (65, 86)
            sister_wings_on_FR_edge = self.get_wings_on_edge(target_wing, 'F', 'R')
            if (65, 86) not in sister_wings_on_FR_edge:
                self.print_cube()
                log.info("sister_wings_on_FR_edge %s" % pformat(sister_wings_on_FR_edge))
                raise SolveError("sister wing should be on FR edge")

            sister_wing = (65, 86)
            sister_wing_value = self.get_wing_value(sister_wing)

            # The sister wing is in the right location but does it need to be flipped?
            if target_wing_value != sister_wing_value:
                for step in ("R", "U'", "B'", "R2"):
                    self.rotate(step)

            if sister_wing[0] == 65:
                # 3Uw Uw'
                if self.use_pair_outside_edges:
                    self.rotate("Uw'")
                self.rotate("Dw")
                self.rotate_y()

                placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

                # We paired all 8 wings on the slice forward so rotate the edges from U and D onto L and F and check again
                if not placed_unpaired_wing:
                    self.rotate("R")
                    self.rotate("L'")
                    self.rotate("U")
                    self.rotate("D")
                    self.rotate("R'")
                    self.rotate("L")
                    placed_unpaired_wing = self.rotate_unpaired_wing_to_bottom_of_F_east()

                    if not placed_unpaired_wing:
                        log.info("pair_four_or_six_wings_555() failed...no unpaired wings to move to F-east")
                        return False

                #log.info("PREP-FOR-3Uw'-SLICE-BACK (end)...SLICE BACK (begin), %d left to pair" % self.get_non_paired_wings_count())
                #self.print_cube()

                # 3Uw' Uw
                if self.use_pair_outside_edges:
                    self.rotate("Uw")
                self.rotate("Dw'")
                self.rotate_y_reverse()
                #log.info("SLICE BACK (end), %d left to pair" % self.get_non_paired_wings_count())

            else:
                raise SolveError("sister_wing %s is in the wrong position" % str(sister_wing))

            current_non_paired_wings_count = self.get_non_paired_wings_count()
        wings_paired = original_non_paired_wings_count - current_non_paired_wings_count
        log.info("pair_one_wing_555() paired %d wings, added %d steps" % (wings_paired, self.get_solution_len_minus_rotates(self.solution) - original_solution_len))

        if self.use_pair_outside_edges:
            if self.state[35] != self.state[45] or self.state[56] != self.state[66]:
                raise SolveError("outside edges have been broken")

        if wings_paired < 1:
            return False
            #raise SolveError("Paired %d wings" % wings_paired)
        else:
            return True

    def pair_edge(self, edge_to_pair):

        #log.info("pair_edge() with edge_to_pair %s" % pformat(edge_to_pair))
        pre_solution_len = self.get_solution_len_minus_rotates(self.solution)
        pre_non_paired_edges_count = self.get_non_paired_edges_count()
        pre_non_paired_wings_count = self.get_non_paired_wings_count()
        self.rotate_edge_to_F_west(edge_to_pair[0])

        # We need to rotate this around so the two unpaired wings are at the bottom of F-west
        if self.state[40] == self.state[45] and self.state[61] == self.state[66]:
            self.rotate_z()
            self.rotate_z()
            self.rotate_y()

        log.info("pair_edge() for %s (%d wings and %d edges left to pair)" % (pformat(edge_to_pair), pre_non_paired_wings_count, pre_non_paired_edges_count))

        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        if self.use_pair_outside_edges:
            if self.state[35] != self.state[45] or self.state[56] != self.state[66]:
                raise SolveError("outside edges have been broken")

        if self.pair_checkboard_edge_555(pre_solution_len, pre_non_paired_wings_count):
            return True

        # Pair two sister edges...all colors involved live on two edges so this
        # is just like solving the last two edges
        if self.pair_two_sister_edges_555(pre_solution_len, pre_non_paired_wings_count, pre_non_paired_edges_count):
            return True

        original_state = self.state[:]
        original_solution = self.solution[:]

        if self.sideF.west_edge_paired():
            raise SolveError("F-west should not be paired")

        if pre_non_paired_edges_count >= 4:
            if self.pair_four_or_six_wings_555(edge_to_pair[0], pre_non_paired_edges_count):
                return True
            else:
                self.state = original_state[:]
                self.solution = original_solution[:]

        if self.pair_one_wing_555():
            return True
        else:
            self.state = original_state[:]
            self.solution = original_solution[:]
            return False

    def group_edges_bfs(self):
        """
        This works and finds a shorter solution than the DFS that is
        group_edges_recursive() but it takes about 30x longer to do so
        """
        original_state = self.state[:]
        original_solution = self.solution[:]

        non_paired_edges = self.get_non_paired_edges()
        workq = deque([])

        for edge_to_pair in non_paired_edges:
            workq.append([edge_to_pair,])

        state_cache = {}
        solution_cache = {}

        while workq:
            self.state = original_state[:]
            self.solution = original_solution[:]

            edges_to_pair = workq.popleft()
            edges_paired_ok = True
            all_but_last_edges_to_pair = tuple(edges_to_pair[0:-1])

            if all_but_last_edges_to_pair in state_cache:
                self.state = state_cache[all_but_last_edges_to_pair][:]
                self.solution = solution_cache[all_but_last_edges_to_pair][:]
                edge_to_pair = edges_to_pair[-1]

                if not self.pair_edge(edge_to_pair):
                    edges_paired_ok = False
            else:

                for edge_to_pair in edges_to_pair:
                    if not self.pair_edge(edge_to_pair):
                        edges_paired_ok = False
                        break

            if edges_paired_ok:
                state_cache[tuple(edges_to_pair)] = self.state[:]
                solution_cache[tuple(edges_to_pair)] = self.solution[:]

                non_paired_edges = self.get_non_paired_edges()

                if non_paired_edges:
                    for edge_to_pair in non_paired_edges:
                        workq.append(edges_to_pair + [edge_to_pair])

                else:
                    # There are no edges left to pair, note how many steps it took pair them all
                    edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len

                    # Remember the solution that pairs all edges in the least number of moves
                    if edge_solution_len < self.min_edge_solution_len:
                        self.min_edge_solution_len = edge_solution_len
                        self.min_edge_solution = self.solution[:]
                        self.min_edge_solution_state = self.state[:]
                        log.warning("NEW MIN: edges paired in %d steps" % self.min_edge_solution_len)

                        # since this is BFS we can go ahead and return
                        return

    def group_edges_recursive(self, depth, edge_to_pair):

        # Should we both going down this branch or should we prune it?
        pre_non_paired_wings_count = len(self.get_non_paired_wings())
        pre_non_paired_edges_count = len(self.get_non_paired_edges())
        edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len
        edge_paired = False

        log.info("")
        log.info("group_edges_recursive(%d) called with edge_to_pair %s (%d edges and %d wings left to pair, min solution len %s, current solution len %d)" %
            (depth,
             pformat(edge_to_pair),
             pre_non_paired_edges_count,
             pre_non_paired_wings_count,
             self.min_edge_solution_len,
             edge_solution_len))

        # Should we continue down this branch or should we prune it? An estimate
        # of 2.5 moves to pair an edge is a good target to hit so if the current number of
        # steps plus 2.5 * pre_non_paired_wings_count is greater than our current minimum
        # there isn't any point in continuing down this branch so prune it and save
        # some CPU cycles.
        #
        # Whether we use 2.5, 3.0, or 3.5 makes a big differnce in how fast the
        # solver runs and how short the solution is. All of the data below is from
        # running the solver on my laptop.
        #
        #   For 5x5x5 test with 2.5 takes 16m 36s to solve 50 cubes, avg solution 120 steps
        #   For 5x5x5 test with 3.0 takes 1m 44s to solve 50 cubes, avg solution 125 steps
        #   For 5x5x5 test with 3.1 takes 2m 01s to solve 50 cubes, avg solution 126 steps
        #   For 5x5x5 test with 3.2 takes 1m 10s to solve 50 cubes, avg solution 127 steps
        #   For 5x5x5 test with 3.3 takes 52s to solve 50 cubes, avg solution 127 steps
        #   For 5x5x5 test with 3.4 takes 35s to solve 50 cubes, avg solution 129 steps
        #   For 5x5x5 test with 3.5 takes 30s to solve 50 cubes, avg solution 131 steps
        #
        #   For our default 7x7x7 cube with 2.5 it takes 13.1s,110/300 edge/total steps
        #   For our default 7x7x7 cube with 3.0 it takes 6.8s, 125/315 edge/total steps
        #   For our default 7x7x7 cube with 3.4 it takes 1.7s, 135/327 edge/total steps
        #   For our default 7x7x7 cube with 3.5 it takes 1.7s, 135/327 edge/total steps

        if self.cpu_mode == 'max':
            estimate_per_wing = 2.0
        else:
            estimate_per_wing = 3.4

        # 9 moves is the least number of moves I know of that will pair the last 2 wings
        if pre_non_paired_wings_count == 2:
            estimated_solution_len = edge_solution_len + 9
        elif pre_non_paired_wings_count == 3:
            estimated_solution_len = edge_solution_len + 7
        elif pre_non_paired_wings_count == 4:
            estimated_solution_len = edge_solution_len + 8
        else:
            estimated_solution_len = edge_solution_len + (estimate_per_wing * pre_non_paired_wings_count)

        if estimated_solution_len >= self.min_edge_solution_len:
            log.info("PRUNE: %s non-paired wings, estimated_solution_len %d, %s + (%s * %d) > %s" %
                (pre_non_paired_wings_count, estimated_solution_len, edge_solution_len, estimate_per_wing, pre_non_paired_wings_count, self.min_edge_solution_len))
            return False

        # The only time this will be None is on the initial call
        if edge_to_pair:
            edge_paired = self.pair_edge(edge_to_pair)
        else:
            edge_paired = True

        non_paired_edges = self.get_non_paired_edges()

        # call group_edges_recursive for each edge left to pair
        if non_paired_edges:
            post_non_paired_wings_count = len(self.get_non_paired_wings())
            edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len
            wings_paired = pre_non_paired_wings_count - post_non_paired_wings_count
            original_state = self.state[:]
            original_solution = self.solution[:]

            if edge_paired and edge_solution_len < self.min_edge_solution_len:
                log.info("group_edges_recursive(%d) paired %d" % (depth, wings_paired))
                for edge in non_paired_edges:
                    self.group_edges_recursive(depth+1, edge)
                    self.state = original_state[:]
                    self.solution = original_solution[:]
        else:

            # There are no edges left to pair, note how many steps it took pair them all
            edge_solution_len = self.get_solution_len_minus_rotates(self.solution) - self.center_solution_len

            # Remember the solution that pairs all edges in the least number of moves
            if edge_solution_len < self.min_edge_solution_len:
                self.min_edge_solution_len = edge_solution_len
                self.min_edge_solution = self.solution[:]
                self.min_edge_solution_state = self.state[:]
                log.warning("NEW MIN: edges paired in %d steps" % self.min_edge_solution_len)
            #else:
            #    log.info("LOST   : edges paired in %s vs MIN %d steps" % (edge_solution_len, self.min_edge_solution_len))

            return True

    def group_edges(self):

        if self.edges_paired():
            self.solution.append('EDGES_GROUPED')
            return

        depth = 0
        self.lt_init()

        if self.use_pair_outside_edges:
            self.pair_outside_edges()
            self.print_cube()
            log.info('outside edges paired, %d steps in' % self.get_solution_len_minus_rotates(self.solution))

        self.center_solution_len = self.get_solution_len_minus_rotates(self.solution)

        use_recursive = True
        #use_recursive = False

        if use_recursive:
            self.min_edge_solution_len = 9999
            self.min_edge_solution = None
            self.min_edge_solution_state = None
            self.group_edges_recursive(depth, None)
            #self.group_edges_bfs()
            self.state = self.min_edge_solution_state[:]
            self.solution = self.min_edge_solution[:]
        else:
            while True:

                # If all edges are paired break out of the loop
                if self.edges_paired():
                    break

                non_paired_wings_count = self.get_non_paired_wings_count()
                non_paired_edges_count = self.get_non_paired_edges_count()
                log.info("%s: %d wings not paired, %d edges not paired" % (self, non_paired_wings_count, non_paired_edges_count))

                self.lt_edges.solve()

        log.info("%s: edges paired, %d steps in" % (self, self.get_solution_len_minus_rotates(self.solution)))
        self.solution.append('EDGES_GROUPED')


tsai_phase2_orient_edges_555 = {
    (2, 104, 'B', 'D'): 'D',
    (2, 104, 'B', 'L'): 'D',
    (2, 104, 'B', 'R'): 'D',
    (2, 104, 'B', 'U'): 'D',
    (2, 104, 'D', 'B'): 'U',
    (2, 104, 'D', 'F'): 'U',
    (2, 104, 'D', 'L'): 'U',
    (2, 104, 'D', 'R'): 'U',
    (2, 104, 'F', 'D'): 'D',
    (2, 104, 'F', 'L'): 'D',
    (2, 104, 'F', 'R'): 'D',
    (2, 104, 'F', 'U'): 'D',
    (2, 104, 'L', 'B'): 'U',
    (2, 104, 'L', 'D'): 'D',
    (2, 104, 'L', 'F'): 'U',
    (2, 104, 'L', 'U'): 'D',
    (2, 104, 'R', 'B'): 'U',
    (2, 104, 'R', 'D'): 'D',
    (2, 104, 'R', 'F'): 'U',
    (2, 104, 'R', 'U'): 'D',
    (2, 104, 'U', 'B'): 'U',
    (2, 104, 'U', 'F'): 'U',
    (2, 104, 'U', 'L'): 'U',
    (2, 104, 'U', 'R'): 'U',
    (4, 102, 'B', 'D'): 'U',
    (4, 102, 'B', 'L'): 'U',
    (4, 102, 'B', 'R'): 'U',
    (4, 102, 'B', 'U'): 'U',
    (4, 102, 'D', 'B'): 'D',
    (4, 102, 'D', 'F'): 'D',
    (4, 102, 'D', 'L'): 'D',
    (4, 102, 'D', 'R'): 'D',
    (4, 102, 'F', 'D'): 'U',
    (4, 102, 'F', 'L'): 'U',
    (4, 102, 'F', 'R'): 'U',
    (4, 102, 'F', 'U'): 'U',
    (4, 102, 'L', 'B'): 'D',
    (4, 102, 'L', 'D'): 'U',
    (4, 102, 'L', 'F'): 'D',
    (4, 102, 'L', 'U'): 'U',
    (4, 102, 'R', 'B'): 'D',
    (4, 102, 'R', 'D'): 'U',
    (4, 102, 'R', 'F'): 'D',
    (4, 102, 'R', 'U'): 'U',
    (4, 102, 'U', 'B'): 'D',
    (4, 102, 'U', 'F'): 'D',
    (4, 102, 'U', 'L'): 'D',
    (4, 102, 'U', 'R'): 'D',
    (6, 27, 'B', 'D'): 'U',
    (6, 27, 'B', 'L'): 'U',
    (6, 27, 'B', 'R'): 'U',
    (6, 27, 'B', 'U'): 'U',
    (6, 27, 'D', 'B'): 'D',
    (6, 27, 'D', 'F'): 'D',
    (6, 27, 'D', 'L'): 'D',
    (6, 27, 'D', 'R'): 'D',
    (6, 27, 'F', 'D'): 'U',
    (6, 27, 'F', 'L'): 'U',
    (6, 27, 'F', 'R'): 'U',
    (6, 27, 'F', 'U'): 'U',
    (6, 27, 'L', 'B'): 'D',
    (6, 27, 'L', 'D'): 'U',
    (6, 27, 'L', 'F'): 'D',
    (6, 27, 'L', 'U'): 'U',
    (6, 27, 'R', 'B'): 'D',
    (6, 27, 'R', 'D'): 'U',
    (6, 27, 'R', 'F'): 'D',
    (6, 27, 'R', 'U'): 'U',
    (6, 27, 'U', 'B'): 'D',
    (6, 27, 'U', 'F'): 'D',
    (6, 27, 'U', 'L'): 'D',
    (6, 27, 'U', 'R'): 'D',
    (10, 79, 'B', 'D'): 'D',
    (10, 79, 'B', 'L'): 'D',
    (10, 79, 'B', 'R'): 'D',
    (10, 79, 'B', 'U'): 'D',
    (10, 79, 'D', 'B'): 'U',
    (10, 79, 'D', 'F'): 'U',
    (10, 79, 'D', 'L'): 'U',
    (10, 79, 'D', 'R'): 'U',
    (10, 79, 'F', 'D'): 'D',
    (10, 79, 'F', 'L'): 'D',
    (10, 79, 'F', 'R'): 'D',
    (10, 79, 'F', 'U'): 'D',
    (10, 79, 'L', 'B'): 'U',
    (10, 79, 'L', 'D'): 'D',
    (10, 79, 'L', 'F'): 'U',
    (10, 79, 'L', 'U'): 'D',
    (10, 79, 'R', 'B'): 'U',
    (10, 79, 'R', 'D'): 'D',
    (10, 79, 'R', 'F'): 'U',
    (10, 79, 'R', 'U'): 'D',
    (10, 79, 'U', 'B'): 'U',
    (10, 79, 'U', 'F'): 'U',
    (10, 79, 'U', 'L'): 'U',
    (10, 79, 'U', 'R'): 'U',
    (16, 29, 'B', 'D'): 'D',
    (16, 29, 'B', 'L'): 'D',
    (16, 29, 'B', 'R'): 'D',
    (16, 29, 'B', 'U'): 'D',
    (16, 29, 'D', 'B'): 'U',
    (16, 29, 'D', 'F'): 'U',
    (16, 29, 'D', 'L'): 'U',
    (16, 29, 'D', 'R'): 'U',
    (16, 29, 'F', 'D'): 'D',
    (16, 29, 'F', 'L'): 'D',
    (16, 29, 'F', 'R'): 'D',
    (16, 29, 'F', 'U'): 'D',
    (16, 29, 'L', 'B'): 'U',
    (16, 29, 'L', 'D'): 'D',
    (16, 29, 'L', 'F'): 'U',
    (16, 29, 'L', 'U'): 'D',
    (16, 29, 'R', 'B'): 'U',
    (16, 29, 'R', 'D'): 'D',
    (16, 29, 'R', 'F'): 'U',
    (16, 29, 'R', 'U'): 'D',
    (16, 29, 'U', 'B'): 'U',
    (16, 29, 'U', 'F'): 'U',
    (16, 29, 'U', 'L'): 'U',
    (16, 29, 'U', 'R'): 'U',
    (20, 77, 'B', 'D'): 'U',
    (20, 77, 'B', 'L'): 'U',
    (20, 77, 'B', 'R'): 'U',
    (20, 77, 'B', 'U'): 'U',
    (20, 77, 'D', 'B'): 'D',
    (20, 77, 'D', 'F'): 'D',
    (20, 77, 'D', 'L'): 'D',
    (20, 77, 'D', 'R'): 'D',
    (20, 77, 'F', 'D'): 'U',
    (20, 77, 'F', 'L'): 'U',
    (20, 77, 'F', 'R'): 'U',
    (20, 77, 'F', 'U'): 'U',
    (20, 77, 'L', 'B'): 'D',
    (20, 77, 'L', 'D'): 'U',
    (20, 77, 'L', 'F'): 'D',
    (20, 77, 'L', 'U'): 'U',
    (20, 77, 'R', 'B'): 'D',
    (20, 77, 'R', 'D'): 'U',
    (20, 77, 'R', 'F'): 'D',
    (20, 77, 'R', 'U'): 'U',
    (20, 77, 'U', 'B'): 'D',
    (20, 77, 'U', 'F'): 'D',
    (20, 77, 'U', 'L'): 'D',
    (20, 77, 'U', 'R'): 'D',
    (22, 52, 'B', 'D'): 'U',
    (22, 52, 'B', 'L'): 'U',
    (22, 52, 'B', 'R'): 'U',
    (22, 52, 'B', 'U'): 'U',
    (22, 52, 'D', 'B'): 'D',
    (22, 52, 'D', 'F'): 'D',
    (22, 52, 'D', 'L'): 'D',
    (22, 52, 'D', 'R'): 'D',
    (22, 52, 'F', 'D'): 'U',
    (22, 52, 'F', 'L'): 'U',
    (22, 52, 'F', 'R'): 'U',
    (22, 52, 'F', 'U'): 'U',
    (22, 52, 'L', 'B'): 'D',
    (22, 52, 'L', 'D'): 'U',
    (22, 52, 'L', 'F'): 'D',
    (22, 52, 'L', 'U'): 'U',
    (22, 52, 'R', 'B'): 'D',
    (22, 52, 'R', 'D'): 'U',
    (22, 52, 'R', 'F'): 'D',
    (22, 52, 'R', 'U'): 'U',
    (22, 52, 'U', 'B'): 'D',
    (22, 52, 'U', 'F'): 'D',
    (22, 52, 'U', 'L'): 'D',
    (22, 52, 'U', 'R'): 'D',
    (24, 54, 'B', 'D'): 'D',
    (24, 54, 'B', 'L'): 'D',
    (24, 54, 'B', 'R'): 'D',
    (24, 54, 'B', 'U'): 'D',
    (24, 54, 'D', 'B'): 'U',
    (24, 54, 'D', 'F'): 'U',
    (24, 54, 'D', 'L'): 'U',
    (24, 54, 'D', 'R'): 'U',
    (24, 54, 'F', 'D'): 'D',
    (24, 54, 'F', 'L'): 'D',
    (24, 54, 'F', 'R'): 'D',
    (24, 54, 'F', 'U'): 'D',
    (24, 54, 'L', 'B'): 'U',
    (24, 54, 'L', 'D'): 'D',
    (24, 54, 'L', 'F'): 'U',
    (24, 54, 'L', 'U'): 'D',
    (24, 54, 'R', 'B'): 'U',
    (24, 54, 'R', 'D'): 'D',
    (24, 54, 'R', 'F'): 'U',
    (24, 54, 'R', 'U'): 'D',
    (24, 54, 'U', 'B'): 'U',
    (24, 54, 'U', 'F'): 'U',
    (24, 54, 'U', 'L'): 'U',
    (24, 54, 'U', 'R'): 'U',
    (27, 6, 'B', 'D'): 'D',
    (27, 6, 'B', 'L'): 'D',
    (27, 6, 'B', 'R'): 'D',
    (27, 6, 'B', 'U'): 'D',
    (27, 6, 'D', 'B'): 'U',
    (27, 6, 'D', 'F'): 'U',
    (27, 6, 'D', 'L'): 'U',
    (27, 6, 'D', 'R'): 'U',
    (27, 6, 'F', 'D'): 'D',
    (27, 6, 'F', 'L'): 'D',
    (27, 6, 'F', 'R'): 'D',
    (27, 6, 'F', 'U'): 'D',
    (27, 6, 'L', 'B'): 'U',
    (27, 6, 'L', 'D'): 'D',
    (27, 6, 'L', 'F'): 'U',
    (27, 6, 'L', 'U'): 'D',
    (27, 6, 'R', 'B'): 'U',
    (27, 6, 'R', 'D'): 'D',
    (27, 6, 'R', 'F'): 'U',
    (27, 6, 'R', 'U'): 'D',
    (27, 6, 'U', 'B'): 'U',
    (27, 6, 'U', 'F'): 'U',
    (27, 6, 'U', 'L'): 'U',
    (27, 6, 'U', 'R'): 'U',
    (29, 16, 'B', 'D'): 'U',
    (29, 16, 'B', 'L'): 'U',
    (29, 16, 'B', 'R'): 'U',
    (29, 16, 'B', 'U'): 'U',
    (29, 16, 'D', 'B'): 'D',
    (29, 16, 'D', 'F'): 'D',
    (29, 16, 'D', 'L'): 'D',
    (29, 16, 'D', 'R'): 'D',
    (29, 16, 'F', 'D'): 'U',
    (29, 16, 'F', 'L'): 'U',
    (29, 16, 'F', 'R'): 'U',
    (29, 16, 'F', 'U'): 'U',
    (29, 16, 'L', 'B'): 'D',
    (29, 16, 'L', 'D'): 'U',
    (29, 16, 'L', 'F'): 'D',
    (29, 16, 'L', 'U'): 'U',
    (29, 16, 'R', 'B'): 'D',
    (29, 16, 'R', 'D'): 'U',
    (29, 16, 'R', 'F'): 'D',
    (29, 16, 'R', 'U'): 'U',
    (29, 16, 'U', 'B'): 'D',
    (29, 16, 'U', 'F'): 'D',
    (29, 16, 'U', 'L'): 'D',
    (29, 16, 'U', 'R'): 'D',
    (31, 110, 'B', 'D'): 'U',
    (31, 110, 'B', 'L'): 'U',
    (31, 110, 'B', 'R'): 'U',
    (31, 110, 'B', 'U'): 'U',
    (31, 110, 'D', 'B'): 'D',
    (31, 110, 'D', 'F'): 'D',
    (31, 110, 'D', 'L'): 'D',
    (31, 110, 'D', 'R'): 'D',
    (31, 110, 'F', 'D'): 'U',
    (31, 110, 'F', 'L'): 'U',
    (31, 110, 'F', 'R'): 'U',
    (31, 110, 'F', 'U'): 'U',
    (31, 110, 'L', 'B'): 'D',
    (31, 110, 'L', 'D'): 'U',
    (31, 110, 'L', 'F'): 'D',
    (31, 110, 'L', 'U'): 'U',
    (31, 110, 'R', 'B'): 'D',
    (31, 110, 'R', 'D'): 'U',
    (31, 110, 'R', 'F'): 'D',
    (31, 110, 'R', 'U'): 'U',
    (31, 110, 'U', 'B'): 'D',
    (31, 110, 'U', 'F'): 'D',
    (31, 110, 'U', 'L'): 'D',
    (31, 110, 'U', 'R'): 'D',
    (35, 56, 'B', 'D'): 'D',
    (35, 56, 'B', 'L'): 'D',
    (35, 56, 'B', 'R'): 'D',
    (35, 56, 'B', 'U'): 'D',
    (35, 56, 'D', 'B'): 'U',
    (35, 56, 'D', 'F'): 'U',
    (35, 56, 'D', 'L'): 'U',
    (35, 56, 'D', 'R'): 'U',
    (35, 56, 'F', 'D'): 'D',
    (35, 56, 'F', 'L'): 'D',
    (35, 56, 'F', 'R'): 'D',
    (35, 56, 'F', 'U'): 'D',
    (35, 56, 'L', 'B'): 'U',
    (35, 56, 'L', 'D'): 'D',
    (35, 56, 'L', 'F'): 'U',
    (35, 56, 'L', 'U'): 'D',
    (35, 56, 'R', 'B'): 'U',
    (35, 56, 'R', 'D'): 'D',
    (35, 56, 'R', 'F'): 'U',
    (35, 56, 'R', 'U'): 'D',
    (35, 56, 'U', 'B'): 'U',
    (35, 56, 'U', 'F'): 'U',
    (35, 56, 'U', 'L'): 'U',
    (35, 56, 'U', 'R'): 'U',
    (41, 120, 'B', 'D'): 'D',
    (41, 120, 'B', 'L'): 'D',
    (41, 120, 'B', 'R'): 'D',
    (41, 120, 'B', 'U'): 'D',
    (41, 120, 'D', 'B'): 'U',
    (41, 120, 'D', 'F'): 'U',
    (41, 120, 'D', 'L'): 'U',
    (41, 120, 'D', 'R'): 'U',
    (41, 120, 'F', 'D'): 'D',
    (41, 120, 'F', 'L'): 'D',
    (41, 120, 'F', 'R'): 'D',
    (41, 120, 'F', 'U'): 'D',
    (41, 120, 'L', 'B'): 'U',
    (41, 120, 'L', 'D'): 'D',
    (41, 120, 'L', 'F'): 'U',
    (41, 120, 'L', 'U'): 'D',
    (41, 120, 'R', 'B'): 'U',
    (41, 120, 'R', 'D'): 'D',
    (41, 120, 'R', 'F'): 'U',
    (41, 120, 'R', 'U'): 'D',
    (41, 120, 'U', 'B'): 'U',
    (41, 120, 'U', 'F'): 'U',
    (41, 120, 'U', 'L'): 'U',
    (41, 120, 'U', 'R'): 'U',
    (45, 66, 'B', 'D'): 'U',
    (45, 66, 'B', 'L'): 'U',
    (45, 66, 'B', 'R'): 'U',
    (45, 66, 'B', 'U'): 'U',
    (45, 66, 'D', 'B'): 'D',
    (45, 66, 'D', 'F'): 'D',
    (45, 66, 'D', 'L'): 'D',
    (45, 66, 'D', 'R'): 'D',
    (45, 66, 'F', 'D'): 'U',
    (45, 66, 'F', 'L'): 'U',
    (45, 66, 'F', 'R'): 'U',
    (45, 66, 'F', 'U'): 'U',
    (45, 66, 'L', 'B'): 'D',
    (45, 66, 'L', 'D'): 'U',
    (45, 66, 'L', 'F'): 'D',
    (45, 66, 'L', 'U'): 'U',
    (45, 66, 'R', 'B'): 'D',
    (45, 66, 'R', 'D'): 'U',
    (45, 66, 'R', 'F'): 'D',
    (45, 66, 'R', 'U'): 'U',
    (45, 66, 'U', 'B'): 'D',
    (45, 66, 'U', 'F'): 'D',
    (45, 66, 'U', 'L'): 'D',
    (45, 66, 'U', 'R'): 'D',
    (47, 141, 'B', 'D'): 'U',
    (47, 141, 'B', 'L'): 'U',
    (47, 141, 'B', 'R'): 'U',
    (47, 141, 'B', 'U'): 'U',
    (47, 141, 'D', 'B'): 'D',
    (47, 141, 'D', 'F'): 'D',
    (47, 141, 'D', 'L'): 'D',
    (47, 141, 'D', 'R'): 'D',
    (47, 141, 'F', 'D'): 'U',
    (47, 141, 'F', 'L'): 'U',
    (47, 141, 'F', 'R'): 'U',
    (47, 141, 'F', 'U'): 'U',
    (47, 141, 'L', 'B'): 'D',
    (47, 141, 'L', 'D'): 'U',
    (47, 141, 'L', 'F'): 'D',
    (47, 141, 'L', 'U'): 'U',
    (47, 141, 'R', 'B'): 'D',
    (47, 141, 'R', 'D'): 'U',
    (47, 141, 'R', 'F'): 'D',
    (47, 141, 'R', 'U'): 'U',
    (47, 141, 'U', 'B'): 'D',
    (47, 141, 'U', 'F'): 'D',
    (47, 141, 'U', 'L'): 'D',
    (47, 141, 'U', 'R'): 'D',
    (49, 131, 'B', 'D'): 'D',
    (49, 131, 'B', 'L'): 'D',
    (49, 131, 'B', 'R'): 'D',
    (49, 131, 'B', 'U'): 'D',
    (49, 131, 'D', 'B'): 'U',
    (49, 131, 'D', 'F'): 'U',
    (49, 131, 'D', 'L'): 'U',
    (49, 131, 'D', 'R'): 'U',
    (49, 131, 'F', 'D'): 'D',
    (49, 131, 'F', 'L'): 'D',
    (49, 131, 'F', 'R'): 'D',
    (49, 131, 'F', 'U'): 'D',
    (49, 131, 'L', 'B'): 'U',
    (49, 131, 'L', 'D'): 'D',
    (49, 131, 'L', 'F'): 'U',
    (49, 131, 'L', 'U'): 'D',
    (49, 131, 'R', 'B'): 'U',
    (49, 131, 'R', 'D'): 'D',
    (49, 131, 'R', 'F'): 'U',
    (49, 131, 'R', 'U'): 'D',
    (49, 131, 'U', 'B'): 'U',
    (49, 131, 'U', 'F'): 'U',
    (49, 131, 'U', 'L'): 'U',
    (49, 131, 'U', 'R'): 'U',
    (52, 22, 'B', 'D'): 'D',
    (52, 22, 'B', 'L'): 'D',
    (52, 22, 'B', 'R'): 'D',
    (52, 22, 'B', 'U'): 'D',
    (52, 22, 'D', 'B'): 'U',
    (52, 22, 'D', 'F'): 'U',
    (52, 22, 'D', 'L'): 'U',
    (52, 22, 'D', 'R'): 'U',
    (52, 22, 'F', 'D'): 'D',
    (52, 22, 'F', 'L'): 'D',
    (52, 22, 'F', 'R'): 'D',
    (52, 22, 'F', 'U'): 'D',
    (52, 22, 'L', 'B'): 'U',
    (52, 22, 'L', 'D'): 'D',
    (52, 22, 'L', 'F'): 'U',
    (52, 22, 'L', 'U'): 'D',
    (52, 22, 'R', 'B'): 'U',
    (52, 22, 'R', 'D'): 'D',
    (52, 22, 'R', 'F'): 'U',
    (52, 22, 'R', 'U'): 'D',
    (52, 22, 'U', 'B'): 'U',
    (52, 22, 'U', 'F'): 'U',
    (52, 22, 'U', 'L'): 'U',
    (52, 22, 'U', 'R'): 'U',
    (54, 24, 'B', 'D'): 'U',
    (54, 24, 'B', 'L'): 'U',
    (54, 24, 'B', 'R'): 'U',
    (54, 24, 'B', 'U'): 'U',
    (54, 24, 'D', 'B'): 'D',
    (54, 24, 'D', 'F'): 'D',
    (54, 24, 'D', 'L'): 'D',
    (54, 24, 'D', 'R'): 'D',
    (54, 24, 'F', 'D'): 'U',
    (54, 24, 'F', 'L'): 'U',
    (54, 24, 'F', 'R'): 'U',
    (54, 24, 'F', 'U'): 'U',
    (54, 24, 'L', 'B'): 'D',
    (54, 24, 'L', 'D'): 'U',
    (54, 24, 'L', 'F'): 'D',
    (54, 24, 'L', 'U'): 'U',
    (54, 24, 'R', 'B'): 'D',
    (54, 24, 'R', 'D'): 'U',
    (54, 24, 'R', 'F'): 'D',
    (54, 24, 'R', 'U'): 'U',
    (54, 24, 'U', 'B'): 'D',
    (54, 24, 'U', 'F'): 'D',
    (54, 24, 'U', 'L'): 'D',
    (54, 24, 'U', 'R'): 'D',
    (56, 35, 'B', 'D'): 'U',
    (56, 35, 'B', 'L'): 'U',
    (56, 35, 'B', 'R'): 'U',
    (56, 35, 'B', 'U'): 'U',
    (56, 35, 'D', 'B'): 'D',
    (56, 35, 'D', 'F'): 'D',
    (56, 35, 'D', 'L'): 'D',
    (56, 35, 'D', 'R'): 'D',
    (56, 35, 'F', 'D'): 'U',
    (56, 35, 'F', 'L'): 'U',
    (56, 35, 'F', 'R'): 'U',
    (56, 35, 'F', 'U'): 'U',
    (56, 35, 'L', 'B'): 'D',
    (56, 35, 'L', 'D'): 'U',
    (56, 35, 'L', 'F'): 'D',
    (56, 35, 'L', 'U'): 'U',
    (56, 35, 'R', 'B'): 'D',
    (56, 35, 'R', 'D'): 'U',
    (56, 35, 'R', 'F'): 'D',
    (56, 35, 'R', 'U'): 'U',
    (56, 35, 'U', 'B'): 'D',
    (56, 35, 'U', 'F'): 'D',
    (56, 35, 'U', 'L'): 'D',
    (56, 35, 'U', 'R'): 'D',
    (60, 81, 'B', 'D'): 'D',
    (60, 81, 'B', 'L'): 'D',
    (60, 81, 'B', 'R'): 'D',
    (60, 81, 'B', 'U'): 'D',
    (60, 81, 'D', 'B'): 'U',
    (60, 81, 'D', 'F'): 'U',
    (60, 81, 'D', 'L'): 'U',
    (60, 81, 'D', 'R'): 'U',
    (60, 81, 'F', 'D'): 'D',
    (60, 81, 'F', 'L'): 'D',
    (60, 81, 'F', 'R'): 'D',
    (60, 81, 'F', 'U'): 'D',
    (60, 81, 'L', 'B'): 'U',
    (60, 81, 'L', 'D'): 'D',
    (60, 81, 'L', 'F'): 'U',
    (60, 81, 'L', 'U'): 'D',
    (60, 81, 'R', 'B'): 'U',
    (60, 81, 'R', 'D'): 'D',
    (60, 81, 'R', 'F'): 'U',
    (60, 81, 'R', 'U'): 'D',
    (60, 81, 'U', 'B'): 'U',
    (60, 81, 'U', 'F'): 'U',
    (60, 81, 'U', 'L'): 'U',
    (60, 81, 'U', 'R'): 'U',
    (66, 45, 'B', 'D'): 'D',
    (66, 45, 'B', 'L'): 'D',
    (66, 45, 'B', 'R'): 'D',
    (66, 45, 'B', 'U'): 'D',
    (66, 45, 'D', 'B'): 'U',
    (66, 45, 'D', 'F'): 'U',
    (66, 45, 'D', 'L'): 'U',
    (66, 45, 'D', 'R'): 'U',
    (66, 45, 'F', 'D'): 'D',
    (66, 45, 'F', 'L'): 'D',
    (66, 45, 'F', 'R'): 'D',
    (66, 45, 'F', 'U'): 'D',
    (66, 45, 'L', 'B'): 'U',
    (66, 45, 'L', 'D'): 'D',
    (66, 45, 'L', 'F'): 'U',
    (66, 45, 'L', 'U'): 'D',
    (66, 45, 'R', 'B'): 'U',
    (66, 45, 'R', 'D'): 'D',
    (66, 45, 'R', 'F'): 'U',
    (66, 45, 'R', 'U'): 'D',
    (66, 45, 'U', 'B'): 'U',
    (66, 45, 'U', 'F'): 'U',
    (66, 45, 'U', 'L'): 'U',
    (66, 45, 'U', 'R'): 'U',
    (70, 91, 'B', 'D'): 'U',
    (70, 91, 'B', 'L'): 'U',
    (70, 91, 'B', 'R'): 'U',
    (70, 91, 'B', 'U'): 'U',
    (70, 91, 'D', 'B'): 'D',
    (70, 91, 'D', 'F'): 'D',
    (70, 91, 'D', 'L'): 'D',
    (70, 91, 'D', 'R'): 'D',
    (70, 91, 'F', 'D'): 'U',
    (70, 91, 'F', 'L'): 'U',
    (70, 91, 'F', 'R'): 'U',
    (70, 91, 'F', 'U'): 'U',
    (70, 91, 'L', 'B'): 'D',
    (70, 91, 'L', 'D'): 'U',
    (70, 91, 'L', 'F'): 'D',
    (70, 91, 'L', 'U'): 'U',
    (70, 91, 'R', 'B'): 'D',
    (70, 91, 'R', 'D'): 'U',
    (70, 91, 'R', 'F'): 'D',
    (70, 91, 'R', 'U'): 'U',
    (70, 91, 'U', 'B'): 'D',
    (70, 91, 'U', 'F'): 'D',
    (70, 91, 'U', 'L'): 'D',
    (70, 91, 'U', 'R'): 'D',
    (72, 127, 'B', 'D'): 'U',
    (72, 127, 'B', 'L'): 'U',
    (72, 127, 'B', 'R'): 'U',
    (72, 127, 'B', 'U'): 'U',
    (72, 127, 'D', 'B'): 'D',
    (72, 127, 'D', 'F'): 'D',
    (72, 127, 'D', 'L'): 'D',
    (72, 127, 'D', 'R'): 'D',
    (72, 127, 'F', 'D'): 'U',
    (72, 127, 'F', 'L'): 'U',
    (72, 127, 'F', 'R'): 'U',
    (72, 127, 'F', 'U'): 'U',
    (72, 127, 'L', 'B'): 'D',
    (72, 127, 'L', 'D'): 'U',
    (72, 127, 'L', 'F'): 'D',
    (72, 127, 'L', 'U'): 'U',
    (72, 127, 'R', 'B'): 'D',
    (72, 127, 'R', 'D'): 'U',
    (72, 127, 'R', 'F'): 'D',
    (72, 127, 'R', 'U'): 'U',
    (72, 127, 'U', 'B'): 'D',
    (72, 127, 'U', 'F'): 'D',
    (72, 127, 'U', 'L'): 'D',
    (72, 127, 'U', 'R'): 'D',
    (74, 129, 'B', 'D'): 'D',
    (74, 129, 'B', 'L'): 'D',
    (74, 129, 'B', 'R'): 'D',
    (74, 129, 'B', 'U'): 'D',
    (74, 129, 'D', 'B'): 'U',
    (74, 129, 'D', 'F'): 'U',
    (74, 129, 'D', 'L'): 'U',
    (74, 129, 'D', 'R'): 'U',
    (74, 129, 'F', 'D'): 'D',
    (74, 129, 'F', 'L'): 'D',
    (74, 129, 'F', 'R'): 'D',
    (74, 129, 'F', 'U'): 'D',
    (74, 129, 'L', 'B'): 'U',
    (74, 129, 'L', 'D'): 'D',
    (74, 129, 'L', 'F'): 'U',
    (74, 129, 'L', 'U'): 'D',
    (74, 129, 'R', 'B'): 'U',
    (74, 129, 'R', 'D'): 'D',
    (74, 129, 'R', 'F'): 'U',
    (74, 129, 'R', 'U'): 'D',
    (74, 129, 'U', 'B'): 'U',
    (74, 129, 'U', 'F'): 'U',
    (74, 129, 'U', 'L'): 'U',
    (74, 129, 'U', 'R'): 'U',
    (77, 20, 'B', 'D'): 'D',
    (77, 20, 'B', 'L'): 'D',
    (77, 20, 'B', 'R'): 'D',
    (77, 20, 'B', 'U'): 'D',
    (77, 20, 'D', 'B'): 'U',
    (77, 20, 'D', 'F'): 'U',
    (77, 20, 'D', 'L'): 'U',
    (77, 20, 'D', 'R'): 'U',
    (77, 20, 'F', 'D'): 'D',
    (77, 20, 'F', 'L'): 'D',
    (77, 20, 'F', 'R'): 'D',
    (77, 20, 'F', 'U'): 'D',
    (77, 20, 'L', 'B'): 'U',
    (77, 20, 'L', 'D'): 'D',
    (77, 20, 'L', 'F'): 'U',
    (77, 20, 'L', 'U'): 'D',
    (77, 20, 'R', 'B'): 'U',
    (77, 20, 'R', 'D'): 'D',
    (77, 20, 'R', 'F'): 'U',
    (77, 20, 'R', 'U'): 'D',
    (77, 20, 'U', 'B'): 'U',
    (77, 20, 'U', 'F'): 'U',
    (77, 20, 'U', 'L'): 'U',
    (77, 20, 'U', 'R'): 'U',
    (79, 10, 'B', 'D'): 'U',
    (79, 10, 'B', 'L'): 'U',
    (79, 10, 'B', 'R'): 'U',
    (79, 10, 'B', 'U'): 'U',
    (79, 10, 'D', 'B'): 'D',
    (79, 10, 'D', 'F'): 'D',
    (79, 10, 'D', 'L'): 'D',
    (79, 10, 'D', 'R'): 'D',
    (79, 10, 'F', 'D'): 'U',
    (79, 10, 'F', 'L'): 'U',
    (79, 10, 'F', 'R'): 'U',
    (79, 10, 'F', 'U'): 'U',
    (79, 10, 'L', 'B'): 'D',
    (79, 10, 'L', 'D'): 'U',
    (79, 10, 'L', 'F'): 'D',
    (79, 10, 'L', 'U'): 'U',
    (79, 10, 'R', 'B'): 'D',
    (79, 10, 'R', 'D'): 'U',
    (79, 10, 'R', 'F'): 'D',
    (79, 10, 'R', 'U'): 'U',
    (79, 10, 'U', 'B'): 'D',
    (79, 10, 'U', 'F'): 'D',
    (79, 10, 'U', 'L'): 'D',
    (79, 10, 'U', 'R'): 'D',
    (81, 60, 'B', 'D'): 'U',
    (81, 60, 'B', 'L'): 'U',
    (81, 60, 'B', 'R'): 'U',
    (81, 60, 'B', 'U'): 'U',
    (81, 60, 'D', 'B'): 'D',
    (81, 60, 'D', 'F'): 'D',
    (81, 60, 'D', 'L'): 'D',
    (81, 60, 'D', 'R'): 'D',
    (81, 60, 'F', 'D'): 'U',
    (81, 60, 'F', 'L'): 'U',
    (81, 60, 'F', 'R'): 'U',
    (81, 60, 'F', 'U'): 'U',
    (81, 60, 'L', 'B'): 'D',
    (81, 60, 'L', 'D'): 'U',
    (81, 60, 'L', 'F'): 'D',
    (81, 60, 'L', 'U'): 'U',
    (81, 60, 'R', 'B'): 'D',
    (81, 60, 'R', 'D'): 'U',
    (81, 60, 'R', 'F'): 'D',
    (81, 60, 'R', 'U'): 'U',
    (81, 60, 'U', 'B'): 'D',
    (81, 60, 'U', 'F'): 'D',
    (81, 60, 'U', 'L'): 'D',
    (81, 60, 'U', 'R'): 'D',
    (85, 106, 'B', 'D'): 'D',
    (85, 106, 'B', 'L'): 'D',
    (85, 106, 'B', 'R'): 'D',
    (85, 106, 'B', 'U'): 'D',
    (85, 106, 'D', 'B'): 'U',
    (85, 106, 'D', 'F'): 'U',
    (85, 106, 'D', 'L'): 'U',
    (85, 106, 'D', 'R'): 'U',
    (85, 106, 'F', 'D'): 'D',
    (85, 106, 'F', 'L'): 'D',
    (85, 106, 'F', 'R'): 'D',
    (85, 106, 'F', 'U'): 'D',
    (85, 106, 'L', 'B'): 'U',
    (85, 106, 'L', 'D'): 'D',
    (85, 106, 'L', 'F'): 'U',
    (85, 106, 'L', 'U'): 'D',
    (85, 106, 'R', 'B'): 'U',
    (85, 106, 'R', 'D'): 'D',
    (85, 106, 'R', 'F'): 'U',
    (85, 106, 'R', 'U'): 'D',
    (85, 106, 'U', 'B'): 'U',
    (85, 106, 'U', 'F'): 'U',
    (85, 106, 'U', 'L'): 'U',
    (85, 106, 'U', 'R'): 'U',
    (91, 70, 'B', 'D'): 'D',
    (91, 70, 'B', 'L'): 'D',
    (91, 70, 'B', 'R'): 'D',
    (91, 70, 'B', 'U'): 'D',
    (91, 70, 'D', 'B'): 'U',
    (91, 70, 'D', 'F'): 'U',
    (91, 70, 'D', 'L'): 'U',
    (91, 70, 'D', 'R'): 'U',
    (91, 70, 'F', 'D'): 'D',
    (91, 70, 'F', 'L'): 'D',
    (91, 70, 'F', 'R'): 'D',
    (91, 70, 'F', 'U'): 'D',
    (91, 70, 'L', 'B'): 'U',
    (91, 70, 'L', 'D'): 'D',
    (91, 70, 'L', 'F'): 'U',
    (91, 70, 'L', 'U'): 'D',
    (91, 70, 'R', 'B'): 'U',
    (91, 70, 'R', 'D'): 'D',
    (91, 70, 'R', 'F'): 'U',
    (91, 70, 'R', 'U'): 'D',
    (91, 70, 'U', 'B'): 'U',
    (91, 70, 'U', 'F'): 'U',
    (91, 70, 'U', 'L'): 'U',
    (91, 70, 'U', 'R'): 'U',
    (95, 116, 'B', 'D'): 'U',
    (95, 116, 'B', 'L'): 'U',
    (95, 116, 'B', 'R'): 'U',
    (95, 116, 'B', 'U'): 'U',
    (95, 116, 'D', 'B'): 'D',
    (95, 116, 'D', 'F'): 'D',
    (95, 116, 'D', 'L'): 'D',
    (95, 116, 'D', 'R'): 'D',
    (95, 116, 'F', 'D'): 'U',
    (95, 116, 'F', 'L'): 'U',
    (95, 116, 'F', 'R'): 'U',
    (95, 116, 'F', 'U'): 'U',
    (95, 116, 'L', 'B'): 'D',
    (95, 116, 'L', 'D'): 'U',
    (95, 116, 'L', 'F'): 'D',
    (95, 116, 'L', 'U'): 'U',
    (95, 116, 'R', 'B'): 'D',
    (95, 116, 'R', 'D'): 'U',
    (95, 116, 'R', 'F'): 'D',
    (95, 116, 'R', 'U'): 'U',
    (95, 116, 'U', 'B'): 'D',
    (95, 116, 'U', 'F'): 'D',
    (95, 116, 'U', 'L'): 'D',
    (95, 116, 'U', 'R'): 'D',
    (97, 135, 'B', 'D'): 'U',
    (97, 135, 'B', 'L'): 'U',
    (97, 135, 'B', 'R'): 'U',
    (97, 135, 'B', 'U'): 'U',
    (97, 135, 'D', 'B'): 'D',
    (97, 135, 'D', 'F'): 'D',
    (97, 135, 'D', 'L'): 'D',
    (97, 135, 'D', 'R'): 'D',
    (97, 135, 'F', 'D'): 'U',
    (97, 135, 'F', 'L'): 'U',
    (97, 135, 'F', 'R'): 'U',
    (97, 135, 'F', 'U'): 'U',
    (97, 135, 'L', 'B'): 'D',
    (97, 135, 'L', 'D'): 'U',
    (97, 135, 'L', 'F'): 'D',
    (97, 135, 'L', 'U'): 'U',
    (97, 135, 'R', 'B'): 'D',
    (97, 135, 'R', 'D'): 'U',
    (97, 135, 'R', 'F'): 'D',
    (97, 135, 'R', 'U'): 'U',
    (97, 135, 'U', 'B'): 'D',
    (97, 135, 'U', 'F'): 'D',
    (97, 135, 'U', 'L'): 'D',
    (97, 135, 'U', 'R'): 'D',
    (99, 145, 'B', 'D'): 'D',
    (99, 145, 'B', 'L'): 'D',
    (99, 145, 'B', 'R'): 'D',
    (99, 145, 'B', 'U'): 'D',
    (99, 145, 'D', 'B'): 'U',
    (99, 145, 'D', 'F'): 'U',
    (99, 145, 'D', 'L'): 'U',
    (99, 145, 'D', 'R'): 'U',
    (99, 145, 'F', 'D'): 'D',
    (99, 145, 'F', 'L'): 'D',
    (99, 145, 'F', 'R'): 'D',
    (99, 145, 'F', 'U'): 'D',
    (99, 145, 'L', 'B'): 'U',
    (99, 145, 'L', 'D'): 'D',
    (99, 145, 'L', 'F'): 'U',
    (99, 145, 'L', 'U'): 'D',
    (99, 145, 'R', 'B'): 'U',
    (99, 145, 'R', 'D'): 'D',
    (99, 145, 'R', 'F'): 'U',
    (99, 145, 'R', 'U'): 'D',
    (99, 145, 'U', 'B'): 'U',
    (99, 145, 'U', 'F'): 'U',
    (99, 145, 'U', 'L'): 'U',
    (99, 145, 'U', 'R'): 'U',
    (102, 4, 'B', 'D'): 'D',
    (102, 4, 'B', 'L'): 'D',
    (102, 4, 'B', 'R'): 'D',
    (102, 4, 'B', 'U'): 'D',
    (102, 4, 'D', 'B'): 'U',
    (102, 4, 'D', 'F'): 'U',
    (102, 4, 'D', 'L'): 'U',
    (102, 4, 'D', 'R'): 'U',
    (102, 4, 'F', 'D'): 'D',
    (102, 4, 'F', 'L'): 'D',
    (102, 4, 'F', 'R'): 'D',
    (102, 4, 'F', 'U'): 'D',
    (102, 4, 'L', 'B'): 'U',
    (102, 4, 'L', 'D'): 'D',
    (102, 4, 'L', 'F'): 'U',
    (102, 4, 'L', 'U'): 'D',
    (102, 4, 'R', 'B'): 'U',
    (102, 4, 'R', 'D'): 'D',
    (102, 4, 'R', 'F'): 'U',
    (102, 4, 'R', 'U'): 'D',
    (102, 4, 'U', 'B'): 'U',
    (102, 4, 'U', 'F'): 'U',
    (102, 4, 'U', 'L'): 'U',
    (102, 4, 'U', 'R'): 'U',
    (104, 2, 'B', 'D'): 'U',
    (104, 2, 'B', 'L'): 'U',
    (104, 2, 'B', 'R'): 'U',
    (104, 2, 'B', 'U'): 'U',
    (104, 2, 'D', 'B'): 'D',
    (104, 2, 'D', 'F'): 'D',
    (104, 2, 'D', 'L'): 'D',
    (104, 2, 'D', 'R'): 'D',
    (104, 2, 'F', 'D'): 'U',
    (104, 2, 'F', 'L'): 'U',
    (104, 2, 'F', 'R'): 'U',
    (104, 2, 'F', 'U'): 'U',
    (104, 2, 'L', 'B'): 'D',
    (104, 2, 'L', 'D'): 'U',
    (104, 2, 'L', 'F'): 'D',
    (104, 2, 'L', 'U'): 'U',
    (104, 2, 'R', 'B'): 'D',
    (104, 2, 'R', 'D'): 'U',
    (104, 2, 'R', 'F'): 'D',
    (104, 2, 'R', 'U'): 'U',
    (104, 2, 'U', 'B'): 'D',
    (104, 2, 'U', 'F'): 'D',
    (104, 2, 'U', 'L'): 'D',
    (104, 2, 'U', 'R'): 'D',
    (106, 85, 'B', 'D'): 'U',
    (106, 85, 'B', 'L'): 'U',
    (106, 85, 'B', 'R'): 'U',
    (106, 85, 'B', 'U'): 'U',
    (106, 85, 'D', 'B'): 'D',
    (106, 85, 'D', 'F'): 'D',
    (106, 85, 'D', 'L'): 'D',
    (106, 85, 'D', 'R'): 'D',
    (106, 85, 'F', 'D'): 'U',
    (106, 85, 'F', 'L'): 'U',
    (106, 85, 'F', 'R'): 'U',
    (106, 85, 'F', 'U'): 'U',
    (106, 85, 'L', 'B'): 'D',
    (106, 85, 'L', 'D'): 'U',
    (106, 85, 'L', 'F'): 'D',
    (106, 85, 'L', 'U'): 'U',
    (106, 85, 'R', 'B'): 'D',
    (106, 85, 'R', 'D'): 'U',
    (106, 85, 'R', 'F'): 'D',
    (106, 85, 'R', 'U'): 'U',
    (106, 85, 'U', 'B'): 'D',
    (106, 85, 'U', 'F'): 'D',
    (106, 85, 'U', 'L'): 'D',
    (106, 85, 'U', 'R'): 'D',
    (110, 31, 'B', 'D'): 'D',
    (110, 31, 'B', 'L'): 'D',
    (110, 31, 'B', 'R'): 'D',
    (110, 31, 'B', 'U'): 'D',
    (110, 31, 'D', 'B'): 'U',
    (110, 31, 'D', 'F'): 'U',
    (110, 31, 'D', 'L'): 'U',
    (110, 31, 'D', 'R'): 'U',
    (110, 31, 'F', 'D'): 'D',
    (110, 31, 'F', 'L'): 'D',
    (110, 31, 'F', 'R'): 'D',
    (110, 31, 'F', 'U'): 'D',
    (110, 31, 'L', 'B'): 'U',
    (110, 31, 'L', 'D'): 'D',
    (110, 31, 'L', 'F'): 'U',
    (110, 31, 'L', 'U'): 'D',
    (110, 31, 'R', 'B'): 'U',
    (110, 31, 'R', 'D'): 'D',
    (110, 31, 'R', 'F'): 'U',
    (110, 31, 'R', 'U'): 'D',
    (110, 31, 'U', 'B'): 'U',
    (110, 31, 'U', 'F'): 'U',
    (110, 31, 'U', 'L'): 'U',
    (110, 31, 'U', 'R'): 'U',
    (116, 95, 'B', 'D'): 'D',
    (116, 95, 'B', 'L'): 'D',
    (116, 95, 'B', 'R'): 'D',
    (116, 95, 'B', 'U'): 'D',
    (116, 95, 'D', 'B'): 'U',
    (116, 95, 'D', 'F'): 'U',
    (116, 95, 'D', 'L'): 'U',
    (116, 95, 'D', 'R'): 'U',
    (116, 95, 'F', 'D'): 'D',
    (116, 95, 'F', 'L'): 'D',
    (116, 95, 'F', 'R'): 'D',
    (116, 95, 'F', 'U'): 'D',
    (116, 95, 'L', 'B'): 'U',
    (116, 95, 'L', 'D'): 'D',
    (116, 95, 'L', 'F'): 'U',
    (116, 95, 'L', 'U'): 'D',
    (116, 95, 'R', 'B'): 'U',
    (116, 95, 'R', 'D'): 'D',
    (116, 95, 'R', 'F'): 'U',
    (116, 95, 'R', 'U'): 'D',
    (116, 95, 'U', 'B'): 'U',
    (116, 95, 'U', 'F'): 'U',
    (116, 95, 'U', 'L'): 'U',
    (116, 95, 'U', 'R'): 'U',
    (120, 41, 'B', 'D'): 'U',
    (120, 41, 'B', 'L'): 'U',
    (120, 41, 'B', 'R'): 'U',
    (120, 41, 'B', 'U'): 'U',
    (120, 41, 'D', 'B'): 'D',
    (120, 41, 'D', 'F'): 'D',
    (120, 41, 'D', 'L'): 'D',
    (120, 41, 'D', 'R'): 'D',
    (120, 41, 'F', 'D'): 'U',
    (120, 41, 'F', 'L'): 'U',
    (120, 41, 'F', 'R'): 'U',
    (120, 41, 'F', 'U'): 'U',
    (120, 41, 'L', 'B'): 'D',
    (120, 41, 'L', 'D'): 'U',
    (120, 41, 'L', 'F'): 'D',
    (120, 41, 'L', 'U'): 'U',
    (120, 41, 'R', 'B'): 'D',
    (120, 41, 'R', 'D'): 'U',
    (120, 41, 'R', 'F'): 'D',
    (120, 41, 'R', 'U'): 'U',
    (120, 41, 'U', 'B'): 'D',
    (120, 41, 'U', 'F'): 'D',
    (120, 41, 'U', 'L'): 'D',
    (120, 41, 'U', 'R'): 'D',
    (122, 149, 'B', 'D'): 'U',
    (122, 149, 'B', 'L'): 'U',
    (122, 149, 'B', 'R'): 'U',
    (122, 149, 'B', 'U'): 'U',
    (122, 149, 'D', 'B'): 'D',
    (122, 149, 'D', 'F'): 'D',
    (122, 149, 'D', 'L'): 'D',
    (122, 149, 'D', 'R'): 'D',
    (122, 149, 'F', 'D'): 'U',
    (122, 149, 'F', 'L'): 'U',
    (122, 149, 'F', 'R'): 'U',
    (122, 149, 'F', 'U'): 'U',
    (122, 149, 'L', 'B'): 'D',
    (122, 149, 'L', 'D'): 'U',
    (122, 149, 'L', 'F'): 'D',
    (122, 149, 'L', 'U'): 'U',
    (122, 149, 'R', 'B'): 'D',
    (122, 149, 'R', 'D'): 'U',
    (122, 149, 'R', 'F'): 'D',
    (122, 149, 'R', 'U'): 'U',
    (122, 149, 'U', 'B'): 'D',
    (122, 149, 'U', 'F'): 'D',
    (122, 149, 'U', 'L'): 'D',
    (122, 149, 'U', 'R'): 'D',
    (124, 147, 'B', 'D'): 'D',
    (124, 147, 'B', 'L'): 'D',
    (124, 147, 'B', 'R'): 'D',
    (124, 147, 'B', 'U'): 'D',
    (124, 147, 'D', 'B'): 'U',
    (124, 147, 'D', 'F'): 'U',
    (124, 147, 'D', 'L'): 'U',
    (124, 147, 'D', 'R'): 'U',
    (124, 147, 'F', 'D'): 'D',
    (124, 147, 'F', 'L'): 'D',
    (124, 147, 'F', 'R'): 'D',
    (124, 147, 'F', 'U'): 'D',
    (124, 147, 'L', 'B'): 'U',
    (124, 147, 'L', 'D'): 'D',
    (124, 147, 'L', 'F'): 'U',
    (124, 147, 'L', 'U'): 'D',
    (124, 147, 'R', 'B'): 'U',
    (124, 147, 'R', 'D'): 'D',
    (124, 147, 'R', 'F'): 'U',
    (124, 147, 'R', 'U'): 'D',
    (124, 147, 'U', 'B'): 'U',
    (124, 147, 'U', 'F'): 'U',
    (124, 147, 'U', 'L'): 'U',
    (124, 147, 'U', 'R'): 'U',
    (127, 72, 'B', 'D'): 'D',
    (127, 72, 'B', 'L'): 'D',
    (127, 72, 'B', 'R'): 'D',
    (127, 72, 'B', 'U'): 'D',
    (127, 72, 'D', 'B'): 'U',
    (127, 72, 'D', 'F'): 'U',
    (127, 72, 'D', 'L'): 'U',
    (127, 72, 'D', 'R'): 'U',
    (127, 72, 'F', 'D'): 'D',
    (127, 72, 'F', 'L'): 'D',
    (127, 72, 'F', 'R'): 'D',
    (127, 72, 'F', 'U'): 'D',
    (127, 72, 'L', 'B'): 'U',
    (127, 72, 'L', 'D'): 'D',
    (127, 72, 'L', 'F'): 'U',
    (127, 72, 'L', 'U'): 'D',
    (127, 72, 'R', 'B'): 'U',
    (127, 72, 'R', 'D'): 'D',
    (127, 72, 'R', 'F'): 'U',
    (127, 72, 'R', 'U'): 'D',
    (127, 72, 'U', 'B'): 'U',
    (127, 72, 'U', 'F'): 'U',
    (127, 72, 'U', 'L'): 'U',
    (127, 72, 'U', 'R'): 'U',
    (129, 74, 'B', 'D'): 'U',
    (129, 74, 'B', 'L'): 'U',
    (129, 74, 'B', 'R'): 'U',
    (129, 74, 'B', 'U'): 'U',
    (129, 74, 'D', 'B'): 'D',
    (129, 74, 'D', 'F'): 'D',
    (129, 74, 'D', 'L'): 'D',
    (129, 74, 'D', 'R'): 'D',
    (129, 74, 'F', 'D'): 'U',
    (129, 74, 'F', 'L'): 'U',
    (129, 74, 'F', 'R'): 'U',
    (129, 74, 'F', 'U'): 'U',
    (129, 74, 'L', 'B'): 'D',
    (129, 74, 'L', 'D'): 'U',
    (129, 74, 'L', 'F'): 'D',
    (129, 74, 'L', 'U'): 'U',
    (129, 74, 'R', 'B'): 'D',
    (129, 74, 'R', 'D'): 'U',
    (129, 74, 'R', 'F'): 'D',
    (129, 74, 'R', 'U'): 'U',
    (129, 74, 'U', 'B'): 'D',
    (129, 74, 'U', 'F'): 'D',
    (129, 74, 'U', 'L'): 'D',
    (129, 74, 'U', 'R'): 'D',
    (131, 49, 'B', 'D'): 'U',
    (131, 49, 'B', 'L'): 'U',
    (131, 49, 'B', 'R'): 'U',
    (131, 49, 'B', 'U'): 'U',
    (131, 49, 'D', 'B'): 'D',
    (131, 49, 'D', 'F'): 'D',
    (131, 49, 'D', 'L'): 'D',
    (131, 49, 'D', 'R'): 'D',
    (131, 49, 'F', 'D'): 'U',
    (131, 49, 'F', 'L'): 'U',
    (131, 49, 'F', 'R'): 'U',
    (131, 49, 'F', 'U'): 'U',
    (131, 49, 'L', 'B'): 'D',
    (131, 49, 'L', 'D'): 'U',
    (131, 49, 'L', 'F'): 'D',
    (131, 49, 'L', 'U'): 'U',
    (131, 49, 'R', 'B'): 'D',
    (131, 49, 'R', 'D'): 'U',
    (131, 49, 'R', 'F'): 'D',
    (131, 49, 'R', 'U'): 'U',
    (131, 49, 'U', 'B'): 'D',
    (131, 49, 'U', 'F'): 'D',
    (131, 49, 'U', 'L'): 'D',
    (131, 49, 'U', 'R'): 'D',
    (135, 97, 'B', 'D'): 'D',
    (135, 97, 'B', 'L'): 'D',
    (135, 97, 'B', 'R'): 'D',
    (135, 97, 'B', 'U'): 'D',
    (135, 97, 'D', 'B'): 'U',
    (135, 97, 'D', 'F'): 'U',
    (135, 97, 'D', 'L'): 'U',
    (135, 97, 'D', 'R'): 'U',
    (135, 97, 'F', 'D'): 'D',
    (135, 97, 'F', 'L'): 'D',
    (135, 97, 'F', 'R'): 'D',
    (135, 97, 'F', 'U'): 'D',
    (135, 97, 'L', 'B'): 'U',
    (135, 97, 'L', 'D'): 'D',
    (135, 97, 'L', 'F'): 'U',
    (135, 97, 'L', 'U'): 'D',
    (135, 97, 'R', 'B'): 'U',
    (135, 97, 'R', 'D'): 'D',
    (135, 97, 'R', 'F'): 'U',
    (135, 97, 'R', 'U'): 'D',
    (135, 97, 'U', 'B'): 'U',
    (135, 97, 'U', 'F'): 'U',
    (135, 97, 'U', 'L'): 'U',
    (135, 97, 'U', 'R'): 'U',
    (141, 47, 'B', 'D'): 'D',
    (141, 47, 'B', 'L'): 'D',
    (141, 47, 'B', 'R'): 'D',
    (141, 47, 'B', 'U'): 'D',
    (141, 47, 'D', 'B'): 'U',
    (141, 47, 'D', 'F'): 'U',
    (141, 47, 'D', 'L'): 'U',
    (141, 47, 'D', 'R'): 'U',
    (141, 47, 'F', 'D'): 'D',
    (141, 47, 'F', 'L'): 'D',
    (141, 47, 'F', 'R'): 'D',
    (141, 47, 'F', 'U'): 'D',
    (141, 47, 'L', 'B'): 'U',
    (141, 47, 'L', 'D'): 'D',
    (141, 47, 'L', 'F'): 'U',
    (141, 47, 'L', 'U'): 'D',
    (141, 47, 'R', 'B'): 'U',
    (141, 47, 'R', 'D'): 'D',
    (141, 47, 'R', 'F'): 'U',
    (141, 47, 'R', 'U'): 'D',
    (141, 47, 'U', 'B'): 'U',
    (141, 47, 'U', 'F'): 'U',
    (141, 47, 'U', 'L'): 'U',
    (141, 47, 'U', 'R'): 'U',
    (145, 99, 'B', 'D'): 'U',
    (145, 99, 'B', 'L'): 'U',
    (145, 99, 'B', 'R'): 'U',
    (145, 99, 'B', 'U'): 'U',
    (145, 99, 'D', 'B'): 'D',
    (145, 99, 'D', 'F'): 'D',
    (145, 99, 'D', 'L'): 'D',
    (145, 99, 'D', 'R'): 'D',
    (145, 99, 'F', 'D'): 'U',
    (145, 99, 'F', 'L'): 'U',
    (145, 99, 'F', 'R'): 'U',
    (145, 99, 'F', 'U'): 'U',
    (145, 99, 'L', 'B'): 'D',
    (145, 99, 'L', 'D'): 'U',
    (145, 99, 'L', 'F'): 'D',
    (145, 99, 'L', 'U'): 'U',
    (145, 99, 'R', 'B'): 'D',
    (145, 99, 'R', 'D'): 'U',
    (145, 99, 'R', 'F'): 'D',
    (145, 99, 'R', 'U'): 'U',
    (145, 99, 'U', 'B'): 'D',
    (145, 99, 'U', 'F'): 'D',
    (145, 99, 'U', 'L'): 'D',
    (145, 99, 'U', 'R'): 'D',
    (147, 124, 'B', 'D'): 'U',
    (147, 124, 'B', 'L'): 'U',
    (147, 124, 'B', 'R'): 'U',
    (147, 124, 'B', 'U'): 'U',
    (147, 124, 'D', 'B'): 'D',
    (147, 124, 'D', 'F'): 'D',
    (147, 124, 'D', 'L'): 'D',
    (147, 124, 'D', 'R'): 'D',
    (147, 124, 'F', 'D'): 'U',
    (147, 124, 'F', 'L'): 'U',
    (147, 124, 'F', 'R'): 'U',
    (147, 124, 'F', 'U'): 'U',
    (147, 124, 'L', 'B'): 'D',
    (147, 124, 'L', 'D'): 'U',
    (147, 124, 'L', 'F'): 'D',
    (147, 124, 'L', 'U'): 'U',
    (147, 124, 'R', 'B'): 'D',
    (147, 124, 'R', 'D'): 'U',
    (147, 124, 'R', 'F'): 'D',
    (147, 124, 'R', 'U'): 'U',
    (147, 124, 'U', 'B'): 'D',
    (147, 124, 'U', 'F'): 'D',
    (147, 124, 'U', 'L'): 'D',
    (147, 124, 'U', 'R'): 'D',
    (149, 122, 'B', 'D'): 'D',
    (149, 122, 'B', 'L'): 'D',
    (149, 122, 'B', 'R'): 'D',
    (149, 122, 'B', 'U'): 'D',
    (149, 122, 'D', 'B'): 'U',
    (149, 122, 'D', 'F'): 'U',
    (149, 122, 'D', 'L'): 'U',
    (149, 122, 'D', 'R'): 'U',
    (149, 122, 'F', 'D'): 'D',
    (149, 122, 'F', 'L'): 'D',
    (149, 122, 'F', 'R'): 'D',
    (149, 122, 'F', 'U'): 'D',
    (149, 122, 'L', 'B'): 'U',
    (149, 122, 'L', 'D'): 'D',
    (149, 122, 'L', 'F'): 'U',
    (149, 122, 'L', 'U'): 'D',
    (149, 122, 'R', 'B'): 'U',
    (149, 122, 'R', 'D'): 'D',
    (149, 122, 'R', 'F'): 'U',
    (149, 122, 'R', 'U'): 'D',
    (149, 122, 'U', 'B'): 'U',
    (149, 122, 'U', 'F'): 'U',
    (149, 122, 'U', 'L'): 'U',
    (149, 122, 'U', 'R'): 'U'
}

if __name__ == '__main__':
    import doctest

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(filename)16s %(levelname)8s: %(message)s')
    log = logging.getLogger(__name__)

    # Color the errors and warnings in red
    logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
    logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

    doctest.testmod()
