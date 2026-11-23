# 5x5 phase 1: search, table, and t/x interaction ideas

Brainstorm from Nov 23. The searcher is `ida_search_555_centers_stage`. Phase 1 stages all centers: the goal is one
canonical state in the recolored 8 F / 8 L / 8 U space, plus the wing parity bit. The current heuristic is
`max(t-cost, x-cost)` from two 9.47-billion-entry byte tables.

## Corrections to the earlier brainstorm message

1. I said all 48 cube symmetries keep the goal. Only 4 do without relabelling colours (identity, x2, y2, z2). If you
   allow the three colours to be relabelled, the 24 rotations each map the goal onto itself, which gives a reduction of
   about 24x. Reflections and the exact factor still need checking.
2. The "one colour across all 48 stickers" table only tracks which positions hold U. That is a two-class projection,
   weaker than the full state, so its size and the "3 queries per node" figures are unverified.
3. The 2-bit mod-3 compression claim was too strong. Knowing that neighbours differ by at most 1 does not by itself
   allow exact recovery of the distance. The scheme needs a careful check before use.
4. The "average depth is about 9 because of counting" argument was rough. It explains why the tables are near their
   ceiling, but it is not a proof.

## Summary

| Idea | Why it could help | Main risk | Cheapest first test |
| --- | --- | --- | --- |
| Meet-in-the-middle with a backward ball around the goal | Removes the last 6 to 7 plies of IDA*, where most nodes are | Ball memory; the ball has to be rebuilt and combined with the cost tables | Count the ball sizes at depth 6 and 7 |
| Transposition table inside IDA* | Merges the many move orders that reach the same center state | Memory and hash collisions | Measure the duplicate-state rate at threshold 14 |
| Move ordering by child `max(t, x)` | Reaches the solution sooner on the final threshold | None for correctness; small overhead per node | Reorder children and compare nodes on 100 cubes |
| Beam or weighted search | Much faster, no proof of optimality | Sometimes one move longer than optimal | Measure the extra moves on the 14-move set |
| Denser table with symmetry reduction | Each lookup covers more states, so the floor is deeper | Reduction factor and index cost unverified | Count canonical states under the 24 rotations |
| Move-compatibility bound on t and x | Proves one extra move in some states, at no table cost | May rarely trigger | Count how often t equals x with no double-progress move |

## 1. A better search than IDA*

IDA* has two clear weaknesses here, and both are fixable. Most of the work happens in the last few plies, and the same
center state is reached through many different move orders.

### Meet-in-the-middle

The goal is one canonical state, so a backward ball of radius k around it can be stored in a hash table. A forward
search of depth 16 - k then only needs to hit the ball. The existing t and x floors still prune the forward search, so
no correctness is lost. An earlier near-table builder (depth 6, keyed by the t and x ranks) was removed with the
learned-model experiment, so the ball would have to be rebuilt.

### Transposition table

A fixed-size table of (state hash, failed budget) turns the search tree into a graph. Commuting and slice moves produce
many duplicates, so this may cut nodes several times over. It does not change the answer.

### Move ordering

`search()` currently tries the 36 moves in a fixed order with no guidance. Trying children that lower both t and x
first should reach a solution sooner on the final threshold. It costs one table lookup per child.

### Give up exact optimality

If one extra move is acceptable for staging, beam search or weighted IDA* avoids the expensive proof that the threshold
has no solution. Most of the wall time for a 16-move cube is spent on that proof.

## 2. Tables that go deeper than t and x

A table with N entries can only tell apart about N states. The number of states within distance d grows roughly
exponentially with d, so the 9.5-billion-entry tables are near their ceiling around depth 9 to 10. To get deeper
floors, the table has to cover more states per byte, not just be bigger.

Routes to try, in order of promise:

- (a) Symmetry reduction, which can shrink a table by about 24x if the reduction is verified.
- (b) A cross-orbit table that tracks t and x together on one axis pair, with its size recalculated.
- (c) Compact storage such as 2-bit mod-3 values, once the exact recovery scheme is worked out.

## 3. How t and x interact

The two cost values alone say little about the interaction, and the 17 by 17 matrix gave little gain. The useful
information is in which moves each table wants.

Provable bound: if t equals x equals c at a state and no single move lowers both, every child has `max(t, x)` at least
c, so the distance is at least c + 1. This holds because each move changes a table value by at most 1. Outer turns
rotate the four t-centers and four x-centers of a face as a rigid pattern, so they never move a t-center into an
x-slot. Only wide turns can change the t-to-x alignment.

