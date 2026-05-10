# RVVI fsflagsi CSR Alias Bug


`fsflagsi` writes CSR 001 (fflags) but NOT CSR 003 (fcsr). Templates using `get_csr_val("fcsr", "fflags")` see stale values after `fsflagsi`. **Fix**: add spacer tests with non-flag-setting inputs after flag-setting FP instructions to force CSR 003=0.

CSR sampling rule:
- After FP instruction: `get_csr_val(..., "fcsr", "fflags")` works (FP writes CSR 001 + 003).
- Before instruction (SAMPLE_BEFORE): use `get_csr_val(..., "fflags", "fflags")` — `fsflagsi` only writes CSR 001.

Affected: any template crossing with `fp_flags_clear` reading from "fcsr".
