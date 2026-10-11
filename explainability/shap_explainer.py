from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

try:
    import shap
except Exception:  # pragma: no cover
    shap = None


@dataclass
class ShapSummary:
    feature_importance: pd.DataFrame
    shap_values: object | None


def compute_shap_summary(model, X: pd.DataFrame) -> ShapSummary:
    if shap is None:
        raise ImportError("shap is not installed. Add it to requirements.txt.")

    # For calibrated pipelines, use the inner classifier if possible
    estimator = model
    if hasattr(model, "base_estimator"):
        estimator = model.base_estimator

    explainer = shap.Explainer(model, X)
    shap_values = explainer(X)

    importance = pd.DataFrame(
        {
            "feature": X.columns,
            "mean_abs_shap": np.abs(shap_values.values).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)

    return ShapSummary(feature_importance=importance, shap_values=shap_values)


def top_drivers(feature_importance: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return feature_importance.head(n).copy()