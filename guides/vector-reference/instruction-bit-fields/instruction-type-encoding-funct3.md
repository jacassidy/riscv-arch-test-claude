## Instruction Type Encoding (funct3)


| funct3 | Type  | Source 2 | Source 1                       |
| ------ | ----- | -------- | ------------------------------ |
| 000    | OPIVV | vector   | vector                         |
| 001    | OPFVV | vector   | vector (FP)                    |
| 010    | OPMVV | vector   | vector (mask/reduction)        |
| 011    | OPIVI | vector   | immediate                      |
| 100    | OPIVX | vector   | scalar (x reg)                 |
| 101    | OPFVF | vector   | scalar (f reg)                 |
| 110    | OPMVX | vector   | scalar (x reg, mask/reduction) |
| 111    | OPCFG | -        | config instructions            |
