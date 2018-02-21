
from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube222 import moves_2x2x2
import logging

log = logging.getLogger(__name__)

moves_3x3x3 = moves_2x2x2
solved_3x3x3 = 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'


class RubiksCube333(RubiksCube):

    def phase(self):
        return 'Solve 3x3x3'

    def solve(self):
        self.rotate_U_to_U()
        self.rotate_F_to_F()

        if self.get_state_all() != 'UUUUUUUUULLLLLLLLLFFFFFFFFFRRRRRRRRRBBBBBBBBBDDDDDDDDD':
            self.solve_333()
            self.compress_solution()


def rotate_333_U(cube):
    return [cube[0],cube[7],cube[4],cube[1],cube[8],cube[5],cube[2],cube[9],cube[6],cube[3]] + cube[19:22] + cube[13:19] + cube[28:31] + cube[22:28] + cube[37:40] + cube[31:37] + cube[10:13] + cube[40:55]

def rotate_333_U_prime(cube):
    return [cube[0],cube[3],cube[6],cube[9],cube[2],cube[5],cube[8],cube[1],cube[4],cube[7]] + cube[37:40] + cube[13:19] + cube[10:13] + cube[22:28] + cube[19:22] + cube[31:37] + cube[28:31] + cube[40:55]

def rotate_333_U2(cube):
    return [cube[0],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1]] + cube[28:31] + cube[13:19] + cube[37:40] + cube[22:28] + cube[10:13] + cube[31:37] + cube[19:22] + cube[40:55]

def rotate_333_L(cube):
    return [cube[0],cube[45]] + cube[2:4] + [cube[42]] + cube[5:7] + [cube[39]] + cube[8:10] + [cube[16],cube[13],cube[10],cube[17],cube[14],cube[11],cube[18],cube[15],cube[12],cube[1]] + cube[20:22] + [cube[4]] + cube[23:25] + [cube[7]] + cube[26:39] + [cube[52]] + cube[40:42] + [cube[49]] + cube[43:45] + [cube[46],cube[19]] + cube[47:49] + [cube[22]] + cube[50:52] + [cube[25]] + cube[53:55]

def rotate_333_L_prime(cube):
    return [cube[0],cube[19]] + cube[2:4] + [cube[22]] + cube[5:7] + [cube[25]] + cube[8:10] + [cube[12],cube[15],cube[18],cube[11],cube[14],cube[17],cube[10],cube[13],cube[16],cube[46]] + cube[20:22] + [cube[49]] + cube[23:25] + [cube[52]] + cube[26:39] + [cube[7]] + cube[40:42] + [cube[4]] + cube[43:45] + [cube[1],cube[45]] + cube[47:49] + [cube[42]] + cube[50:52] + [cube[39]] + cube[53:55]

def rotate_333_L2(cube):
    return [cube[0],cube[46]] + cube[2:4] + [cube[49]] + cube[5:7] + [cube[52]] + cube[8:10] + [cube[18],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[11],cube[10],cube[45]] + cube[20:22] + [cube[42]] + cube[23:25] + [cube[39]] + cube[26:39] + [cube[25]] + cube[40:42] + [cube[22]] + cube[43:45] + [cube[19],cube[1]] + cube[47:49] + [cube[4]] + cube[50:52] + [cube[7]] + cube[53:55]

def rotate_333_F(cube):
    return cube[0:7] + [cube[18],cube[15],cube[12]] + cube[10:12] + [cube[46]] + cube[13:15] + [cube[47]] + cube[16:18] + [cube[48],cube[25],cube[22],cube[19],cube[26],cube[23],cube[20],cube[27],cube[24],cube[21],cube[7]] + cube[29:31] + [cube[8]] + cube[32:34] + [cube[9]] + cube[35:46] + [cube[34],cube[31],cube[28]] + cube[49:55]

def rotate_333_F_prime(cube):
    return cube[0:7] + [cube[28],cube[31],cube[34]] + cube[10:12] + [cube[9]] + cube[13:15] + [cube[8]] + cube[16:18] + [cube[7],cube[21],cube[24],cube[27],cube[20],cube[23],cube[26],cube[19],cube[22],cube[25],cube[48]] + cube[29:31] + [cube[47]] + cube[32:34] + [cube[46]] + cube[35:46] + [cube[12],cube[15],cube[18]] + cube[49:55]

