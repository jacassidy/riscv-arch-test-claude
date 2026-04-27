# Normative-Rule → Coverpoint Mapping Flow

This document explains how the `Vx.yaml` (and sibling) normative-rule coverage files in
`/home/jacassidy/normative_rules/coverpoints/norm/` are generated, where the source-
of-truth lives, and how to extend / fix them.

> **TL;DR** &nbsp;Edit the CSV, then re-run the fill script. The CSV is the database; the
> YAML is a generated artifact.

---

## 1. The data flow

```
┌─────────────────────────────────────┐
│ riscv-isa-manual/src/v-st-ext.adoc  │   ← spec source; contains [[norm:tag]] anchors
└──────────────────┬──────────────────┘
                   │ (anchors are referenced by tags below)
                   ▼
┌──────────────────────────────────────────────────────────┐
│ riscv-isa-manual/normative_rule_defs/v-st-ext.yaml       │   ← groups norm:* tags into
│   - name / - names: <rule name(s)>                        │     named "rules" (the
│     tags: [norm:foo, norm:bar]                           │     atomic unit of mapping)
└──────────────────┬───────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ riscv-arch-test-claude/working-testplans/csvs/                   │
│   v-st-ext-normative-rules.csv                                    │
│   columns: rule_name, spec_text, cp_name_1, coverage_desc_1, ... │   ← the database
│            cp_name_36, coverage_desc_36, coverage_status,         │     of mappings
│            explanation, gaps                                      │
└──────────────────┬───────────────────────────────────────────────┘
                   │ (tools/fill_vx_coverpoints.py)
                   ▼
┌──────────────────────────────────────────────────────────┐
│ normative_rules/coverpoints/norm/Vx.yaml                 │   ← generated artifact
│   normative_rule_definitions:                            │     consumed downstream
│     - name: <rule>                                       │
│       coverpoint: ["cp_a", "cp_b", ...]                  │
└──────────────────────────────────────────────────────────┘
```

Reference for what each `cp_*` means:
* **Standard coverpoints** (`cp_vd`, `cp_vs2_edges`, `cr_vl_lmul`, `cp_vl_0`, …):
  defined in `normative_rules/docs/ctp/src/v.adoc` (table around line 122) plus the
  variant suffixes documented immediately below it (`nv0`, `emul2`, `wv`, `wred`, …).
* **Custom coverpoints** (`cp_custom_*`, `cp_ssstrictv_*`, `cp_custom_v*`, …):
  defined in
  `riscv-arch-test-claude/working-testplans/csvs/Vector - V{x,ls,f}_custom_definitions.csv`.
  The Goal / Feature Description / Expectation columns are the human definition.

---

## 2. Tools (in `riscv-arch-test-claude/tools/`)

| Tool | Purpose |
|---|---|
| `fill_vx_coverpoints.py` | Reads the CSV, replaces `coverpoint: [...]` arrays in `Vx.yaml`. **Run `make covergroupgen` first.** Each CSV coverpoint is resolved against generated `*_coverage.svh` files in `coverpoints/{priv,unpriv}/` and rewritten as `<covergroup>/<coverpoint>` (e.g. `ExceptionsHV_cg/cp_mstatus_vs_off`). Looser matching: exact name first, then prefix match (CSV `cr_vl_lmul` → svh `cr_vl_lmul_sew32`). Textual placeholders (`implicit`, `untestable`, `todo`, `n/a`, `na`, `none`) pass through unchanged. **Anything that doesn't resolve is dropped** and reported on stderr — that list is the work-list for new covergroups (see `guides/normative-rules-status.md`). Handles both `- name: X` and `- names: [X, Y]`. |
| `extract_norm_quotes.py` | Parses `v-st-ext.adoc` and emits `{tag: spec_quote}` JSON. Supports both `[[norm:foo]]` block anchors (captures next paragraph) and `[#norm:foo]#…#` inline anchors. |
| `audit_norm_yaml.py` | Walks `v-st-ext.yaml` rule definitions, joins with the CSV, and emits a per-rule worksheet (`/tmp/vx_audit.csv` + `.json`) with a flag column: `EMPTY`, `PLACEHOLDER`, `GENERIC_ONLY`, `SUSPECT`, `OK`. |
| `update_norm_csv.py` | Applies a JSON patch (list of `{rule_name, coverpoints, descriptions, explanation, gaps}`) to the rule CSV — does a full reset of the `cp_name_*` / `coverage_desc_*` columns for matched rows. Use this when batch-fixing audit results. |

### End-to-end fix workflow

```bash
cd /home/jacassidy/cvw/addins/riscv-arch-test-claude

# 1. Re-extract spec quotes if the spec changed
uv run python tools/extract_norm_quotes.py --out /tmp/norm_quotes.json

# 2. Generate / refresh audit
uv run python tools/audit_norm_yaml.py    # writes /tmp/vx_audit.csv + .json

# 3. Inspect the SUSPECT / PLACEHOLDER / GENERIC_ONLY rows; produce a JSON patch
#    (manual or via sub-agent — see section 4 below)

# 4. Apply the patch to the CSV and regenerate Vx.yaml
uv run python tools/update_norm_csv.py /tmp/my_patch.json
(cd /home/jacassidy/normative_rules && make covergroupgen)   # required before fill
uv run python tools/fill_vx_coverpoints.py

# 5. Re-audit to confirm
uv run python tools/audit_norm_yaml.py
```

---

## 3. Flag semantics from `audit_norm_yaml.py`

