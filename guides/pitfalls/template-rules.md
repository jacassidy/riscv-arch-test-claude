# Template Rules


- **Residual 0% bins fine.** Framework-generated bins not defined in template filled by full suite. Only custom bins must hit 100% during isolated testing.
- **NEVER check `ins.current.insn == "some_string"`** — `insn` = raw 32-bit encoding. Framework already routes per-instruction.
- Use `ins.current.vs2_val` (register contents), NOT `ins.current.vs2` (register name string)
- CSR sampling: `get_csr_val(..., "fcsr", "frm")` not `"frm", "frm"` (returns 0)
- CSR sampling: For fflags **after** FP instruction, `"fcsr", "fflags"` works (FP writes both CSR 001 and 003). For fflags **before** instruction (SAMPLE_BEFORE), use `"fflags", "fflags"` because `fsflagsi` only writes CSR 001, leaving CSR 003 (fcsr) stale.
- Narrowing ops: `get_vr_element_zero()` extracts at OUTPUT SEW. Use `ins.current.vs2_val[63:0]` for source.
- `v0_element_1_active` inactive element bins: use `{0}` (inactive = mask bit 0), not `{1}`
