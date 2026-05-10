# Never Edit Generated Files


`coverpoints/unpriv/*_coverage.svh` and `tests/rv{32,64}i/**/*.S` = **generated outputs** — never hand-edit. Changes land in sources, flow through regen:

- Coverpoint `.svh` ← templates in `generators/coverage/src/covergroupgen/templates/`
- Test `.S` ← `generators/testgen/scripts/custom/*.py` + CSV testplans

Edit template/script/CSV, then rerun `make vector-tests` (or `make coverage`).
