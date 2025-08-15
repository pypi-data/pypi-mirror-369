import math
import numpy as np
from typing import List, Dict, Union

NumberLike = Union[int, float, np.floating]

# ------------------------------
# Core rounding utilities
# ------------------------------

# Round an error value to 1 significant figure, and return metadata for formatting.
def _err_round_1sf(err: float):

    # Handle special cases (zero, NaN, infinity)
    if err == 0 or not np.isfinite(err):
        return 0.0, 0, 0, 0
    
    # Separate sign and work with absolute value
    sgn = 1 if err > 0 else -1
    a = abs(err)

    # Find exponent in base-10 scientific notation: a = d × 10^exp
    exp = math.floor(math.log10(a))   

    # Normalise to mantissa in [1, 10) and round to 1 significant figure (interger)      
    d = a / (10**exp)
    mant = int(round(d))                     

    # Handle rounding overflow (e.g., 9.5 → 10)
    if mant == 10:                            
        mant = 1
        exp += 1
    
    # Reconstruct the rounded error
    err_rounded = sgn * mant * (10**exp)

    # Number of decimal places for fixed-point representation
    decimals_linear = max(-exp, 0)            
    return err_rounded, exp, mant*sgn, decimals_linear

# Determines if we should use scientific notation
def _need_sci(x: float) -> bool:
    ax = abs(x)
    return (ax != 0.0) and (ax < 1e-3 or ax >= 1e4)

# Decomposes a number on mantissa and exponent
def _mant_exp(x: float):
    if x == 0:
        return 0.0, 0
    e = math.floor(math.log10(abs(x)))
    m = x / (10**e)
    return m, e

# Remove trailing zeros from a fixed-point number string.
def _trim_zeros_fixed(s: str) -> str:
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s if s else "0"

# ------------------------------
# Formatting for general (non error-coupled) columns
# ------------------------------
def _format_number_auto(x: float, precision: int = 4, sci_mode: Union[str, bool] = "auto") -> str:
    """
    Format a general number for LaTeX:
      - sci_mode True  -> scientific
      - sci_mode False -> fixed decimal
      - sci_mode "auto"-> scientific only if needed
    """
    if sci_mode is True:
        m, e = _mant_exp(x)
        mant = _trim_zeros_fixed(f"{m:.{precision}g}")
        return rf"{mant} \times 10^{{{e}}}"
    elif sci_mode is False:
        return _trim_zeros_fixed(f"{x:.{precision}f}")
    else:
        if _need_sci(x):
            m, e = _mant_exp(x)
            mant = _trim_zeros_fixed(f"{m:.{precision}g}")
            return rf"{mant} \times 10^{{{e}}}"
        else:
            return _trim_zeros_fixed(f"{x:.{precision}f}")

# ------------------------------
# Merged styles (±, parentheses)
# ------------------------------
def _format_merged(val: float, err: float, style: str, sci_mode="auto") -> str:
    """
    Merge value ± error for one cell.

    - Error shown with 1 significant figure when err != 0.
    - Value rounded to the SAME absolute resolution as the error:
        * Fixed mode: round to multiples of the 1‑s.f. error step and print with
          the implied fixed decimals.
        * Scientific mode: use a shared exponent; round mantissas so both reflect
          the same absolute step at that exponent.
    """

    # Decide notation
    use_sci = (sci_mode is True) or (sci_mode == "auto" and _need_sci(val))

    # Case 1: Zero or invalid error
    if err == 0 or not np.isfinite(err):
        if use_sci and val != 0:
            mant, exp = _mant_exp(val)
            mant_str = _trim_zeros_fixed(f"{mant:.15g}")
            body = rf"{mant_str} \times 10^{{{exp}}} \pm 0"
        else:
            v_str = _trim_zeros_fixed(f"{val:.15g}")
            body = rf"{v_str} \pm 0"
        return body if style == "pm" else body.replace(r" \pm ", "(") + ")"

    # Case 2: Fixed (linear) mode
    if not use_sci:
        # Round error to 1 s.f. and get its fixed-decimal precision
        err_rounded, err_exp, _, err_dec = _err_round_1sf(abs(err))
        err_step = abs(err_rounded)

        # Round value to the SAME absolute step
        if err_step == 0.0:
            val_rounded = val
        else:
            val_rounded = round(val, -err_exp)

        # Render, preserving trailing zeros implied by err_dec
        v_str = f"{val_rounded:.{err_dec}f}" if err_dec > 0 else _trim_zeros_fixed(f"{val_rounded:.0f}")
        e_str = f"{err_rounded:.{err_dec}f}" if err_dec > 0 else _trim_zeros_fixed(f"{err_rounded:.0f}")

        if style == "pm":
            return rf"{v_str} \pm {e_str}"
        elif style == "paren":
            return rf"{v_str}({e_str})"
        else:
            return rf"{v_str} \pm {e_str}"

    # Case 3: Scientific notation mode
    if val != 0:
        mv, ev = _mant_exp(val)
    else:
        # If value is zero, anchor exponent to the error
        err_abs = abs(err)
        ev = int(math.floor(math.log10(err_abs))) if err_abs > 0 else 0
        mv = 0.0

    # Absolute error rounded to 1 s.f. 
    err_step = _err_round_1sf(abs(err))[0]

    # Error order and leading digit (1..9)
    # This is done manually with log10 and integer arithmetic instead of using
    # _mant_exp() to avoid potential floating-point artefacts (e.g., mantissa = 0.9999999)
    # and to keep the result as pure integers for stable rounding. _mant_exp could be
    # used here if extra guards were added for the 0 and mantissa=10.0 cases.
    err_order = int(math.floor(math.log10(err_step)))
    leading   = int(round(err_step / (10.0 ** err_order)))

    # Mantissa decimals so both mantissas correspond to same absolute step at 10^ev
    err_dec = max(0, ev - err_order)

    # Round value mantissa and compute error mantissa at shared exponent
    mv_rounded = round(mv, err_dec)
    me_mant = leading * (10.0 ** (err_order - ev))

    # Renormalize if rounding pushed mantissa to ±10
    if abs(mv_rounded) >= 10.0:
        mv_rounded /= 10.0
        me_mant    /= 10.0
        ev         += 1

    mv_str = f"{mv_rounded:.{err_dec}f}" if err_dec > 0 else _trim_zeros_fixed(f"{mv_rounded:.0f}")
    me_str = f"{me_mant:.{err_dec}f}"     if err_dec > 0 else _trim_zeros_fixed(f"{me_mant:.0f}")

    if style == "pm":
        return rf"\left({mv_str} \pm {me_str}\right) \times 10^{{{ev}}}"
    elif style == "paren":
        return rf"{mv_str}({me_str}) \times 10^{{{ev}}}"
    else:
        return rf"{mv_str} \times 10^{{{ev}}} \pm {me_str} \times 10^{{{ev}}}"
  

