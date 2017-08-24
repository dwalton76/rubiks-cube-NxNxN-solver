#!/usr/bin/env python3

from pprint import pprint
import statistics

data = {}

with open('lookup-table-4x4x4-step70-phase3-tsai.txt.stats', 'r') as fh:
    for line in fh:
        (state, edges_cost, centers_cost, actual_cost) = line.strip().split(',')
        edges_cost = int(edges_cost)
        centers_cost = int(centers_cost)
        actual_cost = int(actual_cost)

        if actual_cost < edges_cost:
            print("ERROR: actual_cost %d < edges_cost %d" % (actual_cost, edges_cost))

        if actual_cost < centers_cost:
            print("ERROR: actual_cost %d < centers_cost %d" % (actual_cost, centers_cost))

        if (edges_cost, centers_cost) not in data:
            data[(edges_cost, centers_cost)] = []

        data[(edges_cost, centers_cost)].append(actual_cost)


# find the min
data_min = {}
for (edges_cost, centers_cost) in sorted(data.keys()):
    list_actual_cost = sorted(data[(edges_cost, centers_cost)])
    data_min[(edges_cost, centers_cost)] = list_actual_cost[0]

print("        heuristic_stats_min = {")
for (edges_cost, centers_cost) in sorted(data.keys()):
    actual_cost = data_min[(edges_cost, centers_cost)]
    if actual_cost > edges_cost and actual_cost > centers_cost:
        print("            (%d, %d) : %d," % (edges_cost, centers_cost, actual_cost))
print("        }\n")


# find the median
data_median = {}
for (edges_cost, centers_cost) in sorted(data.keys()):
    list_actual_cost = data[(edges_cost, centers_cost)]
    data_median[(edges_cost, centers_cost)] = int(statistics.median(list_actual_cost))

print("        heuristic_stats_median = {")
for (edges_cost, centers_cost) in sorted(data.keys()):
    actual_cost = data_median[(edges_cost, centers_cost)]
    if actual_cost > edges_cost and actual_cost > centers_cost:
        print("            (%d, %d) : %d," % (edges_cost, centers_cost, actual_cost))
print("        }\n")
