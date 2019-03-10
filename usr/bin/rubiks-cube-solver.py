#!/usr/bin/env python3

"""
Solve any size rubiks cube:
- For 2x2x2 and 3x3x3 just solve it
- For 4x4x4 and larger, reduce to 3x3x3 and then solve

This is a work in progress
"""

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)22s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))
log.info("rubiks-cube-solver.py begin")


from rubikscubennnsolver import ImplementThis, SolveError, StuckInALoop, NotSolving, reverse_steps
from rubikscubennnsolver.LookupTable import NoSteps, NoPruneTableState
from math import sqrt
from pprint import pformat
from statistics import median
import argparse
import datetime as dt
import logging
import os
import resource
import sys

start_time = dt.datetime.now()


parser = argparse.ArgumentParser()
parser.add_argument('--print-steps', default=False, action='store_true', help='Display animated step-by-step solution')
parser.add_argument('--debug', default=False, action='store_true', help='set loglevel to DEBUG')
parser.add_argument('--no-comments', default=False, action='store_true', help='No comments in alg.cubing.net url')

# CPU mode
parser.add_argument('--min-memory', default=False, action='store_true', help='Load smaller tables to use less memory...takes longer to run')
parser.add_argument('--fast', default=True, action='store_true', help='Find a solution quickly')
parser.add_argument('--normal', default=False, action='store_true', help='Find a shorter solution but takes longer')
parser.add_argument('--slow', default=False, action='store_true', help='Find shortest solution we can, takes a while')


action = parser.add_mutually_exclusive_group(required=False)
parser.add_argument('--openwith', default=None, type=str, help='Colors for sides U, L, etc')
parser.add_argument('--colormap', default=None, type=str, help='Colors for sides U, L, etc')
parser.add_argument('--order', type=str, default='URFDLB', help='order of sides in --state, default kociemba URFDLB')
parser.add_argument('--solution333', type=str, default=None, help='cube explorer optimal steps for solving 3x3x3')
parser.add_argument('--state', type=str, help='Cube state',

# no longer used
# parser.add_argument('--test', default=False, action='store_true')

# 2x2x2
#    default='DLRRFULLDUBFDURDBFBRBLFU')
#    default='UUUURRRRFFFFDDDDLLLLBBBB')

# 3x3x3
#    default='RRBBUFBFBRLRRRFRDDURUBFBBRFLUDUDFLLFFLLLLDFBDDDUUBDLUU')
#    default='UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB') # solved

# 4x4x4
    #default='DRFDFRUFDURDDLLUFLDLLBLULFBUUFRBLBFLLUDDUFRBURBBRBDLLDURFFBBRUFUFDRFURBUDLDBDUFFBUDRRLDRBLFBRRLB') # xyzzy test cube
    #default='FLDFDLBDFBLFFRRBDRFRRURBRDUBBDLURUDRRBFFBDLUBLUULUFRRFBLDDUULBDBDFLDBLUBFRFUFBDDUBFLLRFLURDULLRU') # TPR cube
    default='BRBLLLBRDLBBDDRRFUDFUDUDFUDDDRURBBBUUDRLFRDLLFBRFLRFLFFFBRULDRUBUBBLDBFRDLLUBUDDULFLRRFLFUBFUFUR')
#    default='UUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBB') # solved

# 5x5x5
#    default='RFFFUDUDURBFULULFDBLRLDUFDBLUBBBDDURLRDRFRUDDBFUFLFURRLDFRRRUBFUUDUFLLBLBBULDDRRUFUUUBUDFFDRFLRBBLRFDLLUUBBRFRFRLLBFRLBRRFRBDLLDDFBLRDLFBBBLBLBDUUFDDD')
#    https://www.speedsolving.com/forum/threads/arnauds-5x5x5-edge-pairing-method-examples.1447/
#    default='LDFRDDUUUUFUUUBLUUUFLDFDRFDDFBBRRRULRRRBFRRRURFRFDUBDRUBFFFUBFFFUUFFFRLDLRFDLBDDLDDDRDDDDUDDDDUULDLFBFLFFULLLRFLLLRLLLLRRBLBBRBULULBBBRUBBBRBBBBULBRFB')
#    default='UDLFDLDDLUFDUBRLBDLFLRBFRBLBBFUDURDULRRBRLFUURBUFLUBDUDRURRRBUFUFFFRUFFLDUURURFFULFFRLFDBRRFRDDBRFBBLBRDFBBBBUDDLLLDBUULUDULDLDDLBRRLRLUBBFFBDLFBDDLFR')
#    default='UUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBB') # solved
#    default='DFFURRULDLDLURLBDDRRBFRURFBFBFRBDLBBFRBLRFBRBBFLULDLBLULLFRUBUFLDFFLDULDDLUURRDRFBRLULUDRBDUUUBBRFFDBDFURDBBDDRULBUDRDLLLBDRFDLRDLLFDBBUFBRURFFUFFUUFU') # step10 takes 2s
#    default='URUBFUUFRDFFUUFLRDBLLBDDDLUULRDLDUBDLRBBLFLBRBFUUBBRBFFUDLFLLBFUFUDRLBFUBBURRLLRUFRDUFFDFRFUBRBBDRFRFLLFURLLFBRBLUDRDDRRDRRFDUDLFLDLUUDUDBRBBBRBDDLDFL') # step10 takes 9s
#    default='RFUBLFUBRULLUDDRLRLLFFFLUBDBLBFFUFLFURBFFLDDLFFBBRLUUDRRDLLLRDFFLBBLFURUBULBRLBDRUURDRRDFURDBUUBBFBUDRUBURBRBDLFLBDFBDULLDBBDDDRRFURLDUDUBRDFRFFDFDRLU') # step10 takes 6s, centers take 37 steps :(

