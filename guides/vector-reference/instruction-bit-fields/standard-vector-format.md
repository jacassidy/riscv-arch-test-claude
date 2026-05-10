## Standard Vector Format


```
31    26 25  24   20 19   15 14  12 11    7 6     0
[funct6][vm][  vs2 ][vs1/rs1][funct3][ vd  ][opcode]
```

| Field       | Bits  | Description                   |
| ----------- | ----- | ----------------------------- |
| opcode      | 6:0   | Operation code                |
| vd/rd       | 11:7  | Destination register          |
| funct3      | 14:12 | Operation variant             |
| vs1/rs1/imm | 19:15 | Source 1 / scalar / immediate |
| vs2         | 24:20 | Source 2                      |
| vm          | 25    | 0=masked, 1=unmasked          |
| funct6      | 31:26 | Function code                 |
