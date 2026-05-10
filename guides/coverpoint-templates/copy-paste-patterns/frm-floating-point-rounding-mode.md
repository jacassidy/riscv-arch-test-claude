## FRM (Floating-Point Rounding Mode)


```systemverilog
    frm_valid: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "fcsr", "frm") {
        bins rne = {3'b000};
        bins rtz = {3'b001};
        bins rdn = {3'b010};
        bins rup = {3'b011};
        bins rmm = {3'b100};
    }
    frm_invalid: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "fcsr", "frm") {
        bins reserved_5 = {3'b101};
        bins reserved_6 = {3'b110};
        bins reserved_7 = {3'b111};
    }
```