# 6x6x6
#    default='FBDDDFFUDRFBBLFLLURLDLLUFBLRFDUFLBLLFBFLRRBBFDRRDUBUFRBUBRDLUBFDRLBBRLRUFLBRBDUDFFFDBLUDBBLRDFUUDLBBBRRDRUDLBLDFRUDLLFFUUBFBUUFDLRUDUDBRRBBUFFDRRRDBULRRURULFDBRRULDDRUUULBLLFDFRRFDURFFLDUUBRUFDRFUBLDFULFBFDDUDLBLLRBL')
#    default='UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUURRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB') # solved
#    defult='xxxxxxxDRRLxxLDDBxxLUUDxxFRDUxxxxxxxxxxxxxxBBLBxxURFUxxDRBDxxDFDLxxxxxxxxxxxxxxULLRxxUFLLxxBLFRxxBBRDxxxxxxxxxxxxxxLFBRxxBUUFxxFDDFxxURUFxxxxxxxxxxxxxxRFDLxxURFUxxUBBFxxRULDxxxxxxxxxxxxxxBBLFxxFLLRxxDRBBxxFDRUxxxxxxx') # good step20 IDA test

# 7x7x7
#    default='DBDBDDFBDDLUBDLFRFRBRLLDUFFDUFRBRDFDRUFDFDRDBDBULDBDBDBUFBUFFFULLFLDURRBBRRBRLFUUUDUURBRDUUURFFFLRFLRLDLBUFRLDLDFLLFBDFUFRFFUUUFURDRFULBRFURRBUDDRBDLLRLDLLDLUURFRFBUBURBRUDBDDLRBULBULUBDBBUDRBLFFBLRBURRUFULBRLFDUFDDBULBRLBUFULUDDLLDFRDRDBBFBUBBFLFFRRUFFRLRRDRULLLFRLFULBLLBBBLDFDBRBFDULLULRFDBR')

# 8x8x8
#    default='DRRRURBDDBFBRBDDBRRDUFLLURFBFLFURLFLFRBRFUBDRFDFUUBLFFFUULBBFDBDFBUBBFRFLRDLFDRBBLLFRLDFDRBURULDDRFFBFUUBLLFBRUUFDUBRDBBRDFLURUUFFUDLBRRFDUBFLRUUFFRLBFRFLRULUDFRUBBDBFFLBBDFDFLDBFRRRDDLFLBRBFBBRULDDUUBLBBURULLDDLDRUDRBUDRLUULDURLRDFLFULUFLFULRDDDUBBULRBRDFBBLFURRLULUBDDULRFBRFURBRLBRUBULBDDFBUFFBBRLRUUUFRULLBFFRFDDFFDULLDLBUDLLLLUUBBLDLLBBULULBDUDDFUBFLLDLDLFRDUDDBRRFRURRFRRLDDDDRD')

