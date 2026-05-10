# Allowed Bin Syntax


```systemverilog
bins name = {value};                          // Single value
bins name = {[start:end]};                    // Range
bins name[] = {[start:end]};                  // One bin per value
wildcard bins name = {5'b???00};              // Wildcard pattern
wildcard bins name = (before => after);       // Transition
ignore_bins name = {value};                   // Exclude
wildcard ignore_bins name = {5'b???00};       // Exclude wildcard
```
