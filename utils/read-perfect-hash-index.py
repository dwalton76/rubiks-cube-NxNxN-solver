# standard libraries
import sys

filename = sys.argv[1]
pt0_state = int(sys.argv[2])
pt1_state = int(sys.argv[3])
pt0_max = int(sys.argv[4])

with open(filename, "r") as fh:
    data = fh.read()
    index = (pt0_state * pt0_max) + pt1_state
    print(f"index {index} is {data[index]}")
