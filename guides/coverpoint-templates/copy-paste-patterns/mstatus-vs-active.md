## mstatus.vs Active


```systemverilog
    mstatus_vs_active: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "mstatus", "vs") {
        bins active[] = {[1:3]};
    }
```
