# Architectural Legality Lives in CSV, Not generate.py


**Rule:** If (instruction, SEW) pair is architecturally reserved encoding (e.g. `NF × EMUL > 8` for seg load), blank its `EFFEW{N}` cell. If (instruction, coverpoint) pair unreachable at some SEWs because coverpoint mandates specific LMUL, use `sew_ge{N}` in that coverpoint's column instead of `x`.

**Do not** add instruction/coverpoint legality filters to `generators/coverage/src/covergroupgen/generate.py`. Keep generate.py free of architectural filter tables (no `_nf_emul_legal`, `_CP_MIN_LMUL`, etc.) — those belong in CSV data. Only SEW-aware logic in generate.py should be generic suffix handling (`sew_ge`, `sew_lte`, SEW_DEPENDENT_CPS).

`MAXINDEXEEW_GE{N}` `\`ifdef` guards (config-side hardware support) are a
different category and legitimately live in generate.py, because they vary
per-config rather than per-architecture.
