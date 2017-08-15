#!/usr/bin/env python3

from pprint import pprint
import statistics

data = {}

with open('lookup-table-5x5x5-step10-UD-centers-stage.txt.stats', 'r') as fh:
    for line in fh:
        (t_cost, x_cost, actual_cost) = line.strip().split(',')
        t_cost = int(t_cost)
        x_cost = int(x_cost)
        actual_cost = int(actual_cost)

        if actual_cost < t_cost:
            print("ERROR: actual_cost %d < t_cost %d" % (actual_cost, t_cost))

        if actual_cost < x_cost:
            print("ERROR: actual_cost %d < x_cost %d" % (actual_cost, x_cost))

        # find the min
        #if (t_cost, x_cost) not in data or actual_cost < data[(t_cost, x_cost)]:
        #    data[(t_cost, x_cost)] = actual_cost

        if (t_cost, x_cost) not in data:
            data[(t_cost, x_cost)] = []

        data[(t_cost, x_cost)].append(actual_cost)

# find the average
'''
for (t_cost, x_cost), list_actual_cost in data.items():
    total = 0
    count = 0
    for actual_cost in list_actual_cost:
        total += actual_cost
        count += 1

    data[(t_cost, x_cost)] = int(total/count)
'''


# find the median
for (t_cost, x_cost) in sorted(data.keys()):
    list_actual_cost = data[(t_cost, x_cost)]
    data[(t_cost, x_cost)] = statistics.median(list_actual_cost)
    #print("(%d, %d) has %d entries" % (t_cost, x_cost, len(list_actual_cost)))


for (t_cost, x_cost) in sorted(data.keys()):
    actual_cost = data[(t_cost, x_cost)]
    print("            (%d, %d) : %d," % (t_cost, x_cost, actual_cost))
