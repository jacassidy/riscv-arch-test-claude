# Coverpoint Concatenation Syntax


For multi-signal coverpoints using concatenation, `coverpoint` keyword goes BEFORE opening brace, signal expressions inside are bare (no `coverpoint` keyword per signal).

**Wrong:** `name : {coverpoint expr1, coverpoint expr2, coverpoint expr3}`
**Correct:** `name : coverpoint {expr1, expr2, expr3}`
