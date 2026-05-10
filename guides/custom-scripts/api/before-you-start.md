# Before You Start


**⚠️ Always read definition CSV before modifying any coverpoint template or script.** Definitions at `working-testplans/csvs/Vector - V{ls,x,f}_custom_definitions.csv` describe what each coverpoint tests, expected behavior, relevant spec quotes. Working without reading definition leads to wrong implementations.

If coverage cannot reach 100%, follow Spec-First Debugging Flow in `CLAUDE-coverage-workflow.md` — check definition, quote spec, get Sail trace, determine if issue in test gen, template, or simulator.
