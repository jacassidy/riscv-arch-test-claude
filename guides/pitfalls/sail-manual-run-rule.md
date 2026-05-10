# Sail manual run rule


Always use `timeout Xs` AND `--inst-limit N` when running `sail_riscv_sim` manually. Trapping tests loop forever; trace file gets deleted on failure. Keep inst-limit small (e.g. 500) for short readable trace before trap loop.

```
timeout 2s sail_riscv_sim --config sail.json --trace-instr --trace-exception --trace-output /tmp/trace.txt --inst-limit 500 test.elf
```

For isolated coverpoint debug loops: `timeout 120s make coverage` so hangs cut quickly + stuck test name visible.
