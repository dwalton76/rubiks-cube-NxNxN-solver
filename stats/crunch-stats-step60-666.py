#!/usr/bin/env python3

from pprint import pprint
import statistics

data = {}

with open('lookup-table-6x6x6-step60-LFRB-solve-inner-x-center-and-oblique-edges.txt.stats', 'r') as fh:
    for line in fh:
        (LR_cost, FB_cost, actual_cost) = line.strip().split(',')
        LR_cost = int(LR_cost)
        FB_cost = int(FB_cost)
        actual_cost = int(actual_cost)

        if actual_cost < LR_cost:
            print("ERROR: actual_cost %d < LR_cost %d" % (actual_cost, LR_cost))

        if actual_cost < FB_cost:
            print("ERROR: actual_cost %d < FB_cost %d" % (actual_cost, FB_cost))

        # find the min
        #if (LR_cost, FB_cost) not in data or actual_cost < data[(LR_cost, FB_cost)]:
        #    data[(LR_cost, FB_cost)] = actual_cost

        if (LR_cost, FB_cost) not in data:
            data[(LR_cost, FB_cost)] = []

        data[(LR_cost, FB_cost)].append(actual_cost)

# find the average
'''
for (LR_cost, FB_cost), list_actual_cost in data.items():
    total = 0
    count = 0
    for actual_cost in list_actual_cost:
        total += actual_cost
        count += 1

    data[(LR_cost, FB_cost)] = int(total/count)
'''


# find the median
for (LR_cost, FB_cost) in sorted(data.keys()):
    list_actual_cost = data[(LR_cost, FB_cost)]
    data[(LR_cost, FB_cost)] = statistics.median(list_actual_cost)
    #print("(%d, %d) has %d entries" % (LR_cost, FB_cost, len(list_actual_cost)))


for (LR_cost, FB_cost) in sorted(data.keys()):
    actual_cost = data[(LR_cost, FB_cost)]

    if actual_cost > LR_cost and actual_cost > FB_cost:
        print("            (%d, %d) : %d," % (LR_cost, FB_cost, actual_cost))
