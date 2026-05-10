# Vector Coverage Workflow


> **This file lives in `riscv-arch-test-claude`.** All new Claude-generated files belong here, not main repo.

**Run first, read results, then fix.** No read scripts/templates until coverage report exist.

**Verify by rerunning, not reading.** After fix, rebuild + rerun coverage (steps 2–4) confirm. No read generated tests/asm/framework source guess if fix worked — coverage report = ground truth. Same if hole maybe in multiple instructions: rerun coverage, no read files deduce.

**Simulator verification mindset.** Primary purpose of suite = confirm simulator (Sail) runs correctly. When coverage hole unfillable — especially hangs, signature mismatches, trivial bins — **strongly consider simulator at fault**, not test. Sail bug = significant finding. If suspect simulator issue:

1. **Validate via Spike** (below) — authoritative check, not `.sig` vs `.results`
2. Document in `simulator-issues.md` (repo root) w/ Spike PASS/FAIL evidence + repro commands
3. **DO NOT add instructions to `unsupported_tests`** unless instruction produces blanketly wrong Sail output that directly blocks coverage bins (e.g. Sail hangs in infinite trap loop). Sail/Spike sig disagreements do NOT affect coverage — coverage uses Sail only. See "unsupported_tests policy" below.

**⚠️ unsupported_tests policy — ABSOLUTE LAST RESORT.** Adding instruction to `unsupported_tests` in `vector-testgen-unpriv.py` **completely prevents test generation** for that instruction across ALL coverpoints. Almost never appropriate during coverage work:

- **Coverage runs use Sail only.** Sail-vs-Spike disagreements invisible to `make coverage`. Spike FAIL does NOT justify adding to `unsupported_tests`.
- **ONLY valid reason** to add during coverage work: Sail itself hangs/crashes on it AND hang unfixable by correcting test-gen script (e.g. confirmed Sail decode bug like #7 where Sail treats valid instruction as illegal).
- **Even then**, prefer workarounds: use `MAXINDEXEEW`, guard specific SEW/LMUL combo in script, or skip that test case — not entire instruction.
- **If build fails** on one instruction, investigate test-gen script/template first. Build failures almost always test-gen bugs (register misalignment, nf×EMUL overflow), not Sail bugs.
- **Add to unsupported_tests w/o explicit user approval = error.** Revert immediately.

**Validating Sail vs Spike.** Comparing `.sig` vs `.results` = **circular** — both Sail-generated. Real test = run self-checking ELFs on Spike. Pipeline embeds Sail-generated expected values into ELF, Spike runs + checks own results against those. PASS = Sail + Spike agree. FAIL = disagree (one buggy).

```bash
# 1. Comment out the instruction in unsupported_tests
# 2. Isolate (check CSV with: grep -rl '<instr>' working-testplans/duplicates/)
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py <CSV> --tests <instr1> <instr2>
# 3. Build spike ELFs
make clean && make vector-tests
CONFIG_FILES="config/spike/spike-rv64-max/test_config.yaml config/spike/spike-rv32-max/test_config.yaml" \
  EXTENSIONS=<ext8>,<ext16>,<ext32>,<ext64> make elfs
# 4. Run Spike
./run_tests.py "$(cat config/spike/spike-rv64-max/run_cmd.txt)" work/spike-rv64-max/elfs
./run_tests.py "$(cat config/spike/spike-rv32-max/run_cmd.txt)" work/spike-rv32-max/elfs
# 5. Restore
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py --restore <CSV>
```
