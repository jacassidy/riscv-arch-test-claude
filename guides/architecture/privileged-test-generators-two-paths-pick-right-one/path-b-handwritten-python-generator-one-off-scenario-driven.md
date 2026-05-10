## Path B — handwritten Python generator (one-off / scenario-driven)


Use when test = sequence of *scenarios* better expressed as straight-line code than matrix — e.g. set CSR state, execute one instruction, restore state. "Handwritten test, written in Python so you get framework's macros and signature plumbing" style.

- Generator module: `(main repo) generators/testgen/src/testgen/priv/extensions/<TestSuite>.py`
- Decorator: `@add_priv_test_generator("<TestSuite>", required_extensions=[...], march_extensions=[...], extra_defines=[...])` from `testgen.priv.registry`
- Asm helpers: `comment_banner`, `write_sigupd`, `load_float_reg`, `load_int_reg`, `gen_csr_read_sigupd`, plus `test_data.add_testcase(name, coverpoint, covergroup)` to emit labeled testcase that covergroup samples on.
- Macros in emitted asm: `LI(xR, val)`, `LA(xR, sym)`, `CSRR/CSRW/CSRS/CSRC(csr, xR)`, plus normal asm. Vector tests need `extra_defines=["#define RVTEST_VECTOR", "#define RVTEST_SEW 0", "#define VDSEW 0"]`.
- Auto-defines: `F` in required_extensions adds `#define RVTEST_FP`; `Sm`/`S`/`U`/`H` add relevant `rvtest_*trap_routine` defines (see `io/templates.py:generate_defines_from_extensions`).
- Driver: `(main repo) generators/testgen/src/testgen/generate/priv.py:generate_priv_test()` (one multi-XLEN test file via preprocessor — `xlen=0`).
- Output: `tests/priv/<TestSuite>/<TestSuite>-00.S` (filename from `io/writer.py:write_test_file`, format `<testsuite>-{file_idx:02d}.S`).
- Examples: `SmF.py`, `ExceptionsSm.py`, `InterruptsU.py`, `ExceptionsVf.py`.
- Reserved registers (set by `generate_priv_test`): x0, x1/ra, x6, x7, x9, x16-x31. Allocate from remaining pool via `test_data.int_regs.get_register(...)` / `get_registers(n, ...)` and return at end. **Never hardcode `x{N}` / `f{N}` literal** — see `guides/register-allocation.md` for full rule and corresponding vector-priv helpers.
