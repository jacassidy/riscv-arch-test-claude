# What to read and when


| When                                | Read                                                                                                   |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Planning next coverpoint            | This file + `scripts/claude-scripts/progress.json`                                                     |
| **Modifying any template or script** | **Definition CSV first** (`working-testplans/csvs/Vector - V{ls,x,f}_custom_definitions.csv`) — understand what the coverpoint is testing and what the spec says before touching code |
| Fixing a test script                | `guides/custom-scripts/GUIDE.md` + `guides/pitfalls.md`                               |
| Fixing a template                   | `guides/coverpoint-templates.md` + `guides/pitfalls.md` + `(main repo) generators/coverage/src/covergroupgen/templates/vector/` |
| Investigating coverage failure      | Definition CSV → RISC-V V spec → Sail trace (see "Spec-First Debugging" below)                         |

**⚠️ MANDATORY: Always read definition CSV before modifying coverpoint template/script.** Definitions describe expected behavior, spec quotes, test methodology. Skip = misinterpret what coverpoint tests.
