from __future__ import annotations

from typing import Iterable
import numpy as np
import pandas as pd

from config.haalsi_config import MISSING_VALUES


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Safe replacement of HAALSI missing codes (-97, -98, -99)
    avoiding pandas block corruption
    """

    out = df.copy()

    for col in out.columns:
        try:
            out[col] = out[col].replace(MISSING_VALUES, np.nan)
        except Exception:
            continue

    return out


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]
    return out


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def binary_from_any(series: pd.Series) -> pd.Series:
    s = safe_numeric(series)
    return (s > 0).astype("float64")


def clip_percentile(series: pd.Series, lower: float = 0.01, upper: float = 0.99) -> pd.Series:
    s = safe_numeric(series)
    lo, hi = s.quantile([lower, upper])
    return s.clip(lo, hi)