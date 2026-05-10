## EMUL Computation for Load/Store (3-field compound)


Width field (bits 14:12) encodes EEW: 000=8, 101=16, 110=32, 111=64.

```systemverilog
    emul_8_ls : {coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul")[2:0],
                 coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vsew")[1:0],
                 coverpoint ins.current.insn[14:12]} {
        bins m8_sew8_eew8  = {3'b011, 2'b00, 3'b000};  // EEW=SEW, LMUL=8
        bins m4_sew8_eew16 = {3'b010, 2'b00, 3'b101};  // EEW=2*SEW, LMUL=4
    }
```
