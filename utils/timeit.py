#!/usr/bin/env python3

from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444, rotate_444
from myModule import bitfield_rotate_face_90 as C_bitfield_rotate_face_90
from myModule import rotate_444 as C_rotate_444
from pprint import pformat
import datetime as dt
import logging


def pretty_time(delta):
    delta = str(delta)

    if delta.startswith('0:00:00.'):
        delta_us = int(delta.split('.')[1])
        delta_ms = int(delta_us/1000)

        if delta_ms >= 500:
            return "\033[91m%sms\033[0m" % delta_ms
        else:
            return "%sms" % delta_ms

    elif delta.startswith('0:00:01.'):
        delta_us = int(delta.split('.')[1])
        delta_ms = 1000 + int(delta_us/1000)
        return "\033[91m%sms\033[0m" % delta_ms

    else:
        return "\033[91m%s\033[0m" % delta


def python_bitfield_rotate_face_90(bitfield):
    return (
        (((bitfield >> 12) & 0xF) << 60) | # c30 -> c00
        (((bitfield >> 28) & 0xF) << 56) | # c20 -> c01
        (((bitfield >> 44) & 0xF) << 52) | # c10 -> c02
        (((bitfield >> 60) & 0xF) << 48) | # c00 -> c03

        (((bitfield >>  8) & 0xF) << 44) | # c31 -> c10
        (((bitfield >> 24) & 0xF) << 40) | # c21 -> c11
        (((bitfield >> 40) & 0xF) << 36) | # c11 -> c12
        (((bitfield >> 56) & 0xF) << 32) | # c01 -> c13

        (((bitfield >>  4) & 0xF) << 28) | # c32 -> c20
        (((bitfield >> 20) & 0xF) << 24) | # c22 -> c21
        (((bitfield >> 36) & 0xF) << 20) | # c12 -> c22
        (((bitfield >> 52) & 0xF) << 16) | # c02 -> c23

        (((bitfield >>  0) & 0xF) << 12) | # c33 -> c30
        (((bitfield >> 16) & 0xF) <<  8) | # c23 -> c31
        (((bitfield >> 32) & 0xF) <<  4) | # c13 -> c32
        (((bitfield >> 48) & 0xF) <<  0)   # c03 -> c33
    )


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))


COUNT = 1000000
#COUNT = 10000
cube = RubiksCube444(solved_444, 'URFDLB')
state = cube.state[:]


# For 1,000,000 this took 0:00:05.157367 at 193,897 nodes-per-sec
start_time0 = dt.datetime.now()
for x in range(COUNT):
    state = rotate_444(state[:], "U")
end_time0= dt.datetime.now()
delta = end_time0 - start_time0
print ("{:,} rotates using python rotate_444() took {} at {:,} nodes-per-sec".format(COUNT, pretty_time(delta), int(COUNT/delta.total_seconds())))


# For 1,000,000 this took 0:00:18.350457 at 54,494 nodes-per-sec
'''
cube.re_init()
start_time0 = dt.datetime.now()
for x in range(COUNT):
    cube.rotate("U")
end_time0= dt.datetime.now()
delta = end_time0 - start_time0
print ("{:,} rotates using rotate() took {} at {:,} nodes-per-sec".format(COUNT, pretty_time(delta), int(COUNT/delta.total_seconds())))
'''




cube.re_init()
#cube.print_cube()
state = cube.state[:]
#state = C_rotate_444(state[:], "U")
#cube.state = state
#cube.print_cube()

#cube.re_init()
#cube.print_cube()
state = cube.state[:]
#print("0: %s" % pformat(state))
start_time0 = dt.datetime.now()
for x in range(COUNT):
    #state = C_rotate_444(state[:], "U")
    C_rotate_444(state, "U")
    #print("%d: %s" % (x, pformat(state, width=500)))
    #cube.state = state
    #cube.print_cube()

end_time0= dt.datetime.now()
delta = end_time0 - start_time0
print ("{:,} rotates using C      rotate_444() took {} at {:,} nodes-per-sec".format(COUNT, pretty_time(delta), int(COUNT/delta.total_seconds())))



# For 1,000,000 this took 0:00:02.641851 at 378,522 nodes-per-sec
state_U = 1234567890
start_time0 = dt.datetime.now()
for x in range(COUNT):
    state_U = python_bitfield_rotate_face_90(state_U)
end_time0= dt.datetime.now()
delta = end_time0 - start_time0
print ("{:,} rotates using python bitfield_rotate_face_90() took {} at {:,} nodes-per-sec".format(COUNT, pretty_time(delta), int(COUNT/delta.total_seconds())))


# For 1,000,000 this took 196ms at 5,090,483 nodes-per-sec
state_U = 1234567890
state_F = 9876543219
state_R = 7843789758
state_B = 8747497897
state_L = 1334443112
new_state_F = 0
new_state_R = 0
new_state_B = 0
new_state_L = 0
ROW_01     = 0xFFFF000000000000
NOT_ROW_01 = 0x0000FFFFFFFFFFFF
start_time0 = dt.datetime.now()
for x in range(COUNT):
    #new_state_F = (state_F & NOT_ROW_01) | (state_R & ROW_01)
    #new_state_R = (state_R & NOT_ROW_01) | (state_B & ROW_01)
    #new_state_B = (state_B & NOT_ROW_01) | (state_L & ROW_01)
    #new_state_L = (state_L & NOT_ROW_01) | (state_F & ROW_01)
    state_U = C_bitfield_rotate_face_90(state_U)
    #state_F = new_state_F
    #state_R = new_state_R
    #state_B = new_state_B
    #state_L = new_state_L

end_time0= dt.datetime.now()
delta = end_time0 - start_time0
print ("{:,} rotates using C      bitfield_rotate_face_90() took {} at {:,} nodes-per-sec".format(COUNT, pretty_time(delta), int(COUNT/delta.total_seconds())))