A first experiment is to count, on the recorded datasets, how often t equals x with no double-progress move and how
often that bound adds a move. The earlier datasets were deleted with the model experiment, so generate fresh random
scrambles for this.

## Results so far

### Transposition table inside IDA*: no gain, removed

Tried Nov 23. The table keyed each failed subtree by the exact t-rank, x-rank, wing parity and the previous move's
successor class (moves that allow the same next moves share a class), so a hash collision could not prune a live
branch. It stored "no solution within R more moves", pruned at remaining >= R, was lock-free (two words per entry, the
second XORed with the first), and was disabled for `--solution-count` other than 1. Solution lengths matched the
baseline on every cube.

On a 14-move-solution cube (100-move scramble, final threshold 14, 22 threads):

| Config | Nodes | Search time |
| --- | --- | --- |
| Baseline | 279.9M | 3.55 s |
| 4 GB table, min remaining 3 | 263.2M | 3.55 s |
| 4 GB table, min remaining 2 | 263.2M | 3.57 s |
| 4 GB table, min remaining 1 | 267.6M | 3.57 s |
| 16 GB table | 266.4M | 44 s (memory pressure) |

On a 15-move cube the table cut nodes from 7.07G to 6.33G (10%) and time from 96.3 s to 89.7 s (7%).

Why it does not help: only about 4.5% of nodes (11.8M of 263M) survive the t/x pruning and reach the table, and only
about 3% of those probes hit. Nearly all the work is the leaf frontier, which the table cannot skip, and the commuting
move filter already removes the common duplicate orderings. The earlier hypothesis that many move orders reach the same
center state was wrong for this search. Smaller or larger tables and lower minimum-remaining values did not change it.

### Move ordering by child `max(t, x)`: no gain, removed

Tried Nov 23. Ordering can only help the final IDA* iteration, because every earlier iteration must fail completely.
Two variants were tried:

- **Within a node:** score every child's heuristic first, drop the ones the heuristic prunes, and recurse cheapest
  first (the child cost is passed down, so nothing is evaluated twice). On the cubes with a final iteration of at least
  0.2 s it changed nodes by -7% to +26% depending on the cube, with no consistent direction.
- **Across the thread pool's root tasks:** sort the roughly 918 two-move prefixes by their heuristic cost so the
  threads start on the most promising ones. Races between 22 threads are too noisy to read: it solved cubes the
  baseline timed out on (and the reverse: 0.43 s became 4.9 s on one cube).

To separate luck from signal, the final iteration was enumerated completely (`--solution-count 0`) on 44 cubes, recording
each root task's cost, nodes and solution count. Replaying that under different task orders gives the expected fraction
of the iteration spent before the first solution:

| Root-task order | Mean fraction, 16 deep cubes (>=10M nodes) | Node-weighted, 44 cubes |
| --- | --- | --- |
| Random | 0.431 | 0.395 |
| Cost ascending (cheapest first) | 0.395 | 0.382 |
| Cost descending | 0.451 | 0.386 |

All three are within noise. Most cubes put every shortest solution under a single prefix out of about 918 (29 of 44
cubes had one solution prefix), and the depth-2 heuristic does not point at it. A random order finds the first solution
about 40% of the way through the final iteration, so the best realistic gain from any ordering is small, and the
heuristic gives no information to get it.

The instrumentation and flags were removed. Move ordering is not worth revisiting unless a different signal than
`max(t, x)` can predict which prefix holds the solution.

`utils/benchmark-555-centers-stage.py` compares flag sets on the same scrambles and is kept for the next experiments.
Use `--scramble-length 100` for deep cubes: 14 random moves give solutions of only 5 to 11 moves, which solve in
milliseconds.

### Meet-in-the-middle backward ball: correct, no gain, removed

Tried Nov 23. The ball held every `(t_state, x_state)` within K moves of the staged goal with its shortest distance for
each wide-quarter parity, built in memory at startup by a parallel breadth-first search (`--ball-depth K`, 16-byte
open-addressing entries). At a forward node with `remaining <= K` the ball replaced the table heuristic: a hit at the
exact remaining distance with the right parity was a solution, and a miss pruned.

Ball sizes (distinct states by distance from the goal, matching the old Python counts exactly): 1, 6, 147, 3,054, 65,520,
then about 1.47M at depth 5 (1.54M cumulative). Build time was 0.5 s at depth 5 and about 3 s at depth 6.

