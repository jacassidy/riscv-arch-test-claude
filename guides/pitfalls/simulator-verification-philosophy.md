# Simulator Verification Philosophy


Test suite verify simulator (Sail), not just coverage numbers. Coverage hole persist after debug → ask: test bug or sim bug? Sim issue symptoms: signature mismatch on simple ops, hang on valid instructions, inconsistent results across XLEN.

**⚠️ NEVER add to `unsupported_tests` without explicit user approval.** `unsupported_tests` fully prevents test generation. Coverage runs use Sail only; Sail-vs-Spike disagreement invisible to coverage, NOT reason to skip. Build failure + hang almost always test-gen bug OR slow test, not Sail bug. Even for confirmed Sail bug, prefer workaround (script guard, `MAXINDEXEEW`, skip specific combo) over `unsupported_tests`.
