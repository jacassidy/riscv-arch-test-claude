## Path A — CSV testplan + cp_*.py (instruction × coverpoint matrix)


Use when *table* of instructions, each crossed with set of coverpoints (e.g. exception-style coverage of every vector load/store). Driver auto-iterates instructions × coverpoints.

- Testplan CSV: `(main repo) testplans/priv/<Ext>.csv`
- Coverpoint handlers: `(main repo) generators/testgen/scripts/priv/cp_*.py` decorated with `@register("cp_xxx")` from `priv_coverpoint_registry.py`
- Driver: `(main repo) generators/testgen/scripts/vector-testgen-priv.py`
- Output: `tests/priv/<Ext>/<Ext>_rv{32,64}.S`
- Examples: `ExceptionsVls`, `ExceptionsVx` (CSVs in `testplans/priv/`).
