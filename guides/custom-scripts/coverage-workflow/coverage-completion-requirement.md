# Coverage Completion Requirement


**Coverpoint complete ONLY when custom bins hit 100%.** Every custom bin defined in template must hit.

If custom bin unhittable, **remove from template**. Goal = 100% across all custom bins: write test that hits or delete.

**Residual bins at 0% OK.** Bins not in template (framework-generated like `cp_asm_count`, `std_vec`, precondition crosses) fill when full suite runs. No investigate/fix during isolated coverpoint work.

**Entire covergroups at 0% also residual when instruction has NO custom marks.** Many Vls instructions (e.g. `vle32.v`, `vlse8.v`, `vse16.v`, `vlseg*`, `vlsseg*`, `vsseg*`, `vssseg*`) have no `cp_custom_*` columns marked in CSV. Covergroups only contain `cp_asm_count` + `std_vec` — both framework-generated. Show 0%/ZERO in reports but **not** coverage holes. Cover when full non-custom suite runs. Only instructions w/ `cp_custom_*` marks need custom test scripts.

**Note:** VlsCustom merged into Vls. Single `Vls.csv` testplan now has both custom + non-custom coverpoints. Updating `testplans/Vls.csv` → also update canonical backup at `working-testplans/duplicates/Vls-save.csv`.
