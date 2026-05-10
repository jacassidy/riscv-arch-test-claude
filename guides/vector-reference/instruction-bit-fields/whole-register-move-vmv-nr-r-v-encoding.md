## Whole Register Move (vmv<nr>r.v) Encoding


| Instruction | simm[4:0] | NREG | Alignment Requirement  |
| ----------- | --------- | ---- | ---------------------- |
| vmv1r.v     | 00000 (0) | 1    | None                   |
| vmv2r.v     | 00001 (1) | 2    | vd, vs2 divisible by 2 |
| vmv4r.v     | 00011 (3) | 4    | vd, vs2 divisible by 4 |
| vmv8r.v     | 00111 (7) | 8    | vd, vs2 divisible by 8 |
