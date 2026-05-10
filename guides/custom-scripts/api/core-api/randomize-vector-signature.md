# `randomizeVectorInstructionData(instruction, sew, test_count, suite="base", lmul=1, additional_no_overlap=None, **preset_variables)`

Returns `[vector_register_data, scalar_register_data, floating_point_register_data, imm_val]`.

**Preset kwargs**: `vd=N`, `vs1=N`, `vs2=N`, `vs3=N`, `rs1=N`, `rs2=N`, `fd=N`, `fs1=N`, `rs1_val=V`, `rs2_val=V`, `fs1_val=V`, `vs1_val_pointer=S`, `vs2_val_pointer=S`, `vd_val_pointer=S`, `vs3_val_pointer=S`, `imm=V`

**`additional_no_overlap`**: e.g. `[['vs1', 'v0'], ['vs2', 'v0'], ['vd', 'v0']]`

See sibling shards: `randomize-vector-auto.md`, `randomize-vector-nf-emul-guard.md`.
