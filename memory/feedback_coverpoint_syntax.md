---
name: Coverpoint Concatenation Syntax
description: Correct SystemVerilog coverpoint syntax — keyword before brace, not repeated inside
type: feedback
---

For multi-signal coverpoints using concatenation, the `coverpoint` keyword goes BEFORE the opening brace, and signal expressions inside are bare (no `coverpoint` keyword per signal).

**Wrong:** `name : {coverpoint expr1, coverpoint expr2, coverpoint expr3}`
**Correct:** `name : coverpoint {expr1, expr2, expr3}`

**Why:** The wrong format repeats the `coverpoint` keyword inside the concatenation braces. The correct SystemVerilog syntax uses `coverpoint` once before the concatenation.
**How to apply:** When generating any coverpoint template that concatenates multiple signals, always use `name : coverpoint {signal1, signal2, ...}` syntax.
