# Diagnosis-First Hang Workflow (MANDATORY before unsupported_tests)


Before declaring "hang":

1. **Time in isolation, no parallel load**: `time timeout 1800 /opt/riscv/bin/sail_riscv_sim --config <sail.json> --test-signature=/tmp/x.sig --signature-granularity 4 <elf>` — many "hangs" finish in 5-10 min. 800+ testcases CAN take 7+ min serial, 15-30 min under parallel CPU contention.
2. **Completes? NOT hang.** Need higher SAIL_TIMEOUT (currently 1800s = 30 min in `framework/src/act/build_plan.py:24`).
3. **Truly never completes** → `guides/debugging-hangs.md` for trace diagnosis: `--inst-limit 50000 --trace-instr` to find stuck point, check `mcause` for trap loop, check vtype/LMUL/SEW alignment + register collisions.
4. **Only after exhausting test-gen + config issues** potentially Sail bug. Provide 4-element evidence:

To claim confirmed Sail bug, document in `simulator-issues.md`:
1. Exact reproduction command (copy-pasteable, minimal isolated ELF)
2. Trace quote from `--trace-all` showing loop / invalid behavior
3. Analysis citing RISC-V spec (chapter/section)
4. Comparison with correct behavior (RV64 vs RV32, or another sim)

No trace evidence → label "suspected." See `simulator-issues.md` issue #7 for reference format.