# 9x9x9
#    default='RFBLRUFLLFFLRRBDUDDBBBDUDFRUDUFFFBBFRBRDURBULFUDDFLLLDLFLRDLDBBBUUBRDBBBDFUFRUURULURBURDLFDUBFFDRDFRUBDUBRFLRRLUDLRLFBLBRRLLRDRBRBLURBLLRFRLDDFFFRBFUFURDFRRUDUFDDRRRLFLLUBBLBFDRRDLBRLUUBRDBBUBFLUUFBLLDBFFFBUFBFDBRDDDFLRFFBFFFLFRRDUUDDBUBLUUDURRBDBFFLFURDDLUBULUULULBFBRUBLLDDFLRBDBRFDUUDFURLLUBUFBLULLURDLLLBLFFRLLBLUDRLRDBLDDBRBUDRBLLRDUUUBRRFBFBBULUDUDLDRFUDDDFULRFRBDUDULBRRDBDFFRUUFRRFBDBLFBBDFURLRFDUUFRLUBURFURDDFLDFUBDFRRURRDLUDRBRBDLBFLBBRDLRDBFDUBDFFUBLFLUULLBUDLLLURDBLFFFDFLF'

# 10x10x10
#    default='ULBDLDBUFRBBBBBLBFFFDFRFBBDDFDFRFFLDLDLURRBUDRRBFLUDFRLBDURULRUUDBBBUBRURRRLDLRFFUFFFURRFBLLRRFLFUDBDRRDFULLLURFBFUUBDBBDBFLFDFUUFDUBRLUFDBLRFLUDUFBFDULDFRUBLBBBUBRRDBDDDDFURFLRDBRRLLRFUFLRDFDUULRRDULFDUDRFLBFRLDUDBDFLDBDUFULULLLBUUFDFFDBBBRBRLFLUFLFUFFRLLLFLBUDRRFDDUDLFLBRDULFLBLLULFLDLUULBUDRDFLUDDLLRBLUBBRFRRLDRDUUFLDDFUFLBDBBLBURBBRRRFUBLBRBRUBFFDBBBBLBUFBLURBLDRFLFBUDDFFRFFRLBDBDUURBUFBDFFFLFBDLDUFFBRDLBRLRLBFRUUUULRRBDBRRFDLLRRUUBDBDBFDLRDDBRUUUUUBLLURBDFUFLLRDBLRRBBLBDDBBFUDUDLDLUFDDDUURBFUFRRBLLURDDRURRURLBLDRFRUFBDRULUFFDUDLBBUURFDUDBLRRUDFRLLDULFUBFDLURFBFULFLRRRRRFDDDLFDDRUFRRLBLUBU')

# 14x14x14
#    default='FBDRLBLRRURRLDRBDLBURDFDDDRBLBBFBRDLLFDUBLFRLDFUUBFRDBFBBBULFRLBUFLBDDDLLDRBFLLBBLFBFFDFBFDDFRRRBDRRBRBDUFDRLRUDLDFDDURFLBUBBUUDLBRRDUDRDBBBLDBRBBBUFLBLRUURBDDLDRLUFFBLFRLDFBRFLDLBULFFBRLDBDDFLLRFLUBFDFBRLRLFDBLBURLBLFRFBLLDULUDURLBUUULLRRLUBDDLURLLRFURFRFRBDDUBLDFBLUDRLRDRRBLFUFRDUFFRULBLRBBRUFDBUBBBBLDBRBLDDRRFDDBFFUUBRBLFUBBRFUURBFDRLURLRBFUUFUBRUDRBDFBBFURFLFFDRDFUFFULFLUBDFUFFDLRRFRUDUDLBBBDLLLDUFUDRFDBLRRFFLRUFDRFURDLRRDRDLFBRLRLULRFBDLFDRLFRDDFLLDBFBUBBRLLDLFURFRFULUBLUBFLFFBFDFBDUUBURUUUBFUBDLLFLUUUFDUDLUUULDLLUDDBUFRDRULRLLULRULFBLUDFURFLFUBDLLFLFUBUUBBUFLUDUBRDBLFFUUUFDRLRULUDDRLRBLRUUFBRRRRULBDLFBFLDLRDFUBLUBRDDFUULFLDLUBFURRURUBDFFFDLRFFLBRFRDRUDUULURULLDFRBUDRDLFUFULDBLUBFRFBURDLLUUFDURLRDBLFFRFDBFURLFUBLUUUFFRULUBURRURFDDBFUFRBURBBDRFUDDFDLRUURFBBDBDRLUBRRBFDFRDFDLRDUFFUBRRBDBBLDLFDUDDRLFRRRBUUUBRFUFBUFFBRRDRDDBBDRUULDRFRFBUFLFFBLRBFLLLRUDFDRUDLDRLFRLUFLUBRDUFDDLLUDDRBUBBBDRDBBFRBDDRRLRRUUBBUDUDBLDBDFLFRFUBFLFDBBLRLULDBRFBRRLUUURDFFFDBLDUDBRFDDFFUBLUUURBBULFUFUDFBRDLLFURBULULBUDLUFFBDRBRRDBUUULFDURRDFDDLUDBDRBFBUFLULURUFDRFRFBBFBBBDRLBLUDLDRDLLDRRLLDLFBRBRLDUFBDDUDBLDFRFBBBDRDRDDLDRULFFLLFLBLDFLURLBUDFBDLRBLFDFLUDDFUBUBLURBBBLFRLFLBDDBURFFBFRRL')

