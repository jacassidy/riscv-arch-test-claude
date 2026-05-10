# EMUL Formulas and Constraints


```
EMUL = (EEW / SEW) * LMUL

Widening destination:  EMUL_dst = 2 * LMUL  (EEW_dst = 2 * SEW)
Narrowing source:      EMUL_src = 2 * LMUL  (EEW_src = 2 * SEW)
Extension source:      EMUL_src = LMUL / N  (vzext.vfN, vsext.vfN where N=2,4,8)

Constraint: 1/8 <= EMUL <= 8
```

| Operation | LMUL Constraint | Reason                      |
| --------- | --------------- | --------------------------- |
| Widening  | LMUL <= 4       | Dest EMUL = 2\*LMUL <= 8    |
| Narrowing | LMUL <= 4       | Source EMUL = 2\*LMUL <= 8  |
| vzext.vf8 | LMUL >= 1       | Source EMUL = LMUL/8 >= 1/8 |
| vzext.vf4 | LMUL >= 1/2     | Source EMUL = LMUL/4 >= 1/8 |
| vzext.vf2 | LMUL >= 1/4     | Source EMUL = LMUL/2 >= 1/8 |
| Segment N | EMUL\*N <= 8    | Total registers <= 8 groups |

### EMUL \* NFIELDS Constraint

| LMUL | nf (NFIELDS) | EMUL\*NFIELDS | Status   |
| ---- | ------------ | ------------- | -------- |
| 8    | 1 (2)        | 16            | Reserved |
| 4    | 3 (4)        | 16            | Reserved |
| 2    | 7 (8)        | 16            | Reserved |

### VLMAX Formula

```
VLMAX = (VLEN * LMUL) / SEW
// Fractional LMUL: VLMAX = (VLEN * numerator) / (SEW * denominator)
```