def rotate_333_F2(cube):
    return cube[0:7] + [cube[48],cube[47],cube[46]] + cube[10:12] + [cube[34]] + cube[13:15] + [cube[31]] + cube[16:18] + [cube[28],cube[27],cube[26],cube[25],cube[24],cube[23],cube[22],cube[21],cube[20],cube[19],cube[18]] + cube[29:31] + [cube[15]] + cube[32:34] + [cube[12]] + cube[35:46] + [cube[9],cube[8],cube[7]] + cube[49:55]

def rotate_333_R(cube):
    return cube[0:3] + [cube[21]] + cube[4:6] + [cube[24]] + cube[7:9] + [cube[27]] + cube[10:21] + [cube[48]] + cube[22:24] + [cube[51]] + cube[25:27] + [cube[54],cube[34],cube[31],cube[28],cube[35],cube[32],cube[29],cube[36],cube[33],cube[30],cube[9]] + cube[38:40] + [cube[6]] + cube[41:43] + [cube[3]] + cube[44:48] + [cube[43]] + cube[49:51] + [cube[40]] + cube[52:54] + [cube[37]]

def rotate_333_R_prime(cube):
    return cube[0:3] + [cube[43]] + cube[4:6] + [cube[40]] + cube[7:9] + [cube[37]] + cube[10:21] + [cube[3]] + cube[22:24] + [cube[6]] + cube[25:27] + [cube[9],cube[30],cube[33],cube[36],cube[29],cube[32],cube[35],cube[28],cube[31],cube[34],cube[54]] + cube[38:40] + [cube[51]] + cube[41:43] + [cube[48]] + cube[44:48] + [cube[21]] + cube[49:51] + [cube[24]] + cube[52:54] + [cube[27]]

def rotate_333_R2(cube):
    return cube[0:3] + [cube[48]] + cube[4:6] + [cube[51]] + cube[7:9] + [cube[54]] + cube[10:21] + [cube[43]] + cube[22:24] + [cube[40]] + cube[25:27] + [cube[37],cube[36],cube[35],cube[34],cube[33],cube[32],cube[31],cube[30],cube[29],cube[28],cube[27]] + cube[38:40] + [cube[24]] + cube[41:43] + [cube[21]] + cube[44:48] + [cube[3]] + cube[49:51] + [cube[6]] + cube[52:54] + [cube[9]]

def rotate_333_B(cube):
    return [cube[0],cube[30],cube[33],cube[36]] + cube[4:10] + [cube[3]] + cube[11:13] + [cube[2]] + cube[14:16] + [cube[1]] + cube[17:30] + [cube[54]] + cube[31:33] + [cube[53]] + cube[34:36] + [cube[52],cube[43],cube[40],cube[37],cube[44],cube[41],cube[38],cube[45],cube[42],cube[39]] + cube[46:52] + [cube[10],cube[13],cube[16]]

def rotate_333_B_prime(cube):
    return [cube[0],cube[16],cube[13],cube[10]] + cube[4:10] + [cube[52]] + cube[11:13] + [cube[53]] + cube[14:16] + [cube[54]] + cube[17:30] + [cube[1]] + cube[31:33] + [cube[2]] + cube[34:36] + [cube[3],cube[39],cube[42],cube[45],cube[38],cube[41],cube[44],cube[37],cube[40],cube[43]] + cube[46:52] + [cube[36],cube[33],cube[30]]

def rotate_333_B2(cube):
    return [cube[0],cube[54],cube[53],cube[52]] + cube[4:10] + [cube[36]] + cube[11:13] + [cube[33]] + cube[14:16] + [cube[30]] + cube[17:30] + [cube[16]] + cube[31:33] + [cube[13]] + cube[34:36] + [cube[10],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37]] + cube[46:52] + [cube[3],cube[2],cube[1]]

def rotate_333_D(cube):
    return cube[0:16] + cube[43:46] + cube[19:25] + cube[16:19] + cube[28:34] + cube[25:28] + cube[37:43] + cube[34:37] + [cube[52],cube[49],cube[46],cube[53],cube[50],cube[47],cube[54],cube[51],cube[48]]

def rotate_333_D_prime(cube):
    return cube[0:16] + cube[25:28] + cube[19:25] + cube[34:37] + cube[28:34] + cube[43:46] + cube[37:43] + cube[16:19] + [cube[48],cube[51],cube[54],cube[47],cube[50],cube[53],cube[46],cube[49],cube[52]]

