# FP Edge Values — Half-Precision (16-bit)

| Name       | Hex    | Description         |
| ---------- | ------ | ------------------- |
| pos0       | 0x0000 | +0.0                |
| neg0       | 0x8000 | -0.0                |
| pos1       | 0x3C00 | +1.0                |
| posInf     | 0x7C00 | +Infinity           |
| negInf     | 0xFC00 | -Infinity           |
| qNaN       | 0x7E00 | Quiet NaN           |
| sNaN       | 0x7D01 | Signaling NaN       |
| maxNorm    | 0x7BFF | Largest normalized  |
| minNorm    | 0x0400 | Smallest normalized |
| maxSubnorm | 0x03FF | Largest subnormal   |
| minSubnorm | 0x0001 | Smallest subnormal  |
