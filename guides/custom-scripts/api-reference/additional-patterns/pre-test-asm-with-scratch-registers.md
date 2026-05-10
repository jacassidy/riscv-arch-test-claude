## Pre-test asm with scratch registers


```python
pre_lines = [
    "vsetivli x0, 1, e8, m1, tu, mu",
    "vmv.v.i v0, 1",
    f"vsetvli x{{s0}}, x0, e{sew}, m{lmulflag}, tu, mu",  # {{s0}} → escaped placeholder
]
writeTest(desc, test, data, sew=sew, lmul=lmul, vl="vlmax",
          maskval="zeroes", pre_test_lines=pre_lines,
          pre_test_scratch_regs=1)
```

Use `pre_test_scratch_regs=N` and `{s0}`/`{s1}`/… placeholders for scalar scratch register in `pre_test_lines` or `pre_instruction_lines`. `writeTest` allocate via central `scalar_registers_used` tracker, after `handleSignaturePointerConflict`. **Never write `x{N}` literals or hand-pick "safe" register** — see `GUIDE.md` § Pre-test assembly for why (collide with switched sigReg, cause hang).
