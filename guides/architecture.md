# architecture.md — Project Architecture & Reference

> **This file lives in `riscv-arch-test-claude`.** All new Claude-generated files belong here, not in the main repo. The main repo is your current working directory (whichever checkout or worktree this CLAUDE.md is symlinked into).

## Overview

**RISC-V Architectural Certification Tests (ACTs)** — generates self-checking assembly tests from CSV testplans, Python generators, and UDB config files. Tests run against a reference model (Sail RISC-V) to compute expected results.

Repository: https://github.com/riscv-non-isa/riscv-arch-test (act4 branch)

## Commands

```bash
make --jobs                          # Generate and compile all tests
make vector-tests                    # Generate vector tests only
FAST=True timeout 60s make coverage   # Isolated coverpoint (60s max)
FAST=True timeout 300s make coverage # Full suite iteration (5 min max)
make clean                           # Remove generated tests AND covergroups (only after fixing a hang)
make clean-tests                     # Remove generated tests only
make CONFIG_FILES=config/duts/cvw/cvw-rv64gc/test_config.yaml EXTENSIONS=I,M,A
make lint / make lint-fix / make format
```

### Incremental Rebuild (no clean needed)

After fixing a testgen script, regenerate and re-run coverage without `make clean`:

```bash
make vector-tests                    # Regenerates .S files (~30s)
rm work/sail-rv64-max/build/rv64i/<Ext>/*.sig   # Delete sigs for affected tests
FAST=True make coverage              # Recompiles elfs (~2 min), re-sims only missing sigs
```

If test content is unchanged (same seed), coverage completes in ~2s. See
`guides/custom-scripts/CLAUDE-coverage-workflow.md` for details.

## Never Edit Generated Files

`coverpoints/unpriv/*_coverage.svh` and `tests/rv{32,64}i/**/*.S` are **generated
outputs** — never hand-edit them. Changes land in sources and flow through regen:

- Coverpoint `.svh` ← templates in `generators/coverage/src/covergroupgen/templates/`
- Test `.S` ← `generators/testgen/scripts/custom/*.py` + CSV testplans

Edit the template/script/CSV, then rerun `make vector-tests` (or `make coverage`).

## Coverage Generator (`generate.py`)

`generators/coverage/src/covergroupgen/generate.py` produces per-extension `_coverage.svh` / `_coverage_init.svh` files:

- `write_covergroups` writes to `coverpoints/unpriv/` from testplans at the root of `testplans/` (SEW-expanded for vector extensions).
- `write_priv_covergroups` writes to `coverpoints/priv/` from testplans under `testplans/priv/` (no SEW expansion).
- Both share `_parse_testplan_csv` (CSV parsing) and `_write_extension_files` (per-extension file writer); prefer extending those helpers over duplicating their logic.

Regenerate with `uv run covergroupgen testplans` (or `make covergroupgen`). Do not hand-edit generated files under `coverpoints/unpriv/` or `coverpoints/priv/` for extensions that have a CSV — edits will be clobbered on the next run.

## Privileged Test Generators (Two Paths — pick the right one)

There are **two distinct frameworks** for generating priv-mode tests under `tests/priv/<TestSuite>/`. Use the right one for the task:

### Path A — CSV testplan + cp_*.py (instruction × coverpoint matrix)

Use this when you have a *table* of instructions, each crossed with a set of coverpoints (e.g. exception-style coverage of every vector load/store). The driver auto-iterates instructions × coverpoints.

- Testplan CSV: `(main repo) testplans/priv/<Ext>.csv`
- Coverpoint handlers: `(main repo) generators/testgen/scripts/priv/cp_*.py` decorated with `@register("cp_xxx")` from `priv_coverpoint_registry.py`
- Driver: `(main repo) generators/testgen/scripts/vector-testgen-priv.py`
- Output: `tests/priv/<Ext>/<Ext>_rv{32,64}.S`
- Existing examples: `ExceptionsVls`, `ExceptionsVx` (CSVs in `testplans/priv/`).

### Path B — handwritten Python generator (one-off / scenario-driven)

Use this when the test is a sequence of *scenarios* better expressed as straight-line code than a matrix — e.g. setting CSR state, executing one instruction, restoring state. This is the "handwritten test, written in Python so you get the framework's macros and signature plumbing" style.

- Generator module: `(main repo) generators/testgen/src/testgen/priv/extensions/<TestSuite>.py`
- Decorator: `@add_priv_test_generator("<TestSuite>", required_extensions=[...], march_extensions=[...], extra_defines=[...])` from `testgen.priv.registry`
- Asm helpers: `comment_banner`, `write_sigupd`, `load_float_reg`, `load_int_reg`, `gen_csr_read_sigupd`, plus `test_data.add_testcase(name, coverpoint, covergroup)` to emit a labeled testcase that the covergroup samples on.
- Macros available in emitted asm: `LI(xR, val)`, `LA(xR, sym)`, `CSRR/CSRW/CSRS/CSRC(csr, xR)`, plus normal asm. Vector tests need `extra_defines=["#define RVTEST_VECTOR", "#define RVTEST_SEW 0", "#define VDSEW 0"]`.
- Auto-defines: `F` in required_extensions adds `#define RVTEST_FP`; `Sm`/`S`/`U`/`H` add the relevant `rvtest_*trap_routine` defines (see `io/templates.py:generate_defines_from_extensions`).
- Driver: `(main repo) generators/testgen/src/testgen/generate/priv.py:generate_priv_test()` (one multi-XLEN test file via preprocessor — `xlen=0`).
- Output: `tests/priv/<TestSuite>/<TestSuite>-00.S` (filename comes from `io/writer.py:write_test_file`, format `<testsuite>-{file_idx:02d}.S`).
- Existing examples: `SmF.py`, `ExceptionsSm.py`, `InterruptsU.py`, `ExceptionsVf.py`.
- Reserved registers (set by `generate_priv_test`): x0, x1/ra, x6, x7, x9, x16-x31. Allocate from the remaining pool via `test_data.int_regs.get_register(...)` / `get_registers(n, ...)` and return them at the end.

