# Normative Rules — Remaining Work to Reach Full Coverage

This file tracks what's left to do before `coverpoints/norm/Vx.yaml` is fully
populated with **resolved** `<covergroup>/<coverpoint>` references — i.e. every
coverpoint named in `working-testplans/csvs/v-st-ext-normative-rules.csv` exists
in some generated `*_coverage.svh` under `coverpoints/priv/` or
`coverpoints/unpriv/`.

Companion docs:
- Workflow: `guides/normative-rules-flow.md`
- Tool: `tools/fill_vx_coverpoints.py`

---

## How to refresh this list

```bash
cd /home/jacassidy/normative_rules && make covergroupgen
cd /home/jacassidy/cvw/addins/riscv-arch-test-claude
uv run python tools/fill_vx_coverpoints.py 2> /tmp/fill_dropped.log
sed -n '2,$p' /tmp/fill_dropped.log | sort -u > /tmp/fill_dropped_unique.txt
wc -l /tmp/fill_dropped_unique.txt
```

Anything in `/tmp/fill_dropped_unique.txt` is a coverpoint name that the CSV
references but no covergroup defines — i.e. a hole.

---

## Snapshot — 2026-04-26 (post `make covergroupgen` run)

- Filled rules: **407** in `Vx.yaml`.
- Distinct unmatched (dropped) coverpoint names: **96**.
- Total dropped references (with multiplicity): **398**.

Buckets (counts of unique names):

| Bucket | Count | What it means |
|---|---:|---|
| `cp_ssstrictv_*`  | 69 | SsstrictV strict-mode reserved-encoding / overlap / mask / EEW / EMUL / vmvnr / vrgather / vsetvli / vstart / etc. coverpoints. The `SsstrictV_*_cg` covergroups exist in `coverpoints/priv/SsstrictV_coverage.svh` but are stubs (only `test` / `test_two` defined). |
| `cp_exceptionsv_*` | 6 | V-extension exception coverpoints (LS std-trap-vec, address fault, ff-LS first-element trap, vd/vs1/vs2/v0 overlap with mask active). `ExceptionsVF_cg` exists with two cps (`cp_mstatus_vs_off`, `cp_vsstatus_vs_off`); a separate `ExceptionsV_*_cg` family for these `cp_exceptionsv_*` cps is missing. |
| `cp_custom_*`      | 12 | Custom coverpoints not yet implemented in their templates / scripts. |
| Misc bare names    |  7 | Standalone coverpoints used by the CSV but not implemented anywhere. |
| CSV data bug       |  2 | `line 32` literal + a long English sentence — bad cells in the CSV, not a missing covergroup. |

---

## 1. SsstrictV coverpoints (69 names) — biggest chunk

`coverpoints/priv/SsstrictV_coverage.svh` is currently a stub. Need to implement
covergroups containing at least these names (every `cp_ssstrictv_*` referenced
by the CSV):

- `cp_ssstrict_ls_nf_eew`
- `cp_ssstrictv_all_widening_source_overlap`
- `cp_ssstrictv_ext_emul_lt1_overlap`
- `cp_ssstrictv_lmulgt1_off_group`
- `cp_ssstrictv_ls_eew_2x_elen` / `cp_ssstrictv_ls_eew_lt_sewmin`
- `cp_ssstrictv_ls_element_misaligned`
- `cp_ssstrictv_ls_emul_16` / `cp_ssstrictv_ls_emul_f16` / `cp_ssstrictv_ls_emul_nfields_16`
- `cp_ssstrictv_ls_idx_emul_gt8` / `cp_ssstrictv_ls_idx_emul_lt_f8`
- `cp_ssstrictv_ls_mew_reserved`
- `cp_ssstrictv_ls_seg_idx_vd_vs2_grp_overlap` / `cp_ssstrictv_ls_seg_idx_vd_vs2_overlap`
- `cp_ssstrictv_ls_seg_vd_overflow_emulgt1`
- `cp_ssstrictv_ls_wholereg_misaligned` / `cp_ssstrictv_ls_wr_nf_reserved`
- `cp_ssstrictv_mask_logical_vm0_reserved`
- `cp_ssstrictv_masking_vd_eq_v0` / `cp_ssstrictv_masking_vd_eq_v0_lmulgt1`
- `cp_ssstrictv_narrowing_vs2_emul_16` / `cp_ssstrictv_narrowing_vs2_sew_eq_elen`
- `cp_ssstrictv_vadc_vsbc_vd_v0_reserved` / `cp_ssstrictv_vadc_vsbc_vm1_reserved`
- `cp_ssstrictv_vcompress_vd_vs2_overlap` / `cp_ssstrictv_vcompress_vm0_reserved`
  / `cp_ssstrictv_vcompress_vstart_nonzero` / `cp_ssstrictv_vcompress_vstart_report_zero`
