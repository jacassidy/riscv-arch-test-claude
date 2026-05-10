# Coverage Status


### Vf — Complete
All Vf custom coverpoints at 100%.

### Vls — Complete
Extensions: `Vls8,Vls16,Vls32,Vls64`. Full-suite 100% verified (all extensions combined, RV32+RV64): rv64 1085 covergroups all 100%, rv32 957 covergroups all 100%. All 7 custom + all standard at 100%.

Custom coverpoints (all completed): `cp_custom_vwholeRegLS_vill`, `cp_custom_vwholeRegLS_lmul`, `cp_custom_maskLS`, `cp_custom_ls_indexed`, `cp_custom_ffLS_update_vl`, `cp_custom_indexed_emul_data_only`, `cp_custom_masked_v0_operand`.

Definitions: `working-testplans/duplicates/Vector - Vls_custom_definitions.csv`. Standard defs: `(main repo) docs/ctp/src/v.adoc`.

### Key bugs fixed for Vls full suite

- **SIGUPD_V SEW mismatch (EEW≠SEW)**: `RVTEST_SIGUPD_V` uses `vle##_SEW.v` to load reference, but `vmsne.vv` compares at current vtype's SEW. For LS with EEW≠SEW (e.g., `vlseg5e8ff.v` at SEW=16), only 1 byte loaded but 2 bytes compared → stale-byte mismatch. Fix: always emit `vsetivli x0, 1, e{sig_sew}, m1` before SIGUPD in base tests (not just when lmul≠1).
- **Mask LS reload register**: vsm.v/vlm.v store/load ceil(VL/8) bytes. Stale tail bytes in reload register differ between builds. Fix: zero reload register before reload.
- **Indexed LS vs2 EMUL**: `loadVecReg` always used `m1` for vs2, but indexed LS with EEW≠SEW can have EMUL>1. Fix: `e{register_sew}, m{max(register_emul,1)}`.
- **Whole register LS vd preload EMUL**: Used `lmul*eew/sew` → wrong EMUL for whole register LS. Fix: extract NF from instruction name.
- **Whole register stores vs3 loading**: Cascading `if` chain overwrote `load_unique_vtype=True` with False. Fix: restructured to `elif`. Also: used avlReg for VLMAX vsetvli, clobbering saved VL. Fix: separate vlmaxTempReg.
- **sig.elf for coverage traces**: build_plan.py uses sig.elf instead of final.elf for RVVI trace generation — avoids selfcheck halting
- **Store vd preload cap**: capped vd_emul to lmul for stores, prevents misaligned register access
- **Zero data padding**: `.fill 128, 1, 0` in genVsedges for VLEN=1024 whole-register loads
- **Unreachable bin removal**: removed `bins one = {0}` from cr_vl_lmul_e16_emul1max_sew8.sv
- **cmp_vd_vs2_sew_lte handler**: indexed LS vd==vs2 overlap tests with SEW guard
- **cr_vtype_agnostic_*_nomask handlers**: whole-register LS agnostic bins
- **Template ifdef fixes**: `COVER_VLSCUSTOM*` → `COVER_VLS*`

6 instructions in `unsupported_tests` (Sail bugs): vlseg3e32.v, vlseg3e32ff.v, vlseg4e32.v, vsseg3e32.v, vsseg3e64.v, vwredusum.vs. All issues tracked in `simulator-issues.md`.
