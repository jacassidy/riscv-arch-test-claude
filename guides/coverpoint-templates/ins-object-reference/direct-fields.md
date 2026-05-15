## Direct Fields


| Field         | Type   | Description              |
| ------------- | ------ | ------------------------ |
| `ins.trap`    | bit    | 1 if instruction trapped |
| `ins.hart`    | int    | Hart ID                  |
| `ins.issue`   | int    | Issue number             |
| `ins.ins_str` | string | Instruction mnemonic     |


## Vector helpers

| Method | Returns | Notes |
|--------|---------|-------|
| `ins.get_vr_reg(n)` | int | Extracts vreg from operand n; do NOT index `ins.rs`/`ins.rd` directly for vector ops |

## Fractional LMUL vlmul encoding

vlmul field is 3-bit two's-complement. Fractional values: `0b101`=1/8, `0b110`=1/4, `0b111`=1/2. Template comparisons against raw vlmul must use these encoded values, not decimal fractions.
