## 1–3. Segmented loads — resolved (Spike validates Sail)


- **Status**: resolved
- **Date tested**: 2026-04-08
- **Instructions**: `vlseg3e32.v`, `vlseg3e32ff.v`, `vlseg4e32.v`

All 24 Spike tests PASS on both RV32 and RV64 across all SEW variants (Vls8–Vls64). Sail and Spike agree — not simulator bugs. Removed from `unsupported_tests`.

#### Reproduction

```bash
# 1. Comment out vlseg3e32.v, vlseg3e32ff.v, vlseg4e32.v in unsupported_tests
# 2. Isolate and build:
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py Vls --tests vlseg3e32.v vlseg3e32ff.v vlseg4e32.v
make clean && make vector-tests
# 3. Build spike ELFs and run:
CONFIG_FILES="config/spike/spike-rv64-max/test_config.yaml config/spike/spike-rv32-max/test_config.yaml" \
  EXTENSIONS=Vls8,Vls16,Vls32,Vls64 make elfs
./run_tests.py "$(cat config/spike/spike-rv64-max/run_cmd.txt)" work/spike-rv64-max/elfs
./run_tests.py "$(cat config/spike/spike-rv32-max/run_cmd.txt)" work/spike-rv32-max/elfs
# Result: All 12 RV64 + 12 RV32 = 24 tests PASS
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py --restore Vls
```

---
