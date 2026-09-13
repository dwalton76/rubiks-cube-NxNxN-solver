---
name: unused-lookup-tables
description: Removes lookup-table builders, files, Makefile targets, and solver loaders that the solver no longer uses. Use when deleting a phase, replacing a table, reviewing dead LookupTable classes, or when the user mentions unused tables, leftover builders, or table cleanup.
---

# Unused lookup tables

never keep unused lookup table code. If the table isn't used in the solver, it should not exist in either repo

## What "used in the solver" means

A table is used if production solve code downloads or mmaps it (`download_file_if_needed`, `--*-cost FILE`, `LookupTable`/`LookupTableIDAViaGraph` filename, perfect-hash flags). Tests that only exist to exercise a dead table do not count.

**Exception:** a file that is only an input to building a solver-facing artifact (for example a combo `.txt` fed to `build-perfect-hash.py`) may live in **lookup-tables** as a build intermediate. It must not be loaded by the solver, and it must have a Makefile comment that names the solver file it produces.

## When a table stops being used

Delete it from **both** repos in the same change set:

1. Solver: Python class, `lt_*` assignment, filename constants, C flags, mmap, tests, comments, `AGENTS.md`.
2. Lookup-tables: builder class, `Makefile` target, `builderui.py` references, `tests/builder_table_baselines.json`, histogram lines, `lookup-tables/<file>` and sidecars (`.json`, `.gz`).
3. Grep both trees for the basename and builder class name before finishing.

Do not leave a "legacy" `LookupTable*` class, an unused `C_ida_type`, or a Makefile recipe that nobody runs. Do not start a replacement table build unless the user asks.
