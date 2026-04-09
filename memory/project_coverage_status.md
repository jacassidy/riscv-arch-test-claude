---
name: Coverage Work Status
description: Current state of Vf and Vls coverage work as of 2026-04-08
type: project
---

## Current Branch: merge_vls

**Why:** Each coverage domain (Vf, Vls) gets its own merge branch for clean PR history.
**How to apply:** Work on `merge_vls` for all Vls-related coverage.

## Vf — Complete
All Vf custom coverpoints at 100%.

## VlsCustom — Effectively Complete (2026-04-08)
Full suite run completed. No hangs. All 1240 tests (310 per SEW) passed.

**RV64: 100% custom coverage.** All ZERO covergroups are residual (cp_asm_count/std_vec only).
**RV32: 100% custom coverage except ei64 indexed LS** — a coverage-infra issue where the framework doesn't sample `*ei64*` indexed instructions on RV32 (tests run fine, coverage shows 0%).

6 instructions in `unsupported_tests` (Sail bugs): vlseg3e32.v, vlseg3e32ff.v, vlseg4e32.v, vsseg3e32.v, vsseg3e64.v, vwredusum.vs.

All issues tracked in `simulator-issues.md` (repo root).

## Philosophy Update
Guides updated with "simulator verification mindset" — when coverage can't be filled, consider Sail bugs first. `simulator-issues.md` is the central tracker.
