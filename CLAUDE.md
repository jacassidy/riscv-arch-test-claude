# CLAUDE.md

> **This is the Claude working files repo (`riscv-arch-test-claude`).** All new Claude-generated files (guides, scripts, tools, notes) must be created here, not in the main working repo. The main working repo is your current working directory — whichever checkout or worktree this CLAUDE.md is symlinked into. If you are in a git worktree, all edits target that worktree's directory, not the primary checkout.

## Rules

- Update the relevant guide immediately when corrected or when you learn something new.
- Verify work before marking complete (run tests, check logs).
- Read the guide for a task before reading raw code.
- **NEVER use Agent with `subagent_type=Explore`** unless the user explicitly gives permission. Direct Grep/Glob/Read is fine.
- **Context refresh between problems**: When switching from one problem/coverpoint to another, STOP. Re-read the relevant guide files from the Task Routing table below. Then summarize your current context: what was just completed, what you're starting next, and what the current state is. This is where context drift happens — prevent it by resetting at every transition.
- **File creation rule**: Any new guides, notes, scripts, or tools you create belong in this repo (`riscv-arch-test-claude`), NOT in the main working repo. Only files that are part of the upstream project (test generators, coverpoint scripts, configs) belong in the current working repo.

## Task Routing

All paths below are relative to this repo (`riscv-arch-test-claude`) unless marked `(main repo)`.

| Task                                   | Read                                                                                           |
| -------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Fix coverage holes                     | `guides/custom-scripts/CLAUDE-coverage-workflow.md`                                            |
| Write/edit CSV cells                   | `guides/csv-editing.md`                                                                        |
| Write/fix cp*custom*\*.py script       | `guides/custom-scripts/GUIDE.md`                                                               |
| Look up vector encodings/FP hex values | `guides/vector-reference.md` (grep, don't read whole file)                                     |
| Project structure, build commands      | `guides/architecture.md`                                                                       |
| Debug a hanging test                   | `guides/debugging-hangs.md`                                                                    |
| Known pitfalls and bugs                | `scripts/claude-scripts/knowledge.md`                                                          |
| Fix/edit coverpoint templates          | `(main repo) generators/coverage/src/covergroupgen/templates/` (scalar) and `…/templates/vector/` (vector) |
| Simulator bugs / unsupported tests     | `simulator-issues.md`                                                                          |
