# 4. Audit flag semantics


* `EMPTY` — rule no `cp_name_*` filled.
* `PLACEHOLDER` — only `implicit` / `untestable` / similar markers. Often correct for impl-defined / S-mode / hardware-MAY rules.
* `GENERIC_ONLY` — only `cp_asm_count`. OK for extension-dependency / RVWMO / program-order rules. Suspect for rules describing concrete behavior.
* `SUSPECT` — heuristic flagged possible subject mismatch (e.g. rule mention `vstart` but no coverpoint name contain `vstart`). Many false positives — e.g. `cp_vcsrrswc` and `cp_sew_lmul_vsetvl` test specific CSRs but no CSR token in name. Always read spec quote and coverpoint definition before "fix".
* `OK` — pass heuristics. No guarantee.