- `cp_ssstrictv_vcsr_reserved_bits`
- `cp_ssstrictv_vext{2,4,8}_overlapping_vd_vs2`
- `cp_ssstrictv_vfmv_fs_sf_vm0_reserved` / `cp_ssstrictv_vfmv_vs2_not_v0_reserved`
- `cp_ssstrictv_vfp_eew_unsupported` / `cp_ssstrictv_vfp_widen_eew_unsupported`
  / `cp_ssstrictv_vfp_frm_reserved`
- `cp_ssstrictv_vid_vs2_not_v0_reserved`
- `cp_ssstrictv_vlmul_100_reserved`
- `cp_ssstrictv_vmv_vs2_not_v0_reserved` / `cp_ssstrictv_vmv_xs_sx_vm0_reserved`
- `cp_ssstrictv_vmvnr_off_group` / `cp_ssstrictv_vmvnr_reg_align`
  / `cp_ssstrictv_vmvnr_simm_reserved`
- `cp_ssstrictv_vnarrow_overlapping_vd_vs2`
- `cp_ssstrictv_vrgather_vd_vs1_eq` / `cp_ssstrictv_vrgather_vd_vs2_eq`
  / `cp_ssstrictv_vrgather_vd_vs2_overlap`
- `cp_ssstrictv_vrgatherei16_emul_16` / `cp_ssstrictv_vrgatherei16_emul_f16`
- `cp_ssstrictv_vsetvl{,i}_x0_x0_reserved`
- `cp_ssstrictv_vsetvli_lmul_sew_ratio` / `cp_ssstrictv_vsetvli_reserved_vsew`
- `cp_ssstrictv_vsext_src_reserved` / `cp_ssstrictv_vzext_src_reserved`
  / `cp_ssstrictv_vzext_vf{2,4,8}_reserved`
- `cp_ssstrictv_vslide1up_vd_vs2_overlap`
- `cp_ssstrictv_vstart_ge_vlmax`
- `cp_ssstrictv_vwiden_overlapping_vd_vs{1,2}_lmul1` / `cp_ssstrictv_vwidenw_overlapping_vd_vs1_lmul1`
- `cp_ssstrictv_widen_max_sew` / `cp_ssstrictv_widening_source_overlap`
  / `cp_ssstrictv_widening_vd_emul_16` / `cp_ssstrictv_widening_vd_sew_eq_elen`

**Action**: extend the SsstrictV covergroup template
(`(main repo) generators/coverage/src/covergroupgen/templates/Ssstrict*`) to emit
these. The CSV `working-testplans/csvs/Vector - V*_custom_definitions.csv` is
the single source of truth for what each `cp_ssstrictv_*` needs to test —
populate / update those rows first, then regenerate.

---

## 2. ExceptionsV (V-extension exceptions) — 6 names

Covergroup family is missing. Add covergroups (likely `ExceptionsV_cg` or
`ExceptionsV_*_cg`) under `coverpoints/priv/` containing:

- `cp_exceptionsv_LS_stdtrapvec`
- `cp_exceptionsv_address_fault`
- `cp_exceptionsv_ffLS_first_elm_trap`
- `cp_exceptionsv_vd_v0_overlap_mask_active`
- `cp_exceptionsv_vd_vs1_overlap`
- `cp_exceptionsv_vd_vs2_overlap`

Note: `ExceptionsVF_cg` already exists for the FP-side equivalents (mstatus/vsstatus VS=Off).

---

## 3. Missing custom coverpoints (12 names)

- `cp_custom_f_freg_write_vl0`
- `cp_custom_indexed_emul_data_only_lmul{1,2}_nf{1,2}` (4 variants)
- `cp_custom_maskLS_prestart_no_exception` / `cp_custom_maskLS_tail_no_exception`
- `cp_custom_masked_vs1_v0`
- `cp_custom_vdEqVs_vd_eq_vs{1,2}` (2 variants)
- `cp_custom_vfp_csr_state_mstatus_dirty`
- `cp_custom_vl0`

**Action**: add rows to `working-testplans/csvs/Vector - V{x,ls,f}_custom_definitions.csv`
for each (Goal / Feature Description / Expectation columns), then implement the
generator script under `(main repo) generators/coverage/src/covergroupgen/templates/`
or `(main repo) generators/testgen/scripts/custom/`. See `guides/custom-scripts/GUIDE.md`.

---

## 4. Misc bare coverpoints (7 names)

- `cp_vd (variant x)` — CSV cell with parenthetical that the script's expander doesn't strip the right way. Either fix the cell to use the variant suffix (e.g. `cp_vd_x`) or extend the parenthetical-expander in `fill_vx_coverpoints.py` to handle bare `(X variant)`.
- `cp_vs2_vm_corners`, `cp_vs2_vs1_corners`, `cp_vs2_vs1_mask_corners` — used in saturation/mask rules; need to be added to the corresponding `Vx*_*_cg` covergroups (template work).
- `cp_vsetivli_avl_corners` — used by `vl_op` and friends. Add to a vsetivli/vsetvli covergroup.
- `cp_vtype_walking1s` — used by all the `vtype-*_sz` rules and `RESERVED_VILL_SET`. Needs a new covergroup that walks 1s through XLEN bits of vtype via vsetvl rs2.
- `cp_vxsat` — used by `vxsat_op`. Bins vxsat={0,1}; add to a Vxsat covergroup.

---

## 5. CSV data bugs (NOT a covergroup hole)

Two CSV rows use the literal string `line 32` as a coverpoint name (likely a
stale "see line 32" reviewer note that ended up in the wrong column):

- Line 99: `vstart_vl_dep` rule, `cp_name_1` cell.
- Line 173: `vector_ls_seg_wholereg_evl` rule, `cp_name_3` cell.

Also CSV line 32 (`vtype-vsew_op`) has an unbalanced quote that splits a
sentence into fake `cp_name_*` fields when re-parsed. Fix the cell quoting so
the description text doesn't bleed into coverpoint columns.

**Action**: edit those rows in `working-testplans/csvs/v-st-ext-normative-rules.csv`
and re-run `tools/fill_vx_coverpoints.py`.

---

## Definition of done

```bash
cd /home/jacassidy/normative_rules && make covergroupgen
cd /home/jacassidy/cvw/addins/riscv-arch-test-claude
uv run python tools/fill_vx_coverpoints.py 2> /tmp/log
# Expected:
#   - "Filled N rule(s)" with no "Dropped ..." line.
#   - /tmp/log contains nothing except the "Filled" summary.
uv run python tools/audit_norm_yaml.py
# Expected: zero EMPTY / GENERIC_ONLY / SUSPECT entries (or each remaining one
# justified in CSV `explanation`/`gaps` columns).
```