* `EMPTY` — the rule has no `cp_name_*` filled (CSV row missing or all blank).
* `PLACEHOLDER` — only `implicit` / `untestable` / similar non-coverpoint markers.
  Often correct for impl-defined / S-mode / hardware-MAY rules.
* `GENERIC_ONLY` — only `cp_asm_count`. Acceptable for extension-dependency or
  RVWMO/program-order rules that are verified merely by running any instruction.
  Suspicious for rules describing concrete behavior.
* `SUSPECT` — heuristic flagged a possible subject mismatch (e.g. rule name mentions
  `vstart` but no coverpoint name contains the substring `vstart`). Many false
  positives — e.g. `cp_vcsrrswc` and `cp_sew_lmul_vsetvl` test specific CSRs but
  don't carry the CSR token in their name. Always read the spec quote and the
  coverpoint definition before "fixing".
* `OK` — passes all heuristic checks. Not a guarantee of correctness.

---

## 4. Reviewing a batch with a sub-agent

When auditing many rules at once, dispatch parallel sub-agents — see the prompt
template that produced `/tmp/batch_*_patch.json` in this session. Each agent gets:

1. A batch JSON (`/tmp/batch_N.json`) with `rule_name`, `spec_quote`, `current_coverpoints`.
2. The full coverpoint glossary (`/tmp/full_cp_glossary.json`) — built by unioning
   `std_cp_defs.json` (from `v.adoc` table), `cp_glossary.json` (from custom defs CSVs),
   and previously-used coverpoints from the rule CSV itself.
3. Strict instruction: **only use coverpoint names already in the glossary** OR the
   special markers `implicit` / `untestable` / `cp_asm_count`. Verify with:
   ```python
   g = json.load(open('/tmp/full_cp_glossary.json'))
   allowed = set(g) | {'implicit', 'untestable', 'cp_asm_count'}
   bad = [(p['rule_name'], c) for p in patch for c in p['coverpoints'] if c not in allowed]
   assert not bad
   ```
4. Output: a JSON patch in the format consumed by `update_norm_csv.py`.

---

## 5. Common mistakes / patterns to watch

* **`- names: [X, Y]` plural entries** — older versions of the fill script silently
  skipped these, leaving 77 entries with `coverpoint: [""]`. The script now expands
  the union of coverpoints across all named rules. If you see a `[""]` again, check
  whether the CSV `rule_name` matches one of the names exactly (case-insensitive,
  with `-`/`_` interchangeable via `norm_key`).
* **`vl_op` vs `cp_custom_vindexCorners_*`** — historic example: a rule about the
  `vl` *register* should not be tested by an indexed-instruction edge-case
  coverpoint. When choosing coverpoints, verify that the *subject* of the rule
  matches what the coverpoint exercises, not just topical overlap.
* **CSR rules** — `cp_vcsrrswc`, `cp_vcsrs_walking1s`, `cp_ssstrictv_vcsr_reserved_bits`,
  `cp_vstart_out_of_bounds`, `cp_sew_lmul_vsetvl`, `cp_sew_lmul_vset_i_vli`, and
  `cp_vsetivli_avl_corners` are the right tools for testing CSR access /
  size / write-clear-set / reserved-bit semantics — even though their names don't
  embed the target CSR token.
* **`vtype` field rules (vsew/vlmul/vta/vma)** — `cr_vtype_agnostic` crosses
  `vta×vma`; `cr_vl_lmul` crosses LMUL with vl; `cp_sew_lmul_vset_i_vli` exercises
  the configuration mechanism. These are usually preferable to operand edges
  (`cp_vs2_edges`) for rules describing *what the field means*.
* **Saturation rules (`vxsat_op_*`)** — must include `cp_vxsat` (the bin sampling
  the vxsat bit) in addition to operand-corner coverpoints, otherwise you only
  test the arithmetic, not the flag.
* **Element-group / extension-dependency / RVWMO rules** — `cp_asm_count` alone is
  legitimate; do not invent specialized coverpoints for them.

---

## 6. State left at end of the 2026-04-21 session

* `tools/fill_vx_coverpoints.py` — fixed to handle `- names: [...]` (single and
  multi-line). Now wraps long arrays.
* `tools/extract_norm_quotes.py` — new.
* `tools/audit_norm_yaml.py` — new.
* `tools/update_norm_csv.py` — new.
* CSV: 88 patches applied (87 from sub-agent batches + 1 manual `vl_op` fix). The
  pre-patch CSV is in `/tmp/csv.before.csv` if you need to compare; the pre-fill
  YAML snapshot is `/tmp/Vx.before.yaml`.
* `Vx.yaml` is fully populated — no `coverpoint: [""]` remain.
* Audit re-run after patching: `OK 521, SUSPECT 15, PLACEHOLDER 18, GENERIC_ONLY 33`.
  The remaining `SUSPECT`s are heuristic false positives (CSR rules with
  CSR-targeting coverpoints whose names don't include the CSR token).
* `PLACEHOLDER` count went up because some entries were intentionally relabeled
  from over-specific (incorrect) coverpoints to honest `untestable` / `implicit`
  with the proper rationale recorded in the CSV `explanation` column.

If you re-do the spec-quote extract and still see anchors with empty quotes
(e.g. `norm:vector_indexed_load_op` returned `<MISSING>` on this run), check
whether the anchor in the .adoc uses an unusual syntax — the extractor handles
`[[norm:tag]]` and `[#norm:tag]#…#` but not e.g. tags hidden inside
`[NOTE]\n====\n…\n====` blocks split across multiple paragraphs.
