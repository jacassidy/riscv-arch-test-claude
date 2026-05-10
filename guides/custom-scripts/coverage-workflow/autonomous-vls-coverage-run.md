# Autonomous VLS Coverage Run


### Pre-flight checklist

1. `python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py --restore Vls`
2. Verify Makefile `EXTENSIONS ?= Vls8,Vls16,Vls32,Vls64`
3. Confirm no stale isolation (`wc -l testplans/Vls.csv` should be 311)

### Authoritative references — consult before concluding anything is invalid

| Reference | Path |
| --- | --- |
| V spec (LS = Section 7) | `/home/jacassidy/cvw/addins/riscv-isa-manual/src/v-st-ext.adoc` |
| UDB instruction YAML | `external/riscv-unified-db/spec/std/isa/inst/V/<instruction>.yaml` |
| Custom coverpoint definitions | `working-testplans/duplicates/Vector - Vls_custom_definitions.csv` |
| Standard coverpoint definitions | `docs/ctp/src/v.adoc` |
| Spike validation | `simulator-issues.md` → "How to validate suspected Sail bugs via Spike" |

**Before working on any coverpoint:** Read its definition in `Vector - Vls_custom_definitions.csv`. Definition explains expected behavior — determines whether hang = bug or correct.

**Important:** Coverage runs use Sail only. Sail-vs-Spike sig disagreements NOT visible during `make coverage`. Sig mismatches only surface w/ `make spike` separately, NOT part of coverage loop. All instructions to 100% coverage regardless of known Sail-Spike disagreements. **No add to `unsupported_tests` during coverage work** — see policy above.

### Triage decision tree (coverage run issues only)

- **Hang**: Hangs can be correct (instruction traps, no trap handler). Check coverpoint definition — if expects instruction completes w/o trap, hang = bug.
  1. Read coverpoint definition for expected behavior
  2. Trace w/ `--trace-instr --trace-reg` + `--inst-limit`
  3. Valid V instruction decoded as illegal (check V spec + UDB): suspected Sail bug → document in `simulator-issues.md` w/ all 4 elements → **no add to `unsupported_tests` w/o user approval** — try workarounds first (guard in script, skip specific combo)
  4. Illegal due to EMUL misalignment in scaffolding: test-gen bug → fix script
  5. Genuinely illegal SEW/LMUL/EEW combo (e.g. nf × EMUL > 8): script should not generate this → add guard
- **Uncovered bin**: Check if achievable given instruction's constraints. Unreachable → remove from template. Reachable → fix script
- **Coverage 0% for entire covergroup (no custom marks)**: Residual — only `cp_asm_count`/`std_vec`. Ignore during custom coverage work.
- **Build failure on one instruction**: Investigate test-gen script first. Build failures almost always test-gen bugs, not Sail bugs. **Never add to `unsupported_tests` as quick fix for build failures.**

**Critical rule:** Never remove instruction from CSV, never add to `unsupported_tests` w/o explicit user approval. Sail genuine bug → document in `simulator-issues.md` + work around in script/template. `unsupported_tests` = absolute last resort for cases where Sail output blanketly wrong + directly blocks coverage bins.

### Coverpoint work order (simplest/most isolated first)

1. `cp_custom_ffLS_update_vl` — fault-first VL update, small scope
2. `cp_custom_masked_v0_operand` — masked w/ v0 as source, well-understood pattern
3. `cp_custom_ls_indexed` — indexed LS, interacts w/ RV32 ei64 Sail bug
4. `cp_custom_indexed_emul_data_only` — EMUL constraint for indexed, depends on #3
5. `cp_custom_vwholeRegLS_vill` — partial coverage, possible framework bug to resolve
