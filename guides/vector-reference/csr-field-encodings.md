# CSR Field Encodings


### vtype Fields

| Field | Bits   | Values                            |
| ----- | ------ | --------------------------------- |
| vill  | XLEN-1 | 0=legal, 1=illegal                |
| vma   | 7      | 0=undisturbed, 1=agnostic         |
| vta   | 6      | 0=undisturbed, 1=agnostic         |
| vsew  | 5:3    | 000=e8, 001=e16, 010=e32, 011=e64 |
| vlmul | 2:0    | See LMUL table below              |

### vlmul Encoding

| LMUL | vlmul[2:0] | Decimal | Registers |
| ---- | ---------- | ------- | --------- |
| mf8  | 101        | 5       | 1 (1/8)   |
| mf4  | 110        | 6       | 1 (1/4)   |
| mf2  | 111        | 7       | 1 (1/2)   |
| m1   | 000        | 0       | 1         |
| m2   | 001        | 1       | 2         |
| m4   | 010        | 2       | 4         |
| m8   | 011        | 3       | 8         |

### vsew Encoding

| SEW | vsew[2:0] | Decimal |
| --- | --------- | ------- |
| e8  | 000       | 0       |
| e16 | 001       | 1       |
| e32 | 010       | 2       |
| e64 | 011       | 3       |

### Common CSR Addresses

| CSR     | Address |
| ------- | ------- |
| vtype   | 0xC21   |
| vl      | 0xC20   |
| vstart  | 0x008   |
| fcsr    | 0x003   |
| fflags  | 0x001   |
| frm     | 0x002   |
| mstatus | 0x300   |
| sstatus | 0x100   |
