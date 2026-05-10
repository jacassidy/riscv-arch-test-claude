## SEW64 FP — Excluding Custom Bins


SEW=64 FP instructions require FLEN ≥ 64 (D extension). Systems without D extension cannot
execute SEW=64 FP instructions, so the covergroup shell (`cp_asm_count`, `std_vec`) will
always be 0% — this is **expected and acceptable**. However, custom bins in templates must
be excluded so they don't create unfillable coverage holes. Use `ifndef COVER_VFCUSTOM64`
(alias still valid after VfCustom→Vf merge) / `else` / `ifdef FLEN64`:

```systemverilog
`ifndef COVER_VFCUSTOM64
    // SEW16/SEW32 — always include
    my_cp : coverpoint (...) { bins target = {1}; }
    cp_custom_foo : cross std_vec, my_cp;
`else
    `ifdef FLEN64
    // SEW64 — only when FLEN >= 64 (D extension)
    my_cp : coverpoint (...) { bins target = {1}; }
    cp_custom_foo : cross std_vec, my_cp;
    `endif
`endif
```

When reviewing coverage and Vf64 shows custom bins at 0% on a system without D
extension, wrap them with this pattern. The residual `cp_asm_count`/`std_vec` at 0% is
fine — they are framework-generated and cannot be guarded from the template.
