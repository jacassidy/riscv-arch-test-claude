# Step 5: Read the Source Assembly and Identify the Coverpoint


Open source `.S` at `tests/rv64i/<Extension>/<filename>.S` (not `work/`). Each test section has comment like:

```asm
# Testcase cp_custom_ffLS_update_vl (vle16ff.v, lmul=2, vl=vlmax, masked)
```

Find section with failing instr address, read full asm for that testcase. Comment names `cp_custom_*` script that generated it.
