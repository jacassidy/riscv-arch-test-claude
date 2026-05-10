# Architectural Legality Belongs in the CSV


If template needs specific LMUL (e.g. cross bins use `vtype_lmul_2`),
do NOT add Python-side filter in `generate.py` that drops coverpoint
when `NF × EMUL > 8`. Instead, in CSV, mark cell as `sew_ge{N}`
(smallest SEW where instruction legal at template's required
LMUL). See `guides/csv-editing.md` → "Cell Value Semantics".

Reserved-encoding instructions (e.g. `vlseg8e64.v` at SEW=8) should have
`EFFEW{N}` cell blanked in CSV — instruction filtered out
by existing EFFEW mechanism, no extra code needed.
