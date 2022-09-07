- Bugs in NLDSL:
```py
# This must be a bug in original
dsl = "on data | select rows 'SNo' > 100 and 'SNo' < 200"
# Wrong:
py = 'data["SNo" > 100 & "SNo" < 200]'
# Correct:
py = 'data[("SNo" > 100) & ("SNo" < 200)]'
```
- Actually both are wrong - should i try "csv with header"?

- NLDSL: linear DSL + non-linear Code
- Too specific?