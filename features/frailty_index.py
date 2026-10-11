from __future__ import annotations

import numpy as np
import pandas as pd

from data.preprocessing import binary_from_any, safe_numeric


FRAILTY_DOMAINS = {
    "function",
    "mobility",
    "grip",
    "blood_pressure",
    "bmi",
    "cardiometabolic",
    "disease",
    "hiv",
    "cognition",
    "mental_health",
    "social",
}


def compute_frailty_index(feature_frame: pd.DataFrame) -> pd.Series:
    """
    Compute a simple deficit-count frailty index over selected HAALSI domains.
    The input should already contain numeric columns mapped from the crosswalk.
    """

    if feature_frame.empty:
        return pd.Series(dtype="float64")

    deficits = []

    for col in feature_frame.columns:
        series = pd.to_numeric(feature_frame[col], errors="coerce")

        # Generic deficit rule:
        # - binary / ordinal adverse indicators: >0 counts as a deficit
        # - if the column is mostly continuous, we use a robust z-style fallback below
        valid = series.dropna()
        if valid.empty:
            continue

        nunique = valid.nunique(dropna=True)

        if nunique <= 5:
            deficit = (series > 0).astype(float)
        else:
            median = valid.median()
            mad = (valid - median).abs().median()
            scale = mad if mad and mad > 0 else valid.std(ddof=0)
            if not scale or np.isnan(scale) or scale == 0:
                deficit = pd.Series(0.0, index=series.index)
            else:
                z = (series - median) / scale
                deficit = (z > 1.0).astype(float)

        deficits.append(deficit.rename(col))

    if not deficits:
        return pd.Series(0.0, index=feature_frame.index, name="frailty_index")

    deficit_df = pd.concat(deficits, axis=1)
    frailty = deficit_df.mean(axis=1).fillna(0.0)
    frailty.name = "frailty_index"
    return frailty