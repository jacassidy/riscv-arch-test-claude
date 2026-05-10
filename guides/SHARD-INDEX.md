# SHARD-INDEX — Routing table for hook Sonnet router

Sonnet reads this when a Read/Edit/Write/MultiEdit fires. Picks shards the main agent must read before acting on the tool target. Output strict JSON array of shard paths.

## How to interpret

- **Tool target** = file path being read or written.
- For each row below, ask: "Given the target's path/extension/name, is this shard's topic relevant?" If yes, include. Err on side of inclusion when target plausibly matches.
- Shards already small (<50 lines each, caveman); include 0–6 typical. Hard cap 10.
- If target is unrelated to any topic (e.g. random text file), return `[]`.

## Always-relevant (universal hard rules)

| Shard | When |
|---|---|
| guides/register-allocation.md | Any test generator code: `*.py` under `generators/testgen/`, `cp_custom_*.py`, anything emitting asm with `x{N}/v{N}/f{N}` |

## architecture/ — build, layout, make, priv tests

| Shard | When |
|---|---|
| guides/architecture/intro.md | First read of repo / general orientation |
| guides/architecture/overview.md | Same as intro |
| guides/architecture/directory-structure.md | Asking where a dir lives, navigating unknown paths |
| guides/architecture/commands.md | Running `make` targets, build commands |
| guides/architecture/pipeline-csv-to-elf.md | Understanding test generation flow |
| guides/architecture/coverage-generator-generate-py.md | Editing `generators/coverage/src/covergroupgen/generate.py` |
| guides/architecture/never-edit-generated-files.md | Touching `coverpoints/{unpriv,priv}/*_coverage*.svh` or `tests/rv{32,64}i/**/*.S` (also hard-blocked by hook) |
| guides/architecture/python-environment.md | Running `uv run`, Python deps |
| guides/architecture/known-deviations-from-upstream.md | Comparing to upstream riscv-arch-test |
| guides/architecture/privileged-test-generators-two-paths-pick-right-one/intro.md | Editing anything under `tests/priv/` |
| guides/architecture/privileged-test-generators-two-paths-pick-right-one/decision-rule.md | Same |
| guides/architecture/privileged-test-generators-two-paths-pick-right-one/path-a-csv-testplan-cp-py-instruction-coverpoint-matrix.md | Priv test, CSV-driven path |
| guides/architecture/privileged-test-generators-two-paths-pick-right-one/path-b-handwritten-python-generator-one-off-scenario-driven.md | Priv test, handwritten path |
| guides/architecture/privileged-test-generators-two-paths-pick-right-one/possibly-trapping-vector-priv-tests-dual-signature-design.md | Priv test that may trap |
| guides/architecture/privileged-test-generators-two-paths-pick-right-one/coverage-caveats-worth-documenting-in-svh.md | Priv test svh notes |

## coverpoint-templates/ — `.sv` template authoring

