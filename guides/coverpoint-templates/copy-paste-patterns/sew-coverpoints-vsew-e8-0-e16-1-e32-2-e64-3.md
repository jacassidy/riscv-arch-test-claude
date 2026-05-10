## SEW Coverpoints (vsew: e8=0, e16=1, e32=2, e64=3)


```systemverilog
    // Single SEW
    vtype_sew_8:  coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vsew") { bins e8  = {0}; }
    vtype_sew_16: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vsew") { bins e16 = {1}; }
    vtype_sew_32: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vsew") { bins e32 = {2}; }
    vtype_sew_64: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vsew") { bins e64 = {3}; }

    // All SEW values (REQUIRED when covering all SEW — guard fractional support)
    vtype_all_sew: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vsew") {
        `ifdef SEW8_SUPPORTED
            bins e8  = {0};
        `endif
        `ifdef SEW16_SUPPORTED
            bins e16 = {1};
        `endif
        `ifdef SEW32_SUPPORTED
            bins e32 = {2};
        `endif
        `ifdef SEW64_SUPPORTED
            bins e64 = {3};
        `endif
    }
```
