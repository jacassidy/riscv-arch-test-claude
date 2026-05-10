# Workflow


```bash
# 1. Isolate
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py <Category> <cp_column_name>

# 2. Build (should finish <30s for one coverpoint; if not, isolation failed)
make clean && make vector-tests

# 3. Coverage — always use FAST=True for normal runs (skips objdump, much faster)
#    60s timeout for isolated coverpoint; 300s for full suite
FAST=True timeout 60s make coverage

# 4. Read results
python3 $WALLY/addins/riscv-arch-test-claude/scripts/claude-scripts/coverage_summary.py --uncovered
python3 $WALLY/addins/riscv-arch-test-claude/scripts/claude-scripts/coverage_summary.py --bins <instruction>

# 5. Fix scripts/templates based on report, then repeat 2-4 to verify (do NOT read files to check — rerun coverage)

# 6. Restore when done
python3 $WALLY/addins/riscv-arch-test-claude/tools/isolate_coverpoint.py --restore <Category>
```
