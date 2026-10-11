import pandas as pd
import numpy as np


def compute_domain_score(df, columns):
    """
    Aggregate a domain (e.g., mobility, cognition)
    """
    subset = df[columns].apply(pd.to_numeric, errors="coerce")
    return subset.mean(axis=1)


def compute_trajectory_score(w1_score, w2_score, w3_score):
    """
    Compute change pattern
    """
    delta1 = w2_score - w1_score
    delta2 = w3_score - w2_score

    return delta1, delta2


def assign_trajectory_class(delta1, delta2):
    """
    Rule-based trajectory classification
    """

    traj = []

    for d1, d2 in zip(delta1, delta2):
        if pd.isna(d1) or pd.isna(d2):
            traj.append("Unknown")

        elif d1 <= 0 and d2 <= 0:
            traj.append("Stable")

        elif d1 > 0 and d2 > 0:
            traj.append("Rapid Decline")

        elif d1 > 0 and d2 <= 0:
            traj.append("Recovery")

        elif d1 <= 0 and d2 > 0:
            traj.append("Late Decline")

        else:
            traj.append("Mixed")

    return pd.Series(traj)