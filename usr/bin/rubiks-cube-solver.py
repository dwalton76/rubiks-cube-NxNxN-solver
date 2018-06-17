#!/usr/bin/env python3

"""
Solve any size rubiks cube:
- For 2x2x2 and 3x3x3 just solve it
- For 4x4x4 and larger, reduce to 3x3x3 and then solve

This is a work in progress
"""

from rubikscubennnsolver import ImplementThis, SolveError, StuckInALoop
from rubikscubennnsolver.LookupTable import NoSteps
from math import sqrt
import argparse
import datetime as dt
import logging
import os
import resource
import sys

def remove_slices(solution):
    results = []

    for step in solution:

        if 'w' in step:
            results.append(step)

        elif step == "2U":
            results.append("Uw")
            results.append("U'")

        elif step == "2U'":
            results.append("Uw'")
            results.append("U")

        elif step == "2U2":
            results.append("Uw2")
            results.append("U2")

        elif step == "3U":
            results.append("3Uw")
            results.append("Uw'")

        elif step == "3U'":
            results.append("3Uw'")
            results.append("Uw")

        elif step == "3U2":
            results.append("3Uw2")
            results.append("Uw2")

        elif step == "2L":
            results.append("Lw")
            results.append("L'")

        elif step == "2L'":
            results.append("Lw'")
            results.append("L")

        elif step == "2L2":
            results.append("Lw2")
            results.append("L2")

        elif step == "3L":
            results.append("3Lw")
            results.append("Lw'")

        elif step == "3L'":
            results.append("3Lw'")
            results.append("Lw")

        elif step == "3L2":
            results.append("3Lw2")
            results.append("Lw2")




        elif step == "2F":
            results.append("Fw")
            results.append("F'")

        elif step == "2F'":
            results.append("Fw'")
            results.append("F")

        elif step == "2F2":
            results.append("Fw2")
            results.append("F2")

        elif step == "3F":
            results.append("3Fw")
            results.append("Fw'")

        elif step == "3F'":
            results.append("3Fw'")
            results.append("Fw")

        elif step == "3F2":
            results.append("3Fw2")
            results.append("Fw2")



        elif step == "2R":
            results.append("Rw")
            results.append("R'")

        elif step == "2R'":
            results.append("Rw'")
            results.append("R")

        elif step == "2R2":
            results.append("Rw2")
            results.append("R2")

        elif step == "3R":
            results.append("3Rw")
            results.append("Rw'")

        elif step == "3R'":
            results.append("3Rw'")
            results.append("Rw")

        elif step == "3R2":
            results.append("3Rw2")
            results.append("Rw2")



        elif step == "2B":
            results.append("Bw")
            results.append("B'")

        elif step == "2B'":
            results.append("Bw'")
            results.append("B")

        elif step == "2B2":
            results.append("Bw2")
            results.append("B2")

        elif step == "3B":
            results.append("3Bw")
            results.append("Bw'")

        elif step == "3B'":
            results.append("3Bw'")
            results.append("Bw")

        elif step == "3B2":
            results.append("3Bw2")
            results.append("Bw2")



        elif step == "2D":
            results.append("Dw")
            results.append("D'")

        elif step == "2D'":
            results.append("Dw'")
            results.append("D")

        elif step == "2D2":
            results.append("Dw2")
            results.append("D2")

        elif step == "3D":
            results.append("3Dw")
            results.append("Dw'")

        elif step == "3D'":
            results.append("3Dw'")
            results.append("Dw")

        elif step == "3D2":
            results.append("3Dw2")
            results.append("Dw2")

        else:
            results.append(step)

    return results

start_time = dt.datetime.now()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))


parser = argparse.ArgumentParser()
parser.add_argument('--print-steps', default=False, action='store_true', help='Display animated step-by-step solution')
parser.add_argument('--debug', default=False, action='store_true', help='set loglevel to DEBUG')

# CPU mode
action = parser.add_mutually_exclusive_group(required=False)
action.add_argument('--tsai', default=False, help='Use the tsai solver, 4x4x4 only', action='store_true')

