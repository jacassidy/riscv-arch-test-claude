# FP Edge Values — Double-Precision (64-bit)

| Name       | Hex                | Description         |
| ---------- | ------------------ | ------------------- |
| pos0       | 0x0000000000000000 | +0.0                |
| neg0       | 0x8000000000000000 | -0.0                |
| pos1       | 0x3FF0000000000000 | +1.0                |
| posInf     | 0x7FF0000000000000 | +Infinity           |
| negInf     | 0xFFF0000000000000 | -Infinity           |
| qNaN       | 0x7FF8000000000000 | Quiet NaN           |
| sNaN       | 0x7FF0000000000001 | Signaling NaN       |
| maxNorm    | 0x7FEFFFFFFFFFFFFF | Largest normalized  |
| minNorm    | 0x0010000000000000 | Smallest normalized |
| maxSubnorm | 0x000FFFFFFFFFFFFF | Largest subnormal   |
| minSubnorm | 0x0000000000000001 | Smallest subnormal  |