| Shard | When |
|---|---|
| guides/coverpoint-templates/intro.md | First touch of any template `.sv` |
| guides/coverpoint-templates/file-naming.md | Creating new template file |
| guides/coverpoint-templates/architectural-legality-belongs-in-the-csv.md | Adding LMUL/SEW filter logic |
| guides/coverpoint-templates/template-format-rules/intro.md | Editing any `.sv` template |
| guides/coverpoint-templates/template-format-rules/non-custom-template.md | Standard (non-custom) coverpoint |
| guides/coverpoint-templates/template-format-rules/custom-template-with-crosses.md | `cp_custom_*.sv` template |
| guides/coverpoint-templates/template-replacement-keywords.md | Using INSTR/EFFEW/ARCH placeholders |
| guides/coverpoint-templates/allowed-bin-syntax.md | Defining `bins`, `wildcard bins`, `ignore_bins` |
| guides/coverpoint-templates/copy-paste-patterns/standard-vector-conditions-std-vec.md | Need `std_vec` block |
| guides/coverpoint-templates/copy-paste-patterns/lmul-coverpoints-vlmul-mf8-5-mf4-6-mf2-7-m1-0-m2-1-m4-2-m8-3.md | Coverpoint on LMUL |
| guides/coverpoint-templates/copy-paste-patterns/sew-coverpoints-vsew-e8-0-e16-1-e32-2-e64-3.md | Coverpoint on SEW |
| guides/coverpoint-templates/copy-paste-patterns/register-bit-fields-vd-11-7-vs1-19-15-vs2-24-20-vm-25.md | Reading insn[N:M] for vd/vs1/vs2/vm |
| guides/coverpoint-templates/copy-paste-patterns/register-alignment-for-lmul.md | Vector reg alignment bins |
| guides/coverpoint-templates/copy-paste-patterns/vl-at-vlmax.md | vl/VLMAX coverpoint |
| guides/coverpoint-templates/copy-paste-patterns/vl-zero.md | vl=0 coverpoint |
| guides/coverpoint-templates/copy-paste-patterns/vstart-vl.md | vstart vs vl |
| guides/coverpoint-templates/copy-paste-patterns/trap-occurred.md | trap coverpoint |
| guides/coverpoint-templates/copy-paste-patterns/valid-vtype-vill-0.md | vtype/vill coverpoint |
| guides/coverpoint-templates/copy-paste-patterns/frm-floating-point-rounding-mode.md | FP frm coverpoint |
| guides/coverpoint-templates/copy-paste-patterns/mstatus-vs-active.md | mstatus.vs coverpoint |
| guides/coverpoint-templates/copy-paste-patterns/widening-overlap-detection.md | Widening vd/vs2 overlap |
| guides/coverpoint-templates/copy-paste-patterns/compound-coverpoints-multi-field-bins.md | Multi-signal compound coverpoints |
| guides/coverpoint-templates/copy-paste-patterns/emul-computation-for-load-store-3-field-compound.md | LS EMUL compound |
| guides/coverpoint-templates/copy-paste-patterns/xlen-sew-conditionals.md | XLEN/SEW `ifdef` in template |
| guides/coverpoint-templates/copy-paste-patterns/sew-specific-bin-values-cover-vfcustom-guards.md | COVER_VFCUSTOMxx guarded bins |
| guides/coverpoint-templates/copy-paste-patterns/sew64-fp-excluding-custom-bins.md | SEW64 FP custom bin gating |
| guides/coverpoint-templates/copy-paste-patterns/rvmodel-access-fault-address-guarding-fault-address-references.md | Using RVMODEL_ACCESS_FAULT_ADDRESS |
| guides/coverpoint-templates/copy-paste-patterns/gpr-value-access.md | Reading rs1_val/rs2_val |
| guides/coverpoint-templates/ins-object-reference/direct-fields.md | Using `ins.trap`/`ins.hart`/etc |
| guides/coverpoint-templates/ins-object-reference/ins-current-fields.md | Using `ins.current.*` |
| guides/coverpoint-templates/ins-object-reference/ins-prev-fields.md | Using `ins.prev.*` |
| guides/coverpoint-templates/global-helper-functions.md | get_csr_val/get_vr_num/etc |
| guides/coverpoint-templates/self-maintenance-rule.md | Discovering new template pattern |

## csv-editing/ — testplan CSVs (`working-testplans/csvs/*.csv`)

| Shard | When |
|---|---|
| guides/csv-editing/intro.md | Any CSV touch |
| guides/csv-editing/file-locations.md | Same |
| guides/csv-editing/csv-edit-py-api.md | Calling `tools/csv_edit.py` |
| guides/csv-editing/cell-value-semantics.md | Setting cell values, sew_ge/sew_lte |
| guides/csv-editing/architectural-legality-lives-in-csv-not-generate-py.md | Tempted to add filter to generate.py |
| guides/csv-editing/stateless-processing.md | Sub-agent CSV editing |
| guides/csv-editing/knowledge-persistence.md | Discovered new fact, where to write |

## custom-scripts/api/ — `cp_custom_*.py` generator authoring

| Shard | When |
|---|---|
| guides/custom-scripts/api/intro.md | Any `cp_custom_*.py` touch |
| guides/custom-scripts/api/before-you-start.md | Same |
| guides/custom-scripts/api/function-signature.md | Defining `make()` |
| guides/custom-scripts/api/two-core-patterns.md | Choosing pattern |
| guides/custom-scripts/api/core-api/randomize-vector-signature.md | Calling `randomizeVectorInstructionData` |
| guides/custom-scripts/api/core-api/randomize-vector-auto.md | Same |
| guides/custom-scripts/api/core-api/randomize-vector-nf-emul-guard.md | LS instruction, lmul>1 |
| guides/custom-scripts/api/core-api/writetest-signature.md | Calling `writeTest` |
| guides/custom-scripts/api/pre-test-assembly-and-scratch-registers.md | Scratch reg / pre-test asm |
| guides/custom-scripts/api/important-register-assignment-for-ls-instructions.md | LS instruction code |
| guides/custom-scripts/api/file-modification-rules-for-test-generation.md | Editing testgen files |
| guides/custom-scripts/api/coverage-completion-rule.md | Marking coverage done |
| guides/custom-scripts/api/full-api-reference.md | Looking up API |

## custom-scripts/api-reference/ — extra patterns

