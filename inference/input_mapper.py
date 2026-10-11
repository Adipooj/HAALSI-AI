from __future__ import annotations

from typing import Any, Dict
import pandas as pd


import numpy as np


def map_user_inputs_to_frame(user_inputs: Dict[str, Any], feature_columns: list[str], defaults: dict[str, Any]) -> pd.DataFrame:
    row = {}
    for col in feature_columns:
        val = user_inputs.get(col, None)
        if val is None or val == "" or pd.isna(val):
            row[col] = np.nan
        else:
            row[col] = val
    return pd.DataFrame([row], columns=feature_columns)


def align_frame_to_schema(df: pd.DataFrame, feature_columns: list[str], defaults: dict[str, Any]) -> pd.DataFrame:
    aligned = df.copy()
    for col in feature_columns:
        if col not in aligned.columns:
            aligned[col] = np.nan
        else:
            val = aligned.loc[0, col]
            if val is None or val == "" or pd.isna(val):
                aligned.loc[0, col] = np.nan
    aligned = aligned[feature_columns]
    return aligned