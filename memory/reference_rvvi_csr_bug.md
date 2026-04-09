---
name: RVVI fsflagsi CSR Alias Bug
description: fsflagsi writes CSR 001 (fflags) but not CSR 003 (fcsr) — templates reading fcsr see stale values
type: reference
---

`fsflagsi` writes CSR 001 (fflags) but NOT CSR 003 (fcsr). Templates using `get_csr_val("fcsr", "fflags")` see stale values after fsflagsi.

**Fix:** Add "spacer" vfrec7/vfrsqrt7 tests with non-flag-setting inputs after flag-setting tests. The spacer writes CSR 003=0, clearing stale fcsr.

**Affected templates:** Any template that crosses with `fp_flags_clear` reading from "fcsr".

**CSR sampling rule:**
- After an FP instruction: `get_csr_val(..., "fcsr", "fflags")` works (FP instructions write both CSR 001 and 003).
- Before an instruction (SAMPLE_BEFORE): use `get_csr_val(..., "fflags", "fflags")` because `fsflagsi` only writes CSR 001.