parser.add_argument('--colormap', default=None, type=str, help='Colors for sides U, L, etc')
parser.add_argument('--order', type=str, default='URFDLB', help='order of sides in --state, default kociemba URFDLB')
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
#    default='FUULURFFRLRBDDDULUDFLFBBFUURRRUBLBLBDLUBDBULDDRDFLFBBRDBFDBLRBLDULUFFRLRDLDBBRLRUFFRUBFDUDFRLFRU')
    default='DRFDFRUFDURDDLLUFLDLLBLULFBUUFRBLBFLLUDDUFRBURBBRBDLLDURFFBBRUFUFDRFURBUDLDBDUFFBUDRRLDRBLFBRRLB') # xyzzy test cube
#    default='UDRFFBFLFUDLBDDDRUFLBBBFBDUDBBFFUBRBBRRUBRRUFULDRFDLLDFLDUFLUFLRBRDLFDBRRUFRLBBDDULRRLLURLLUUUDF') # OLL
#    default='DRDBBBRFBBDFLDUURRRDDUUBLFRRUFUUFLFFUUFRURLFURRRLBBBDBLDFLDLDLDLFLLDUUBFDDDBBLBBLFURUFLLUFRRFBDR') # OLL
#    default='RRRRRRRLRRRLRRRFLBBFBBBBBBBBRBBBUUUUUDDDUDDDDDDULLLFLLLRLLLRLFFLBFFBLFFFLFFFBFFFDDDDUUUUUUUUUDDD')
#    default='DUFFRDLRDLBUDLBULLBLFFUBURFFURFURDUBUDLLFDLRFDLRRRDBBBDDUFULLBFFBBBBLBBRFFUDFFUDDDLLDRRBRRUURRLU') # edges take 27 steps (used to take 46 steps)
#    default='LFBDUFLDBUBBFDFBLDLFRDFRRURFDFDLULUDLBLUUDRDUDUBBFFRBDFRRRRRRRLFBLLRDLDFBUBLFBLRLURUUBLBDUFUUFBD')
#    default='DFBRULBFFUDFDRULURDUUFLLRFLFDLRRFBRFUDUFLRBDBDULRBLBBBFDUFUBUFBDLLLRURDBDBDDBBLUFDRFFULRURRRBLDL') # takes a lot of moves
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

if args.debug:
    log.setLevel(logging.DEBUG)

# no longer used
#if args.test:
#    cube = RubiksCube444(solved_444, args.order, args.colormap, avoid_pll=True, debug=args.debug)
#    cube.test()
#    sys.exit(0)

