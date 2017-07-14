# rubiks-cube-NxNxN-solver

## Overview
This is a work in progress...here is what works so far:
* 2x2x2 works
* 3x3x3 works via the kociemba solver
* 4x4x4 works, average solution is 65 moves
* 5x5x5 works, average solution is 119 moves
* 6x6x6 works, average solution is X moves
* 7x7x7 works, average solution is X moves

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
