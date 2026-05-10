# 7. RV32 `vloxei64.v` (and all ei64 indexed LS) — Illegal instruction decode

- **Status**: confirmed-sail-bug
- **Instructions**: All `*ei64*` indexed LS on RV32:
  `vloxei64.v`, `vluxei64.v`, `vsoxei64.v`, `vsuxei64.v`, plus segmented variants
  (`vloxseg*ei64.v`, `vluxseg*ei64.v`, `vsoxseg*ei64.v`, `vsuxseg*ei64.v`)
- **Affected**: RV32 only (RV64 works)
- **Custom bins blocked on RV32**:
  `cp_custom_indexed_emul_data_only`, `cp_custom_masked_vs2_v0`,
  `cp_custom_ls_indexed_truncated`, `cp_custom_ls_indexed_zero_extended_sew*`

See sibling shards: `7-rv32-ei64-repro.md`, `7-rv32-ei64-trace.md`, `7-rv32-ei64-analysis.md`, `7-rv32-ei64-workaround.md`.