Correctness held: on 11 solved 19-move cubes (no parity flag) and 24 solved 15-move cubes (12 each with
`--orbit0-need-even-w` and `--orbit0-need-odd-w`), solution lengths were identical to the table-only search at ball
depths 4, 5 and 6, and every tail staged the centers with the right parity.

It did not pay. Node counts on the final iteration moved by only about -10% to +20% (depth 6 on the 98M-node cube: 87.8M
nodes; on the 1.33B-node cube: 1.30B at depth 4 and 6, 1.63B at depth 5, which is thread-race noise), and search time was
unchanged within noise. Including the build, wall time was worse everywhere except the hardest cubes, where it was a wash:

| Cube (19 moves, seed 23) | Base wall | Ball 4 wall | Ball 5 wall | Ball 6 wall |
| --- | --- | --- | --- | --- |
| 002 (150M nodes) | 2.58 s | 2.52 s | 2.68 s | 5.42 s |
| 013 (98M nodes) | 1.31 s | 1.34 s | 1.62 s | 4.46 s |
| 010 (1.3B nodes) | 18.50 s | 18.50 s | 23.61 s | 24.13 s |

Why it does not help: it is the same story as the transposition table. About 95% of the nodes are leaf-frontier nodes at
`remaining > K` that the `max(t, x)` heuristic prunes, so they are paid for before the ball is ever consulted. Below
that, `max(t, x)` appears to be close to exact within 6 moves of the goal, so replacing it with the true distance prunes
few extra nodes (inferred from the small node change, not measured directly). The ball would only help by pruning
earlier, which means a much larger K than memory allows; the depth-6 ball was not counted, but each level grows about
20x, so it is already on the order of 10^7 to 10^8 states.

The ball code, the `--ball-depth` flags and the focused tests were removed. This closes the "better search than IDA*"
branch of the ideas: transposition table, move ordering and backward ball all fail for the same reason, which is that
the cost is in the pruned frontier, not in the solved tail.

### Move-compatibility bound on t and x: already implicit in IDA*, no gain

Measured Nov 23 with temporary counters (since removed) on fresh 100-move scrambles, counting over complete failed
iterations. A node is *tight* when `max(t, x)` equals the remaining budget, so every move must lower it. A tight node is
*dead* when no child passes the heuristic, which is exactly the situation where the bound proves one more move.

| Cube, threshold | Nodes | Expanded | Tight | Dead (of tight) | Nodes that are children of dead tight nodes |
| --- | --- | --- | --- | --- | --- |
| 0, 13 | 27.7M | 1.12M | 95.8% of expanded | 71.9% | 68.0% |
| 1, 14 | 314.4M | 12.56M | 96.2% of expanded | 73.7% | 70.2% |
| 4, 14 | 402.5M | 16.24M | 96.0% of expanded | 72.8% | 69.1% |

Splitting the tight nodes: about 75% have `t == x == remaining`, and 82% of those are dead. Of those dead `t == x` nodes,
about one third have a table with no improving move at all, and the rest have improving moves in both tables but no move
that improves both at once. So the bound triggers almost always, and the "no double-progress move" case is the common one.

It still cannot save anything. Expanding a tight node and pruning every child with `bounded_heuristic` is the same
computation as testing the bound: each child is one rank plus one `t` read (and an `x` read only if `t` passes), which
is the same lookups the bound needs to find the improving moves. Counting it separately adds work, it does not remove
any. A saving would need the improving-move sets without the lookups, for example a per-state bitmask in the table,
which costs 36 bits instead of 8 and defeats the table size.

What the numbers do show is where the time goes: roughly 70% of all nodes are the immediate children of a dead tight
node, and each one is a random read into a 9.4 GB table. The search is memory-latency bound at the leaves. That points to
batching the child lookups with software prefetch (compute all child ranks, prefetch, then compare) instead of any new
bound. This is not measured yet.

### Joint LR t+x table (reusable for UD and FB): strong, recommend building

Measured Nov 23 without building the table. The table would store, for each pair (L/R mask over the 24 t positions,
L/R mask over the 24 x positions), the exact number of moves to stage LR. Because the move set is invariant under all 48
cube symmetries, the same table gives UD and FB staging after a fixed position permutation, so the heuristic becomes
`max(joint LR, joint UD, joint FB)`.

