
from rubikscubennnsolver import RubiksCube, SolveError
import logging

log = logging.getLogger(__name__)


moves_222 = (
    "U", "U'", "U2",
    "L", "L'", "L2",
    "F" , "F'", "F2",
    "R" , "R'", "R2",
    "B" , "B'", "B2",
    "D" , "D'", "D2"
)
solved_222 = 'UUUURRRRFFFFDDDDLLLLBBBB'


class RubiksCube222(RubiksCube):

    def phase(self):
        return 'Solve 2x2x2'

    def solve_non_table(self):
        """
        100% of the credit for this 2x2x2 solver goes to
        http://codegolf.stackexchange.com/questions/35002/solve-the-rubiks-pocket-cube

        In the codegolf challenge they defined the input as

        - -   A B   - -   - -
        - -   C D   - -   - -

        E F   G H   I J   K L
        M N   O P   Q R   S T

        - -   U V   - -   - -
        - -   W X   - -   - -

        But normally we number cubes like this

               01 02
               03 04
        05 06  09 10  13 14  17 18
        07 08  11 12  15 16  19 20
               21 22
               23 24

        So we will define the former layout as "scramble" and the latter as "normal".
        Convert the normal layout (sys.argv[1] must be in the 'normal' layout) to
        the scramble layout.
        """

        # 'normal' must be in U, R, F, D, L, B order
        # This is the order used by the kociemba 3x3x3 solver so
        # the rubiks-color-resolver uses this order
        normal = self.get_kociemba_string(False)
        upper = normal[0:4]
        right = normal[4:8]
        front = normal[8:12]
        down = normal[12:16]
        left = normal[16:20]
        back = normal[20:24]

        scramble = []
        scramble.extend(upper)
        scramble.append(left[0])
        scramble.append(left[1])
        scramble.append(front[0])
        scramble.append(front[1])
        scramble.append(right[0])
        scramble.append(right[1])
        scramble.append(back[0])
        scramble.append(back[1])

        scramble.append(left[2])
        scramble.append(left[3])
        scramble.append(front[2])
        scramble.append(front[3])
        scramble.append(right[2])
        scramble.append(right[3])
        scramble.append(back[2])
        scramble.append(back[3])
        scramble.extend(down)

        data = [{''.join((' ', x)[x in scramble[12] + scramble[19] + scramble[22]]for x in scramble):[]},
             {' ' * 4 + (scramble[12] * 2 + ' ' * 4 + scramble[19] * 2) * 2 + scramble[22] * 4:[]}]

        wtf_table = [
            [0, 7, 2, 15, 4, 5, 6, 21, 16, 8, 3, 11, 12, 13, 14, 23, 17, 9, 1, 19, 20, 18, 22, 10],
            [0, 7, 2, 15, 4, 5, 6, 21, 16, 8, 3, 11, 12, 13, 14, 23, 17, 9, 1, 19, 20, 18, 22, 10],
            [0, 7, 2, 15, 4, 5, 6, 21, 16, 8, 3, 11, 12, 13, 14, 23, 17, 9, 1, 19, 20, 18, 22, 10],
            [0, 7, 2, 15, 4, 5, 6, 21, 16, 8, 3, 11, 12, 13, 14, 23, 17, 9, 1, 19, 20, 18, 22, 10],
            [2, 0, 3, 1, 6, 7, 8, 9, 10, 11, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
            [2, 0, 3, 1, 6, 7, 8, 9, 10, 11, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
            [2, 0, 3, 1, 6, 7, 8, 9, 10, 11, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
            [2, 0, 3, 1, 6, 7, 8, 9, 10, 11, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
            [0, 1, 13, 5, 4, 20, 14, 6, 2, 9, 10, 11, 12, 21, 15, 7, 3, 17, 18, 19, 16, 8, 22, 23],
            [0, 1, 13, 5, 4, 20, 14, 6, 2, 9, 10, 11, 12, 21, 15, 7, 3, 17, 18, 19, 16, 8, 22, 23],
            [0, 1, 13, 5, 4, 20, 14, 6, 2, 9, 10, 11, 12, 21, 15, 7, 3, 17, 18, 19, 16, 8, 22, 23],
            [0, 1, 13, 5, 4, 20, 14, 6, 2, 9, 10, 11, 12, 21, 15, 7, 3, 17, 18, 19, 16, 8, 22, 23]
        ]

        for h in (0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1):
            for s, x in list(data[h].items()):
                for y in range(12):

                    data[h][s] = x + [y - [1, -1, 1, 3][h * y % 4]]

                    if s in data[1 - h]:
                        try:
                            result = ''.join('RUF'[int(x / 4)] + " 2'"[x % 4] for x in data[0][s] + data[1][s][::-1])
                        except IndexError:
                            print("Cube is already solved")
                            sys.exit(0)

                        result = result.replace('2', '2 ')
                        result = result.replace("'", "' ")
                        for step in result.strip().split():
                            self.rotate(step)
                        return

                    s = ''.join(s[x] for x in wtf_table[y])

        raise SolveError("Could not find a solution")

    def solve(self):
        self.solve_non_table()
        self.compress_solution()

        # Cube is solved, rotate it around so white is on top, etc
        #self.rotate_U_to_U()
        #self.rotate_F_to_F()

def rotate_222_U(cube):
    return [cube[0],cube[3],cube[1],cube[4],cube[2]] + cube[9:11] + cube[7:9] + cube[13:15] + cube[11:13] + cube[17:19] + cube[15:17] + cube[5:7] + cube[19:25]

def rotate_222_U_prime(cube):
    return [cube[0],cube[2],cube[4],cube[1],cube[3]] + cube[17:19] + cube[7:9] + cube[5:7] + cube[11:13] + cube[9:11] + cube[15:17] + cube[13:15] + cube[19:25]

def rotate_222_U2(cube):
    return [cube[0],cube[4],cube[3],cube[2],cube[1]] + cube[13:15] + cube[7:9] + cube[17:19] + cube[11:13] + cube[5:7] + cube[15:17] + cube[9:11] + cube[19:25]

def rotate_222_L(cube):
    return [cube[0],cube[20],cube[2],cube[18],cube[4],cube[7],cube[5],cube[8],cube[6],cube[1],cube[10],cube[3]] + cube[12:18] + [cube[23],cube[19],cube[21],cube[9],cube[22],cube[11],cube[24]]

def rotate_222_L_prime(cube):
    return [cube[0],cube[9],cube[2],cube[11],cube[4],cube[6],cube[8],cube[5],cube[7],cube[21],cube[10],cube[23]] + cube[12:18] + [cube[3],cube[19],cube[1],cube[20],cube[22],cube[18],cube[24]]

def rotate_222_L2(cube):
    return [cube[0],cube[21],cube[2],cube[23],cube[4],cube[8],cube[7],cube[6],cube[5],cube[20],cube[10],cube[18]] + cube[12:18] + [cube[11],cube[19],cube[9],cube[1],cube[22],cube[3],cube[24]]

def rotate_222_F(cube):
    return cube[0:3] + [cube[8],cube[6],cube[5],cube[21],cube[7],cube[22],cube[11],cube[9],cube[12],cube[10],cube[3],cube[14],cube[4]] + cube[16:21] + [cube[15],cube[13]] + cube[23:25]

def rotate_222_F_prime(cube):
    return cube[0:3] + [cube[13],cube[15],cube[5],cube[4],cube[7],cube[3],cube[10],cube[12],cube[9],cube[11],cube[22],cube[14],cube[21]] + cube[16:21] + [cube[6],cube[8]] + cube[23:25]

def rotate_222_F2(cube):
    return cube[0:3] + [cube[22],cube[21],cube[5],cube[15],cube[7],cube[13],cube[12],cube[11],cube[10],cube[9],cube[8],cube[14],cube[6]] + cube[16:21] + [cube[4],cube[3]] + cube[23:25]

def rotate_222_R(cube):
    return cube[0:2] + [cube[10],cube[3],cube[12]] + cube[5:10] + [cube[22],cube[11],cube[24],cube[15],cube[13],cube[16],cube[14],cube[4],cube[18],cube[2]] + cube[20:22] + [cube[19],cube[23],cube[17]]

def rotate_222_R_prime(cube):
    return cube[0:2] + [cube[19],cube[3],cube[17]] + cube[5:10] + [cube[2],cube[11],cube[4],cube[14],cube[16],cube[13],cube[15],cube[24],cube[18],cube[22]] + cube[20:22] + [cube[10],cube[23],cube[12]]

def rotate_222_R2(cube):
    return cube[0:2] + [cube[22],cube[3],cube[24]] + cube[5:10] + [cube[19],cube[11],cube[17],cube[16],cube[15],cube[14],cube[13],cube[12],cube[18],cube[10]] + cube[20:22] + [cube[2],cube[23],cube[4]]

def rotate_222_B(cube):
    return [cube[0],cube[14],cube[16]] + cube[3:5] + [cube[2],cube[6],cube[1]] + cube[8:14] + [cube[24],cube[15],cube[23],cube[19],cube[17],cube[20],cube[18]] + cube[21:23] + [cube[5],cube[7]]

def rotate_222_B_prime(cube):
    return [cube[0],cube[7],cube[5]] + cube[3:5] + [cube[23],cube[6],cube[24]] + cube[8:14] + [cube[1],cube[15],cube[2],cube[18],cube[20],cube[17],cube[19]] + cube[21:23] + [cube[16],cube[14]]

def rotate_222_B2(cube):
    return [cube[0],cube[24],cube[23]] + cube[3:5] + [cube[16],cube[6],cube[14]] + cube[8:14] + [cube[7],cube[15],cube[5],cube[20],cube[19],cube[18],cube[17]] + cube[21:23] + [cube[2],cube[1]]

def rotate_222_D(cube):
    return cube[0:7] + cube[19:21] + cube[9:11] + cube[7:9] + cube[13:15] + cube[11:13] + cube[17:19] + cube[15:17] + [cube[23],cube[21],cube[24],cube[22]]

def rotate_222_D_prime(cube):
    return cube[0:7] + cube[11:13] + cube[9:11] + cube[15:17] + cube[13:15] + cube[19:21] + cube[17:19] + cube[7:9] + [cube[22],cube[24],cube[21],cube[23]]

def rotate_222_D2(cube):
    return cube[0:7] + cube[15:17] + cube[9:11] + cube[19:21] + cube[13:15] + cube[7:9] + cube[17:19] + cube[11:13] + [cube[24],cube[23],cube[22],cube[21]]

def rotate_222_x(cube):
    return [cube[0]] + cube[9:13] + [cube[6],cube[8],cube[5],cube[7]] + cube[21:25] + [cube[15],cube[13],cube[16],cube[14],cube[4],cube[3],cube[2],cube[1],cube[20],cube[19],cube[18],cube[17]]

def rotate_222_x_prime(cube):
    return [cube[0],cube[20],cube[19],cube[18],cube[17],cube[7],cube[5],cube[8],cube[6]] + cube[1:5] + [cube[14],cube[16],cube[13],cube[15],cube[24],cube[23],cube[22],cube[21]] + cube[9:13]

def rotate_222_y(cube):
    return [cube[0],cube[3],cube[1],cube[4],cube[2]] + cube[9:21] + cube[5:9] + [cube[22],cube[24],cube[21],cube[23]]

def rotate_222_y_prime(cube):
    return [cube[0],cube[2],cube[4],cube[1],cube[3]] + cube[17:21] + cube[5:17] + [cube[23],cube[21],cube[24],cube[22]]

def rotate_222_z(cube):
    return [cube[0],cube[7],cube[5],cube[8],cube[6],cube[23],cube[21],cube[24],cube[22],cube[11],cube[9],cube[12],cube[10],cube[3],cube[1],cube[4],cube[2],cube[18],cube[20],cube[17],cube[19],cube[15],cube[13],cube[16],cube[14]]

def rotate_222_z_prime(cube):
    return [cube[0],cube[14],cube[16],cube[13],cube[15],cube[2],cube[4],cube[1],cube[3],cube[10],cube[12],cube[9],cube[11],cube[22],cube[24],cube[21],cube[23],cube[19],cube[17],cube[20],cube[18],cube[6],cube[8],cube[5],cube[7]]

rotate_mapper_222 = {
    "B" : rotate_222_B,
    "B'" : rotate_222_B_prime,
    "B2" : rotate_222_B2,
    "D" : rotate_222_D,
    "D'" : rotate_222_D_prime,
    "D2" : rotate_222_D2,
    "F" : rotate_222_F,
    "F'" : rotate_222_F_prime,
    "F2" : rotate_222_F2,
    "L" : rotate_222_L,
    "L'" : rotate_222_L_prime,
    "L2" : rotate_222_L2,
    "R" : rotate_222_R,
    "R'" : rotate_222_R_prime,
    "R2" : rotate_222_R2,
    "U" : rotate_222_U,
    "U'" : rotate_222_U_prime,
    "U2" : rotate_222_U2,
    "x" : rotate_222_x,
    "x'" : rotate_222_x_prime,
    "y" : rotate_222_y,
    "y'" : rotate_222_y_prime,
    "z" : rotate_222_z,
    "z'" : rotate_222_z_prime,
}

def rotate_222(cube, step):
    return rotate_mapper_222[step](cube)
