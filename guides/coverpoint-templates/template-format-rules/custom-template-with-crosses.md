## Custom Template (with crosses)


```systemverilog
//////////////////////////////////////////////////////////////////////////////////
    // cp_custom_vexample
    //////////////////////////////////////////////////////////////////////////////////

    std_vec: coverpoint {get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vill") == 0 &
                        get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vstart", "vstart") == 0 &
                        get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vl", "vl") != 0 &
                        ins.trap == 0
                    }
    {
        bins true = {1'b1};
    }

    vtype_lmul_4: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul") {
        bins four = {2};
    }

    vd_aligned_lmul_4: coverpoint ins.current.insn[11:7] {
        wildcard bins divisible_by_4 = {5'b???00};
    }

    cp_custom_vexample_lmul4: cross std_vec, vtype_lmul_4, vd_aligned_lmul_4;

    //// end cp_custom_vexample////////////////////////////////////////////////
```
