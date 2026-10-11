from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from models.risk_fusion import fuse_risk


@dataclass
class TrajectoryResult:
    horizon_years: int
    mean_risk: float
    std_risk: float


def estimate_wave_drift(base: pd.DataFrame, follow: pd.DataFrame) -> pd.Series:
    base_num = base.apply(pd.to_numeric, errors="coerce")
    follow_num = follow.apply(pd.to_numeric, errors="coerce")

    common = [c for c in base_num.columns if c in follow_num.columns]
    if not common:
        return pd.Series(dtype="float64")

    drift = (follow_num[common].mean(numeric_only=True) - base_num[common].mean(numeric_only=True))
    return drift.fillna(0.0)


def simulate_forward_risk(
    base_features: pd.DataFrame,
    model,
    frailty: pd.Series,
    age: pd.Series,
    horizons=(1, 3, 5),
    n_simulations: int = 500,
    drift_scale: float = 1.0,
) -> pd.DataFrame:
    """
    Very first-pass pseudo-longitudinal simulator:
    - draws noisy perturbations around current features
    - rescored by the trained model
    - then fused with frailty and age
    """
    rng = np.random.default_rng(42)
    base = base_features.copy()

    rows = []
    feature_cols = list(base.columns)

    base_proba = model.predict_proba(base)[:, 1] if hasattr(model, "predict_proba") else model.predict(base)

    for h in horizons:
        sims = []
        for _ in range(n_simulations):
            perturbed = base.copy()

            for c in feature_cols:
                s = pd.to_numeric(perturbed[c], errors="coerce")
                noise = rng.normal(0, 0.05 * max(float(s.std(skipna=True) or 1.0), 1.0), size=len(s))
                perturbed[c] = (s + drift_scale * h * noise).astype(float)

            p = model.predict_proba(perturbed)[:, 1] if hasattr(model, "predict_proba") else model.predict(perturbed)
            fused = fuse_risk(frailty=frailty, decline_prob=pd.Series(p, index=base.index), age=age)
            sims.append(fused.values)

        sims_arr = np.vstack(sims)
        rows.append(
            {
                "horizon_years": h,
                "mean_risk": float(np.nanmean(sims_arr)),
                "std_risk": float(np.nanstd(sims_arr)),
            }
        )

    return pd.DataFrame(rows)