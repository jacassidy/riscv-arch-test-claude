# Verification Rule


**Always rerun coverage to verify fix.** After editing script/template, rebuild (`make clean && make vector-tests`) and rerun (`make coverage` + `coverage_summary.py`). Don't read generated files / asm / framework code to guess if fix worked or if problem affects other instructions — coverage report answers both faster and certainly.
