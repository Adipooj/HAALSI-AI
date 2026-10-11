from __future__ import annotations

import pandas as pd
import numpy as np

from targets.trajectory_utils import compute_domain_score
from models.trajectory_clustering import cluster_trajectories


def print_domain_availability(domain_varlists):
    print("\n[DEBUG] Domain availability:")
    for d in domain_varlists:
        w1 = len(domain_varlists[d].get("W1", []))
        w2 = len(domain_varlists[d].get("W2", []))
        w3 = len(domain_varlists[d].get("W3", []))
        print(f"{d:20s} | W1: {w1:3d} | W2: {w2:3d} | W3: {w3:3d}")


def zscore_series(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    mu = s.mean()
    sigma = s.std(ddof=0)
    if pd.isna(sigma) or sigma == 0:
        return pd.Series(0.0, index=s.index)
    return (s - mu) / sigma


def compute_multidomain_scores(df: pd.DataFrame, domain_varlists):
    """
    Build a composite longitudinal signal from domains that are present in W1, W2, and W3.
    Each domain score is z-scored before averaging so one scale cannot dominate the others.
    """
    preferred_domains = ["mobility", "disease", "cognition", "bmi"]

    used_domains = []
    w1_scores = []
    w2_scores = []
    w3_scores = []

    print("\n[INFO] Domains used for trajectory:")

    for d in preferred_domains:
        w1_cols = domain_varlists.get(d, {}).get("W1", [])
        w2_cols = domain_varlists.get(d, {}).get("W2", [])
        w3_cols = domain_varlists.get(d, {}).get("W3", [])

        if w1_cols and w2_cols and w3_cols:
            used_domains.append(d)
            print(f" - {d}")

            w1_scores.append(zscore_series(compute_domain_score(df, w1_cols)))
            w2_scores.append(zscore_series(compute_domain_score(df, w2_cols)))
            w3_scores.append(zscore_series(compute_domain_score(df, w3_cols)))

    if not used_domains:
        raise ValueError("No valid domains found for trajectory modeling.")

    weights = {
        "mobility": 2.0,
        "disease": 1.5,
        "bmi": 1.0
    }

    w1_list, w2_list, w3_list = [], [], []

    for d in used_domains:
        weight = weights.get(d, 1.0)

        w1_list.append(weight * compute_domain_score(df, domain_varlists[d]["W1"]))
        w2_list.append(weight * compute_domain_score(df, domain_varlists[d]["W2"]))
        w3_list.append(weight * compute_domain_score(df, domain_varlists[d]["W3"]))

    w1 = pd.concat(w1_list, axis=1).mean(axis=1)
    w2 = pd.concat(w2_list, axis=1).mean(axis=1)
    w3 = pd.concat(w3_list, axis=1).mean(axis=1)

    return w1, w2, w3, used_domains


def extract_trajectory_features(w1: pd.Series, w2: pd.Series, w3: pd.Series) -> pd.DataFrame:
    delta1 = w2 - w1
    delta2 = w3 - w2
    slope = (w3 - w1) / 2.0
    acceleration = delta2 - delta1
    variability = pd.concat([w1, w2, w3], axis=1).std(axis=1)

    return pd.DataFrame(
        {
            "delta1": delta1,
            "delta2": delta2,
            "slope": slope,
            "acceleration": acceleration,
            "variability": variability,
        }
    )


def label_clusters(traj_features: pd.DataFrame, labels) -> tuple[pd.Series, dict[int, str]]:
    """
    Map latent clusters to clinical labels using rank order of temporal trend.
    Higher trajectory score = worse progression.
    """
    df = traj_features.copy()
    df["cluster"] = labels

    summary = df.groupby("cluster")[["delta1", "delta2", "slope", "acceleration", "variability"]].mean()

    summary["trajectory_score"] = (
        0.60 * summary["slope"]
        + 0.25 * summary["acceleration"]
        + 0.15 * summary["variability"]
    )

    ordered_clusters = summary["trajectory_score"].sort_values(ascending=False).index.tolist()

    label_names = ["Rapid Decline", "Slow Decline", "Stable"]
    label_map: dict[int, str] = {}

    for i, cluster_id in enumerate(ordered_clusters):
        label_map[int(cluster_id)] = label_names[min(i, len(label_names) - 1)]

    print("\n[INFO] Cluster interpretation:")
    for k in sorted(label_map):
        print(f"Cluster {k} → {label_map[k]}")

    labeled_series = pd.Series(labels, index=traj_features.index).map(label_map)
    return labeled_series, label_map


def build_trajectory_labels(df: pd.DataFrame, domain_varlists):
    print_domain_availability(domain_varlists)

    w1, w2, w3, used_domains = compute_multidomain_scores(df, domain_varlists)

    traj_features = extract_trajectory_features(w1, w2, w3)
    traj_features = traj_features.replace([np.inf, -np.inf], np.nan)
    traj_features = traj_features.fillna(traj_features.median(numeric_only=True))

    labels, model = cluster_trajectories(traj_features)

    # -----------------------
    # STABLE TRAJECTORY SCORE
    # -----------------------

    # Primary signal: long-term change
    delta_long = (w3 - w1)

    # Secondary signal: early change
    delta_mid = (w2 - w1)

    # Weighted combination
    trajectory_score = 0.7 * delta_long + 0.3 * delta_mid

    trajectory_score = (trajectory_score - trajectory_score.mean()) / trajectory_score.std()

    trajectory_score = trajectory_score.clip(-3, 3)

    trajectory_score = trajectory_score.replace([np.inf, -np.inf], np.nan)
    trajectory_score = trajectory_score.fillna(trajectory_score.median())

    return trajectory_score, model