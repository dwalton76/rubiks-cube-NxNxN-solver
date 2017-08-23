#!/usr/bin/env python3

from pprint import pprint
import statistics

data = {}

with open('lookup-table-6x6x6-step20-UD-oblique-edge-pairing.txt.stats', 'r') as fh:
    for line in fh:
        (state, left_cost, right_cost, actual_cost) = line.strip().split(',')
        left_cost = int(left_cost)
        right_cost = int(right_cost)
        actual_cost = int(actual_cost)

        if actual_cost < left_cost:
            print("ERROR: actual_cost %d < left_cost %d" % (actual_cost, left_cost))

        if actual_cost < right_cost:
            print("ERROR: actual_cost %d < right_cost %d" % (actual_cost, right_cost))

        if (left_cost, right_cost) not in data:
            data[(left_cost, right_cost)] = []

        data[(left_cost, right_cost)].append(actual_cost)

# find the min
data_min = {}
for (left_cost, right_cost) in sorted(data.keys()):
    list_actual_cost = sorted(data[(left_cost, right_cost)])
    data_min[(left_cost, right_cost)] = list_actual_cost[0]

print("        heuristic_stats_min = {")
for (left_cost, right_cost) in sorted(data.keys()):
    actual_cost = data_min[(left_cost, right_cost)]
    if actual_cost > left_cost and actual_cost > right_cost:
        print("            (%d, %d) : %d," % (left_cost, right_cost, actual_cost))
print("        }\n")


# find the median
data_median = {}
for (left_cost, right_cost) in sorted(data.keys()):
    list_actual_cost = data[(left_cost, right_cost)]
    data_median[(left_cost, right_cost)] = int(statistics.median(list_actual_cost))

print("        heuristic_stats_median = {")
for (left_cost, right_cost) in sorted(data.keys()):
    actual_cost = data_median[(left_cost, right_cost)]
    if actual_cost > left_cost and actual_cost > right_cost:
        print("            (%d, %d) : %d," % (left_cost, right_cost, actual_cost))
print("        }\n")

