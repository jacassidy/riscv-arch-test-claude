## ins.current Fields


**Instruction bits**: `ins.current.insn[31:0]`

| Bits    | Field         |
| ------- | ------------- |
| [6:0]   | opcode        |
| [11:7]  | rd/vd         |
| [14:12] | funct3        |
| [19:15] | rs1/vs1       |
| [24:20] | rs2/vs2       |
| [25]    | vm (0=masked) |
| [31:25] | funct7        |

**Register values**:

- `ins.current.rd_val`, `ins.current.rd_val_pre`
- `ins.current.rs1_val`, `ins.current.rs2_val`
- `ins.current.fd_val`, `ins.current.fs1_val`, `ins.current.fs2_val`
- `ins.current.vd_val`, `ins.current.vs1_val`, `ins.current.vs2_val`
- `ins.current.v0_val` — mask register

**Vector state**:

- `ins.current.vm` — 1=unmasked, 0=masked
- `ins.current.eSEW` — 0=e8, 1=e16, 2=e32, 3=e64
- `ins.current.mLMUL` — 5=mf8, 6=mf4, 7=mf2, 0=m1, 1=m2, 2=m4, 3=m8
- `ins.current.ta`, `ins.current.ma` — tail/mask agnostic

**Other**:

- `ins.current.imm` — immediate value
- `ins.current.mode` — 0=User, 1=Supervisor, 3=Machine
- `ins.current.mem_addr` — calculated memory address
