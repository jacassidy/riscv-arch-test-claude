# 7. RV32 ei64 — Analysis + RV64 Comparison

Encoding `0x0FC9FB87` decodes as:

- `opcode[6:0] = 0000111` (LOAD-FP / vector load)
- `funct3[14:12] = 111` (EEW=64, indexed load)
- `funct6[31:26] = 000011` (unordered indexed)
- `vm[25] = 1` (unmasked)
- `vd = v23, rs1 = x19, vs2 = v28`

= `vloxei64.v v23, (x19), v28` — valid RISC-V V instruction. Per V spec (Section 7.3), indexed vector loads valid when implementation supports index EEW (`elen_exp=6` in `sail.json` → ELEN=64). **Sail wrongly decodes as `illegal` on RV32.**

Same class succeeds on RV64:

```bash
timeout 10s sail_riscv_sim --trace-all \
  --trace-output /tmp/vloxei64_rv64_trace.log \
  --config config/sail/sail-rv64-max/sail.json \
  work/sail-rv64-max/build/rv64i/VlsCustom16/VlsCustom16-vloxei64.v.sig.elf
# Exit code 0 — SUCCESS
```

RV64 trace shows correct decode:

```
[187] [M]: 0x00000000800002DA (0x0FCA7B87) vloxei64.v v23, (x20), v28
```
