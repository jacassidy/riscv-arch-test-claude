# First Instinct: Assume It's a Hang


Single Sail sim finish ~5s; max 20s. >10s on one file = hang. **Do not wait** — find ELF (Step 1), run manually with graduated `--inst-limit` (Step 2). Sail hit inst limit consistently = infinite loop.
