# Register Allocation in Test Generators

> **Hard rule — no exceptions:** Test generators must **never** hardcode register numbers. This applies to **every** register class — vector (`v0`–`v31`), scalar/integer (`x0`–`x31`), and floating-point (`f0`–`f31`) — and to **every** position the register can appear: `vd=`, `vs1=`, `vs2=`, `rd=`, `rs1=`, `rs2=` arguments to randomizer calls; literal `x{N}` / `v{N}` / `f{N}` in f-string assembly templates; pre-test scratch picks; trap-handler setup; signature stores; the lot. **Always generate the register through the framework's randomizer, within the instruction's legal constraints** (EMUL alignment, no-overlap rules, segment `nf × EMUL` fit, framework-reserved set `x0`–`x5`). Hardcoded registers shrink the search space, hide real bugs behind always-passing register choices, and produce false-positive coverage. Reducing test diversity to a single register tuple is exactly what these generators exist to prevent.
>
> The only literals that may appear in emitted asm are **architecturally required** ABI registers — `a0` when the calling convention demands it, `x0` when you specifically need the zero register, `x2`/`common.sigReg` as the framework signature pointer — and even these should come from named constants (`common.sigReg`, `common.tempReg`, `common.linkReg`, …), never bare integers. Anything else is a bug.

This applies to **every** generator: scalar priv (`generators/testgen/src/testgen/priv/extensions/*.py`), vector priv (`generators/testgen/scripts/vector-testgen-priv.py` + `generators/testgen/scripts/priv/cp_*.py`), and unprivileged generators alike.

## How to do it correctly

- **Scalar priv flow** (`Sm.py`, `SmF.py`, `U.py`, `ExceptionsVf.py`, etc.):
  use `test_data.int_regs.get_registers(n)` / `get_registers(1)` to pull `n` randomly chosen integer registers, and the analogous `fp_regs` API for floats. Never write `x5`, `x6`, ... directly in emitted assembly.
- **Vector priv flow** (`vector-testgen-priv.py`, `priv/cp_*.py`):
  call `randomizeVectorInstructionData(instruction, sew, count, ...)` **without** passing `vd=`, `vs1=`, `vs2=`, `rd=`, `rs1=`, `rs2=` arguments. Read back the chosen register numbers from `instruction_data[0][...]['reg']` (vector) and `instruction_data[1][...]['reg']` (scalar) and use those in any setup / init / fault-trigger lines you emit. For temporary scratch registers (e.g. for `la random_mask_0` or `vsetivli`'s discarded result), use the `pickPrivScratch(scalar_register_data)` helper from `vector_testgen_common`, which avoids framework-reserved registers (`x0`–`x5`) and any operand register the randomizer chose.
- **Reserved framework registers** (do not pick or clobber): `x0` (zero), `x1` (ra), `x2` (`sigReg`), `x3` (gp), `x4` (`tempReg`), `x5` (`linkReg`). The framework calls `handleSignaturePointerConflict()` to reroute `sigReg` if a randomized operand collides with `x2`, but you should still avoid using these as scratch.

If you ever feel the need to write a literal `vd=8` or `la x2, ...`, stop and use the helpers above instead. The same applies to FP: never type `f5` / `f12` / etc. — request FP registers through the FP randomizer / `fp_regs` API.

## What "within legal constraints" means

The randomizer is not a free `randint(0, 31)`. It already understands the per-instruction rules and will reject illegal picks **as long as you let it know the constraints**:

- **EMUL alignment** for vector LS: `vd` must be `EMUL`-aligned where `EMUL = EEW/SEW × LMUL`. `randomizeVectorInstructionData` handles this — do **not** post-process the result with `randint()`.
- **No-overlap rules**: pass `additional_no_overlap=[(opA, opB), ...]` (e.g. widening / narrowing / mask-producing instructions) instead of hand-filtering after the fact.
- **Segment fit**: `nf × EMUL` must not exceed 32. The randomizer enforces this; your script's only job is to skip illegal `(SEW, LMUL, EEW, nf)` combinations *before* calling it.
- **Reserved registers**: `x0`–`x5` are framework-reserved. The randomizer avoids them; `pickPrivScratch(scalar_register_data)` also avoids any register the randomizer just chose for the instruction's operands.

If you discover a constraint the randomizer doesn't know about, **teach the randomizer** (extend `randomizeVectorInstructionData` / its helpers) — do not work around it by hardcoding.

## Quick checklist for priv test generators

- Begin each coverpoint with a call to `comment_banner(coverpoint, "comments")` to add a descriptive marker to the generated test.
- Include a call to `test_data.add_testcase` at the beginning of each testcase within a coverpoint. This creates the appropriate labels and debug strings.
- To the extent possible, reuse functions and define new helper functions if a snippet of assembly seems like it will be useful in multiple tests.
- Follow the formatting rules of the rest of the assembly tests:
  - Labels and comments are not indented.
  - Code (instructions and macros) is indented by 2 spaces.
  - If deviations from this help the readability of a test (most often indenting certain comments), use the `INDENT` global at the beginning of the line (e.g. `f"{INDENT}# comment"`).
