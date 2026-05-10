## Widening Overlap Detection


```systemverilog
    // vd[4:1] == vs2[4:1] (LMUL=1, 2-register widened group)
    vs2_vd_overlap_lmul1: coverpoint (ins.current.insn[24:21] == ins.current.insn[11:8]) {
        bins overlapping = {1'b1};
    }
    // vd[4:2] == vs2[4:2] (LMUL=2, 4-register widened group)
    vs2_vd_overlap_lmul2: coverpoint (ins.current.insn[24:22] == ins.current.insn[11:9]) {
        bins overlapping = {1'b1};
    }
    // vd[4:3] == vs2[4:3] (LMUL=4, 8-register widened group)
    vs2_vd_overlap_lmul4: coverpoint (ins.current.insn[24:23] == ins.current.insn[11:10]) {
        bins overlapping = {1'b1};
    }
```
