# Debugging with Trace Files


Use `DEBUG=True` (no FAST) to gen trace files. **Trace files grow extremely fast** — max 10s timeout (1s usually enough).

```bash
DEBUG=True timeout 1s make coverage    # preferred — short burst
DEBUG=True timeout 10s make coverage   # max allowed
```

**Switch back to `FAST=True` immediately after** collecting traces.
