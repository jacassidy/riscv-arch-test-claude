# Vector Tests: Traps Cause Immediate Sail FAILURE Exit


**Applies to:** any test defining `RVTEST_VECTOR` (all generated vector tests under `tests/rv{32,64}i/V{ls,x,f}*`).

Vector test runs install mtvec stub in `RVMODEL_BOOT` that, on any trap, writes `3` to HTIF `tohost`. Halts sail with non-zero exit — run reported **FAILED**, not hung or passed-with-trap-logged.

**Implication for debugging:** vector coverage run fails on sail → unexpected trap (illegal instr, misaligned access, etc.) prime suspect. Check sail trace for trap entry before assuming signature mismatch. Normal trap-signature logging flow bypassed for vector tests.

**Source:**
- `config/sail/sail-rv64-max/rvmodel_macros.h` — defines `RVMODEL_BOOT` stub (rv32/clang variants symlink here). Gated on `#ifdef RVTEST_VECTOR`.
- `tests/env/sail_macros.h` — must **not** `#undef RVMODEL_BOOT`, else stub stripped from `.sig.elf` build path (sig-gen traps hang 30 min until `SAIL_TIMEOUT`).

Both `.sig.elf` (`-DSIGNATURE`) and final `.elf` (`-DRVTEST_SELFCHECK`) inherit stub.

**Verified:** clean vector test → sail exit 0 `SUCCESS`; same test with `unimp` injected → sail exit 1 `FAILURE: 1`, build fails fast (~0s).

**To disable:** remove or `#if 0`-out `RVTEST_VECTOR` branch of `RVMODEL_BOOT` in `config/sail/sail-rv64-max/rvmodel_macros.h`.

---
