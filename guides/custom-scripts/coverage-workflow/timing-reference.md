# Timing Reference


| Scope                        | Expected time | Timeout to use |
| ---------------------------- | ------------- | -------------- |
| Single Sail simulation       | ~5 seconds    | 20s            |
| Isolated coverpoint coverage | < 30 seconds  | **60s max**    |
| Full custom suite (Vls etc.) | ~10 minutes   | **5 min max**  |

**⚠️ NEVER run `make coverage` without `timeout`.** Even if expect success, always wrap. Hangs common, block terminal forever. No exceptions.
