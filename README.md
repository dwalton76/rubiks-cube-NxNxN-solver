# rubiks-cube-NxNxN-solver

## Overview
This is a work in progress...here is what works so far:
* 2x2x2 works
* 3x3x3 works via the kociemba solver
* 4x4x4 works, average solution is 65 moves
* 5x5x5 works, average solution is 119 moves
* 6x6x6 works, average solution is 214 moves
* 7x7x7 works, average solution is 304 moves
* NxNxN even cubes, am testing with a 14x14x14, not working yet
* NxNxN odd cubes, am testing with a 15x15x15, not working yet

All cubes 4x4x4 and larger follow the same basic approach:
* Solve centers
* Pair edges
* Solve as 3x3x3

## Install

### Install 3x3x3 solver
The kociemba solver is required to solve the larger cubes that have been
reduced to 3x3x3.

```
$ git clone https://github.com/dwalton76/kociemba.git
$ cd ~/kociemba/kociemba/ckociemba/
$ make
$ sudo make install
```

### Install the rubikscubennnsolver python module
```
$ git clone https://github.com/dwalton76/rubiks-cube-NxNxN-solver.git
$ cd rubiks-cube-NxNxN-solver
$ sudo python2 setup.py install
$ gunzip lookup-table*.gz
```

## Usage
Run rubiks-cube-solver.py where --state is your cube state in kociemba
order (URFDLB). You must run rubiks-cube-solver.py from the directory that
holds your lookup-table\*.txt files

Example:
```
$ cd ~/rubiks-cube-NxNxN-solver
$ ./usr/bin/rubiks-cube-solver.py --state LFBDUFLDBUBBFDFBLDLFRDFRRURFDFDLULUDLBLUUDRDUDUBBFFRBDFRRRRRRRLFBLLRDLDFBUBLFBLRLURUUBLBDUFUUFBD
```

## History
One of my hobbies is building Lego Mindstorms robots that can solve rubiks cubes. I was able to find solvers for 2x2x2, 3x3x3, 4x4x4 and 5x5x5 but I couldn't find a solver for anything larger than that :(  The solvers that I did find for 4x4x4 and 5x5x5 took quite a bit of RAM (several gigs) but I wanted to be able to run the solver on a Lego Mindstorms EV3 which is 300Mhz and 64M of RAM. So I decided to write my own solver and here we are :)

Here is the thread on speedsolving.com where I first posted looking for solvers. I ended up posting updates to this thread as my solver evolved:
https://www.speedsolving.com/forum/threads/5x5x5-6x6x6-7x7x7-or-nxnxn-solvers.63592/
