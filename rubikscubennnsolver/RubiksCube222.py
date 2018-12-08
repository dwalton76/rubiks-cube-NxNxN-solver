
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

    def solve(self, solution333=None):
        self.solve_non_table()
        self.compress_solution()

        # Cube is solved, rotate it around so white is on top, etc
        #self.rotate_U_to_U()
        #self.rotate_F_to_F()

swaps_222 = {'B': (0, 14, 16, 3, 4, 2, 6, 1, 8, 9, 10, 11, 12, 13, 24, 15, 23, 19, 17, 20, 18, 21, 22, 5, 7),
 "B'": (0, 7, 5, 3, 4, 23, 6, 24, 8, 9, 10, 11, 12, 13, 1, 15, 2, 18, 20, 17, 19, 21, 22, 16, 14),
 'B2': (0, 24, 23, 3, 4, 16, 6, 14, 8, 9, 10, 11, 12, 13, 7, 15, 5, 20, 19, 18, 17, 21, 22, 2, 1),
 'D': (0, 1, 2, 3, 4, 5, 6, 19, 20, 9, 10, 7, 8, 13, 14, 11, 12, 17, 18, 15, 16, 23, 21, 24, 22),
 "D'": (0, 1, 2, 3, 4, 5, 6, 11, 12, 9, 10, 15, 16, 13, 14, 19, 20, 17, 18, 7, 8, 22, 24, 21, 23),
 'D2': (0, 1, 2, 3, 4, 5, 6, 15, 16, 9, 10, 19, 20, 13, 14, 7, 8, 17, 18, 11, 12, 24, 23, 22, 21),
 'F': (0, 1, 2, 8, 6, 5, 21, 7, 22, 11, 9, 12, 10, 3, 14, 4, 16, 17, 18, 19, 20, 15, 13, 23, 24),
 "F'": (0, 1, 2, 13, 15, 5, 4, 7, 3, 10, 12, 9, 11, 22, 14, 21, 16, 17, 18, 19, 20, 6, 8, 23, 24),
 'F2': (0, 1, 2, 22, 21, 5, 15, 7, 13, 12, 11, 10, 9, 8, 14, 6, 16, 17, 18, 19, 20, 4, 3, 23, 24),
 'L': (0, 20, 2, 18, 4, 7, 5, 8, 6, 1, 10, 3, 12, 13, 14, 15, 16, 17, 23, 19, 21, 9, 22, 11, 24),
 "L'": (0, 9, 2, 11, 4, 6, 8, 5, 7, 21, 10, 23, 12, 13, 14, 15, 16, 17, 3, 19, 1, 20, 22, 18, 24),
 'L2': (0, 21, 2, 23, 4, 8, 7, 6, 5, 20, 10, 18, 12, 13, 14, 15, 16, 17, 11, 19, 9, 1, 22, 3, 24),
 'R': (0, 1, 10, 3, 12, 5, 6, 7, 8, 9, 22, 11, 24, 15, 13, 16, 14, 4, 18, 2, 20, 21, 19, 23, 17),
 "R'": (0, 1, 19, 3, 17, 5, 6, 7, 8, 9, 2, 11, 4, 14, 16, 13, 15, 24, 18, 22, 20, 21, 10, 23, 12),
 'R2': (0, 1, 22, 3, 24, 5, 6, 7, 8, 9, 19, 11, 17, 16, 15, 14, 13, 12, 18, 10, 20, 21, 2, 23, 4),
 'U': (0, 3, 1, 4, 2, 9, 10, 7, 8, 13, 14, 11, 12, 17, 18, 15, 16, 5, 6, 19, 20, 21, 22, 23, 24),
 "U'": (0, 2, 4, 1, 3, 17, 18, 7, 8, 5, 6, 11, 12, 9, 10, 15, 16, 13, 14, 19, 20, 21, 22, 23, 24),
 'U2': (0, 4, 3, 2, 1, 13, 14, 7, 8, 17, 18, 11, 12, 5, 6, 15, 16, 9, 10, 19, 20, 21, 22, 23, 24),
 'x': (0, 9, 10, 11, 12, 6, 8, 5, 7, 21, 22, 23, 24, 15, 13, 16, 14, 4, 3, 2, 1, 20, 19, 18, 17),
 "x'": (0, 20, 19, 18, 17, 7, 5, 8, 6, 1, 2, 3, 4, 14, 16, 13, 15, 24, 23, 22, 21, 9, 10, 11, 12),
 'x2': (0, 21, 22, 23, 24, 8, 7, 6, 5, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 1, 2, 3, 4),
 'y': (0, 3, 1, 4, 2, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 5, 6, 7, 8, 22, 24, 21, 23),
 "y'": (0, 2, 4, 1, 3, 17, 18, 19, 20, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 21, 24, 22),
 'y2': (0, 4, 3, 2, 1, 13, 14, 15, 16, 17, 18, 19, 20, 5, 6, 7, 8, 9, 10, 11, 12, 24, 23, 22, 21),
 'z': (0, 7, 5, 8, 6, 23, 21, 24, 22, 11, 9, 12, 10, 3, 1, 4, 2, 18, 20, 17, 19, 15, 13, 16, 14),
 "z'": (0, 14, 16, 13, 15, 2, 4, 1, 3, 10, 12, 9, 11, 22, 24, 21, 23, 19, 17, 20, 18, 6, 8, 5, 7),
 'z2': (0, 24, 23, 22, 21, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 20, 19, 18, 17, 4, 3, 2, 1)}

def rotate_222(cube, step):
    return [cube[x] for x in swaps_222[step]]
