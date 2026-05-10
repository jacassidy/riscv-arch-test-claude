## Register Alignment for LMUL


```systemverilog
    vd_aligned_lmul_2: coverpoint ins.current.insn[11:7] { wildcard bins div2 = {5'b????0}; }
    vd_aligned_lmul_4: coverpoint ins.current.insn[11:7] { wildcard bins div4 = {5'b???00}; }
    vd_aligned_lmul_8: coverpoint ins.current.insn[11:7] { wildcard bins div8 = {5'b??000}; }

    // NOT aligned (off-group)
    wildcard ignore_bins divisible_by_4 = {5'b???00};  // use inside a coverpoint
```
