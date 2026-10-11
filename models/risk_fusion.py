from __future__ import annotations

import numpy as np
import pandas as pd

from config.haalsi_config import AGE_WEIGHT, DECLINE_WEIGHT, FRAILTY_WEIGHT


def _normalize_age(age: pd.Series | float | int) -> pd.Series:
    if isinstance(age, (float, int)):
        return pd.Series([age], dtype="float64")
    return pd.to_numeric(age, errors="coerce").fillna(age.median() if hasattr(age, "median") else 0)


def fuse_risk(frailty: pd.Series, decline_prob: pd.Series, age: pd.Series) -> pd.Series:
    age_s = pd.to_numeric(age, errors="coerce")
    age_scaled = (age_s - age_s.min()) / (age_s.max() - age_s.min() + 1e-9)
    frailty_s = pd.to_numeric(frailty, errors="coerce").fillna(0.0).clip(0, 1)
    decline_s = pd.to_numeric(decline_prob, errors="coerce").fillna(0.0).clip(0, 1)

    risk = (
        FRAILTY_WEIGHT * frailty_s +
        DECLINE_WEIGHT * decline_s +
        AGE_WEIGHT * age_scaled
    ).clip(0, 1)
    risk.name = "fused_risk"
    return risk


def categorize_risk(risk: pd.Series) -> pd.Series:
    bins = [-np.inf, 0.30, 0.55, 0.75, np.inf]
    labels = ["Low", "Moderate", "High", "Very High"]
    return pd.cut(risk, bins=bins, labels=labels, right=False)