# Step 4: Add Register Trace if Needed


```bash
timeout 30 /opt/riscv/bin/sail_riscv_sim \
  --inst-limit 500 \
  --trace-instr --trace-reg \
  --test-signature /dev/null \
  <path-to-elf>
```

- `--trace-reg` show reg reads/writes (verbose, smaller inst-limit)
- Useful for vtype/vl state: grep `vtype` or `vl` in output