| Shard | When |
|---|---|
| guides/custom-scripts/api-reference/intro.md | API deep-dive |
| guides/custom-scripts/api-reference/edge-value-sets.md | Edge value testing |
| guides/custom-scripts/api-reference/fp-vector-data-labels.md | FP vector data |
| guides/custom-scripts/api-reference/instruction-category-lists.md | Categorizing instruction |
| guides/custom-scripts/api-reference/suite-convention.md | suite= naming |
| guides/custom-scripts/api-reference/additional-patterns/edge-value-test.md | Edge value test pattern |
| guides/custom-scripts/api-reference/additional-patterns/overlap-test-widening-vd-overlaps-vs2-top.md | Widening overlap test |
| guides/custom-scripts/api-reference/additional-patterns/pre-test-asm-with-scratch-registers.md | Pre-test asm pattern |
| guides/custom-scripts/api-reference/additional-patterns/registercustomdata.md | `registerCustomData` |
| guides/custom-scripts/api-reference/additional-patterns/vl-lmul-sweep.md | vl/lmul sweep pattern |

## custom-scripts/coverage-workflow/ — debug + fill coverage holes

| Shard | When |
|---|---|
| guides/custom-scripts/coverage-workflow/intro.md | Coverage hole / debug / fix request |
| guides/custom-scripts/coverage-workflow/workflow.md | Same |
| guides/custom-scripts/coverage-workflow/spec-first-debugging-flow.md | Same |
| guides/custom-scripts/coverage-workflow/what-to-read-and-when.md | Same |
| guides/custom-scripts/coverage-workflow/timing-reference.md | Estimating run times |
| guides/custom-scripts/coverage-workflow/isolation.md | Isolating one coverpoint |
| guides/custom-scripts/coverage-workflow/incremental-rebuild-after-testgen-fix.md | Rebuilding after fix |
| guides/custom-scripts/coverage-workflow/reading-coverage-reports.md | Parsing coverage report |
| guides/custom-scripts/coverage-workflow/debugging-with-trace-files.md | Trace files |
| guides/custom-scripts/coverage-workflow/hang-detection.md | Test hang during coverage run |
| guides/custom-scripts/coverage-workflow/coverage-completion-requirement.md | Defining "done" |
| guides/custom-scripts/coverage-workflow/progress-tracking.md | Tracking progress |
| guides/custom-scripts/coverage-workflow/autonomous-vls-coverage-run.md | Long autonomous run |
| guides/custom-scripts/coverage-workflow/if-stuck.md | Stuck during workflow |

## debugging-hangs/ — Sail simulator hang

| Shard | When |
|---|---|
| guides/debugging-hangs/intro.md | Test hangs in build/sim |
| guides/debugging-hangs/timing-reference.md | Timing budget for sim |
| guides/debugging-hangs/first-instinct-assume-it-s-a-hang.md | First reaction |
| guides/debugging-hangs/coverage-saves-progress.md | Decide whether to clean |
| guides/debugging-hangs/sail-binary-location.md | Need Sail path |
| guides/debugging-hangs/step-1-find-the-elf.md | Locating hanging ELF |
| guides/debugging-hangs/step-2-run-with-instruction-trace-and-limit.md | Running Sail with trace |
| guides/debugging-hangs/step-3-programmatically-check-for-traps.md | Detect traps quickly |
| guides/debugging-hangs/step-4-add-register-trace-if-needed.md | Reg trace |
| guides/debugging-hangs/step-5-read-the-source-assembly-and-identify-the-coverpoint.md | Map asm to coverpoint |
| guides/debugging-hangs/step-6-diagnose-from-the-assembly-first.md | Asm-first diagnosis |
| guides/debugging-hangs/step-7-cross-reference-with-objdump-if-needed.md | objdump |
| guides/debugging-hangs/other-useful-sail-flags.md | Sail flag lookup |
| guides/debugging-hangs/common-hang-causes.md | Match symptoms |
| guides/debugging-hangs/sail-model-configuration.md | VLEN/ELEN config |

## normative-rules/ — `coverpoints/norm/Vx.yaml`, `tools/fill_vx_coverpoints.py`

| Shard | When |
|---|---|
| guides/normative-rules/intro.md | Norm rules / Vx.yaml work |
| guides/normative-rules/1-data-flow.md | Same |
| guides/normative-rules/2-tools-riscv-arch-test-claude-tools.md | Picking norm tool |
| guides/normative-rules/3-end-to-end-fix-workflow.md | Fixing norm rule |
| guides/normative-rules/4-audit-flag-semantics.md | Reading audit output |
| guides/normative-rules/5-reviewing-a-batch-with-sub-agents.md | Sub-agent batch review |
| guides/normative-rules/6-common-mistakes.md | Avoid past errors |
| guides/normative-rules/7-status-remaining-work.md | Status check |

## pitfalls/ — past bugs, gotchas, lessons

