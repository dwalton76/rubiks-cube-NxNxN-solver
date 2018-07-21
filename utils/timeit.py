#!/usr/bin/env python3

import datetime as dt

solved_777 = 'xUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB'


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

rotate_777_3Lw_swaps = ((1, 245), (2, 244), (3, 243), (8, 238), (9, 237), (10, 236), (15, 231), (16, 230), (17, 229), (22, 224), (23, 223), (24, 222), (29, 217), (30, 216), (31, 215), (36, 210), (37, 209), (38, 208), (43, 203), (44, 202), (45, 201), (50, 92), (51, 85), (52, 78), (53, 71), (54, 64), (55, 57), (50, 56), (57, 93), (58, 86), (59, 79), (60, 72), (61, 65), (58, 62), (51, 63), (64, 94), (65, 87), (66, 80), (67, 73), (66, 68), (59, 69), (52, 70), (71, 95), (72, 88), (73, 81), (67, 75), (60, 76), (53, 77), (78, 96), (79, 89), (80, 82), (75, 81), (68, 82), (61, 83), (54, 84), (85, 97), (86, 90), (83, 87), (76, 88), (69, 89), (62, 90), (55, 91), (92, 98), (91, 93), (84, 94), (77, 95), (70, 96), (63, 97), (56, 98), (1, 99), (2, 100), (3, 101), (8, 106), (9, 107), (10, 108), (15, 113), (16, 114), (17, 115), (22, 120), (23, 121), (24, 122), (29, 127), (30, 128), (31, 129), (36, 134), (37, 135), (38, 136), (43, 141), (44, 142), (45, 143), (201, 290), (202, 289), (203, 288), (208, 283), (209, 282), (210, 281), (215, 276), (216, 275), (217, 274), (222, 269), (223, 268), (224, 267), (229, 262), (230, 261), (231, 260), (236, 255), (237, 254), (238, 253), (243, 248), (244, 247), (245, 246), (99, 246), (100, 247), (101, 248), (106, 253), (107, 254), (108, 255), (113, 260), (114, 261), (115, 262), (120, 267), (121, 268), (122, 269), (127, 274), (128, 275), (129, 276), (134, 281), (135, 282), (136, 283), (141, 288), (142, 289), (143, 290))

def rotate_777_3Lw(cube):
    for (x, y) in rotate_777_3Lw_swaps:
        cube[x], cube[y] = cube[y], cube[x]

cube = list(solved_777)

cube = 4200000000
ROW_01 = 0xFFFFF00000000000
NOT_ROW_01 = 0x00000FFFFFFFFFFF

start_time0 = dt.datetime.now()
for x in range(1000000):
    cube = (cube & NOT_ROW_01) | (cube & ROW_01)
    #rotate_777_3Lw(cube)

end_time0= dt.datetime.now()
delta = end_time0 - start_time0
print ("Took %s" % pretty_time(delta))
