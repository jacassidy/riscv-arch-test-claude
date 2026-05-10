# Timing Budget


- Single Sail simulation ~5 sec. Longest never > 20 sec.
- **Always expect hangs while developing.** Use timeouts on every coverage run.
- Isolated coverpoint coverage: timeout 60s (should finish <30s).
- Full custom suite (e.g. Vls): timeout 300s / 5 min while iterating. Full run ~10 min but never wait that long during development.
- Never huge timeouts (10 min). Short timeouts catch hangs fast.
- Hang found → grep for `mcause` in trace output — catches illegal instructions faster than reading asm.
