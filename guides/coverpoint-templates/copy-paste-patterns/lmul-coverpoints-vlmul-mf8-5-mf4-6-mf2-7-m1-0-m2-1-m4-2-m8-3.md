## LMUL Coverpoints (vlmul: mf8=5, mf4=6, mf2=7, m1=0, m2=1, m4=2, m8=3)


```systemverilog
    // Single LMUL
    vtype_lmul_1: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul") {
        bins one = {0};
    }
    vtype_lmul_2: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul") {
        bins two = {1};
    }
    vtype_lmul_4: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul") {
        bins four = {2};
    }
    vtype_lmul_8: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul") {
        bins eight = {3};
    }

    // All integer LMULs (no guards needed — always supported)
    vtype_all_lmulge1: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul") {
        bins one = {0}; bins two = {1}; bins four = {2}; bins eight = {3};
    }

    // All LMULs including fractional (REQUIRED when covering fractional — DUT-optional)
    // NOTE: For FP instructions (SEW >= 16), fractional LMULs must satisfy LMUL >= SEW/ELEN.
    // Gate fractional bins with COVER_VFCUSTOM* defines (aliases defined in header_vector.sv,
    // still valid after VfCustom merge into Vf): mf8 never valid for FP,
    // mf4 only at SEW=16 (COVER_VFCUSTOM16), mf2 not at SEW=64 (ifndef COVER_VFCUSTOM64).
    vtype_all_lmul: coverpoint get_csr_val(ins.hart, ins.issue, `SAMPLE_BEFORE, "vtype", "vlmul") {
        `ifdef LMULf8_SUPPORTED
            bins eighth  = {5};
        `endif
        `ifdef LMULf4_SUPPORTED
            bins fourth = {6};
        `endif
        `ifdef LMULf2_SUPPORTED
            bins half   = {7};
        `endif
        bins one    = {0};
        bins two    = {1};
        bins four   = {2};
        bins eight  = {3};
    }
```
