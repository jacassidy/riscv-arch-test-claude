# Coverage Saves Progress


Done `.sig` files persist between runs. Timed-out run lose nothing — fix hang, re-run. **Do NOT `make clean` while iterating on hang** — discard saved progress.

**Run `make clean` only once hang fixed**, for full clean run + verify suite passes end-to-end.