### Decision rule

- Many instructions × few coverpoints → Path A.
- Few instructions × many CSR / mode permutations → Path B.
- Mixed → Path B for the scenario glue; call into shared helpers (see `priv/extensions/ExceptionsCommon.py` for examples).

### Possibly-trapping vector priv tests: dual signature design

Vector priv coverpoints often run an instruction whose trap behavior depends on the *config* (e.g. `cp_exceptionsv_indexed` runs an indexed load that traps iff `MAXINDEXEEW < EEW(index)`). For these, both the trap path and the data path must produce a config-deterministic signature.

The framework already supports running both signatures simultaneously:

- **Trap path**: the framework trap handler (`tests/env/rvtest_trap_handler.h`) writes mcause/mepc/etc. to the per-test trap-signature region pointed to by `mtrap_sigptr`. This fires automatically whenever a trap occurs.
- **Data path**: `writeVecTest(..., priv=True)` emits `<testline>; nop; vsetivli (restore); writeSIGUPD_V(vd)`. The trap handler skips the trapping instruction by mepc+=4, landing on the `nop`. The subsequent `SIGUPD_V` then samples whatever `vd` contains (initialized pre-test, possibly overwritten if no trap).

Both DUT and reference simulator run the same code under the same config — they trap (or don't) identically — so both signature regions match across models. **Do NOT pass `skip_sigupd=True` to `writeVecTest` for these coverpoints**; that would discard the no-trap data check. The flag exists for the rare case where vd post-trap is not deterministic across models.

Required preconditions for this to work:
- Pre-test setup must put the test in an *otherwise-legal* state (vill=0, vstart=0, vl>0, mstatus.vs!=0, valid base, aligned rs1 if the coverpoint constrains it). `random_mask_0` is `.align 3` so `la x?, random_mask_0` satisfies `rs1_val[2:0] == 3'b000`.
- The trap handler's mepc-skip stride must match the trapping instruction width (4 bytes for non-RVC).

When debugging a signature mismatch on these tests, first confirm the reference and DUT use the same MAXINDEXEEW (or whichever config gates the trap) — divergence almost always traces back to config skew, not test structure.

### Coverage caveats worth documenting in the .svh

When a coverpoint is conceptually unimplementable (e.g. observing an FS state-transition on hardware that's allowed to be always-Dirty, or crossing on misa.V when misa is permitted to be all-zero read-only), drop the unimplementable cross from the .svh and add a comment explaining why — but keep the test exercising the scenario. Cross-model signature comparison still catches divergence.

## Pipeline: CSV to ELF

1. CSV testplan maps instructions to coverpoints
2. Coverpoint generators create assembly templates
3. `make vector-tests` invokes covergroupgen + testgen, creates `.S` files
4. UDB config filters applicable tests
5. Sail model runs tests, computes expected results
6. Final self-checking ELFs embedded with expected values

## Directory Structure

### Main repo (`riscv-arch-test-cvw`)
```
riscv-arch-test-cvw/
├── config/duts/cvw/                              # CVW-specific configs (rv32gc, rv64gc)
├── generators/
│   ├── testgen/src/testgen/coverpoints/          # Coverpoint generator modules (cp_*.py)
│   ├── testgen/scripts/custom/                   # Custom cp_custom_*.py scripts
│   ├── coverage/src/covergroupgen/templates/      # Scalar/general .sv/.txt coverpoint templates
│   │   └── vector/                                # Vector covergroup templates (cmp_*, cp_*, cr_*, sample_*)
│   └── coverage/covergroupgen.py
├── testplans/*.csv                               # Live CSVs (managed by isolation scripts)
├── tests/rv32i,rv64i/                            # Generated .S files
├── work/sail-rv64-max/reports/                   # RV64 coverage reports
└── work/sail-rv32-max/reports/                   # RV32 coverage reports
```

### Claude repo (`riscv-arch-test-claude`, this repo)
```
riscv-arch-test-claude/
├── CLAUDE.md                                      # Task routing
├── guides/                                        # All guides and references
├── scripts/claude-scripts/                        # Coverage tools, orchestrator, knowledge
├── tools/csv_edit.py, isolate_coverpoint.py       # CSV editing and isolation tools
└── working-testplans/                             # Canonical CSV source + backups
    └── duplicates/                                # Canonical backups (Vf-save.csv, etc.)
```

## Known Deviations from Upstream

### `-DRVTEST_SELFCHECK` disabled in coverage builds

`build_plan.py` compiles `final.elf` without `-DRVTEST_SELFCHECK`. Coverage runs are unchecked (store-only). Correctness verified separately via RVVI lock-step.

### `RVTEST_SIGUPD` 6-arg API

Upstream added a 6th argument `_STR_PTR`. Vector testgen updated `writeSIGUPD`/`writeSIGUPD_F` accordingly. If builds break with "macro requires 6 arguments but only 5 given", check those functions.

## Python Environment

- Tool: `uv`; Location: `.venv/`; Python 3.12+
- Always invoke via `uv` to ensure correct environment
