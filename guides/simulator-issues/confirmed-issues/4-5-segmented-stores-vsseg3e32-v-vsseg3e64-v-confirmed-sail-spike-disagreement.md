## 4–5. Segmented stores (`vsseg3e32.v`, `vsseg3e64.v`) — confirmed Sail/Spike disagreement


- **Status**: confirmed-sail-spike-mismatch (NOT coverage blocker — Sail runs fine, Spike disagrees)
- **Date tested**: 2026-04-08
- **Instructions**: `vsseg3e32.v`, `vsseg3e64.v`
- **Affected**: RV32 + RV64, all SEW variants that complete Sail sim
- **Coverage impact**: None. Not in `unsupported_tests`, should generate tests normally. Coverage uses Sail only.

Spike FAILS on every self-checking ELF for both instructions. Sail generates signatures Spike disagrees with, specifically in masked segmented store ops.

| Instruction   | Spike RV64 | Spike RV32 |
| ------------- | ---------- | ---------- |
| `vsseg3e32.v` | 3/3 FAIL   | 3/3 FAIL   |
| `vsseg3e64.v` | 1/1 FAIL   | 1/1 FAIL   |

**Note**: Some SEW variants (Vls8, Vls16 for e32; Vls8–Vls32 for e64) hang during Sail sim due to test-gen register alignment bug. Tests that DO complete Sail sim all fail Spike comparison.

#### Spike Evidence (vsseg3e32.v, Vls32, RV64)

```
RVCP-SUMMARY: TEST FAILED - Test File "vsseg3e32.v.S"
RVCP: Test Info: "test: 63; cp: Vls32_vsseg3e32.v_cg/cp_masking_edges (Test v0 = zeroes)"
RVCP: Bad Value:      0x000000008002bb40
RVCP: Expected Value: 0x000000008f0d885c
```

Sail produced `0x8f0d885c` as expected sig; Spike produced `0x8002bb40`. Mismatch in `cp_masking_edges` — masked store op.

#### Reproduction

```bash
# 1. Comment out vsseg3e32.v, vsseg3e64.v in unsupported_tests
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py Vls --tests vsseg3e32.v vsseg3e64.v
make clean && make vector-tests
CONFIG_FILES="config/spike/spike-rv64-max/test_config.yaml config/spike/spike-rv32-max/test_config.yaml" \
  EXTENSIONS=Vls8,Vls16,Vls32,Vls64 make elfs
./run_tests.py "$(cat config/spike/spike-rv64-max/run_cmd.txt)" work/spike-rv64-max/elfs
./run_tests.py "$(cat config/spike/spike-rv32-max/run_cmd.txt)" work/spike-rv32-max/elfs
# Result: All tests FAIL
# Logs: work/spike-rv64-max/logs/rv64i/Vls32/Vls32-vsseg3e32.v.log
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py --restore Vls
```

---