| Shard | When |
|---|---|
| guides/pitfalls/intro.md | Looking up known issues |
| guides/pitfalls/simulator-verification-philosophy.md | Trust philosophy |
| guides/pitfalls/diagnosis-first-hang-workflow-mandatory-before-unsupported-tests.md | Hang triage |
| guides/pitfalls/verification-rule.md | Verifying changes |
| guides/pitfalls/custom-script-rules.md | Editing `cp_custom_*.py` |
| guides/pitfalls/template-rules.md | Editing template `.sv` |
| guides/pitfalls/sew64-fp-ifdef-guard-for-custom-bins.md | SEW64 FP custom bin |
| guides/pitfalls/rvvi-fsflagsi-csr-alias-bug.md | RVVI fflags/fcsr |
| guides/pitfalls/transition-bins-nv1-dz1-nx1.md | FP flag transition bins |
| guides/pitfalls/nx-triggers-for-approximation-sqrt.md | NX flag for sqrt/approx |
| guides/pitfalls/fp-lookup-table-coverage.md | FP lookup |
| guides/pitfalls/snan-actual-values.md | sNaN values |
| guides/pitfalls/coverpoint-concatenation-syntax.md | Multi-signal coverpoint syntax |
| guides/pitfalls/vill-testing-pattern.md | vill testing |
| guides/pitfalls/framework-limitations.md | Framework caveats |
| guides/pitfalls/hang-detection-quick.md | Quick hang detect |
| guides/pitfalls/timing-budget.md | Timing budget |
| guides/pitfalls/coverage-saves-progress-make-clean-discipline.md | When to `make clean` |
| guides/pitfalls/sail-manual-run-rule.md | Manual Sail run |
| guides/pitfalls/coverage-status.md | Vf/Vls status |
| guides/pitfalls/fixed-bug-details-archive.md | History of fixed bugs |

## simulator-issues/ — Sail/Spike disagreements + bugs

| Shard | When |
|---|---|
| guides/simulator-issues/intro.md | Suspected sim bug |
| guides/simulator-issues/status-legend.md | Reading bug status |
| guides/simulator-issues/triage-decision-tree.md | Decide if it's a sim bug |
| guides/simulator-issues/bug-report-standard.md | Filing bug report |
| guides/simulator-issues/coverage-summary-as-of-2026-04-08.md | Coverage % checkin |
| guides/simulator-issues/vector-tests-traps-cause-immediate-sail-failure-exit.md | Trap-induced sail failure |
| guides/simulator-issues/confirmed-issues/1-3-segmented-loads-resolved-spike-validates-sail.md | Seg load issue |
| guides/simulator-issues/confirmed-issues/4-5-segmented-stores-vsseg3e32-v-vsseg3e64-v-confirmed-sail-spike-disagreement.md | Seg store disagreement |
| guides/simulator-issues/confirmed-issues/7-rv32-ei64-overview.md | RV32 ei64 illegal-decode |
| guides/simulator-issues/confirmed-issues/7-rv32-ei64-repro.md | Reproducing #7 |
| guides/simulator-issues/confirmed-issues/7-rv32-ei64-trace.md | #7 trace |
| guides/simulator-issues/confirmed-issues/7-rv32-ei64-analysis.md | #7 analysis |
| guides/simulator-issues/confirmed-issues/7-rv32-ei64-workaround.md | #7 workaround |

## vector-reference/ — encoding lookup, FP hex, SEW/EMUL

| Shard | When |
|---|---|
| guides/vector-reference/intro.md | Vector encoding lookup |
| guides/vector-reference/instruction-bit-fields/standard-vector-format.md | Standard vector encoding |
| guides/vector-reference/instruction-bit-fields/segment-load-store-format.md | Seg LS encoding |
| guides/vector-reference/instruction-bit-fields/instruction-type-encoding-funct3.md | funct3 lookup |
| guides/vector-reference/instruction-bit-fields/whole-register-move-vmv-nr-r-v-encoding.md | vmv.nr.v encoding |
| guides/vector-reference/csr-field-encodings.md | vtype/vsew/vlmul encoding |
| guides/vector-reference/load-store-eew.md | LS EEW lookup |
| guides/vector-reference/emul-formulas-and-constraints.md | EMUL math |
| guides/vector-reference/segment-load-vd-constraints.md | Seg load vd alignment |
| guides/vector-reference/element-index-regions.md | Element index region |
| guides/vector-reference/shift-amount-extraction.md | Shift amount |
| guides/vector-reference/integer-edge-values-by-sew.md | Integer edges per SEW |
| guides/vector-reference/edge-values-reference.md | General edge values |
| guides/vector-reference/fp-edge-half.md | FP16 hex |
| guides/vector-reference/fp-edge-single.md | FP32 hex |
| guides/vector-reference/fp-edge-double.md | FP64 hex |

## register-allocation

Already a single shard, listed in always-relevant.
