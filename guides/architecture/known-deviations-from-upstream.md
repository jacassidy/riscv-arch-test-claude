# Known Deviations from Upstream


### `-DRVTEST_SELFCHECK` disabled in coverage builds

`build_plan.py` compiles `final.elf` without `-DRVTEST_SELFCHECK`. Coverage runs unchecked (store-only). Correctness verified separately via RVVI lock-step.

### `RVTEST_SIGUPD` 6-arg API

Upstream added 6th argument `_STR_PTR`. Vector testgen updated `writeSIGUPD`/`writeSIGUPD_F` accordingly. If builds break with "macro requires 6 arguments but only 5 given", check those functions.
