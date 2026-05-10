# Step 2: Run with Instruction Trace and Limit


```bash
timeout 30 /opt/riscv/bin/sail_riscv_sim \
  --inst-limit 50000 \
  --trace-instr \
  --test-signature /dev/null \
  <path-to-elf>
```

- `--inst-limit 50000` blocks infinite loops (raise if needed)
- `--trace-instr` print every executed instr w/ address + disasm
- `--test-signature /dev/null` required (sail expects)
- `timeout 30` safety net

Last lines show where hang occur. Look for:

- `illegal 0x...` — illegal instr causing trap loop
- Repeating address sequence — infinite loop in trap handler
- Specific instr sail can't complete
