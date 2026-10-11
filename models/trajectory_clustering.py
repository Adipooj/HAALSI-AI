from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


def cluster_trajectories(features: pd.DataFrame, n_clusters: int = 3):
    """
    Fit a standardized Gaussian mixture model to temporal trajectory features.
    Returns cluster labels and a serializable model bundle.
    """
    if features.empty:
        raise ValueError("Trajectory feature matrix is empty.")

    clean = features.replace([np.inf, -np.inf], np.nan)
    clean = clean.fillna(clean.median(numeric_only=True))

    scaler = StandardScaler()
    scaled = scaler.fit_transform(clean)

    gmm = GaussianMixture(
        n_components=n_clusters,
        covariance_type="diag",
        reg_covar=1e-6,
        random_state=42,
    )

    labels = gmm.fit_predict(scaled)

    model_bundle = {
        "scaler": scaler,
        "gmm": gmm,
        "feature_columns": list(clean.columns),
        "n_clusters": n_clusters,
    }

    return labels, model_bundle