## Segment Load/Store Format


```
31  29 28 27 26 25  24   20 19   15 14  12 11    7 6     0
[ nf ][mew][mop][vm][lumop][  rs1 ][width][ vd  ][opcode]
```

| Field | Bits  | Description                                           |
| ----- | ----- | ----------------------------------------------------- |
| nf    | 31:29 | NFIELDS-1 (0=1 segment, 7=8 segments)                 |
| mop   | 27:26 | 00=unit, 01=indexed-unord, 10=strided, 11=indexed-ord |
| vm    | 25    | Mask (0=masked, 1=unmasked)                           |
| lumop | 24:20 | rs2 for strided/indexed                               |
| width | 14:12 | EEW: 000=8, 101=16, 110=32, 111=64                    |
| vd    | 11:7  | Destination vector register                           |
