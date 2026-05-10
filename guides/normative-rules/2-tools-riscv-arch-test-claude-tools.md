# 2. Tools (`riscv-arch-test-claude/tools/`)


| Tool | Purpose |
|---|---|
| `fill_vx_coverpoints.py` | Read CSV, replace `coverpoint: [...]` arrays in `Vx.yaml`. **Run `make covergroupgen` first.** Resolves each CSV coverpoint against generated `*_coverage.svh` under `coverpoints/{priv,unpriv}/` and rewrites as `<covergroup>/<coverpoint>` (e.g. `ExceptionsHV_cg/cp_mstatus_vs_off`). Looser match: exact name, then prefix (CSV `cr_vl_lmul` → svh `cr_vl_lmul_sew32`). Textual placeholders (`implicit`, `untestable`, `todo`, `n/a`, `na`, `none`) pass through unchanged. **Unresolved drop** and report stderr — that list = work-list. Handles `- name:` and `- names: [...]`. |
| `extract_norm_quotes.py` | Parse `v-st-ext.adoc`, emit `{tag: spec_quote}` JSON. Handles `[[norm:foo]]` block anchors (capture next paragraph) and `[#norm:foo]#…#` inline anchors. |
| `audit_norm_yaml.py` | Walk `v-st-ext.yaml` rule defs, join with CSV, emit per-rule worksheet (`/tmp/vx_audit.csv` + `.json`) with flags: `EMPTY`, `PLACEHOLDER`, `GENERIC_ONLY`, `SUSPECT`, `OK`. |
| `update_norm_csv.py` | Apply JSON patch (`[{rule_name, coverpoints, descriptions, explanation, gaps}, ...]`) to rule CSV — full reset of `cp_name_*` / `coverage_desc_*` cols for matched rows. |
