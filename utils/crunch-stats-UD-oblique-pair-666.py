#!/usr/bin/env python3

from pprint import pprint
import statistics

data = {}

with open('lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt.stats', 'r') as fh:
    for line in fh:
        (left_cost, right_cost, actual_cost) = line.strip().split(',')
        left_cost = int(left_cost)
        right_cost = int(right_cost)
        actual_cost = int(actual_cost)

        if actual_cost < left_cost:
            print("ERROR: actual_cost %d < left_cost %d" % (actual_cost, left_cost))

        if actual_cost < right_cost:
            print("ERROR: actual_cost %d < right_cost %d" % (actual_cost, right_cost))

        # find the min
        #if (left_cost, right_cost) not in data or actual_cost < data[(left_cost, right_cost)]:
        #    data[(left_cost, right_cost)] = actual_cost

        if (left_cost, right_cost) not in data:
            data[(left_cost, right_cost)] = []

        data[(left_cost, right_cost)].append(actual_cost)

# find the average
'''
for (left_cost, right_cost), list_actual_cost in data.items():
    total = 0
    count = 0
    for actual_cost in list_actual_cost:
        total += actual_cost
        count += 1

    data[(left_cost, right_cost)] = int(total/count)
'''


# find the median
for (left_cost, right_cost) in sorted(data.keys()):
    list_actual_cost = data[(left_cost, right_cost)]
    data[(left_cost, right_cost)] = statistics.median(list_actual_cost)
    #print("(%d, %d) has %d entries" % (left_cost, right_cost, len(list_actual_cost)))


for (left_cost, right_cost) in sorted(data.keys()):
    actual_cost = data[(left_cost, right_cost)]
    print("            (%d, %d) : %d," % (left_cost, right_cost, actual_cost))
