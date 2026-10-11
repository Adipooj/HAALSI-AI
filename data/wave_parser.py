from __future__ import annotations

from collections import defaultdict
from typing import Dict, List
import pandas as pd


def get_wave_columns(df: pd.DataFrame) -> Dict[str, List[str]]:
    wave_cols = defaultdict(list)
    for col in df.columns:
        s = str(col)
        if s.startswith("W1"):
            wave_cols["W1"].append(s)
        elif s.startswith("W2"):
            wave_cols["W2"].append(s)
        elif s.startswith("W3"):
            wave_cols["W3"].append(s)
    return dict(wave_cols)


def split_by_wave(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    cols = get_wave_columns(df)
    return {wave: df[wave_cols].copy() for wave, wave_cols in cols.items()}


def get_panel_pairs(df: pd.DataFrame, base_wave: str = "W1", follow_wave: str = "W2") -> tuple[pd.DataFrame, pd.DataFrame]:
    base_cols = [c for c in df.columns if str(c).startswith(base_wave)]
    follow_cols = [c for c in df.columns if str(c).startswith(follow_wave)]
    return df[base_cols].copy(), df[follow_cols].copy()