**Method.** The current searcher sampled uniformly from real node calls of complete failed iterations (12 fresh
100-move scrambles, none solved by threshold 14, so every sampled node truly cannot reach the goal in its remaining
budget and 100% pruning is the ceiling). A temporary tool then computed the exact joint distance of each node for each
axis by IDA with the existing 735,471-entry LR t-only and x-only tables (`step11` and `step12`) and all 36 moves. Because
the future table stores exact distances, this is what it would return. No query timed out (limit 4e9 nodes).

**Validity checks of the tool.** All 48 symmetries conjugate the 5x5 move set onto itself (t and x together), so the
sticker geometry matches the move tables. Distances were identical under all 16 LR-axis symmetries (2,400 checks, 0
mismatches). For 1,200 axis distances of states reached by 3 to 8 random moves from the staged state, none exceeded the
walk length, so the bound is admissible on all three axes.

**Pruning power (expanded nodes, 47,875 samples).** An expanded node is one that passes the current `max(t, x)` check;
each costs about 29 child evaluations.

| Subset | Pruned by joint LR | UD | FB | Any of the three |
| --- | --- | --- | --- | --- |
| All expanded nodes | 86.9% | 89.3% | 89.7% | 98.1% |
| Tight (h == remaining), 96% of nodes | 88.6% | 91.0% | 91.3% | 99.2% |
| remaining 8 (40% of nodes) | 96.0% | 97.8% | 97.7% | 100.0% |
| remaining 9 (47% of nodes) | 81.6% | 85.2% | 85.9% | 99.4% |
| remaining 10 | 27.6% | 28.1% | 30.8% | 62.7% |

The joint bound is consistent (a move changes it by at most 1, and the budget by exactly 1), so a pruned node's
descendants would also be pruned. The nodes that survive therefore form an ancestor-closed subtree, and the number of
expanded nodes falls by 1/(1-p), about 50x on this sample.

**Add versus replace (93,909 samples of every node call, thresholds 13 and 14).**

| Outcome | Share of calls |
| --- | --- |
| Pruned by both the current heuristic and the joint bound | 95.99% |
| Joint bound only | 3.92% |
| Current heuristic only | 0.01% |
| Neither (expanded) | 0.089% |

The joint bound almost dominates `max(t, x)`: the current heuristic prunes something the joint bound misses in only 0.01%
of calls, all at remaining 9. Expanded nodes would fall about 45x if the joint bound is added to the current tables and
about 42x if it replaces them (84 and 90 passing nodes in the sample, so each figure is good to roughly 10%).

**Distance distribution of random states (1,500 samples).** Joint LR distance is 8 (1.2%), 9 (11.3%), 10 (59.0%), 11
(28.3%), 12 (0.1%); nothing above 12. The maximum depth should therefore fit a 4-bit entry (depth plus one at most 15),
to be confirmed when the table is built.

**Size.** Group of 16 (rotations and mirrors that keep the LR axis).

| Quantity | Value |
| --- | --- |
| Raw universe, 735,471^2 | 540,917,591,841 |
| t-classes under the 16 symmetries | 46,935 (orbit sizes 1:3, 2:10, 4:122, 8:1,730, 16:45,070) |
| True (t, x) pair orbits (Burnside) | 33,807,856,581 |
| Two-coordinate table, t-class x 735,471 | 34,519,331,385 entries (2.1% above the true orbit count) |
| At 1 byte per entry (build form) | 34.5 GB |
| At 4 bits per entry (solver form) | 17.3 GB |
| Existing t table plus x table | 18.9 GB |

The two-coordinate index (canonicalize the t mask to its class and transform the x mask by the same symmetry) needs only
a few MB of helper tables, so one lookup is one random read. Alternatives that store only the true orbits need a rank to
index map and were not considered worth the 2%.

**Memory picture.** Replacing the two existing tables with the joint table shrinks phase-1 memory from 18.9 GB to 17.3
GB and still predicts a large win, because each node call would cost up to three lookups instead of about one but there
would be about 42x fewer expanded nodes to pay for. Adding it needs about 36 GB.

**Caveats.** Wing parity (orbit-0 OLL) is ignored, so the bound is a relaxation that never exceeds the true distance. The
50x figure counts expanded nodes; wall time also depends on per-lookup cost (random reads into a 17 GB table, three axes)
and will be measured once a table exists. Samples come from random 100-move scrambles, where the search runs to
thresholds 13 and 14.

