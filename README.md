# rubiks-cube-NxNxN-solver

## Overview
This is a work in progress...here is what works so far:
* 2x2x2 works
* 3x3x3 works via the kociemba solver
* 4x4x4 works, average solution is 66 moves
* 5x5x5 works, average solution is 127 moves
* 6x6x6 UD centers

All cubes 4x4x4 and larger follow the same basic approach:
* Stage UD centers to sides U or D
* Stage LR centers to sides L or R
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
$ sudo python2 setup.py install
```

### Install 2x2x2 and 4x4x4 lookup tables
These are small enough to include in the repo, you just have to unzip them.
```
$ gunzip lookup-table*.gz
```

### Install 5x5x5, 6x6x6, etc lookup tables
These are large and will take a little while to download but they take days to
build, it is best to download them. They are too large to store in the repo so
I currently have them in a dropbox folder.  If you send me your email address
I will give you access to the dropbox folder.

Once you've downloaded them unzip them via `gunzip lookup-table*.gz  If you are
curious, the lookup tables were built using the following:
https://github.com/dwalton76/rubiks-cube-lookup-tables


## Usage
Run rubiks-cube-solver.py where --state is your cube state in kociemba
order (URFDLB). You must run rubiks-cube-solver.py from the directory that
holds your lookup-table\*.txt files

Example:
```
$ rubiks-cube-solver.py --state LFBDUFLDBUBBFDFBLDLFRDFRRURFDFDLULUDLBLUUDRDUDUBBFFRBDFRRRRRRRLFBLLRDLDFBUBLFBLRLURUUBLBDUFUUFBD
```
