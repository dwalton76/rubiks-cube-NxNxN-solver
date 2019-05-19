#!/usr/bin/env python3

from rubikscubennnsolver.RubiksCube333 import solved_333
from rubikscubennnsolver.RubiksCube444 import solved_444
from rubikscubennnsolver.RubiksCube555 import solved_555
from rubikscubennnsolver.RubiksCube666 import solved_666
from rubikscubennnsolver.RubiksCubeBuildHighLowMapping import (
    RubiksCubeHighLow333,
    RubiksCubeHighLow444,
    RubiksCubeHighLow555,
    RubiksCubeHighLow666,
)
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)20s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)


cube = RubiksCubeHighLow333(solved_333, 'URFDLB')
#cube = RubiksCubeHighLow444(solved_444, 'URFDLB')
#cube = RubiksCubeHighLow555(solved_555, 'URFDLB')
#cube = RubiksCubeHighLow666(solved_666, 'URFDLB')
cube.build_highlow_edge_values()
