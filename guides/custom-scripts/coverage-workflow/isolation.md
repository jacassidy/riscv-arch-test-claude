# Isolation


`tools/isolate_coverpoint.py` (this repo):

- Reads canonical backup from `working-testplans/duplicates/<Category>-save.csv`
- Strips rows w/o `x` in target column, strips other `cp_custom_*` columns
- Writes to `testplans/`, deletes other vector testplans, updates Makefile EXTENSIONS
- **Always restore** before isolating different coverpoint

### Isolate by coverpoint

```bash
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py Vls cp_custom_maskLS
```

### Isolate by instruction (test) name

```bash
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py Vls --tests vlseg3e32.v vsseg3e32.v
```

Keeps only named rows, all columns intact. Use when need run specific instructions (e.g. verify suspected Sail bugs) without regen entire suite.

**IMPORTANT: Always isolate before run `make vector-tests`.** No isolation = `make vector-tests` regenerates ALL vector tests across all extensions, very slow. Even quick verification, isolate first.

Manual EXTENSIONS if needed: `Vf16,Vf32,Vf64` (VfCustom now part of Vf) or `Vls8,Vls16,Vls32,Vls64` (VlsCustom now merged into Vls)