# ------------------------------
# Separate style (two columns)
# ------------------------------
def _format_separate(val: float, err: float, sci_mode: Union[str, bool] = "auto"):
    """
    Two columns: (value, error).

    - Error is shown at 1 significant figure (auto sci/fixed unless sci_mode forces).
    - Value is rounded to the SAME absolute resolution as the 1‑s.f. error:
        * Sci: round value mantissa in steps of err_step / 10**ev and print mantissas
          with the exact decimals needed so (mantissas)*10**ev match abs resolution.
        * Fixed: round value to nearest multiples of err_step and print with the same
          decimals implied by the error's exponent.
    """

    # 1) Error to 1 s.f. (+ metadata). err_r is signed 1‑s.f. error.
    err_r, err_exp, _, err_decimals = _err_round_1sf(err)
    err_step = abs(err_r)

    # Decide sci/fixed for columns based on sci_mode
    use_sci_err = (sci_mode is True) or (sci_mode == "auto" and _need_sci(err_r))
    use_sci_val = (sci_mode is True) or (sci_mode == "auto" and _need_sci(val))

    # Precompute error order/leading once (integers; avoids FP artefacts)
    if err_step > 0:
        err_order = int(math.floor(math.log10(err_step)))            # e.g. 0.005 -> -3
        leading   = int(round(err_step / (10.0 ** err_order)))       # 1..9
    else:
        err_order = 0
        leading   = 0

    # Error cell
    if use_sci_err:
        # err_r is already 1 s.f.: show mantissa at 1 s.f. with shared error exponent
        me, ee_sci = _mant_exp(abs(err_r))
        e_cell = rf"{_trim_zeros_fixed(f'{me:.1g}')} \times 10^{{{ee_sci}}}"
    else:
        # Fixed: decimals from error exponent only (no special trailing-zero policy)
        e_cell = (f"{abs(err_r):.{err_decimals}f}"
                  if err_decimals > 0 else _trim_zeros_fixed(f"{abs(err_r):.0f}"))

    # Value cell (match the same absolute resolution)
    if use_sci_val:
        # Scientific: round value to the same decimal place as the (1‑s.f.) error 
        mv, ev = _mant_exp(val)
        if err_step == 0:
            mv_rounded = mv
            mant_dec = 0
        else:
            mant_dec = max(0, ev - err_order)  
            mv_rounded = round(mv, mant_dec)    

        mv_str = (f"{mv_rounded:.{mant_dec}f}"
                if mant_dec > 0 else _trim_zeros_fixed(f"{mv_rounded:.0f}"))
        v_cell = rf"{mv_str} \times 10^{{{ev}}}"
    else:
        # Fixed: round value to the same decimal place as the (1‑s.f.) error
        if err_step == 0:
            v_lin = val
        else:
            v_lin = round(val, -err_order)

        decimals = max(0, -err_order)
        v_cell = (f"{v_lin:.{decimals}f}"
                if decimals > 0 else _trim_zeros_fixed(f"{v_lin:.0f}"))

    return v_cell, e_cell
