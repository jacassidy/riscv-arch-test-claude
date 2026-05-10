## `writeTest(description, instruction, instruction_data, sew=None, lmul=1, vl=1, vstart=0, maskval=None, vxrm=None, frm=None, vxsat=None, vta=0, vma=0, pre_test_lines=None, pre_instruction_lines=None, pre_test_scratch_regs=0)`


Mask values: `"ones"`, `"zeroes"`, `"vlmaxm1_ones"`, `"vlmaxd2p1_ones"`, `"cp_mask_random"`, `"random_mask_0"`/`1`/`2`, or `None`

`pre_test_lines` / `pre_instruction_lines` — lists of asm lines emitted before testcase label / before test instruction. See **Pre-test assembly and scratch registers** below — never put hand-picked `x{N}` literals in these lists.
