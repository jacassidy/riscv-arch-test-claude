# Incremental Rebuild After Testgen Fix


After fixing testgen script bug, **no** `make clean` needed. Build system tracks `.sig` files, only re-simulates tests missing them. Saves time (~2 min recompile vs 5–10+ min full rebuild + sim):

```bash
# 1. Fix the bug in the testgen script (e.g. vector-testgen-unpriv.py or cp_custom_*.py)

# 2. Regenerate test .S files (no clean needed, ~30s)
make vector-tests

# 3. Delete .sig files for affected tests so they get re-simulated
#    Delete specific tests:
rm work/sail-rv64-max/build/rv64i/<Ext>/<test>.sig
#    Or delete all sigs for an extension:
rm work/sail-rv64-max/build/rv64i/<Ext>/*.sig work/sail-rv32-max/build/rv32i/<Ext>/*.sig

# 4. Run coverage — only missing .sig files are re-simulated (~2 min recompile + sim time)
FAST=True timeout 300s make coverage
```

**Key details:**

- .S content unchanged (same seed, same logic) → `act` detects, skips everything (~2s).
- .S content changed → `.elf` recompiled (~2 min for all VF), only tests w/ missing `.sig` re-simulated by Sail.
- **Always delete `.sig` for tests want re-simulated** — stale sigs not auto-invalidated by new .S.
