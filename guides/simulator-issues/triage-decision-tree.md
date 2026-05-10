# Triage Decision Tree


| Symptom                                             | Most likely cause                 | Action                                                                                                                                                  |
| --------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Hang on valid instruction (check V spec + UDB)      | Sail decode bug                   | Document with all 4 elements. Try workaround in script first (guard, skip combo). `unsupported_tests` is absolute last resort — requires user approval. |
| Hang on helper instruction (vle/vse in scaffolding) | Test-gen misaligned reg           | Fix script                                                                                                                                              |
| Hang on illegal SEW/LMUL/EEW combo                  | Script missing guard              | Add nf × EMUL ≤ 8 or similar guard in script                                                                                                            |
| 0% on custom bin                                    | Script not generating case        | Fix script                                                                                                                                              |
| 0% on asm_count/std_vec only                        | Residual (no custom tests)        | Expected, ignore                                                                                                                                        |
| Build failure on one instruction                    | Test-gen bug                      | Investigate script — almost never a Sail bug. **Never add to `unsupported_tests` as a quick fix.**                                                      |
| Full-suite store hangs (EEW≠SEW)                    | SIGUPD_V scaffolding SEW mismatch | Known test-gen bug in standard tests. Residual only (no custom marks). Use timeout, ignore during custom coverage work.                                 |

**⚠️ `unsupported_tests` policy:** Adding instruction to `unsupported_tests` blocks test gen across ALL coverpoints. **Absolute last resort**, only when Sail output blanketly wrong and directly blocks coverage bins (e.g., Sail decodes valid instr as illegal → infinite trap loop). **Sail-vs-Spike disagreements do NOT justify adding to `unsupported_tests`** — coverage uses Sail only, unaffected by Spike mismatches. Any addition requires explicit user approval.

Coverage uses Sail only. Sail-vs-Spike disagreements NOT visible during `make coverage` — only surface via `make spike` separately. Instructions in `unsupported_tests` don't gen tests; all others should hit 100%. Don't run `make spike` during coverage iteration.

Key principle: hangs can be correct — if coverpoint expects instr to complete but hangs = bug (test-gen or Sail). If combo genuinely illegal per spec, script shouldn't generate it.

Authoritative refs: V spec `v-st-ext.adoc`, UDB `external/riscv-unified-db/spec/std/isa/inst/V/`, custom defs `Vector - Vls_custom_definitions.csv`.

---

### How to validate suspected Sail bugs via Spike

**Important**: Comparing `.sig` vs `.results` files is circular — both from Sail. Authoritative test = running self-checking ELFs on Spike via `run_tests.py`.

```bash
# 1. Comment out the instruction in unsupported_tests in vector-testgen-unpriv.py
# 2. Isolate (check CSV with: grep -rl '<instr>' working-testplans/duplicates/)
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py <CSV> --tests <instr1> <instr2>
# 3. Build spike ELFs
make clean && make vector-tests
CONFIG_FILES="config/spike/spike-rv64-max/test_config.yaml config/spike/spike-rv32-max/test_config.yaml" \
  EXTENSIONS=<ext8>,<ext16>,<ext32>,<ext64> make elfs
# 4. Run Spike
./run_tests.py "$(cat config/spike/spike-rv64-max/run_cmd.txt)" work/spike-rv64-max/elfs
./run_tests.py "$(cat config/spike/spike-rv32-max/run_cmd.txt)" work/spike-rv32-max/elfs
# 5. Interpret: PASS = Sail and Spike agree. FAIL = they disagree (one has a bug).
# 6. Restore
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py --restore <CSV>
```

---
