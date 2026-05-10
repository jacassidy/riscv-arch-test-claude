# Coverage Saves Progress / make clean Discipline


- **Coverage saves progress.** Completed `.sig` files persist between runs. Timed-out run loses nothing.
- **DO NOT run `make clean` while iterating on hang** — destroys saved progress.
- **Only run `make clean` after believing hang fixed**, to verify with full clean run of consistently-compiled suite.
