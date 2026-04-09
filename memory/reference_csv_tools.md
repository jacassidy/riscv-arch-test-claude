---
name: CSV and Isolation Tools
description: How to use csv_edit.py and isolate_coverpoint.py — now in riscv-arch-test-claude repo
type: reference
originSessionId: daedb7c8-f61c-41ac-ac2d-d0913dc324e1
---
## csv_edit.py ($WALLY/addins/riscv-arch-test-claude/tools/csv_edit.py)
Operates on `(main repo) testplans/` via $WALLY env var.

Key functions:
- `read_structure(csv_name)` — print headers + first column only (lightweight context)
- `set_cells(csv_name, [(row, col), ...], value="x")` — set specific cells
- `fill_column(csv_name, col_name, row_names=None, value="x")` — fill a whole column
- `fill_row(csv_name, row_name, col_names=None, value="x")` — fill a whole row
- `clear_cells(csv_name, [(row, col), ...])` — clear cells

CSV name auto-resolves (e.g. 'I', 'Vx' → `testplans/I.csv`). Always use `read_structure()` first. Do NOT read full CSVs with the Read tool — they can be very large.

## isolate_coverpoint.py ($WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py)
For isolated coverage testing of a single coverpoint:
- `python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py Vls cp_custom_maskLS`
- `python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py --restore Vls`

Canonical backups: `$WALLY/addins/riscv-arch-test-claude/working-testplans/duplicates/` (e.g. `Vls-save.csv`).
After isolation, set Makefile EXTENSIONS to relevant categories. After coverage, restore CSV before next isolation.
