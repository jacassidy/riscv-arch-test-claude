# 7. RV32 ei64 — Reproduction

```bash
# Config: sail-rv32-max with V extension "Full", elen_exp=6 (ELEN=64), vlen_exp=10 (VLEN=1024)
# Required: MAXINDEXEEW=64 in config/sail/sail-rv32-max/rvtest_config.h

# 1. Build the test
make clean && make vector-tests
# 2. Run Sail with trace (will hang — use 10s timeout)
timeout 10s sail_riscv_sim --trace-all \
  --trace-output /tmp/vloxei64_rv32_trace.log \
  --config config/sail/sail-rv32-max/sail.json \
  work/sail-rv32-max/build/rv32i/VlsCustom16/VlsCustom16-vloxei64.v.sig.elf
# Exit code 124 (timeout) — Sail hangs in infinite trap loop
```