def rotate_333_D2(cube):
    return cube[0:16] + cube[34:37] + cube[19:25] + cube[43:46] + cube[28:34] + cube[16:19] + cube[37:43] + cube[25:28] + [cube[54],cube[53],cube[52],cube[51],cube[50],cube[49],cube[48],cube[47],cube[46]]

def rotate_333_x(cube):
    return [cube[0]] + cube[19:28] + [cube[12],cube[15],cube[18],cube[11],cube[14],cube[17],cube[10],cube[13],cube[16]] + cube[46:55] + [cube[34],cube[31],cube[28],cube[35],cube[32],cube[29],cube[36],cube[33],cube[30],cube[9],cube[8],cube[7],cube[6],cube[5],cube[4],cube[3],cube[2],cube[1],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37]]

def rotate_333_x_prime(cube):
    return [cube[0],cube[45],cube[44],cube[43],cube[42],cube[41],cube[40],cube[39],cube[38],cube[37],cube[16],cube[13],cube[10],cube[17],cube[14],cube[11],cube[18],cube[15],cube[12]] + cube[1:10] + [cube[30],cube[33],cube[36],cube[29],cube[32],cube[35],cube[28],cube[31],cube[34],cube[54],cube[53],cube[52],cube[51],cube[50],cube[49],cube[48],cube[47],cube[46]] + cube[19:28]

def rotate_333_y(cube):
    return [cube[0],cube[7],cube[4],cube[1],cube[8],cube[5],cube[2],cube[9],cube[6],cube[3]] + cube[19:46] + cube[10:19] + [cube[48],cube[51],cube[54],cube[47],cube[50],cube[53],cube[46],cube[49],cube[52]]

def rotate_333_y_prime(cube):
    return [cube[0],cube[3],cube[6],cube[9],cube[2],cube[5],cube[8],cube[1],cube[4],cube[7]] + cube[37:46] + cube[10:37] + [cube[52],cube[49],cube[46],cube[53],cube[50],cube[47],cube[54],cube[51],cube[48]]

def rotate_333_z(cube):
    return [cube[0],cube[16],cube[13],cube[10],cube[17],cube[14],cube[11],cube[18],cube[15],cube[12],cube[52],cube[49],cube[46],cube[53],cube[50],cube[47],cube[54],cube[51],cube[48],cube[25],cube[22],cube[19],cube[26],cube[23],cube[20],cube[27],cube[24],cube[21],cube[7],cube[4],cube[1],cube[8],cube[5],cube[2],cube[9],cube[6],cube[3],cube[39],cube[42],cube[45],cube[38],cube[41],cube[44],cube[37],cube[40],cube[43],cube[34],cube[31],cube[28],cube[35],cube[32],cube[29],cube[36],cube[33],cube[30]]

def rotate_333_z_prime(cube):
    return [cube[0],cube[30],cube[33],cube[36],cube[29],cube[32],cube[35],cube[28],cube[31],cube[34],cube[3],cube[6],cube[9],cube[2],cube[5],cube[8],cube[1],cube[4],cube[7],cube[21],cube[24],cube[27],cube[20],cube[23],cube[26],cube[19],cube[22],cube[25],cube[48],cube[51],cube[54],cube[47],cube[50],cube[53],cube[46],cube[49],cube[52],cube[43],cube[40],cube[37],cube[44],cube[41],cube[38],cube[45],cube[42],cube[39],cube[12],cube[15],cube[18],cube[11],cube[14],cube[17],cube[10],cube[13],cube[16]]

rotate_mapper_333 = {
    "B" : rotate_333_B,
    "B'" : rotate_333_B_prime,
    "B2" : rotate_333_B2,
    "D" : rotate_333_D,
    "D'" : rotate_333_D_prime,
    "D2" : rotate_333_D2,
    "F" : rotate_333_F,
    "F'" : rotate_333_F_prime,
    "F2" : rotate_333_F2,
    "L" : rotate_333_L,
    "L'" : rotate_333_L_prime,
    "L2" : rotate_333_L2,
    "R" : rotate_333_R,
    "R'" : rotate_333_R_prime,
    "R2" : rotate_333_R2,
    "U" : rotate_333_U,
    "U'" : rotate_333_U_prime,
    "U2" : rotate_333_U2,
    "x" : rotate_333_x,
    "x'" : rotate_333_x_prime,
    "y" : rotate_333_y,
    "y'" : rotate_333_y_prime,
    "z" : rotate_333_z,
    "z'" : rotate_333_z_prime,
}

def rotate_333(cube, step):
    return rotate_mapper_333[step](cube)
