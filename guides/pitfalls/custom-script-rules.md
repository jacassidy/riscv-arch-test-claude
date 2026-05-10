# Custom Script Rules


- `@register("cp_custom_...")` must match **CSV column name**, not definition name
- Function signature: `make(test, sew)` — `test` = instruction mnemonic
- VVM unary ops (vfsqrt, vfrsqrt7, vfrec7, vfclass): source data = **vs2**, use `vs2_val_pointer`
- **NEVER use `vs2_val=integer`** — sign-extends from XLEN, truncates on RV32. Always `vs2_val_pointer=label`
- Wrap `randomizeVectorInstructionData()` in `try/except ValueError: pass` for segmented/whole-register LS instructions (overlap constraints unsolvable at high LMUL/NF)
- Always add `if sew > common.flen: return` guard for FP scripts (V spec §3.4: SEW ≤ FLEN for FP)
- `.wf` scalar presets: SEW-sized values for `fs1_val`, not widened-width (scalar load follows SEW)
- **LS register assignment + nf×EMUL guard** — see `guides/custom-scripts/GUIDE.md` "Important: Register Assignment for LS Instructions" + nf×EMUL guard pattern
- **Never write `x{N}` literal into `pre_test_lines` / `pre_instruction_lines`.** Use `pre_test_scratch_regs=N` + `{s0}`/`{s1}` placeholders. See `guides/custom-scripts/GUIDE.md` § Pre-test assembly. (Why: `handleSignaturePointerConflict` can reassign `sigReg` to *any* register including x31 after script runs, silently colliding with hand-picked temps and causing sail hang.)
