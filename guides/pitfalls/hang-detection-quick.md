# Hang Detection (Quick)


Sail can run **indefinite** number of tests. Build hanging = test bug (illegal instruction → trap loop), NOT sail limitation. Single isolated coverpoint should build in <30s. Longer:

1. Kill build
2. Note hanging file from `make coverage` output (e.g. `oldest: .../Vf64-vfmv.s.f.sig`)
3. Follow `guides/debugging-hangs.md` to trace + fix script

**⚠️ NEVER run `make coverage` without `timeout`.** Hangs common, will block terminal indefinitely. No exceptions. Always `FAST=True timeout <N>s make coverage`.
