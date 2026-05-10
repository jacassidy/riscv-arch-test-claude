# Spec-First Debugging Flow


Coverpoint fails 100% (uncovered bins, hangs, weird behavior) → follow flow **in order**:

### 1. Read the definition CSV
Look up coverpoint in `working-testplans/csvs/Vector - V{ls,x,f}_custom_definitions.csv`. Understand:
- Behavior tested
- Spec section referenced
- Expected outcome

### 2. Check the RISC-V V spec
Spec at `/home/jacassidy/cvw/addins/riscv-isa-manual/src/v-st-ext.adoc`. Quote relevant section. Common:
- §7 (Vector Loads and Stores)
- §11.16 (vrgather)
- §12 (Vector Reductions)
- §13 (Vector Narrowing/Widening)
- §3.4.2 (EMUL constraints)
- §7.7 (Unit-stride Fault-Only-First Loads)

### 3. Get a Sail trace
```bash
# Short trace to see what Sail does with the edge case
DEBUG=True timeout 1s make coverage
# Trace is at work/sail-rv64-max/build/rv64i/<Ext>/<test>.sig.log
```

### 4. Determine root cause
| Symptom | Likely cause | Action |
| --- | --- | --- |
| Bin unhit, test runs fine | Test doesn't exercise the edge case | Fix test gen script |
| Hang (infinite trap loop) | Illegal instruction or test-gen bug | Check trace for trap cause, compare against spec |
| Sail produces wrong result | Possible Sail bug | Validate via Spike (see coverage workflow above), document in `simulator-issues.md` |
| Template bin unreachable | Template defines impossible condition | Remove bin from template |

### 5. If Sail bug suspected
**Be extremely scrutinous.** Custom coverpoints test edge cases — subtle situations — may expose real simulator bugs. But may also = poor spec reading. Before concluding Sail wrong:

1. Quote exact spec text
2. Show Sail trace demonstrating wrong behavior
3. Run same test on Spike for second opinion
4. Document w/ repro steps in `simulator-issues.md`:
   - Instruction + operands
   - SEW/LMUL/vl config
   - Expected behavior (w/ spec quote)
   - Actual Sail behavior (from trace)
   - Spike behavior (from run)
   - Repro: exact isolate cmd, make cmds, trace inspection
5. Sail bug directly blocks coverage bins AND no template/script workaround → add affected instructions to `unsupported_tests` in `vector-testgen-unpriv.py` w/ comment referencing issue — **only w/ user approval**
