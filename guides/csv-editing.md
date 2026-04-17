# csv-editing.md — CSV Testplan Editing Guide

> **This file lives in `riscv-arch-test-claude`.** All new Claude-generated files belong here, not in the main repo.

## File Locations

| What                  | Where                                                          |
| --------------------- | -------------------------------------------------------------- |
| Canonical CSV source  | `working-testplans/*.csv` (this repo)                          |
| Live CSVs (framework) | `(main repo) testplans/*.csv` — **NEVER edit directly**        |
| CSV editor script     | `tools/csv_edit.py` (this repo)                                |

## csv_edit.py API

CSV name auto-resolves (e.g., `'Vf'`, `'Vls'`) to `(main repo) testplans/`. Note: VfCustom is now merged into Vf (like VxCustom is part of Vx).

| Function         | Usage                                                        | Description                                  |
| ---------------- | ------------------------------------------------------------ | -------------------------------------------- |
| `read_structure` | `read_structure(csv_name)`                                   | Headers + first column (lightweight context) |
| `set_cells`      | `set_cells(csv_name, [(row, col), ...], value="x")`          | Set specific cells                           |
| `fill_column`    | `fill_column(csv_name, col_name, row_names=None, value="x")` | Fill a column                                |
| `fill_row`       | `fill_row(csv_name, row_name, col_names=None, value="x")`    | Fill a row                                   |
| `clear_cells`    | `clear_cells(csv_name, [(row, col), ...])`                   | Clear cells                                  |

Always call `read_structure()` first. Do NOT read full CSVs with the Read tool — they can be very large.

## Stateless Processing

CSV editor agents are launched fresh per row with NO conversation history. All knowledge must come from .md files. If you learn something new, add it to the appropriate guide before finishing.

## Cell Value Semantics

Most cells are `x` (coverpoint applies) or empty (does not). Two special markers exist for per-SEW gating:

| Value       | Meaning                                                       |
| ----------- | ------------------------------------------------------------- |
| `x`         | Coverpoint applies for every SEW listed in EFFEW* columns     |
| `sew_ge{N}` | Applies only when arch SEW ≥ N (e.g. `sew_ge16`, `sew_ge32`)  |
| `sew_lte_{N}` | Applies only when arch SEW ≤ N (suffix form, see generate.py)|

Use `sew_ge{N}` when a coverpoint is architecturally unreachable at low SEWs
for that instruction — for example, a coverpoint requiring LMUL=2 applied to
a seg load where `NF × EMUL > 8` at SEW=8.

## Architectural Legality Lives in the CSV, Not generate.py

**Rule:** If an (instruction, SEW) pair is an architecturally reserved
encoding (e.g. `NF × EMUL > 8` for a seg load), blank its `EFFEW{N}` cell.
If an (instruction, coverpoint) pair is unreachable at some SEWs because the
coverpoint mandates a specific LMUL, use `sew_ge{N}` in that coverpoint's
column instead of `x`.

**Do not** add instruction/coverpoint legality filters to
`generators/coverage/src/covergroupgen/generate.py`. Keep generate.py free of
architectural filter tables (no `_nf_emul_legal`, `_CP_MIN_LMUL`, etc.) —
those belong in the CSV data. The only SEW-aware logic in generate.py should
be generic suffix handling (`sew_ge`, `sew_lte`, SEW_DEPENDENT_CPS).

`MAXINDEXEEW_GE{N}` `\`ifdef` guards (config-side hardware support) are a
different category and legitimately live in generate.py, because they vary
per-config rather than per-architecture.

## Knowledge Persistence

| Discovery Type                   | Add To                                                |
| -------------------------------- | ----------------------------------------------------- |
| New encoding / bit field value   | `guides/vector-reference.md`                          |
| New script pitfall or API detail | `guides/custom-scripts/GUIDE.md`                      |
| New workflow step or tool        | `guides/custom-scripts/CLAUDE-coverage-workflow.md`   |
| Custom coverpoint outcome/bug    | `scripts/claude-scripts/knowledge.md`                 |
