# 7. Status / remaining work


Refresh dropped (unmatched) coverpoint list — work-list for new covergroups:

```bash
cd /home/jacassidy/normative_rules && make covergroupgen
cd /home/jacassidy/cvw/addins/riscv-arch-test-claude
uv run python tools/fill_vx_coverpoints.py 2> /tmp/fill_dropped.log
sed -n '2,$p' /tmp/fill_dropped.log | sort -u > /tmp/fill_dropped_unique.txt
wc -l /tmp/fill_dropped_unique.txt
```

Anything in `/tmp/fill_dropped_unique.txt` = CSV-referenced coverpoint no covergroup defines — i.e. hole.
