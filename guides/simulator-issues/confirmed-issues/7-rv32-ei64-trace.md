# 7. RV32 ei64 — Trace Evidence

Last valid instruction before hang (from `/tmp/vloxei64_rv32_trace.log`):

```
[161] [M]: 0x80000272 (0x5E0FBE57) vmv.v.i v28, -0x1
v28 <- 0x...FFFFFFFFFFFFFFFF

[162] [M]: 0x80000276 (0x0FC9FB87) illegal 0xfc9fb87    VlsCustom16_vloxei64_v_cg_cp_custom_ls_indexed+0
trapping from M to M to handle illegal-instruction
handling exc#illegal-instruction at priv M with tval 0x0FC9FB87
CSR mcause (0x342) <- 0x00000002
CSR mepc (0x341) <- 0x80000276

trapping from M to M to handle fetch-access-fault
handling exc#fetch-access-fault at priv M with tval 0x00000000
CSR mcause (0x342) <- 0x00000001
CSR mepc (0x341) <- 0x00000000
[... infinite trap loop at PC=0x0 ...]
```
