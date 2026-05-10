# Hang Detection


**Always expect hangs while developing tests.** Use timeouts every coverage run:

```bash
# Single coverpoint iteration
FAST=True timeout 60s make coverage

# Full suite iteration (checking for hangs)
FAST=True timeout 300s make coverage
```

Single coverpoint never near 1 min. Full suite never near 10 min during iteration. **Slow vs benchmarks = assume hang immediately.** `make coverage` output shows oldest running task — same file stays "oldest" across runs = hanging. Follow `guides/debugging-hangs.md` to diagnose + fix.

**Coverage saves progress.** Completed `.sig` files preserved between runs. Timeout = lose nothing — fix hang + re-run. Skip `make clean` keeps prior progress intact.

**Incremental hang checking**: Run `FAST=True timeout 60s make coverage` in intervals to confirm `.sig` files completing. No new files complete between intervals = investigate now.

### Known full-suite hangs: store EEW≠SEW in standard tests

When run **full** (non-isolated) Vls suite, many standard store tests hang because test-gen scaffolding uses `RVTEST_SIGUPD_V` w/ `vle` readback at different EEW than current SEW. Known test-gen bug in standard (non-custom) testgen, **not** Sail bug. Affected:

- **Vls8**: 73 hangs — all stores where EEW ≥ 8 (vse16/32/64, vsse*, vsseg*, vssseg* with EEW>8, plus high-nf vssseg*e8 where EMUL×NF>8)
- **Vls16**: 15 hangs — stores with EEW=32 or 64
- **Vls32**: 8 hangs — stores with EEW=64
- **Vls64**: 0 hangs (EEW=SEW=64, no mismatch)

Hangs **residual** (only `cp_asm_count`/`std_vec` bins, no custom marks). No effect on custom coverpoint coverage. Full suite = expect these hangs, use timeouts. Custom coverpoints all hit 100% in isolation regardless.

### When to `make clean`

**Only run `make clean` after believe hang fixed**, to verify fix w/ full clean run of consistently-compiled suite. Do NOT `make clean` while iterating on hang — lose all saved progress for nothing.
