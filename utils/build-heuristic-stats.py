#!/usr/bin/env python3

from rubikscubennnsolver import RubiksCube
from rubikscubennnsolver.RubiksCube555 import solved_555
import json
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)12s %(levelname)8s: %(message)s')
log = logging.getLogger(__name__)

# Color the errors and warnings in red
logging.addLevelName(logging.ERROR, "\033[91m   %s\033[0m" % logging.getLevelName(logging.ERROR))
logging.addLevelName(logging.WARNING, "\033[91m %s\033[0m" % logging.getLevelName(logging.WARNING))

stats = {
    "5x5x5" : [],
}


# Step 1 - lookup-table-5x5x5-step100-ALL-centers-stage.txt
# - reverse the steps and apply them to a solved cube
# - record the stats for all 6 tables at each step

# Step 2 - take a solved cube and start scrambling it
# - record the stats for all 6 tables at each step
# - only record the state if it is one that we haven't seen before
#   or if it has a lower cost than the one we have seen...or
#   do we record a bunch of them and take the median?
#
# Step 3 - write the results to a file
#
# For 5x5x5 centers there are 6 tables each with a max cost of 8
# So that would be 8^6 or 262,144 possible combinations. I can't
# imagine us actually finding that many, I don't think it is possible
# for the cube to be in a state where all 6 tables have a cost
# of 8 (one example)

'''
for x in range(5):

    cube = RubiksCube(solved_555, 'URFDLB')
    cube.randomize()
    ks = cube.get_kociemba_string(True)
    stats["5x5x5"].append(ks)
'''

print(json.dumps(stats, indent=4, sort_keys=True))

