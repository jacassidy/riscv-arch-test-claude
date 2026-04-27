# CLAUDE.md

> **This is the Claude working files repo (`riscv-arch-test-claude`).** All new Claude-generated files (guides, scripts, tools, notes) must be created here, not in the main working repo. The main working repo is your current working directory — whichever checkout or worktree this CLAUDE.md is symlinked into. If you are in a git worktree, all edits target that worktree's directory, not the primary checkout.

## Rules

- **Never commit, only `git add`** — the user handles all commits. Stage files with `git add` after changes, but never run `git commit`.
- Update the relevant guide immediately when corrected or when you learn something new.
- Verify work before marking complete (run tests, check logs).
- Read the guide for a task before reading raw code.
- **NEVER use Agent with `subagent_type=Explore`** unless the user explicitly gives permission. Direct Grep/Glob/Read is fine.
- **Context refresh between problems**: When switching from one problem/coverpoint to another, STOP. Re-read the relevant guide files from the Task Routing table below. Then summarize your current context: what was just completed, what you're starting next, and what the current state is. This is where context drift happens — prevent it by resetting at every transition.
- **File creation rule**: Any new guides, notes, scripts, or tools you create belong in this repo (`riscv-arch-test-claude`), NOT in the main working repo. Only files that are part of the upstream project (test generators, coverpoint scripts, configs) belong in the current working repo.
- **Never edit generated files**: `coverpoints/unpriv/*_coverage.svh` and `tests/rv{32,64}i/**/*.S` are generated outputs. Always modify the source (templates in `generators/coverage/src/covergroupgen/templates/`, scripts in `generators/testgen/scripts/custom/`, or the CSV) and regenerate via `make vector-tests`.
- **Normative-rule YAMLs (`coverpoints/norm/Vx.yaml` etc.) are owned by `tools/fill_vx_coverpoints.py` in THIS repo**, NOT by `(main repo) generators/ctp/norm_yaml_gen.py`. The main-repo `norm_yaml_gen.py` generates *new* YAML scaffolds from testplan CSVs into `coverpoints/norm/yaml/new/` and is unrelated to the CSV-driven `Vx.yaml` workflow. Symptoms of working on the wrong file: you see CSV column headers like `EFFEW8` / `cr_vl_lmul` / `cp_custom_*` ending up in coverpoint arrays — those are testplan-CSV column names, not coverpoints. STOP and switch to `tools/fill_vx_coverpoints.py`. See `guides/normative-rules-flow.md`.
- **Don't follow the IDE "file was modified" reminder blindly**: that's just whatever file the user last touched, not necessarily the file relevant to the current task. Always verify by re-reading the routing table below.

## Task Routing

All paths below are relative to this repo (`riscv-arch-test-claude`) unless marked `(main repo)`.

| Task                                   | Read                                                                                           |
| -------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Fix coverage holes                     | `guides/custom-scripts/CLAUDE-coverage-workflow.md`                                            |
| Write/edit CSV cells                   | `guides/csv-editing.md`                                                                        |
| Write/fix cp*custom*\*.py script       | **Definition CSV first** (`working-testplans/csvs/Vector - V{ls,x,f}_custom_definitions.csv`) then `guides/custom-scripts/GUIDE.md` |
| Modify/create coverpoint template      | **Definition CSV first** (`working-testplans/csvs/Vector - V{ls,x,f}_custom_definitions.csv`) then `guides/coverpoint-templates.md` then `(main repo) generators/coverage/src/covergroupgen/templates/` |
| Look up vector encodings/FP hex values | `guides/vector-reference.md` (grep, don't read whole file)                                     |
| Project structure, build commands      | `guides/architecture.md`                                                                       |
| Debug a hanging test                   | `guides/debugging-hangs.md`                                                                    |
| Known pitfalls and bugs                | `scripts/claude-scripts/knowledge.md`                                                          |
| Investigate coverage failure           | Definition CSV → RISC-V V spec (`/home/jacassidy/cvw/addins/riscv-isa-manual/src/v-st-ext.adoc`) → Sail trace (see `guides/custom-scripts/CLAUDE-coverage-workflow.md` "Spec-First Debugging Flow") |
| Simulator bugs / unsupported tests     | `simulator-issues.md`                                                                          |
| Add/edit a priv test (`tests/priv/<X>`) | `guides/architecture.md` "Privileged Test Generators" — choose Path A (CSV+cp_*.py) or Path B (handwritten Python via `priv/extensions/<X>.py` + `@add_priv_test_generator`) |
| Modify/refresh `coverpoints/norm/Vx.yaml` (or sibling norm YAMLs) | `guides/normative-rules-flow.md` — the tool is `tools/fill_vx_coverpoints.py` in THIS repo. Run `make covergroupgen` first. Status of remaining holes: `guides/normative-rules-status.md`. |
