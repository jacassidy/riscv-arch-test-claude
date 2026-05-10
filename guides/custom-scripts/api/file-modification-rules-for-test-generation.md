# File Modification Rules for Test Generation


**Strongly prefer modifying only `cp_custom_*.py` scripts.** Exhaust all options in custom scripts before changing `vector_testgen_common.py` or `vector-testgen-unpriv.py`.

When non-custom test gen work requires modifying shared files:

- Changes necessary to progress — files not off-limits.
- Be **extremely frugal**: only systematic, general-purpose changes.
- **Avoid specific patch solutions** — every change should benefit multiple instructions or coverpoints, not just one.
- Keep changes minimal, well-scoped.
