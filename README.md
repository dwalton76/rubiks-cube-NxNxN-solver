# rubiks-cube-NxNxN-solver

## Overview
This is a rubiks cube solver that can solve any size cube, I have tested
up to 17x17x17. The following tables show the reduction in move counts
as the solver has evolved. The table starts in July 2018, the earlier
releases of the solver had drastically higher move counts, I think it was
over 400 moves the first time I solved a 5x5x5.

Solving a 2x2x2 takes around 9 moves while solving a 3x3x3 takes around 20 moves.
I am not working on those solvers so I did not include them in the table below.

### Move Counts
The move counts here are to reduce the cube to a 3x3x3. Solving the reduced 3x3x3 cube
will add another ~20 moves.

| Date | Commit | 4x4x4 | 5x5x5 | 6x6x6 | 7x7x7 | 8x8x8 | 9x9x9 | 10x10x10 |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| 09/26/2021 | [b6ab34f](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/b6ab34f9ef0323cb55466e67a1bf4d3510a8b7c0) | 51.6 | 78.9 | 139.7 | 193.8 | **320.6** | 394.4 | **549.2** |
| 09/09/2021 | [722673f](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/722673f7c95e17768623185de0c847ed28ca2d52) | 50 | **77.5** | **139** | **193** | **335** | **393** | **573** |
| 10/5/2019 | [TBD](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/TBD) | 50 | **79** | **145** | **202** | 353 | **406** | 618 |
| 10/17/2018 | [TBD](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/TBD) | 50 | 88 | 156 | 218 | 344 | **430** | **601** |
| 09/24/2018 | [TBD](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/TBD) | 50 | **88** | **156** | **218** | **344** | 454 | 630 |
| 09/17/2018 | [TBD](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/TBD) | 50 | 103 | **160** | **221** | 346 | **444** | **614** |
| 08/24/2018 | [9dc52a7](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/9dc52a7afa7951aa3483818d72bfb47373a65131) | 50 | 103 | **161** | **224** | **346** | 469 | **617** |
| 08/20/2018 | [39bf371](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/39bf3718d0444317b20e07994321c053d54abcaf) | 50 | 103 | **162** | **228** | **366** | **466** | **636** |
| 08/19/2018 | [6b8993a](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/6b8993a7a2cc6bf000e8559b3e2006112621080d) | 50 | **103** | 165 | 244 | 362 | 513 | 669 |
| 08/13/2018 | [b754e60](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/b754e60cd6b907d3208301807c1108492475ef44) | **50** | 107 | 165 | 244 | 362 | 513 | 669 |
| 08/13/2018 | [bdbbd46](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/bdbbd46c3f3bf4d150dd1a45466489709c4d2e45) | 52 | 107 | **165** | **244** | **362** | **513** | **669** |
| 07/16/2018 | [456ddd1](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/456ddd18f761590294b0b28ac1574a2494514917) | **52** | 107 | **172** | 247 | **376** | 520 | **725** |
| 07/12/2018 | [c9484d9](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/c9484d93cd55ae50bffb658165e2f843ac5c5fe1) | 60 | 107 | **176** | 247 | 386 | 520 | 743 |
| 07/12/2018 | [5cda2c8](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/5cda2c8e94deba9cecc6b9e87f265b401b3d97a4) | 60 | 107 | 181 | **247** | **386** | **520** | 743 |
| 07/08/2018 | [9c13b16](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/9c13b16dbea8abd0581dfaa0abeb4960c54010a4) | 60 | 107 | 181 | **257** | **403** | **531** | **743** |
| 07/07/2018 | [e876493](https://github.com/dwalton76/rubiks-cube-NxNxN-solver/commit/e87649306139adebdc86ba1880b1e0c0e9265c5a) | 60 | 107 | **181** | **272** | 408 | 556 | 768 |
| 07/04/2018 | | 60 | 107 | 200 | 278 | 408 | 556 | 768 |

## Install

### Install the rubikscubennnsolver python module
```bash
$ cd ~/
$ git clone https://github.com/dwalton76/rubiks-cube-NxNxN-solver.git
$ cd rubiks-cube-NxNxN-solver
$ make init
```

### Install 3x3x3 solver
The kociemba solver is required to solve the larger cubes that have been
reduced to 3x3x3.

```bash
$ git clone https://github.com/dwalton76/kociemba.git
$ cd ~/kociemba/kociemba/ckociemba/
$ make
$ sudo make install
```

### Download lookup tables from Amazon S3 bucket
A few hundred hours of CPU time were used to build the "lookup tables" used by this cube solver.
These lookup table are stored in an Amazon S3 bucket and will be downloaded as needed (different
size cubes will download different lookup tables). Once downloaded they will not need to be
downloaded again.

## Usage
Run rubiks-cube-solver.py where --state is your cube state in kociemba
order (URFDLB). You must run rubiks-cube-solver.py from the directory that
holds your lookup-table\*.txt files

Example:
```bash
$ cd ~/rubiks-cube-NxNxN-solver
$ source ./venv/bin/activate
$ ./rubiks-cube-solver.py --state LFBDUFLDBUBBFDFBLDLFRDFRRURFDFDLULUDLBLUUDRDUDUBBFFRBDFRRRRRRRLFBLLRDLDFBUBLFBLRLURUUBLBDUFUUFBD
```

## History
One of my hobbies is building Lego Mindstorms robots that can solve rubiks cubes.
I was able to find solvers for 2x2x2, 3x3x3, 4x4x4 and 5x5x5 but I couldn't find
a solver for anything larger than that :( The solvers that I did find for 4x4x4
and 5x5x5 took quite a bit of RAM (several gigs) but I wanted to be able to run
the solver on a Lego Mindstorms EV3 which is 300Mhz and 64M of RAM. So I decided
to write my own solver and here we are :)

Here is the thread on speedsolving.com where I first posted looking for solvers.
I ended up posting updates to this thread as my solver evolved:
https://www.speedsolving.com/forum/threads/5x5x5-6x6x6-7x7x7-or-nxnxn-solvers.63592/


## Examples
```bash
2x2x2
=====
reset; ./rubiks-cube-solver.py --state DLRRFULLDUBFDURDBFBRBLFU


3x3x3
=====
reset; ./rubiks-cube-solver.py --state RRBBUFBFBRLRRRFRDDURUBFBBRFLUDUDFLLFFLLLLDFBDDDUUBDLUU


4x4x4
=====
reset; ./rubiks-cube-solver.py --state FLDFDLBDFBLFFRRBDRFRRURBRDUBBDLURUDRRBFFBDLUBLUULUFRRFBLDDUULBDBDFLDBLUBFRFUFBDDUBFLLRFLURDULLRU


5x5x5
=====
reset; ./rubiks-cube-solver.py --state LLFBRBFUDULBULBBDDUBBBBLDFDULDLURFBDFRLDUFDBRLDUFBLURFRFRDRBULFBLLLBURUFRFURDDLBULLLRLRDFRDRBBRUDFDUFRBUDULFDUFULDFRBRBULLUFFBLRDDDDFRRBUBRLBUUFFRRDFF


6x6x6
=====
reset; ./rubiks-cube-solver.py --state FBDDDFFUDRFBBLFLLURLDLLUFBLRFDUFLBLLFBFLRRBBFDRRDUBUFRBUBRDLUBFDRLBBRLRUFLBRBDUDFFFDBLUDBBLRDFUUDLBBBRRDRUDLBLDFRUDLLFFUUBFBUUFDLRUDUDBRRBBUFFDRRRDBULRRURULFDBRRULDDRUUULBLLFDFRRFDURFFLDUUBRUFDRFUBLDFULFBFDDUDLBLLRBL


7x7x7
=====
reset; ./rubiks-cube-solver.py --state DBDBDDFBDDLUBDLFRFRBRLLDUFFDUFRBRDFDRUFDFDRDBDBULDBDBDBUFBUFFFULLFLDURRBBRRBRLFUUUDUURBRDUUURFFFLRFLRLDLBUFRLDLDFLLFBDFUFRFFUUUFURDRFULBRFURRBUDDRBDLLRLDLLDLUURFRFBUBURBRUDBDDLRBULBULUBDBBUDRBLFFBLRBURRUFULBRLFDUFDDBULBRLBUFULUDDLLDFRDRDBBFBUBBFLFFRRUFFRLRRDRULLLFRLFULBLLBBBLDFDBRBFDULLULRFDBR


8x8x8
=====
reset; ./rubiks-cube-solver.py --state DRRRURBDDBFBRBDDBRRDUFLLURFBFLFURLFLFRBRFUBDRFDFUUBLFFFUULBBFDBDFBUBBFRFLRDLFDRBBLLFRLDFDRBURULDDRFFBFUUBLLFBRUUFDUBRDBBRDFLURUUFFUDLBRRFDUBFLRUUFFRLBFRFLRULUDFRUBBDBFFLBBDFDFLDBFRRRDDLFLBRBFBBRULDDUUBLBBURULLDDLDRUDRBUDRLUULDURLRDFLFULUFLFULRDDDUBBULRBRDFBBLFURRLULUBDDULRFBRFURBRLBRUBULBDDFBUFFBBRLRUUUFRULLBFFRFDDFFDULLDLBUDLLLLUUBBLDLLBBULULBDUDDFUBFLLDLDLFRDUDDBRRFRURRFRRLDDDDRD


9x9x9
=====
reset; ./rubiks-cube-solver.py --state RFBLRUFLLFFLRRBDUDDBBBDUDFRUDUFFFBBFRBRDURBULFUDDFLLLDLFLRDLDBBBUUBRDBBBDFUFRUURULURBURDLFDUBFFDRDFRUBDUBRFLRRLUDLRLFBLBRRLLRDRBRBLURBLLRFRLDDFFFRBFUFURDFRRUDUFDDRRRLFLLUBBLBFDRRDLBRLUUBRDBBUBFLUUFBLLDBFFFBUFBFDBRDDDFLRFFBFFFLFRRDUUDDBUBLUUDURRBDBFFLFURDDLUBULUULULBFBRUBLLDDFLRBDBRFDUUDFURLLUBUFBLULLURDLLLBLFFRLLBLUDRLRDBLDDBRBUDRBLLRDUUUBRRFBFBBULUDUDLDRFUDDDFULRFRBDUDULBRRDBDFFRUUFRRFBDBLFBBDFURLRFDUUFRLUBURFURDDFLDFUBDFRRURRDLUDRBRBDLBFLBBRDLRDBFDUBDFFUBLFLUULLBUDLLLURDBLFFFDFLF


10x10x10
========
reset; ./rubiks-cube-solver.py --state ULBDLDBUFRBBBBBLBFFFDFRFBBDDFDFRFFLDLDLURRBUDRRBFLUDFRLBDURULRUUDBBBUBRURRRLDLRFFUFFFURRFBLLRRFLFUDBDRRDFULLLURFBFUUBDBBDBFLFDFUUFDUBRLUFDBLRFLUDUFBFDULDFRUBLBBBUBRRDBDDDDFURFLRDBRRLLRFUFLRDFDUULRRDULFDUDRFLBFRLDUDBDFLDBDUFULULLLBUUFDFFDBBBRBRLFLUFLFUFFRLLLFLBUDRRFDDUDLFLBRDULFLBLLULFLDLUULBUDRDFLUDDLLRBLUBBRFRRLDRDUUFLDDFUFLBDBBLBURBBRRRFUBLBRBRUBFFDBBBBLBUFBLURBLDRFLFBUDDFFRFFRLBDBDUURBUFBDFFFLFBDLDUFFBRDLBRLRLBFRUUUULRRBDBRRFDLLRRUUBDBDBFDLRDDBRUUUUUBLLURBDFUFLLRDBLRRBBLBDDBBFUDUDLDLUFDDDUURBFUFRRBLLURDDRURRURLBLDRFRUFBDRULUFFDUDLBBUURFDUDBLRRUDFRLLDULFUBFDLURFBFULFLRRRRRFDDDLFDDRUFRRLBLUBU


11x11x11
========
reset; ./rubiks-cube-solver.py --state URBDLBURUBUFDDRBUFDDUBFRDBLRFUUBLDRLBBUBLUFBLRBFFDDLLLDRULRBUDBBRLULBUUUFFRUBLUFUUBRLBLUUDRLDUBLUFDLBLFDBLFRLFLRUDFLLLDFULDRFDFLLFLLRDUUDRFRFFFFBFRBFRFUUBBUULURLULBBLLDDLBUFRURBLFFBRFFRRURFUFLLRUFDBDDDBLRDUBLBRBLRLBUBULLBBFRBFRBLFUDDULLFBRLDUFBBLDBBFBDBDUFFRRDBUUULDDBRFRDBDDRDRFUDBBFULDLUDBLRRFDBLDBLRFFBDLRBUBLDLUDFUFBDDRUDRDFUBLFFRBDFDDDBULBDRBUDBBDRLUFUFFFFDRBDLRLRDRRBFRLUBFFURFRLRLRRLDBLFLFULBURULDURURBLUFUULFBFULULUDLFLLUFLRFLRLFFDRBLLFRDDDBFBFFBLULDLRUDUURLRUFDRFRDURDUFFFULRRUURUDFURBDLBLLDFBBRDRLUBULFRDLRUFUFDBBDLRRURFULBBBBDBRUDUUULFFBUDLRUBRDDRBFDDBURRLURRDDRRRUURURFUBRRBFRFFFBLBLLDURBDRDFDFRRDRDDLDUFUFFLBDLBBDFLLLFDULDBLDRUUFDURBDLUBBLBDDFFDUURBLDRBRLDBLUDRLRFBFDUFUUBFBRDRFFFFUDDDRFFLDFLRRBLDRRDRFBFBLUDBFBBB


14x14x14
========
reset; ./rubiks-cube-solver.py --state FBDRLBLRRURRLDRBDLBURDFDDDRBLBBFBRDLLFDUBLFRLDFUUBFRDBFBBBULFRLBUFLBDDDLLDRBFLLBBLFBFFDFBFDDFRRRBDRRBRBDUFDRLRUDLDFDDURFLBUBBUUDLBRRDUDRDBBBLDBRBBBUFLBLRUURBDDLDRLUFFBLFRLDFBRFLDLBULFFBRLDBDDFLLRFLUBFDFBRLRLFDBLBURLBLFRFBLLDULUDURLBUUULLRRLUBDDLURLLRFURFRFRBDDUBLDFBLUDRLRDRRBLFUFRDUFFRULBLRBBRUFDBUBBBBLDBRBLDDRRFDDBFFUUBRBLFUBBRFUURBFDRLURLRBFUUFUBRUDRBDFBBFURFLFFDRDFUFFULFLUBDFUFFDLRRFRUDUDLBBBDLLLDUFUDRFDBLRRFFLRUFDRFURDLRRDRDLFBRLRLULRFBDLFDRLFRDDFLLDBFBUBBRLLDLFURFRFULUBLUBFLFFBFDFBDUUBURUUUBFUBDLLFLUUUFDUDLUUULDLLUDDBUFRDRULRLLULRULFBLUDFURFLFUBDLLFLFUBUUBBUFLUDUBRDBLFFUUUFDRLRULUDDRLRBLRUUFBRRRRULBDLFBFLDLRDFUBLUBRDDFUULFLDLUBFURRURUBDFFFDLRFFLBRFRDRUDUULURULLDFRBUDRDLFUFULDBLUBFRFBURDLLUUFDURLRDBLFFRFDBFURLFUBLUUUFFRULUBURRURFDDBFUFRBURBBDRFUDDFDLRUURFBBDBDRLUBRRBFDFRDFDLRDUFFUBRRBDBBLDLFDUDDRLFRRRBUUUBRFUFBUFFBRRDRDDBBDRUULDRFRFBUFLFFBLRBFLLLRUDFDRUDLDRLFRLUFLUBRDUFDDLLUDDRBUBBBDRDBBFRBDDRRLRRUUBBUDUDBLDBDFLFRFUBFLFDBBLRLULDBRFBRRLUUURDFFFDBLDUDBRFDDFFUBLUUURBBULFUFUDFBRDLLFURBULULBUDLUFFBDRBRRDBUUULFDURRDFDDLUDBDRBFBUFLULURUFDRFRFBBFBBBDRLBLUDLDRDLLDRRLLDLFBRBRLDUFBDDUDBLDFRFBBBDRDRDDLDRULFFLLFLBLDFLURLBUDFBDLRBLFDFLUDDFUBUBLURBBBLFRLFLBDDBURFFBFRRL


15x15x15
========
reset; ./rubiks-cube-solver.py --state RLURLURBDDULFUUURFLRBLURUBFDBULFLUBBFLDUFBDRFRBRUDFULFRUFLUDFRLFDFLLFDBULURRLBFBUURDULFDFBLRRRLFULLFFFDUULRRRUUUUFDBLDDFFLRDLLUURUBBULUFFURBRRLBBUUBBFDRRBRBRLUDLUDRBFBFULLRRBBFBFRDDDLDDDFRFUFLURUFLBDLUBRLDFRRDBDBFLFUDFLDFFURLFULLDDRURRDLRFLDFLULUUDDRFDRBLRBRBFUFDBDUUDBRRBDFBLBLRBBLBFLLDUBFFFFBDDRLBBBRFDFFUBBDURFLUUDDDRDDLDBRLBULLFLFBRBRBLUDDLRDRDUDFLFRUFLDLBLURDDDRUFDLBRDRLFBDBLDRFBFFBURULUDRRBRDFRFFLULLUBRDRRRDUFRBLFULUBBUFFBRBBFRLFDRRDBLDFRDRDDRLRUULBDURDURFDDLFDUUDBFLBDUFBULFRRDUDUBFBUDBBFUDFUUDLUDDRFDDDFRRRBUDRBFBBULLUFBLRLFLLBRRRRUBDRFLFDFDBLRFLURULULFFBUUUUFDBBLDLUBBRUBBBRBFLULLBLUUULLUBFFDULDFFBFFFUFFDUDRFBUFLDDLURFLRFLRFBUUBLRFDDRULUUUFFRDDBLRDULFURUDDBDLBBUUBFURFRFBRLBUULBLDDDBUBRFFULLUDFFDLDFUBLLBLDFFDDLBDUFUFFLBBBUBULDDFBRRFFLDUDDFRBLRRDDUDLBDBLURBUDBRRLUBBDRFBUFRDRDRBBDULBUFFDRBBDFBUULFFRLLDURRRDFFUUFULDULURLDLUUUDLBBUDLDRFBDBBDLUFBRRFDFLLDLFDBRBBRFUDDDBURDRBUBRUBDUBLDLLDLURLDFDBRUBDLDFRRRBRLULFRFLDRLBUBRUBLFBFDFFLFRFDFLBRULLRBLDRBBFURRRDUUULLULLDLBLBBDFBUUUBRRUFFBRUDBFRDFDLFLFFRFFFFRULDFFDFRUBBBRURBUFLBDFBBBBBRRRLFLFBDRRUFLURDDLRRBRLLFURRURBRFLLLFFURBFULFRFFBLDUUUUBDDUFFDRBRLDDFRBULDDDFFRURUFLDRFLDFBLRUFFUBBDFFDBLLDBDUBDLDLUDFBFLRULRRBDBLRBLDLUURRLLRULDBLBLLRRFDDRBBRBUBDDULDRFBFBBFLUFBLUULDDFDBRLLUBUBBDFBBLBBUBLULDRUDBLRULDUDLUFRRDLLUDDBUFLFLBUFUURFDRDLBURLLRRRULRBFFRRBRFBUBRBUUFRLRDRDLBBRFLLLDDBRFUFRBULFLFDRDDRRDBF
```