**What to do next (needs approval to build).** A dedicated C builder in the lookup-tables repo: two-coordinate index,
level-synchronous parallel BFS over a 1-byte array on the 128 GB machine (about 1e12 transitions, unmeasured), a shallow
partial build validated against the exact IDA distances first, then packing to 4 bits. Then `--lr-joint-cost` in the
searcher with the three-axis lookup only for nodes that pass the existing check (add) or for every call (replace).

### Joint LR table builder (shallow validation done)

`rubikscubelookuptables/build-555-lr-joint.c` (lookup-tables repo) builds the table with a level-synchronous BFS over
one byte per cell; `rubikscubennnsolver/lr_joint_555.h` (solver repo) holds the geometry and cell indexing that the
builder and the searcher share. `make 555-lr-joint` in the lookup-tables repo builds the full table (needs about 36 GB
of RAM; not part of `make 555` or `make 555-tables`).

Validated locally with `--max-depth 6` (1,154,900 cells; depth counts 1, 1, 9, 158, 2,968, 57,335, 1,094,428):

- 100,000 random-walk states: the table equals the exact IDA distance (computed from the separate step11/step12
  tables) for every state at distance 0 to 6 and reads 0 for every state farther than 6, with 0 mismatches.
- `--verify` (goal reads 1, every neighbour differs by at most 1, a lower neighbour exists, all 16 LR-axis images
  agree) reports 0 failures on 149,159 states, including classes with a nontrivial stabilizer.

A depth-7 or deeper build touches nearly every page of the 34.5 GB array, so it cannot run on the 31 GB machine. The
full build time is still unmeasured.

### Joint LR table in the searcher (flag only)

`ida_search_555_centers_stage --lr-joint-cost FILE` reads the joint table for the L, U, and F axes. Each axis's FLU masks
are mapped onto the LR goal by a symmetry found at startup, and the cell comes from the shared header. An unseen cell
gives a bound of 0, so partial tables stay admissible. `--print-ranks` prints `JOINT_<axis> CELL <cell> VALUE <nibble>`.

Two modes:

- **Add:** pass the step10 `--t-center-cost` and `--x-center-cost` tables too. The joint table is read only after
  `max(t, x)` passes the budget. All three files total about 36 GB.
- **Joint only:** omit both t/x flags (they must be given together or not at all). The bound is the joint table alone,
  17 GB resident.

Lookup cost: the C(24,8) rank is two table reads split at bit 12, the three axis cells are prefetched together, the
mapping is `MADV_RANDOM`, and the file is preloaded with `MAP_POPULATE` when it is fully allocated (sparse test files are
not). The searcher skips the builder's 47 MB `x_sym_rank` table, so startup is about 0.14 s instead of 1.3 s.

Checks (solver `tests/test_ida_search_555_lr_joint.py`, 8 tests, all pass; the 28 ranked-phase tests still pass):

- An empty joint file keeps the optimal solution unchanged on a real 4-move scramble.
- A solved cube reads value 1 on all three axes, and walks of 1 to 3 moves read between 1 and k+1 on each axis, using a
  depth-3 table from `build-555-lr-joint`. This ties the searcher's axis mapping and cell indexing to the builder.
- Joint-only mode solves the solved cube at cost 0 and finds the t/x solution length on 3-move walks.
- An injected root value shows up in `--print-ranks` and raises the printed cost; a value above the threshold prunes.
- A file of the wrong size, or a t table without its x table, is rejected.

Benchmark on the 31 GB laptop: `utils/benchmark-555-centers-stage.py --count 10 --scramble-length 100 --seed 1
--timeout 600`, 22 threads, search seconds (`-` is a 600 s timeout). Joint only is `--no-t-x-tables --lr-joint-cost FILE`.

| Cube | Length | Base | Add | Joint only |
| --- | --- | --- | --- | --- |
| 000 | 16 | 545.7 | 380.2 | 27.8 |
| 001 | 14 | 5.7 | 4.1 | 0.4 |
| 002 | 15 | 102.3 | 37.4 | 4.4 |
| 003 | 16 | 286.1 | 303.5 | 21.4 |
| 004 | 16 | - | 500.6 | 39.5 |
| 005 | 16 | - | - | 34.7 |
| 006 | 14 | 4.5 | 5.3 | 0.2 |
| 007 | 16 | 253.7 | 228.8 | 12.0 |
| 008 | 15 | 99.7 | 76.8 | 5.4 |
| 009 | 16 | - | 556.6 | 25.4 |