# ------------------------------
# Table generator
# ------------------------------
def generate_latex_table(
    column_headers: List[str],
    data_columns: Dict[str, List[float]],
    caption: str = "Data Table",
    label: str = "tab:data",
    error_map: Union[Dict[str, str], List[str]] = None,
    merge_error_style: str = "separate",  # "pm" | "paren" | "separate"
    sci_mode: Union[str, bool] = "auto",
    precision_other_cols: int = 4,
    use_booktabs: bool = True,
) -> str:
    """
    Build a LaTeX table from column data. Supports merging value±error columns or keeping them separate.

    Guarantees:
      - No IndexError: rows are truncated to the shortest among actually-used columns.
      - Clear error if a referenced column is missing.
    """

    if not isinstance(data_columns, dict):
        # Assume sequence of arrays in same order as column_headers
        data_columns = {h: np.asarray(col).tolist()
                        for h, col in zip(column_headers, data_columns)}
    else:
        # Ensure values are lists
        data_columns = {k: np.asarray(v).tolist() for k, v in data_columns.items()}

    # Normalize error_map
    if isinstance(error_map, list):
        emap = {}
        for pair in error_map:
            left, right = pair.split(":")
            emap[left.strip()] = right.strip()
        error_map = emap
    elif error_map is None:
        error_map = {}

    # --- Determine which columns are actually used (so we can compute a safe row count)
    used_cols: List[str] = []
    for h in column_headers:
        if h in error_map:
            # 'h' is an error header listed in error_map; it will be handled with its value partner
            continue
        err_cols_for_this_value = [e for e, v in error_map.items() if v == h]
        if err_cols_for_this_value:
            val_col = h
            err_col = err_cols_for_this_value[0]
            used_cols.extend([val_col, err_col])
        else:
            used_cols.append(h)

    # Sanity checks
    missing = [c for c in used_cols if c not in data_columns]
    if missing:
        raise KeyError(f"Missing columns in data_columns: {missing}")

    lengths = [len(data_columns[c]) for c in used_cols]
    if not lengths:
        raise ValueError("No columns to render.")
    n_rows = min(lengths)  # Truncate to the shortest list to avoid IndexError

    # --- Build the output columns in the requested order
    merged_headers: List[str] = []
    merged_data_cols: List[List[str]] = []

    for h in column_headers:
        if h in error_map:
            # This is an error column header; skip here (paired with its value column below)
            continue

        # If this header is a "value" that has an error partner
        err_cols_for_this_value = [e for e, v in error_map.items() if v == h]
        if err_cols_for_this_value:
            err_col = err_cols_for_this_value[0]
            if merge_error_style in ("pm", "paren"):
                merged_headers.append(h)
                col_vals = []
                for i in range(n_rows):
                    val = data_columns[h][i]
                    err = data_columns[err_col][i]
                    col_vals.append(_format_merged(val, err, merge_error_style, sci_mode=sci_mode))
                merged_data_cols.append(col_vals)
            else:  # separate
                merged_headers.extend([h, err_col])
                v_col, e_col = [], []
                for i in range(n_rows):
                    val = data_columns[h][i]
                    err = data_columns[err_col][i]
                    v_cell, e_cell = _format_separate(val, err, sci_mode=sci_mode)
                    v_col.append(v_cell)
                    e_col.append(e_cell)
                merged_data_cols.append(v_col)
                merged_data_cols.append(e_col)
        else:
            # standalone column (no paired error)
            merged_headers.append(h)
            col_vals = []
            for i in range(n_rows):
                x = data_columns[h][i]
                if isinstance(x, (float, np.floating, int, np.integer)):
                    col_vals.append(_format_number_auto(float(x), precision=precision_other_cols, sci_mode=sci_mode))
                else:
                    col_vals.append(str(x))
            merged_data_cols.append(col_vals)

    # Transpose for rows
    rows = list(zip(*merged_data_cols))

    # LaTeX boilerplate
    if use_booktabs:
        col_format = "@{}l" + "c" * len(merged_headers) + "@{}"
    else:
        col_format = "|" + "l|" + "c|" * len(merged_headers)

    lines = []
    lines.append(r"\begin{table}[h!]")
    lines.append(r"\centering")
    lines.append(rf"\caption{{{caption}}}")
    lines.append(rf"\label{{{label}}}")
    lines.append(rf"\begin{{tabular}}{{{col_format}}}")
    lines.append(r"\toprule" if use_booktabs else r"\hline")

    header_line = " & ".join([""] + merged_headers) + r" \\"
    if use_booktabs:
        header_line += " \midrule"
    else:
        header_line += r" \hline"
    lines.append(header_line)

    # Row content: wrap cells in math mode
    for i, row in enumerate(rows):
        math_cells = [
            f"${cell}$" if not (str(cell).startswith("$") and str(cell).endswith("$")) else str(cell)
            for cell in row
        ]
        line = " & ".join([f"${i}$"] + math_cells) + r" \\"
        if not use_booktabs:
            line += r"\hline"
        lines.append(line)

    lines.append(r"\bottomrule" if use_booktabs else r"\hline")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return "\n".join(lines)

