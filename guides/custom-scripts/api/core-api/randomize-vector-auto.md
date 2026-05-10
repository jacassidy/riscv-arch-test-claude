# `randomizeVectorInstructionData` — auto-handled (do NOT duplicate)

Function inspects `instruction` string, auto-configures:

- **LS EMUL**: Looks up EEW, sets `size_multiplier = EEW/SEW` on correct operand (vd for loads, vs3 for stores, vs2 for indexed)
- **Segments**: Parses nf, sets `segments` on all vector operands, ensures `nf × EMUL` registers fit
- **Widening/narrowing**: Sets `size_multiplier=2` on widened operands via `getVectorEmulMultipliers`
- **Overlap constraints**: Adds spec-mandated `_top`/`_bottom` overlap rules (widening, narrowing, mask-producing, compress, vext, indexed segments). Use `additional_no_overlap` only for constraints beyond spec (e.g., `['vd', 'v0']`)
- **LS addresses**: Auto-sets `rs1_val_pointer = "vector_ls_random_base"` and `rs2_val` (stride)
- **Whole register LS**: Uses `nfields` as effective LMUL
- **Mask/scalar types**: Sets `reg_type="mask"` or `"scalar"` for mask-producing, reduction, move instructions
