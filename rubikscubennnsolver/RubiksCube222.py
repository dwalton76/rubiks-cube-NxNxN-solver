
from rubikscubennnsolver import RubiksCube, SolveError
from rubikscubennnsolver.LookupTable import LookupTable
import logging

log = logging.getLogger(__name__)


moves_2x2x2 = ("U", "U'", "U2",
               "L", "L'", "L2",
               "F" , "F'", "F2",
               "R" , "R'", "R2",
               "B" , "B'", "B2",
               "D" , "D'", "D2")
solved_2x2x2 = 'UUUURRRRFFFFDDDDLLLLBBBB'


class RubiksCube222(RubiksCube):

    def __init__(self, kociemba_string, debug=False):
        RubiksCube.__init__(self, kociemba_string, debug)

        if debug:
            log.setLevel(logging.DEBUG)

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
        log.info("NORMAL: %s" % normal)
        upper = normal[0:4]
        right = normal[4:8]
        front = normal[8:12]
        down = normal[12:16]
        left = normal[16:20]
        back = normal[20:24]

        '''
        from pprint import pformat
        print "upper: %s" % pformat(upper)
        print "right: %s" % pformat(right)
        print "front: %s" % pformat(front)
        print "down: %s" % pformat(down)
        print "left: %s" % pformat(left)
        print "back: %s" % pformat(back)
        '''

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

        o = ''.join
        data = [{''.join((' ', x)[x in scramble[12] + scramble[19] + scramble[22]]for x in scramble):[]},
             {' ' * 4 + (scramble[12] * 2 + ' ' * 4 + scramble[19] * 2) * 2 + scramble[22] * 4:[]}]

        from pprint import pprint
        #pprint(data)

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
            for s, x in data[h].items():
                for y in xrange(12):

                    data[h][s] = x + [y - [1, -1, 1, 3][h * y % 4]]

                    if s in data[1 - h]:
                        # pprint(data[0][s])
                        # pprint(data[1][s])
                        try:
                            result = ''.join('RUF'[x / 4] + " 2'"[x % 4] for x in data[0][s] + data[1][s][::-1])
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

    def solve_via_table(self):
        '''
        For grins I built a full lookup table for 2x2x2, it is too large to put in the
        repo though and the solver from stackoverflow works just fine but I'll leave
        this here for a rainy day.

        lookup-table-2x2x2-solve.txt
        ============================
        1 steps has 18 entries (0 percent, 0.00x previous step)
        2 steps has 244 entries (0 percent, 13.56x previous step)
        3 steps has 2,874 entries (0 percent, 11.78x previous step)
        4 steps has 28,000 entries (0 percent, 9.74x previous step)
        5 steps has 205,416 entries (0 percent, 7.34x previous step)
        6 steps has 1,168,516 entries (1 percent, 5.69x previous step)
        7 steps has 5,402,628 entries (6 percent, 4.62x previous step)
        8 steps has 20,776,176 entries (23 percent, 3.85x previous step)
        9 steps has 45,391,616 entries (51 percent, 2.18x previous step)
        10 steps has 15,139,616 entries (17 percent, 0.33x previous step)
        11 steps has 64,736 entries (0 percent, 0.00x previous step)

        Total: 88,179,840 entries
        '''
        self.lt = LookupTable(self, 'lookup-table-2x2x2-solve.txt', 'all', 'UUUULLLLFFFFRRRRBBBBDDDD')
        self.lt.solve()
        self.compress_solution()

    def solve(self):
        self.solve_non_table()
        self.compress_solution()

