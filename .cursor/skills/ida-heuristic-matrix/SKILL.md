---
name: ida-heuristic-matrix
description: Speeds a slow IDA phase by finding a minimal --multiplier, sampling 100 random cubes, and replacing the multiplier with a production cost matrix. Use when a phase is slow, IDA thresholds explode, the user mentions --multiplier, print-ida-summary, or heuristic matrix, or when editing utils/build-*-cost-matrix.py.
---

# IDA heuristic matrix

if a phase is slow, find a minimal --multiplier value that allows most cubes to solve in a few minutes, solve 100 random cubes to build a heuristic matrix and then use that matrix in production instead of --multiplie

`--multiplier` inflates cost-to-goal so IDA finishes, at the cost of longer solutions. A sampled matrix keeps most of that speed without leaving the multiplier in production.

## Workflow

1. **Confirm the bottleneck** is combined-heuristic IDA (max of several table costs is admissible but too weak), not a missing table or legal-move bug.
2. **Find the minimal multiplier.** Start near 1.2 and raise until most random cubes finish in a few minutes. Prefer the smallest F that rarely hits a several-minute timeout. Pass it only on the C command line while sampling (`--multiplier F`). Do not commit that F on the Python lookup object.
3. **Sample 100 random cubes** at that F with `--print-ida-summary`. Reuse or add a script under `rubiks-cube-NxNxN-solver/utils/build-*-cost-matrix.py` (see `build-777-daisy-cost-matrix.py`, `build-555-centers-stage-matrix.py`). Default `--count` is 100. Legal moves for the scramble must match the phase.
4. **Build the matrix** from summary rows: cell = max(admissible max of the axis costs, smallest remaining-move count seen for that tuple). Fill unsampled cells with `F * admissible` (or the script's monotonic fill). Never go below the admissible max.
5. **Install in production:** splice the C array into the searcher; C uses the matrix when `--multiplier` is omitted; Python `self.multiplier = None`. Re-running the sample against the new matrix can tighten it; do not leave `--multiplier` on the production `solve_via_c` path.

Do not start a 100-cube sample or rewrite a matrix unless the user asked to speed the phase or to rebuild the matrix.
