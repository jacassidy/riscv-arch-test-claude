# Template Format Rules


1. **NO COVERGROUP WRAPPER** — Never write `covergroup ... endgroup`. Files paste into existing covergroup.
2. **Header**: `//` line (~80 chars), `// cp_name`, `//` line. First `//` start at column 0.
3. **Footer**: `//// end cp_name` + slashes to ~80 chars
4. **Indentation**: 4 spaces coverpoints, 8 spaces bins
5. **No unused coverpoints**: Every helper MUST appear in at least one cross. Review after writing.
6. **No unfillable custom bins**: Every custom bin MUST be reachable by tests. If bin never hit, delete. Custom bins must reach **100% coverage**. Residual 0% on framework-generated bins (not defined in template) acceptable — those filled by full suite.
7. **One blank line** at end of file
8. **Comments**: Max 1 line. Readers have CSV already.
9. **Concatenation syntax** — multi-signal coverpoints: `coverpoint` keyword goes BEFORE opening brace, signal expressions inside are bare. **Wrong:** `name : {coverpoint expr1, coverpoint expr2}`. **Correct:** `name : coverpoint {expr1, expr2}`.
