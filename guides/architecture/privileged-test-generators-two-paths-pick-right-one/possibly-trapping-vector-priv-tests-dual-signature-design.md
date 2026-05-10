## Possibly-trapping vector priv tests: dual signature design


Vector priv coverpoints often run instruction whose trap behavior depends on *config* (e.g. `cp_exceptionsv_indexed` runs indexed load that traps iff `MAXINDEXEEW < EEW(index)`). For these, both trap path and data path must produce config-deterministic signature.

Framework already supports running both signatures simultaneously:

- **Trap path**: framework trap handler (`tests/env/rvtest_trap_handler.h`) writes mcause/mepc/etc. to per-test trap-signature region pointed to by `mtrap_sigptr`. Fires automatically whenever trap occurs.
- **Data path**: `writeVecTest(..., priv=True)` emits `<testline>; nop; vsetivli (restore); writeSIGUPD_V(vd)`. Trap handler skips trapping instruction via mepc+=4, lands on `nop`. Subsequent `SIGUPD_V` samples whatever `vd` contains (initialized pre-test, possibly overwritten if no trap).

Both DUT and reference simulator run same code under same config — trap (or don't) identically — so both signature regions match across models. **Do NOT pass `skip_sigupd=True` to `writeVecTest` for these coverpoints**; would discard no-trap data check. Flag exists for rare case where vd post-trap not deterministic across models.

Required preconditions:
- Pre-test setup must put test in *otherwise-legal* state (vill=0, vstart=0, vl>0, mstatus.vs!=0, valid base, aligned rs1 if coverpoint constrains it). `random_mask_0` is `.align 3` so `la x?, random_mask_0` satisfies `rs1_val[2:0] == 3'b000`.
- Trap handler's mepc-skip stride must match trapping instruction width (4 bytes for non-RVC).

When debugging signature mismatch on these tests, first confirm reference and DUT use same MAXINDEXEEW (or whichever config gates trap) — divergence almost always traces to config skew, not test structure.