try:
    size = int(sqrt((len(args.state) / 6)))

    if size == 2:
        from rubikscubennnsolver.RubiksCube222 import RubiksCube222
        cube = RubiksCube222(args.state, args.order, args.colormap, args.debug)
    elif size == 3:
        from rubikscubennnsolver.RubiksCube333 import RubiksCube333
        cube = RubiksCube333(args.state, args.order, args.colormap, args.debug)
    elif size == 4:
        from rubikscubennnsolver.RubiksCube444 import RubiksCube444, solved_444
        if args.tsai:
            from rubikscubennnsolver.RubiksCubeTsai444 import RubiksCubeTsai444
            cube = RubiksCubeTsai444(args.state, args.order, args.colormap, avoid_pll=True, debug=args.debug)
        else:
            cube = RubiksCube444(args.state, args.order, args.colormap, avoid_pll=True, debug=args.debug)
    elif size == 5:
        from rubikscubennnsolver.RubiksCube555 import RubiksCube555, solved_555
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

    # Uncomment to produce a cube from alg.cubing.net
    # https://alg.cubing.net/?alg=R_Rw-_D_Uw_R2_Fw2_Uw2_F2_Uw_Fw_%2F%2F_stage_centres%0AU_L_Fw2_D2_L_Fw2_U_Rw2_U-_%2F%2F_3_dedges_%26%232b%3B_partial_centres%0AB_D-_B-_Uw2_L_U-_F_R_Fw2_%2F%2F_6_dedges_%26%232b%3B_centres%0ARw2_U_R-_U-_D-_L2_D_Rw2_%2F%2F_9_dedges%0AFw2_D-_F-_D_Fw2_%2F%2F_12_dedges%0AL2_U-_D_R2_L-_B2_D-_F_%2F%2F_Kociemba_phase_1%0AR2_F2_U2_R2_L2_F2_U-_R2_U-_L2_U2_R2_B2_%2F%2F_Kociemba_phase_2&puzzle=4x4x4&setup=(R1_Rw3_D1_Uw1_R2_Fw2_Uw2_F2_Uw1_Fw1_U1_L1_Fw2_D2_L1_Fw2_U1_Rw2_U3_B1_D3_B3_Uw2_L1_U3_F1_R1_Fw2_Rw2_U1_R3_U3_D3_L2_D1_Rw2_Fw2_D3_F3_D1_Fw2_L2_U3_D1_R2_L3_B2_D3_F1_R2_F2_U2_R2_L2_F2_U3_R2_U3_L2_U2_R2_B2_x-_z-)-&view=playback
    '''
    cube = RubiksCube555(solved_555, args.order, args.colormap)
    for step in remove_slices("y' L 2F2 R 2R2 U D2 R 2U2 D' R 3R2 L' 3R L2 R2 L2 3R L2 B D 2R 3R2 3F 2B' 3U2 2D' L 3R2 2R 3U2 L' B 2U 3U 2B' L2 2U2 2R2 F L 2R' U 2D 2L 2B 2F 3R2 2D2 L' F' 2U' 2L' U2 B R' 3F2 2U2 F 2U' R2 2U' 2D2 L' 3U2 2R2 2F2 2R 2F' 2B 3R2 2U 2F' 3U 3R' D2 2L2 2U F' 2L F' 2B' 3F' U R' F 2R2 2F 3F 2B' 2L2 3U' 2R 3R2 U2 2R' 2B2 2U' 2D 2U2 R2".split()):
        cube.rotate(step)

    kociemba_string = cube.get_kociemba_string(True)
    print(kociemba_string)
    cube.print_cube()
    sys.exit(0)
    '''

    # compress a solution
    '''
    cube = RubiksCube555(solved_555, args.order, args.colormap)
    cube.solution = "Rw' Lw x F2 Rw Lw' x' F' Uw Dw' y' B' Uw Dw' y' B Uw Dw' y' B Uw Dw' y' B' Uw Dw' y' F'".split()
    cube.compress_solution()
    cube.print_solution()
    sys.exit(0)
    '''

    # run build_tsai_phase2_orient_edges_555
    '''
    cube = RubiksCube555(solved_555, args.order, args.colormap)
    cube.build_tsai_phase2_orient_edges_555()
    sys.exit(0)
    '''

    # print cube rotations
    '''
    cube = RubiksCube444(solved_444, args.order, args.colormap)
    original_state = cube.state[:]
    rotations = (
                (),
                ("y",),
                ("y'",),
                ("y", "y"),
                ("x", "x", "y"),
                ("x", "x", "y'"),
                ("x", "x", "y", "y"),
                ("y'", "x", "y"),
                ("y'", "x", "y'"),
                ("y'", "x", "y", "y"),
                ("x", "y"),
                ("x", "y'"),
                ("x", "y", "y"),
                ("y", "x", "y"),
                ("y", "x", "y'"),
                ("y", "x", "y", "y"),
                ("x'", "y"),
                ("x'", "y'"),
                ("x'", "y", "y")
    )

    for rotation_seq in rotations:
        cube.state = original_state[:]

        for step in rotation_seq:
            cube.rotate(step)

        result = []
        for side in (cube.sideU, cube.sideL, cube.sideF, cube.sideR, cube.sideB, cube.sideD):
            result.append(cube.state[side.center_pos[0]])
        print(''.join(result))

    sys.exit(0)
    '''

    cube.sanity_check()
    cube.print_cube()
    cube.www_header()
    cube.www_write_cube("Initial Cube")

    cube.solve()
    log.info("Final Cube")
    cube.print_cube()
    cube.print_solution()

    log.info("***********************************************************")
    log.info("See /tmp/solution.html for more detailed solve instructions")
    log.info("***********************************************************\n")

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

    if not cube.solved():
        kociemba_string = cube.get_kociemba_string(False)
        edge_swap_count = cube.get_edge_swap_count(edges_paired=True, orbit=None, debug=True)
        corner_swap_count = cube.get_corner_swap_count(debug=True)

        raise SolveError("cube should be solved but is not, edge parity %d, corner parity %d, kociemba %s" %
            (edge_swap_count, corner_swap_count, kociemba_string))

    end_time = dt.datetime.now()
    print("\nMemory : {:,} bytes".format(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    print("Time   : %s" % (end_time - start_time))
    print("")

except (ImplementThis, SolveError, StuckInALoop, NoSteps, KeyError):
    cube.print_cube_layout()
    cube.print_cube()
    #cube.tsai_phase2_orient_edges_print()
    cube.print_solution()
    print((cube.get_kociemba_string(True)))
    raise
