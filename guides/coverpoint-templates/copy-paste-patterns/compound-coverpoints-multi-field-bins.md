## Compound Coverpoints (multi-field bins)


```systemverilog
    my_compound_cp : {coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul")[2:0],
                      coverpoint ins.current.insn[31:29]} {
        bins combo1 = {3'b011, 3'b001};  // vlmul=8, nf=1
        bins combo2 = {3'b010, 3'b011};  // vlmul=4, nf=3
    }
```
