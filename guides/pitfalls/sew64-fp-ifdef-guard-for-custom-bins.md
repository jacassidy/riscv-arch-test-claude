# SEW64 FP — ifdef Guard for Custom Bins


SEW=64 FP needs FLEN ≥ 64 (D extension). On systems without D, Vf64 covergroups always show `cp_asm_count` + `std_vec` at 0%. Expected, counts as 100%. Custom bins defined in templates **must** be guarded so they don't show when FLEN < 64. Use `` `ifndef COVER_VFCUSTOM64 `` / `` `else `` / `` `ifdef FLEN64 `` (note: `COVER_VFCUSTOM*` macros still defined as aliases in `header_vector.sv`):

```systemverilog
`ifndef COVER_VFCUSTOM64
    // bins for SEW16/SEW32 (always included)
    my_coverpoint : coverpoint ... { bins ... }
    cp_custom_foo : cross std_vec, my_coverpoint;
`else
    `ifdef FLEN64
    // same bins, only included when FLEN >= 64
    my_coverpoint : coverpoint ... { bins ... }
    cp_custom_foo : cross std_vec, my_coverpoint;
    `endif
`endif
```

Custom bins at 0% in Vf64 report on no-D system → wrap with this. Residual `cp_asm_count`/`std_vec` at 0% acceptable — framework-generated, can't be ifdefed from template.