# 15x15x15
#    default='RLURLURBDDULFUUURFLRBLURUBFDBULFLUBBFLDUFBDRFRBRUDFULFRUFLUDFRLFDFLLFDBULURRLBFBUURDULFDFBLRRRLFULLFFFDUULRRRUUUUFDBLDDFFLRDLLUURUBBULUFFURBRRLBBUUBBFDRRBRBRLUDLUDRBFBFULLRRBBFBFRDDDLDDDFRFUFLURUFLBDLUBRLDFRRDBDBFLFUDFLDFFURLFULLDDRURRDLRFLDFLULUUDDRFDRBLRBRBFUFDBDUUDBRRBDFBLBLRBBLBFLLDUBFFFFBDDRLBBBRFDFFUBBDURFLUUDDDRDDLDBRLBULLFLFBRBRBLUDDLRDRDUDFLFRUFLDLBLURDDDRUFDLBRDRLFBDBLDRFBFFBURULUDRRBRDFRFFLULLUBRDRRRDUFRBLFULUBBUFFBRBBFRLFDRRDBLDFRDRDDRLRUULBDURDURFDDLFDUUDBFLBDUFBULFRRDUDUBFBUDBBFUDFUUDLUDDRFDDDFRRRBUDRBFBBULLUFBLRLFLLBRRRRUBDRFLFDFDBLRFLURULULFFBUUUUFDBBLDLUBBRUBBBRBFLULLBLUUULLUBFFDULDFFBFFFUFFDUDRFBUFLDDLURFLRFLRFBUUBLRFDDRULUUUFFRDDBLRDULFURUDDBDLBBUUBFURFRFBRLBUULBLDDDBUBRFFULLUDFFDLDFUBLLBLDFFDDLBDUFUFFLBBBUBULDDFBRRFFLDUDDFRBLRRDDUDLBDBLURBUDBRRLUBBDRFBUFRDRDRBBDULBUFFDRBBDFBUULFFRLLDURRRDFFUUFULDULURLDLUUUDLBBUDLDRFBDBBDLUFBRRFDFLLDLFDBRBBRFUDDDBURDRBUBRUBDUBLDLLDLURLDFDBRUBDLDFRRRBRLULFRFLDRLBUBRUBLFBFDFFLFRFDFLBRULLRBLDRBBFURRRDUUULLULLDLBLBBDFBUUUBRRUFFBRUDBFRDFDLFLFFRFFFFRULDFFDFRUBBBRURBUFLBDFBBBBBRRRLFLFBDRRUFLURDDLRRBRLLFURRURBRFLLLFFURBFULFRFFBLDUUUUBDDUFFDRBRLDDFRBULDDDFFRURUFLDRFLDFBLRUFFUBBDFFDBLLDBDUBDLDLUDFBFLRULRRBDBLRBLDLUURRLLRULDBLBLLRRFDDRBBRBUBDDULDRFBFBBFLUFBLUULDDFDBRLLUBUBBDFBBLBBUBLULDRUDBLRULDUDLUFRRDLLUDDBUFLFLBUFUURFDRDLBURLLRRRULRBFFRRBRFBUBRBUUFRLRDRDLBBRFLLLDDBRFUFRBULFLFDRDDRRDBF')

args = parser.parse_args()

if 'G' in args.state:
    args.state = args.state.replace('G', 'F')
    args.state = args.state.replace('Y', 'D')
    args.state = args.state.replace('O', 'L')
    args.state = args.state.replace('W', 'U')

if args.debug:
    log.setLevel(logging.DEBUG)

