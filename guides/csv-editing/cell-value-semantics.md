# Cell Value Semantics


Most cells `x` (coverpoint applies) or empty (does not). Two special markers for per-SEW gating:

| Value       | Meaning                                                       |
| ----------- | ------------------------------------------------------------- |
| `x`         | Coverpoint applies for every SEW listed in EFFEW* columns     |
| `sew_ge{N}` | Applies only when arch SEW ≥ N (e.g. `sew_ge16`, `sew_ge32`)  |
| `sew_lte_{N}` | Applies only when arch SEW ≤ N (suffix form, see generate.py)|

Use `sew_ge{N}` when coverpoint architecturally unreachable at low SEWs for that instruction — e.g., coverpoint requiring LMUL=2 applied to seg load where `NF × EMUL > 8` at SEW=8.
