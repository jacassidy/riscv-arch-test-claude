# Register Allocation in Test Generators

> **Hard rule — no exceptions:** Test generators must **never** hardcode register numbers. Applies to **every** register class — vector (`v0`–`v31`), scalar/integer (`x0`–`x31`), floating-point (`f0`–`f31`) — and **every** position register appear: `vd=`, `vs1=`, `vs2=`, `rd=`, `rs1=`, `rs2=` args to randomizer calls; literal `x{N}` / `v{N}` / `f{N}` in f-string asm templates; pre-test scratch picks; trap-handler setup; signature stores; all of it. **Always generate register via framework randomizer, within instruction's legal constraints** (EMUL alignment, no-overlap rules, segment `nf × EMUL` fit, framework-reserved set `x0`–`x5`). Hardcoded registers shrink search space, hide real bugs behind always-passing register choices, produce false-positive coverage. Reducing test diversity to single register tuple = exactly what these generators exist to prevent.
>
> Only literals allowed in emitted asm = **architecturally required** ABI registers — `a0` when calling convention demands, `x0` when zero register needed, `x2`/`common.sigReg` as framework signature pointer — and even these should come from named constants (`common.sigReg`, `common.tempReg`, `common.linkReg`, …), never bare integers. Anything else = bug.

Applies to **every** generator: scalar priv (`generators/testgen/src/testgen/priv/extensions/*.py`), vector priv (`generators/testgen/scripts/vector-testgen-priv.py` + `generators/testgen/scripts/priv/cp_*.py`), unprivileged generators too.

## How to do it correctly

- **Scalar priv flow** (`Sm.py`, `SmF.py`, `U.py`, `ExceptionsVf.py`, etc.):
  use `test_data.int_regs.get_registers(n)` / `get_registers(1)` to pull `n` random integer registers, analogous `fp_regs` API for floats. Never write `x5`, `x6`, ... directly in emitted asm.
- **Vector priv flow** (`vector-testgen-priv.py`, `priv/cp_*.py`):
  call `randomizeVectorInstructionData(instruction, sew, count, ...)` **without** passing `vd=`, `vs1=`, `vs2=`, `rd=`, `rs1=`, `rs2=` args. Read chosen register numbers from `instruction_data[0][...]['reg']` (vector) and `instruction_data[1][...]['reg']` (scalar), use those in any setup / init / fault-trigger lines emitted. For temp scratch registers (e.g. `la random_mask_0` or `vsetivli`'s discarded result), use `pickPrivScratch(scalar_register_data)` helper from `vector_testgen_common` — avoids framework-reserved registers (`x0`–`x5`) and any operand register randomizer chose.
- **Reserved framework registers** (do not pick or clobber): `x0` (zero), `x1` (ra), `x2` (`sigReg`), `x3` (gp), `x4` (`tempReg`), `x5` (`linkReg`). Framework calls `handleSignaturePointerConflict()` to reroute `sigReg` if randomized operand collides with `x2`, but still avoid these as scratch.

If urge to write literal `vd=8` or `la x2, ...` arise, stop and use helpers above. Same for FP: never type `f5` / `f12` / etc. — request FP registers via FP randomizer / `fp_regs` API.

## What "within legal constraints" means

Randomizer not free `randint(0, 31)`. Knows per-instruction rules, rejects illegal picks **if told constraints**:

- **EMUL alignment** for vector LS: `vd` must be `EMUL`-aligned where `EMUL = EEW/SEW × LMUL`. `randomizeVectorInstructionData` handles — do **not** post-process result with `randint()`.
- **No-overlap rules**: pass `additional_no_overlap=[(opA, opB), ...]` (e.g. widening / narrowing / mask-producing instructions) instead of hand-filtering after.
- **Segment fit**: `nf × EMUL` must not exceed 32. Randomizer enforces; script's only job = skip illegal `(SEW, LMUL, EEW, nf)` combos *before* calling.
- **Reserved registers**: `x0`–`x5` framework-reserved. Randomizer avoids; `pickPrivScratch(scalar_register_data)` also avoids any register randomizer just chose for instruction's operands.

If constraint randomizer doesn't know about found, **teach randomizer** (extend `randomizeVectorInstructionData` / helpers) — do not work around by hardcoding.

## Quick checklist for priv test generators

- Begin each coverpoint with `comment_banner(coverpoint, "comments")` call to add descriptive marker to generated test.
- Include `test_data.add_testcase` call at start of each testcase within coverpoint. Creates appropriate labels and debug strings.
- Where possible, reuse functions and define new helper functions if asm snippet useful in multiple tests.
- Follow formatting rules of rest of asm tests:
  - Labels and comments not indented.
  - Code (instructions and macros) indented 2 spaces.
  - If deviations help readability (most often indenting certain comments), use `INDENT` global at line start (e.g. `f"{INDENT}# comment"`).