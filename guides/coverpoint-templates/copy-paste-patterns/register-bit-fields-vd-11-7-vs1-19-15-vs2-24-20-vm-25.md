## Register Bit Fields (vd[11:7], vs1[19:15], vs2[24:20], vm[25])


```systemverilog
    vd_v0:        coverpoint ins.current.insn[11:7] { bins zero   = {5'b00000}; }
    vd_not_v0:    coverpoint ins.current.insn[11:7] { bins not_v0[] = {[1:31]}; }
    vs2_v0:       coverpoint ins.current.insn[24:20] { bins v0    = {5'b00000}; }
    mask_enabled: coverpoint ins.current.insn[25]   { bins masked = {1'b0}; }
```
