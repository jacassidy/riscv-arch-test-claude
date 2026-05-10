# Step 6: Diagnose from the Assembly First


Understand problem from asm before reading Python. Asm shows exact instrs + order. Check:

- Vector reg misaligned for current LMUL? (e.g. `vid.v v1` with LMUL=2)
- vtype valid after most recent `vsetvli`?
- Failing instr part of test or scaffolding (mask setup, operand loads)?

If issue in scaffolding (mask preamble, reg loads), fix likely belong in `vector_testgen_common.py`. If in test instr itself, fix belong in `cp_custom_*.py` script named in comment.

Read `vector_testgen_common.py` only after understanding asm-level problem + knowing which function to target.