- Every length matches across modes. Joint only solves all 10, base 7, add 9.
- Joint only is about 18x faster than base (geomean over the 7 cubes base solves) and totals 171 s against base's
  3,098 s. Its node counts are within about 10% of add mode, so the t/x tables add almost no pruning on top of the
  joint table.
- Node rate is about 22 million per second against base's 75 million, but joint only expands 30 to 70 times fewer nodes.
- Add mode gains little here because the 36 GB of tables do not fit in 31 GB. A 14-move cube took 1,358,769 major
  page faults (one per 4 KB joint page read from disk) against 1 for base. Joint only keeps 17 GB resident, less than
  base's 18.5 GB.

### Cross-axis joint table (x-centers on one axis, t-centers on another): measured, about 2x, not built

Idea: a second table over (x L/R mask, t U/D mask), 735,471^2 raw cells like the LR/LR table, usable for all six ordered
axis pairs. Its symmetry group is only the 8 sign flips (both axes must stay fixed), so it holds about 67.6 billion cells,
34 GB packed, and a byte-per-cell build would need 68 GB of RAM.

Measured Nov 24 without building it. 7,285 expanded nodes were sampled uniformly from complete joint-only searches of the
10 benchmark scrambles (every node passed the three same-axis joint lookups, thresholds 13 to 16). For each node and each
of the 9 axis pairs, a temporary tool found the exact projection distance by IDA with the step11/step12 tables, which is
what the table would store. Checks: the 3 same-axis distances equal the joint table on all 21,855 lookups, no same-axis
lookup prunes a sampled node, no query timed out, and 300 random walks never exceeded their length on any of the 9 pairs.

Because the new bounds are exact and consistent, expanded nodes fall by 1/(1-p), where p is the share of currently
expanded nodes a new bound prunes.

| Cross lookups added to the three same-axis lookups | Pruned | Expanded-node reduction |
| --- | --- | --- |
| Best single pair (x on L, t on F) | 20.8% | 1.26x |
| Best two | 30.7% | 1.44x |
| Best three | 37.7% | 1.60x |
| All six | 49.7% | 1.99x (95% interval 1.95x to 2.04x) |

By remaining moves, all six prune 100% of nodes at 8 and 98% at 9, but only 46% of the 5,500 nodes at remaining 10, and
none at 11 or more. The tight nodes at remaining 10 dominate the tree, and the cross bound is no better than the
same-axis maximum for 48% of the sampled nodes.

Cost: the cross reads can wait until a node passes the three same-axis lookups, which is about 4% of calls, so they add
roughly 5 to 10% to the time per call. The net speedup is therefore about 1.9x for a 34 GB table (51 GB resident with the
17 GB table) and a builder that needs a nibble or 2-bit frontier. The same-axis joint table gave about 18x, so this is a
much weaker return.

Tools (not in the repo): the sampler is a copy of the searcher with a node dump, and the measurement is a tool that
extends the same-axis distance code to all 9 axis pairs.

### Parity-aware joint table: built, verified, 1.87x fewer nodes and 1.44x faster search time

The color projection discards orbit-0 OLL parity, and every real phase-1 search passes `--orbit0-need-even-w` or
`--orbit0-need-odd-w`. The searcher enforces parity only on the last ply (and as a floor of 1 at cost 0), so a node
whose shortest staging paths all have the wrong parity is expanded until the final move rejects it. Joint-only on the
10 benchmark scrambles (22 threads, search seconds, total nodes):

| Parity | Nodes | Search | Cubes whose length grew by 1 |
| --- | --- | --- | --- |
| none | 3.90e9 | 106.5 s | - |
| even | 5.31e9 | 141.9 s | 3 of 10 |
| odd | 14.2e9 | 375.6 s | 2 of 10 |

Odd costs 2.5x the nodes of no parity (cube 000: 32 s without parity, 146 s with odd, because 16 is not reachable with odd
parity).

Measured Nov 24 without building anything: 4,871 (even) and 5,545 (odd) expanded nodes sampled from the constrained joint-only
searches. For each node the exact same-axis projection distance was found with the parity of the remaining path fixed
(the table would store this). Checks: 300 random walks, constrained distance never below the plain distance and never
above the walk length, and parity raised the distance in 221 of 2,700 cases.

| Added bound | Even | Odd |
| --- | --- | --- |
| Parity-aware same-axis lookups (3) | 1.84x fewer expanded nodes | 1.84x |
| Parity-aware cross lookups only (6) | 3.26x | 3.28x |
| Parity-aware same-axis plus cross (9) | 4.22x | 4.39x |

