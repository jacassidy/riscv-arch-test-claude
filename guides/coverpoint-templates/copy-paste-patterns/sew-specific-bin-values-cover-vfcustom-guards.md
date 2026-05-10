## SEW-Specific Bin Values (COVER_VFCUSTOM guards)


When bins need different values per SEW (e.g., NaN encodings at different FP widths), use
`ifdef COVER_VFCUSTOMxx` guards. VfCustom now merged into Vf (like VxCustom part of Vx),
but `COVER_VFCUSTOM*` macros still defined as aliases in `header_vector.sv`, so existing
templates using them still work. Each generated coverage file (`Vf16_coverage.svh`, etc.)
defines both `COVER_VFxx` and `COVER_VFCUSTOMxx`. Sibling macros auto-`undef`'d by
`generate.py` at top of each file, so only one SEW variant active at compile time. Both
`ifdef`/`endif` chains and `ifdef`/`elsif`/`endif` chains safe.

```systemverilog
    vs2_element0 : coverpoint get_vr_element_zero(ins.hart, ins.issue, ins.current.vs2_val) {
        `ifdef COVER_VFCUSTOM16
            bins val = {64'h0000_0000_0000_7E00}; // half
        `endif
        `ifdef COVER_VFCUSTOM32
            bins val = {64'h0000_0000_7FC0_0000}; // single
        `endif
        `ifdef COVER_VFCUSTOM64
            bins val = {64'h7FF8_0000_0000_0000}; // double
        `endif
    }
```

**Important**: `undef` logic lives in `generate.py` (`_get_sibling_sew_macros`). If new
vector category with SEW variants added, handled automatically. Do NOT manually add
`define`/`undef` in templates — `generate.py` handles this.
