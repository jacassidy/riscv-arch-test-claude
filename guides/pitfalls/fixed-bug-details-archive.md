# Fixed bug details (archive)


### vmv.v.i v0 Before vsetvli

`writeTest()` previously emitted `vmv.v.i v0, 0` (mask init) before `prepBaseV()` which calls `vsetvli`. After reset, `vtype.vill=1`, so bare `vmv.v.i` had undefined behavior — sail hung. Fixed in `vector_testgen_common.py`: bare `vmv.v.i v0, 0` cases (`"zeroes"` + default masked-instruction init) now emit after `prepBaseV`. Mask types with own `vsetvli` (`"ones"`, `"vlmaxm1_ones"`, etc.) still run before `prepBaseV` so it restores correct vtype.

### prepMaskV vid.v Alignment

`prepMaskV()` uses `vid.v` + `vmsltu` to build mask patterns in v0. Previously always used `vid.v v1`, illegal when LMUL>=2. Fixed: temp vreg = `int(lmul)` when lmul>=2 (v2 for LMUL=2, v4 for LMUL=4, v8 for LMUL=8), v1 otherwise.

### Completed coverpoint outcomes

| Coverpoint | Status | Key Notes |
| --- | --- | --- |
| cp_custom_FpRecSqrtEst_edges | 100% | Fixed: even+odd exponents |
| cp_custom_FpRecipEst_edges | 100% | Out of box |
| cp_custom_vfclass_onehot | 100% | — |
| cp_custom_vfncvt_rod_overflow | 100% (SEW32) | Fixed: `get_vr_element_zero()` → `vs2_val[63:0]` |
| cp_custom_vfredosum_ordered_sum | 100% | — |
| cp_custom_FpRecSqrtEst_flag_edges | 100% | Spacer tests (RVVI alias bug) |
| cp_custom_FpRecipEst_flag_edges | 100% | Spacer tests |
| cp_custom_vfncvt_rup_overflow | 100% RV64 | Only vfncvt.f.f.w + .rod can set OF at SEW32. Int-to-float/float-to-int can't overflow. Fixed CSR name + comment. |
| cp_custom_vfp_state | 50% | 2 crosses 0%: template checks mstatus.vs==0 (traps), hardcodes wrong insn |
| cp_custom_vfredosum_NAN_vl0 | 55.55% | Cross 0%. Framework vl=0 limit + wrong bin values |
| cp_custom_vfp_flags | 100% | Root cause for rv32+SEW64 was sew>xlen skip |
| cp_custom_vfp_flags_nv_nx | 100% | Back-to-back NX tests + .wf scalar width correction |
