# Directory Structure


### Main repo (`riscv-arch-test-cvw`)
```
riscv-arch-test-cvw/
├── config/duts/cvw/                              # CVW-specific configs (rv32gc, rv64gc)
├── generators/
│   ├── testgen/src/testgen/coverpoints/          # Coverpoint generator modules (cp_*.py)
│   ├── testgen/scripts/custom/                   # Custom cp_custom_*.py scripts
│   ├── coverage/src/covergroupgen/templates/      # Scalar/general .sv/.txt coverpoint templates
│   │   └── vector/                                # Vector covergroup templates (cmp_*, cp_*, cr_*, sample_*)
│   └── coverage/covergroupgen.py
├── testplans/*.csv                               # Live CSVs (managed by isolation scripts)
├── tests/rv32i,rv64i/                            # Generated .S files
├── work/sail-rv64-max/reports/                   # RV64 coverage reports
└── work/sail-rv32-max/reports/                   # RV32 coverage reports
```

### Claude repo (`riscv-arch-test-claude`, this repo)
```
riscv-arch-test-claude/
├── CLAUDE.md                                      # Task routing
├── guides/                                        # All guides and references
├── scripts/claude-scripts/                        # Coverage tools, orchestrator, knowledge
├── tools/csv_edit.py, isolate_coverpoint.py       # CSV editing and isolation tools
└── working-testplans/                             # Canonical CSV source + backups
    └── duplicates/                                # Canonical backups (Vf-save.csv, etc.)
```
