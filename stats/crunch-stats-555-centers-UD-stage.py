#!/usr/bin/env python3

from pprint import pprint
import statistics

data = {}

with open('lookup-table-5x5x5-step10-UD-centers-stage.txt.stats', 'r') as fh:
    for line in fh:
        (state, t_cost, x_cost, actual_cost) = line.strip().split(',')
        t_cost = int(t_cost)
        x_cost = int(x_cost)
        actual_cost = int(actual_cost)

        if actual_cost < t_cost:
            print("ERROR: actual_cost %d < t_cost %d" % (actual_cost, t_cost))

        if actual_cost < x_cost:
            print("ERROR: actual_cost %d < x_cost %d" % (actual_cost, x_cost))

        if (t_cost, x_cost) not in data:
            data[(t_cost, x_cost)] = []

        data[(t_cost, x_cost)].append(actual_cost)


# find the min
data_min = {}
for (t_cost, x_cost) in sorted(data.keys()):
    list_actual_cost = sorted(data[(t_cost, x_cost)])
    data_min[(t_cost, x_cost)] = list_actual_cost[0]

print("        heuristic_stats_min = {")
for (t_cost, x_cost) in sorted(data.keys()):
    actual_cost = data_min[(t_cost, x_cost)]
    if actual_cost > x_cost and actual_cost > t_cost:
        print("            (%d, %d) : %d," % (t_cost, x_cost, actual_cost))
print("        }\n")


# find the median
data_median = {}
for (t_cost, x_cost) in sorted(data.keys()):
    list_actual_cost = data[(t_cost, x_cost)]
    data_median[(t_cost, x_cost)] = statistics.median(list_actual_cost)

print("        heuristic_stats_median = {")
for (t_cost, x_cost) in sorted(data.keys()):
    actual_cost = data_median[(t_cost, x_cost)]
    if actual_cost > x_cost and actual_cost > t_cost:
        print("            (%d, %d) : %d," % (t_cost, x_cost, actual_cost))
print("        }\n")
