#!/usr/bin/env python3

"""
Print the layout of a cube
"""
# standard libraries
import sys

# rubiks cube libraries
from rubikscubennnsolver import get_cube_layout

print(f"\n{get_cube_layout(int(sys.argv[1]))}\n")
