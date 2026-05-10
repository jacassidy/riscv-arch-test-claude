# csv_edit.py API


CSV name auto-resolves (e.g., `'Vf'`, `'Vls'`) to `(main repo) testplans/`. VfCustom now merged into Vf (like VxCustom part of Vx).

| Function         | Usage                                                        | Description                                  |
| ---------------- | ------------------------------------------------------------ | -------------------------------------------- |
| `read_structure` | `read_structure(csv_name)`                                   | Headers + first column (lightweight context) |
| `set_cells`      | `set_cells(csv_name, [(row, col), ...], value="x")`          | Set specific cells                           |
| `fill_column`    | `fill_column(csv_name, col_name, row_names=None, value="x")` | Fill a column                                |
| `fill_row`       | `fill_row(csv_name, row_name, col_names=None, value="x")`    | Fill a row                                   |
| `clear_cells`    | `clear_cells(csv_name, [(row, col), ...])`                   | Clear cells                                  |

Always call `read_structure()` first. Do NOT read full CSVs with Read tool — can be huge.
