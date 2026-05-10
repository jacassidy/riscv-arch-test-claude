# 7. RV32 ei64 — Workaround

`config/sail/sail-rv32-max/rvtest_config.h` sets `MAXINDEXEEW 32` to skip ei64 tests on RV32, avoiding hang. Correct given Sail bug — change to `MAXINDEXEEW 64` once Sail fixed.
