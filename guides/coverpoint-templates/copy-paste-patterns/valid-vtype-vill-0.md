## Valid vtype (vill=0)


```systemverilog
    vtype_valid: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vill") {
        bins valid = {1'b0};
    }
```
