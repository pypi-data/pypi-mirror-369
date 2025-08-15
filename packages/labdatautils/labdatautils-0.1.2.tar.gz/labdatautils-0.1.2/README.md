# labdatautils

A Python library for **experimental data analysis and reporting**.  
Includes tools for **error propagation** and **LaTeX-ready table formatting** — all with consistent significant-figure handling.

## Features

- **Error propagation** via finite difference derivatives, with correct significant figures.
- **LaTeX table generation** with support for merged value ± error columns.
- Designed for **clarity** and **reproducibility** in lab reports.

## Installation

```bash
pip install labdatautils
```
---

## Function Reference

### 1. `propagate(func, *args)`

**Arguments:**
- `func` *(callable)* — Function whose result and uncertainty are to be calculated.
- `*args` — Values and uncertainties, alternating: `val1, err1, val2, err2, ...`  
  Each can be a float, list, or NumPy array (all arrays must have the same length).

**Returns:**
- `values` *(ndarray)* — Computed function results.
- `errors` *(ndarray)* — Propagated uncertainties.

---

### 2. `generate_latex_table(column_headers, data_columns, **kwargs)`

**Arguments:**
- `column_headers` *(list of str)* — Ordered list of column names to display.
- `data_columns` *(sequence of arrays)* — One array per column, in the same order as `column_headers`.  
  Each array should contain the values for that column.
- `caption` *(str, optional)* — Table caption. Default: `"Data Table"`.
- `label` *(str, optional)* — LaTeX label for referencing. Default: `"tab:data"`.
- `error_map` *(dict or list of str, optional)* — Maps error columns to their associated value column.  
  Example: `{"dx": "x", "dy": "y"}` or `["dx:x", "dy:y"]`.
- `merge_error_style` *(str, optional)* — How to display value and error pairs:  
  `"separate"` (two columns), `"pm"` (e.g. `1.23 ± 0.04`), `"paren"` (e.g. `1.23(4)`). Default: `"separate"