The same-axis gain is 44.6% of nodes at remaining 10, 72% at remaining 9, and 1% at 11. Storing only two flag bits per
cell (which parities are reachable at the plain distance d, bound d + 1 otherwise) prunes exactly as much as storing the
exact parity distance on these samples, so a cell needs 4 bits of distance plus 2 flag bits.

A same-axis parity table is 34.5 billion cells at 6 bits (26 GB packed), one read per lookup, so the per-call cost is
unchanged.

Implemented and built Nov 24:

- File: `lookup-table-5x5x5-step13-LR-t-x-centers-joint.sym-parity6.bin`, 25,889,498,540 bytes. Cell `i` is 6 bits at bit
  `6i` (little endian): bits 0-3 are the plain depth + 1 (0 unseen), bit 4 is set when an even path reaches the goal in
  that depth, bit 5 when an odd path does. One pad byte keeps the 16-bit load at the last cell inside the file.
- Parity means the number of wide quarter turns mod 2, defined once in `lr_joint_555.h` (`lrj_move_parity`) and used by
  the searcher and the builder. `lrj_init` now fails if any of the 48 symmetries maps a move to one with different parity.
- Builder: `build-555-lr-joint --parity` (`make 555-lr-joint-parity`) runs the breadth-first search over two byte layers,
  node `(cell, parity)`, about 69 GB. A move flips the layer when it is a wide quarter turn. The plain depth is the
  smaller of the two node depths, and a parity is flagged when its node depth equals it.
- Searcher: `--lr-joint-parity-cost FILE`. With the parity the rest of the path needs (`required ^ parity played`), an
  axis lookup returns `d`, or `d + 1` when that parity is not flagged. With no `--orbit0-need-*` flag it is the plain `d`.
  `RubiksCube555` prefers this file over `.sym-nibble.bin` when present (both remain supported so machines with under
  69 GB can still build `.sym-nibble.bin`).
- Startup mapping fix (`ida_map_cost_file_random` in `ida_search_core.c`): `MAP_POPULATE` across 25.9 GB (~6.3M 4 KB
  pages) added ~0.55–1.6 s of page-table setup per process even on trivial cubes. Skipping `MAP_POPULATE` and advising
  `MADV_RANDOM` drops short-cube startup from 0.67 s to 0.12 s with no penalty on deep cubes once the OS page cache is
  warm. Pages that are not cached are read sequentially first (see the page cache notes below).
- Benchmark on the 128 GB machine (`utils/benchmark-555-centers-stage.py --count 10 --scramble-length 60`, odd and even):
  - Optimal solution lengths matched 20/20.
  - On the fully warm-cache `even` pass (10 deep cubes, lengths 15–16), `parity` won **10/10** cubes: total nodes fell
    from `8,135,228,726` to `4,349,740,291` (**0.535x / 1.87x fewer nodes**, matching the 1.84x sample prediction) and
    search time fell from `277.6 s` to `193.0 s` (**0.70x / 1.44x faster**).
  - On the hardest cube (`odd` `cube=004`, length 17), nodes fell from `2.93B` to `1.49B` (**1.96x fewer**) and search
    time fell from `107.2 s` to `58.8 s` (**48.4 s saved**).

### Node rate with the parity table: mask state, page cache

Profiled Nov 25 on the 58 GB laptop (Core Ultra 7 165H, 22 threads, WSL2) with the 16-move test cube at threshold 15
(93.8M nodes). `perf` is not available in this WSL kernel, so a microbenchmark of the lookup path on random states split
the per-node cost (single thread, warm cache): about 60 ns to build the FLU masks from the 24-byte t and x arrays (each
step of that loop reads and writes the same mask), about 35 ns for the three cell indexes, and about 80 ns for the three
prefetched table reads.

- The search state is now one 24-bit mask per symbol per orbit (`struct centers`). A move is three reads per mask from
  `lr_joint_555.h`'s per-move chunk tables, which removes both the byte permutation and the mask build. Same solution
  and node counts; five alternating 22-thread runs at threshold 15 went from 4.34 s to 3.88 s mean search time (95.3 s
  to 85.4 s CPU). With 22 threads the DRAM reads dominate, so the gain is smaller than single-thread numbers suggest.
- Cold or evicted page cache is the larger effect. On a 58 GB machine the parity table, nibble table, step10 tables and
  goal ball (about 70 GB) do not fit together; a run that faults the parity table from disk drops to about 7M nodes per
  second (13.2 s at threshold 15) against 23-28M warm.
