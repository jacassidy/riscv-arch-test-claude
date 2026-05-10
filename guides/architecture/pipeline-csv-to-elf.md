# Pipeline: CSV to ELF


1. CSV testplan maps instructions to coverpoints
2. Coverpoint generators create assembly templates
3. `make vector-tests` invokes covergroupgen + testgen, creates `.S` files
4. UDB config filters applicable tests
5. Sail model runs tests, computes expected results
6. Final self-checking ELFs embedded with expected values
