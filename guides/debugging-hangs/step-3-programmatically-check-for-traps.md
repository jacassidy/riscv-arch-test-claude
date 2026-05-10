# Step 3: Programmatically Check for Traps


Before reading full trace, grep `mcause` writes to detect traps instantly:

```bash
timeout 120 /opt/riscv/bin/sail_riscv_sim \
  --inst-limit 500000 \
  --trace-instr --trace-reg \
  --test-signature /dev/null \
  <path-to-elf> 2>&1 | grep -B5 "mcause"
```

`-B5` context show faulting instr + test label. See "Common Hang Causes" below for `mcause` meanings (2 = illegal instr, most common).
