# Global Helper Functions


### Sampling Constants

```systemverilog
`SAMPLE_BEFORE   // (1) state before instruction
`SAMPLE_AFTER    // (0) state after instruction
```

### CSR Access

```systemverilog
get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vill")    // vill bit
get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul")   // LMUL field
get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vsew")    // SEW field
get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vl", "vl")         // vector length
get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vstart", "vstart") // vstart
get_csr_val(ins.hart, ins.issue, `SAMPLE_AFTER,  "fcsr", "fflags")   // FP flags after
get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "fcsr", "frm")      // rounding mode
```

**Note**: `fsflagsi` writes CSR 001 (fflags) but NOT CSR 003 (fcsr). Use `get_csr_val("fcsr", "fflags")` carefully after `fsflagsi` — may read stale value. See `guides/pitfalls.md` § "RVVI fsflagsi CSR Alias Bug".

### Register Number Conversion

```systemverilog
get_vr_num("v1")     // returns 1
get_gpr_num("x1")    // returns 1  (also handles ABI names like "ra")
get_fpr_num("f1")    // returns 1
```

### Vector Helpers

```systemverilog
get_vr_element_zero(ins.hart, ins.issue, ins.current.vs2_val)  // element 0 at current SEW
get_vtype_vlmax(ins.hart, ins.issue, `SAMPLE_BEFORE)           // VLMAX value
vs_edges_check(ins.hart, ins.issue, val, sew_multiplier)       // edge case check
```

### Register Lookup

```systemverilog
ins.get_gpr_reg(ins.current.rd)   // gpr_name_t
ins.get_fpr_reg(ins.current.fs1)  // fpr_name_t
ins.get_vr_reg(ins.current.vs1)   // vr_name_t
ins.get_gpr_val(ins.hart, ins.issue, "x1", `SAMPLE_BEFORE)
ins.get_vr_val(ins.hart, ins.issue, "v1", `SAMPLE_BEFORE)
```
