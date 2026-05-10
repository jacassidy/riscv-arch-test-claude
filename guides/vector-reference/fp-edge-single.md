# FP Edge Values — Single-Precision (32-bit)

| Name       | Hex        | Description         |
| ---------- | ---------- | ------------------- |
| pos0       | 0x00000000 | +0.0                |
| neg0       | 0x80000000 | -0.0                |
| pos1       | 0x3F800000 | +1.0                |
| posInf     | 0x7F800000 | +Infinity           |
| negInf     | 0xFF800000 | -Infinity           |
| qNaN       | 0x7FC00000 | Quiet NaN           |
| sNaN       | 0x7F800001 | Signaling NaN       |
| maxNorm    | 0x7F7FFFFF | Largest normalized  |
| minNorm    | 0x00800000 | Smallest normalized |
| maxSubnorm | 0x007FFFFF | Largest subnormal   |
| minSubnorm | 0x00000001 | Smallest subnormal  |
