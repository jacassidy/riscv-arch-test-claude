# Register Allocation in Test Generators

> **Rule:** Test generators must **never** hardcode register numbers (e.g. `vd=8`, `rs1=7`, `la x2, ...`). Registers should be **randomized** unless a specific architectural register is required (e.g. `a0` for an ABI-specified helper argument, `x0` to read zero, or `x2` as the framework signature pointer). Hardcoded registers defeat the purpose of generated tests — they reduce the search space for randomization to find bugs and create false positives where the same registers always pass.

This applies to **every** generator: scalar priv (`generators/testgen/src/testgen/priv/extensions/*.py`), vector priv (`generators/testgen/scripts/vector-testgen-priv.py` + `generators/testgen/scripts/priv/cp_*.py`), and unprivileged generators alike.

## How to do it correctly

- **Scalar priv flow** (`Sm.py`, `SmF.py`, `U.py`, `ExceptionsVf.py`, etc.):
  use `test_data.int_regs.get_registers(n)` / `get_registers(1)` to pull `n` randomly chosen integer registers, and the analogous `fp_regs` API for floats. Never write `x5`, `x6`, ... directly in emitted assembly.
- **Vector priv flow** (`vector-testgen-priv.py`, `priv/cp_*.py`):
  call `randomizeVectorInstructionData(instruction, sew, count, ...)` **without** passing `vd=`, `vs1=`, `vs2=`, `rd=`, `rs1=`, `rs2=` arguments. Read back the chosen register numbers from `instruction_data[0][...]['reg']` (vector) and `instruction_data[1][...]['reg']` (scalar) and use those in any setup / init / fault-trigger lines you emit. For temporary scratch registers (e.g. for `la random_mask_0` or `vsetivli`'s discarded result), use the `pickPrivScratch(scalar_register_data)` helper from `vector_testgen_common`, which avoids framework-reserved registers (`x0`–`x5`) and any operand register the randomizer chose.
- **Reserved framework registers** (do not pick or clobber): `x0` (zero), `x1` (ra), `x2` (`sigReg`), `x3` (gp), `x4` (`tempReg`), `x5` (`linkReg`). The framework calls `handleSignaturePointerConflict()` to reroute `sigReg` if a randomized operand collides with `x2`, but you should still avoid using these as scratch.

If you ever feel the need to write a literal `vd=8` or `la x2, ...`, stop and use the helpers above instead.

## Quick checklist for priv test generators

- Begin each coverpoint with a call to `comment_banner(coverpoint, "comments")` to add a descriptive marker to the generated test.
- Include a call to `test_data.add_testcase` at the beginning of each testcase within a coverpoint. This creates the appropriate labels and debug strings.
- To the extent possible, reuse functions and define new helper functions if a snippet of assembly seems like it will be useful in multiple tests.
- Follow the formatting rules of the rest of the assembly tests:
  - Labels and comments are not indented.
  - Code (instructions and macros) is indented by 2 spaces.
  - If deviations from this help the readability of a test (most often indenting certain comments), use the `INDENT` global at the beginning of the line (e.g. `f"{INDENT}# comment"`).