- How the table enters the page cache matters. Random faults (`MADV_RANDOM`) cache it in 4 KB pages: 397,000 minor
  faults and 3.45 s of system time per run. Dropped and re-read sequentially (`cat FILE > /dev/null`), the kernel uses
  large folios and maps most of the file with 2 MB entries: 15,000 faults, 0.24 s system time, threshold 15 in 3.25 s
  instead of 3.66 s. `MADV_HUGEPAGE` made no further difference.
- Lazy mapping made the cold case worse: with no `MAP_POPULATE`, a cold start faulted all 25.9 GB as random 4 KB disk
  reads, and the 16-move cube took about 77 s. `ida_map_cost_file_random` now checks each 8 MB chunk with `mincore`
  and `pread`s only the runs of pages that are not cached, then advises `MADV_RANDOM`. On the 16-move cube a fully cold
  start reads 25.7 GB in 8.4 s and solves in 17 s total; a warm start reads nothing and solves in 6-7 s, at 37-51M
  nodes per second.
- Batching the three reads of 8 states before using any of them gained only 5-10% in the microbenchmark and was not
  tried in the searcher.

### 48-symmetry depth-8 goal ball (`--goal-ball`): correct, caps depth at `T - 8`, no wall-time gain

Implemented Nov 24 (`rubikscubennnsolver/goal_ball_555.h`, `rubikscubelookuptables/build-555-goal-ball.c`, `make
555-goal-ball-8` / `555-goal-ball-8-verify`). Relabelling FLU per symmetry makes all 48 cube symmetries fix the staged
goal and preserve wide-quarter parity, shrinking the depth-8 ball from ~18B raw states to **384,047,640** canonical
orbits (per-ply counts: `1, 1, 5, 75, 1402, 30733, 695587, 15932130, 367387706`). Stored in \(2^{30}\) 8-byte open-addressed
slots (8.59 GB, 35.8% load, longest probe 35; build took 27.5 s on 22 threads; 2M random/walk states verified with 0
failures).

At threshold `T`, forward IDA stops at `H = max(T - ball_depth, 0)` (hard exit if `depth > H`) and `ball_finish` probes
the canonical key, checks the exact distance for the needed parity, and greedily reconstructs the tail inside the ball.

On the 16-move test cube (`--lr-joint-cost ... --orbit0-need-even-w`):

| Setup | Max depth at `T = 16` | Nodes at `T = 16` | Search time at `T = 16` |
| --- | --- | --- | --- |
| Joint table only | 16 | 301.5M | 7.7 s |
| + depth-6 ball | 10 | 303.3M | 6.4 s |
| + depth-8 ball | 8 | 302.5M / 290.5M | 8.4 s / 8.5 s |

Why there is no speedup: ~89% of expanded nodes sit at `remaining = 10` (~76%) and `remaining = 9` (~13%), before the
depth-8 horizon is reached, and the joint table was already nearly exact below `remaining = 8`. Replacing three axis
prefetches at `remaining = 8` with 48-symmetry canonicalization + hash probe costs slightly more per leaf than it saves.
Kept as an optional CLI flag (`--goal-ball`) with builder and searcher unit tests; not wired into `RubiksCube555.py`.

A depth-9 cache-line Bloom filter (~8.4B states, ~8–12 GB at 1–5% FPR, no deduplication needed during build) could
prune `remaining = 9` parents before expansion, but since `remaining <= 8` is only ~10% of total nodes it would save at
most ~10% — not worth building unless deeper tables first shrink the `remaining = 10` frontier.

## Suggested order

1. ~~Transposition table~~ (tried, no gain; see Results).
2. ~~Backward ball~~ (tried raw to depth 6 and 48-sym to depth 8; caps depth cleanly, no wall-time gain; `--goal-ball` kept as optional CLI).
3. ~~Move ordering~~ (tried, no gain; see Results).
4. ~~Move-compatibility bound~~ (redundant with the child expansion; see Results).
5. Joint LR t+x table with UD and FB lookups: built; joint-only nibble is ~18x faster than the step10 t/x tables, and
   the 6-bit parity-aware table (`.sym-parity6.bin`) cuts another 1.87x nodes / 1.44x search time on top. `RubiksCube555`
   prefers `.sym-parity6.bin`, then `.sym-nibble.bin`, then step10 t/x.
6. Prefetch the child table reads at tight nodes (unmeasured; likely still worthwhile).
