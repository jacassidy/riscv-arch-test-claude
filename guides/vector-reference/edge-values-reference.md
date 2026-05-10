# Edge Values Reference


### vl Edge Values

| Name     | Value                  | Purpose                 |
| -------- | ---------------------- | ----------------------- |
| vl_one   | 1                      | Minimum active elements |
| vl_vlmax | VLMAX                  | Maximum elements        |
| vl_legal | random in [2, VLMAX-1] | General coverage        |

### vstart Edge Values

| Name           | Value   | Purpose                  |
| -------------- | ------- | ------------------------ |
| vstart_one     | 1       | Skip first element       |
| vstart_vlmaxm1 | VLMAX-1 | Only last element active |
| vstart_vlmaxd2 | VLMAX/2 | Half elements skipped    |

### Mask Edge Values

| Name             | Pattern              | Purpose               |
| ---------------- | -------------------- | --------------------- |
| mask_zero        | All 0s               | No active elements    |
| mask_ones        | All 1s               | All elements active   |
| mask_vlmaxm1ones | (VLMAX-1) 1s, then 0 | Last element inactive |
| mask_random      | Random               | General coverage      |
