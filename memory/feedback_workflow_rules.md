---
name: Workflow Rules and Constraints
description: User-specified rules about testing workflow, guide-first approach, hang detection, and make clean discipline
type: feedback
---

## File Modification
- No global file-modification restrictions — follow per-directory guides for specific rules.
- For test generation: strongly prefer `cp_custom_*.py` scripts; changes to `vector_testgen_common.py` or `vector-testgen-unpriv.py` are allowed but must be systematic and general-purpose, not specific patches. See `generators/testgen/scripts/custom/GUIDE.md`.
- CSV files: authorized via csv_edit.py when explicitly asked.

**Why:** The old blanket rule ("ONLY templates and cp_custom") was too restrictive. File-specific guidance now lives in the relevant directory guides (as of 2026-04-01).
**How to apply:** Check the guide for the directory you're working in. For testgen, exhaust custom script options before touching shared files.

## Testing Workflow
- NEVER delete completed work to re-test. Always preserve progress and test on the next unprocessed item. Scripts have resume support — use it.
- NEVER read `vector-testgen-unpriv.py`, `vector_testgen_common.py`, or other large test generation scripts directly. They have accompanying .md guide files in `generators/testgen/scripts/custom/` that are specifically written for Claude to read instead.

**Why:** Large scripts waste context and have purpose-built guides. Deleting completed work causes regressions.
**How to apply:** Always use .md guide files for context on testgen scripts. Check progress.json before starting any coverage work.

## Guide-First Approach
- For ANY coverpoint or CSV task, read `guides/csv-editing.md` then `generators/coverage/templates/GUIDE.md` FIRST before doing anything else.
- Do not explore the codebase or spawn search agents before reading these guides.

**Why:** The guides contain all needed patterns, formats, and examples — exploring wastes time.
**How to apply:** On any coverpoint/CSV task, read guides before touching code.

## Hang Detection and Timing (updated 2026-04-08)
- A single Sail simulation takes ~5 seconds. The longest should never exceed 20 seconds.
- **Always expect hangs while developing tests.** Use timeouts on every coverage run.
- Isolated coverpoint coverage: timeout 60s (should finish in <30s).
- Full custom suite (e.g. Vls): timeout 300s / 5 min while iterating. Full run takes ~10 min but you should never wait that long during development.
- Never use huge timeouts (10 min). Short timeouts catch hangs fast.
- When a hang is found, grep for `mcause` in the trace output — this catches illegal instructions faster than reading assembly.

**Why:** Hangs are the most common failure mode. The user explicitly corrected old timing numbers (2026-04-08) and emphasized that timeouts should be aggressive during iteration. A 10-min timeout is never appropriate for a single coverpoint.
**How to apply:** `FAST=True timeout 60s make coverage` for isolated coverpoints; `FAST=True timeout 300s make coverage` for full suite iteration.

## Coverage Saves Progress / make clean Discipline (added 2026-04-08)
- **Coverage saves progress.** Completed `.sig` files persist between runs. A timed-out run loses nothing.
- **DO NOT run `make clean` while iterating on a hang** — it destroys all saved progress.
- **Only run `make clean` after you believe a hang is fixed**, to verify with a full clean run of a consistently-compiled test suite.
- User explicitly said "DO NOT RUN MAKE CLEAN, I have a lot of coverage progress" (2026-04-08).

**Why:** `make clean` wipes all `.sig` files. Coverage work is incremental — losing progress means re-running all tests. Clean builds are only needed to verify that a complete, consistently-compiled suite passes end-to-end.
**How to apply:** Default to skipping `make clean`. Only use it as a final verification step after confirming a fix.

## vill Testing Pattern (added 2026-04-08)
- When testing vill (illegal vtype), do NOT assume a particular SEW/LMUL configuration will set vill. Instead, explicitly load a register with the vtype vill bit set and use `vsetvl` to load that as vtype.
- Reference implementation: `cp_custom_vwholeRegLS_vill.py`

**Why:** User corrected this pattern — relying on a specific config to trigger vill is fragile and ISA-dependent. Explicit vill injection is deterministic.
**How to apply:** Any test that needs vill state should follow the cp_custom_vwholeRegLS_vill.py pattern.

## Context Refresh Between Problems
- When switching from one problem/coverpoint to another, STOP.
- Re-read the relevant guide files from the CLAUDE.md Task Routing table.
- Summarize current context: what was just completed, what's being started next, current state.

**Why:** Context drift causes mistakes when handling multiple problems in sequence — this is where Claude gets lost most often.
**How to apply:** At every transition between problems, force a guide re-read and context summary before proceeding.
