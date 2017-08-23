#!/usr/bin/env python3

from pprint import pprint
import statistics

data = {}

with open('lookup-table-4x4x4-step10-ULFRBD-centers-stage.txt.stats', 'r') as fh:
    for line in fh:
        (state, UD_cost, LR_cost, FB_cost, actual_cost) = line.strip().split(',')
        UD_cost = int(UD_cost)
        LR_cost = int(LR_cost)
        FB_cost = int(FB_cost)
        actual_cost = int(actual_cost)

        if actual_cost < UD_cost:
            print("ERROR: actual_cost %d < UD_cost %d" % (actual_cost, UD_cost))

        if actual_cost < LR_cost:
            print("ERROR: actual_cost %d < LR_cost %d" % (actual_cost, LR_cost))

        if actual_cost < FB_cost:
            print("ERROR: actual_cost %d < FB_cost %d" % (actual_cost, FB_cost))

        if (UD_cost, LR_cost, FB_cost) not in data:
            data[(UD_cost, LR_cost, FB_cost)] = []

        data[(UD_cost, LR_cost, FB_cost)].append(actual_cost)

# find the min
data_min = {}
for (UD_cost, LR_cost, FB_cost) in sorted(data.keys()):
    list_actual_cost = sorted(data[(UD_cost, LR_cost, FB_cost)])
    data_min[(UD_cost, LR_cost, FB_cost)] = list_actual_cost[0]

print("        heuristic_stats_min = {")
for (UD_cost, LR_cost, FB_cost) in sorted(data.keys()):
    actual_cost = data_min[(UD_cost, LR_cost, FB_cost)]
    if actual_cost > UD_cost and actual_cost > LR_cost and actual_cost > FB_cost:
        print("            (%d, %d, %d) : %d," % (UD_cost, LR_cost, FB_cost, actual_cost))
print("        }\n")

# find the median
data_median = {}
for (UD_cost, LR_cost, FB_cost) in sorted(data.keys()):
    list_actual_cost = data[(UD_cost, LR_cost, FB_cost)]
    data_median[(UD_cost, LR_cost, FB_cost)] = statistics.median(list_actual_cost)

print("        heuristic_stats_median = {")
for (UD_cost, LR_cost, FB_cost) in sorted(data.keys()):
    actual_cost = data_median[(UD_cost, LR_cost, FB_cost)]
    if actual_cost > UD_cost and actual_cost > LR_cost and actual_cost > FB_cost:
        print("            (%d, %d, %d) : %d," % (UD_cost, LR_cost, FB_cost, actual_cost))
print("        }\n")
