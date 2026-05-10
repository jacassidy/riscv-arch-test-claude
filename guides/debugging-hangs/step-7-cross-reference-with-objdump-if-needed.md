# Step 7: Cross-reference with objdump if Needed


Use `objdump` to map addresses back to test labels:

```bash
riscv64-unknown-elf-objdump -d <path-to-elf> | grep -A2 -B2 "<address>"
```
