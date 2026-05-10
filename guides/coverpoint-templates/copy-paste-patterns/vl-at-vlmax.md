## VL at VLMAX


```systemverilog
    vl_max: coverpoint (get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vl", "vl")
                        == get_vtype_vlmax(ins.hart, ins.issue, `SAMPLE_BEFORE)) {
        bins target = {1'b1};
    }
```