try:
    size = int(sqrt((len(args.state) / 6)))

    if args.slow:
        cpu_mode = "slow"
    elif args.normal:
        cpu_mode = "normal"
    elif args.fast:
        cpu_mode = "fast"
    else:
        raise Exception("What CPU mode to use?")

    if size == 2:
        from rubikscubennnsolver.RubiksCube222 import RubiksCube222
        cube = RubiksCube222(args.state, args.order, args.colormap, args.debug)
    elif size == 3:
        from rubikscubennnsolver.RubiksCube333 import RubiksCube333
        cube = RubiksCube333(args.state, args.order, args.colormap, args.debug)
    elif size == 4:
        from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
        cube = RubiksCube444(args.state, args.order, args.colormap, avoid_pll=True, debug=args.debug)
    elif size == 5:
        from rubikscubennnsolver.RubiksCube555 import solved_555

        if cpu_mode == "fast":
            from rubikscubennnsolver.RubiksCube555ForNNN import RubiksCube555ForNNN
            cube = RubiksCube555ForNNN(args.state, args.order, args.colormap, args.debug)
        else:
            from rubikscubennnsolver.RubiksCube555 import RubiksCube555
            cube = RubiksCube555(args.state, args.order, args.colormap, args.debug)

    elif size == 6:
        from rubikscubennnsolver.RubiksCube666 import RubiksCube666
        cube = RubiksCube666(args.state, args.order, args.colormap, args.debug)
    elif size == 7:
        from rubikscubennnsolver.RubiksCube777 import RubiksCube777
        cube = RubiksCube777(args.state, args.order, args.colormap, args.debug)
    elif size % 2 == 0:
        from rubikscubennnsolver.RubiksCubeNNNEven import RubiksCubeNNNEven
        cube = RubiksCubeNNNEven(args.state, args.order, args.colormap, args.debug)
    else:
        from rubikscubennnsolver.RubiksCubeNNNOdd import RubiksCubeNNNOdd
        cube = RubiksCubeNNNOdd(args.state, args.order, args.colormap, args.debug)

    if args.openwith:
        cube.print_cube()
        for step in args.openwith.split():
            cube.rotate(step)

    cube.cpu_mode = cpu_mode
    log.info("CPU mode %s" % cube.cpu_mode)
    cube.sanity_check()
    cube.print_cube()
    cube.www_header()
    cube.www_write_cube("Initial Cube")

    try:
        if args.solution333:
            solution333 = reverse_steps(args.solution333.split())
        else:
            solution333 = []
        cube.solve(solution333)
    except NotSolving:
        if cube.heuristic_stats:
            log.info("%s: heuristic_stats raw\n%s\n\n" % (cube, pformat(cube.heuristic_stats)))

            for (key, value) in cube.heuristic_stats.items():
                cube.heuristic_stats[key] = int(median(value))

            log.info("%s: heuristic_stats median\n%s\n\n" % (cube, pformat(cube.heuristic_stats)))
            sys.exit(0)
        else:
            raise

    end_time = dt.datetime.now()
    log.info("Final Cube")
    cube.print_cube()
    cube.print_solution(not args.no_comments)

    log.info("*********************************************************************************")
    log.info("See /tmp/rubiks-cube-NxNxN-solver/index.html for more detailed solve instructions")
    log.info("*********************************************************************************\n")

    # Now put the cube back in its initial state and verify the solution solves it
    solution = cube.solution
    cube.re_init()
    len_steps = len(solution)

    for (i, step) in enumerate(solution):

        if args.print_steps:
            print(("Phase     : %s" % cube.phase()))
            print(("Move %d/%d: %s" % (i+1, len_steps, step)))

        cube.rotate(step)

        www_desc = "Phase: %s<br>\nCube After Move %d/%d: %s<br>\n" % (cube.phase(), i+1, len_steps, step)
        cube.www_write_cube(www_desc)

        if args.print_steps:
            cube.print_cube()
            print("\n\n\n\n")

    cube.www_footer()

    if args.print_steps:
        cube.print_cube()

    if args.min_memory:
        print("\n\n****************************************")
        print("--min-memory has been replaced by --fast")
        print("****************************************\n\n")

    log.info("rubiks-cube-solver.py end")
    log.info("Memory : {:,} bytes".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    log.info("Time   : %s" % (end_time - start_time))
    log.info("")

    if not cube.solved():
        kociemba_string = cube.get_kociemba_string(False)
        #edge_swap_count = cube.get_edge_swap_count(edges_paired=True, orbit=None, debug=True)
        #corner_swap_count = cube.get_corner_swap_count(debug=True)

        #raise SolveError("cube should be solved but is not, edge parity %d, corner parity %d, kociemba %s" %
        #    (edge_swap_count, corner_swap_count, kociemba_string))
        raise SolveError("cube should be solved but is not")


except (ImplementThis, SolveError, StuckInALoop, NoSteps, KeyError, NoPruneTableState):
    cube.enable_print_cube = True
    cube.print_cube_layout()
    cube.print_cube()
    cube.print_solution(False)
    print((cube.get_kociemba_string(True)))
    log.info("rubiks-cube-solver.py end")
    raise
