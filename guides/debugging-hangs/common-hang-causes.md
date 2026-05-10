# Common Hang Causes


### 1. Illegal vtype (vill bit set)

If `vsetvli`/`vsetvl` produce `vtype = 0x8000000000000000` (RV64) or `0x80000000` (RV32), **vill** bit set. All subsequent vector instrs illegal → trap loop.

**Diagnosis**: In `--trace-reg`, look for `CSR vtype <- 0x80000000...`. Means SEW/LMUL combo unsupported.

**Common trigger**: Fractional LMUL (mf8, mf4, mf2) where `VLMAX = VLEN * LMUL / SEW < 1`, or configs sail model don't support.

**Fix**: Guard code with `#ifdef` checks, or avoid unsupported SEW/LMUL combo in test generator.

### 2. No trap handler

Test framework no install trap handlers. Any exception (illegal instr, misaligned access, etc.) → infinite loop at default trap vector.

### 3. LMUL-misaligned vector register in scaffolding (fixed)

`prepMaskV()` used `vid.v v1` regardless of LMUL — illegal when LMUL>=2. Fixed: now uses LMUL-aligned temp reg. Diagnosis: `mcause <- 0x2` after `vid.v` on odd reg with LMUL>1.

### 4. vmv.v.i before vsetvli (fixed)

Mask init emitted before `vsetvli` — hung when `vtype.vill=1` after reset. Fixed: now emits after `prepBaseV`. See `guides/pitfalls.md` § "vmv.v.i v0 Before vsetvli".
