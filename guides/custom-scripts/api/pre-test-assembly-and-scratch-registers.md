# Pre-test assembly and scratch registers


> **Reminder:** registers **never** hardcoded — see `guides/register-allocation.md`. Mechanism below (`pre_test_scratch_regs` + `{s0}` / `{s1}` placeholders) is *only* correct way to obtain scratch X-registers inside `pre_test_lines` / `pre_instruction_lines`. Likewise, vector / scalar operand registers come from `randomizeVectorInstructionData(...)` (read back from `instruction_data`); never write `vd=N`, `vs1=N`, `rs1=N`, or literal `x{N}` / `v{N}` / `f{N}` in emitted asm.


If custom script needs scratch scalar registers in `pre_test_lines` or `pre_instruction_lines`, **must** request via `pre_test_scratch_regs=N` and reference as `{s0}`, `{s1}`, … inside f-string templates (escape braces: `f"... x{{s0}} ..."`). `writeTest` allocates `N` unique X-registers via centralized `scalar_registers_used` tracker, substitutes into every line containing placeholder.

**Why matters**: `writeTest` calls `handleSignaturePointerConflict` after custom script built its `pre_test_lines` strings. If test's rs1/rs2 conflict with default `sigReg` (x2), resolver picks new sigReg at random — can be x31. Script that hand-picks "safe" temp by scanning `range(31, 0, -1)` lands on x31, silently clobbers signature pointer; test stores signature to tiny VLMAX value (e.g. `0x10`), faults, hangs in trap loop (no trap handler installed). Bug existed in `cp_custom_ffLS.py`, stalled coverage runs.

**Right** (centralized allocation):

```python
pre_lines = [
    "vsetivli x0, 1, e8, m1, tu, mu",
    "vmv.v.i v0, 2",
    f"vsetvli x{{s0}}, x0, e{sew}, m{lmulflag}, tu, mu",
]
writeTest(desc, test, data, sew=sew, lmul=lmul, vl="vlmax",
          maskval="zeroes", pre_test_lines=pre_lines,
          pre_test_scratch_regs=1)
```

**Wrong** (hand-picked, races with sigReg switch):

```python
avoid = {rs1, rs2, common.sigReg, 0}
temp = next(r for r in range(31, 0, -1) if r not in avoid)  # may pick x31!
pre_lines = [f"vsetvli x{temp}, x0, e{sew}, m{lmulflag}, tu, mu"]
writeTest(..., pre_test_lines=pre_lines)
```

### Counters

Call after each `writeTest`: `incrementBasetestCount()` + `vsAddressCount()` (base suite) or `incrementLengthtestCount()` + `vsAddressCount("length")` (length suite).
