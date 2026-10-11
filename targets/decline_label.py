from __future__ import annotations

import pandas as pd
import numpy as np


def compute_decline_label(X_w1: pd.DataFrame, X_w2: pd.DataFrame) -> pd.Series:
    """
    Compute decline using domain-aligned aggregation.

    Works for HAALSI where W1 and W2 variable names differ.
    """

    # -----------------------
    # Extract domains
    # -----------------------
    def group_by_domain(df):
        domain_map = {}

        for col in df.columns:
            if "__" not in col:
                continue

            domain = col.split("__")[0]

            if domain not in domain_map:
                domain_map[domain] = []

            domain_map[domain].append(col)

        return domain_map

    w1_domains = group_by_domain(X_w1)
    w2_domains = group_by_domain(X_w2)

    common_domains = set(w1_domains.keys()).intersection(w2_domains.keys())

    if not common_domains:
        raise ValueError("No overlapping domains between W1 and W2.")

    w1_scores = []
    w2_scores = []

    # -----------------------
    # Compute per-domain scores
    # -----------------------
    for d in common_domains:

        w1_cols = w1_domains[d]
        w2_cols = w2_domains[d]

        if not w1_cols or not w2_cols:
            continue

        w1_block = X_w1[w1_cols].apply(pd.to_numeric, errors="coerce")
        w2_block = X_w2[w2_cols].apply(pd.to_numeric, errors="coerce")

        # Standardize within domain
        w1_std = (w1_block - w1_block.mean()) / w1_block.std(ddof=0)
        w2_std = (w2_block - w2_block.mean()) / w2_block.std(ddof=0)

        w1_scores.append(w1_std.mean(axis=1))
        w2_scores.append(w2_std.mean(axis=1))

    if not w1_scores:
        raise ValueError("No usable domains for decline computation.")

    # -----------------------
    # Aggregate across domains
    # -----------------------
    score_w1 = pd.concat(w1_scores, axis=1).mean(axis=1)
    score_w2 = pd.concat(w2_scores, axis=1).mean(axis=1)

    # -----------------------
    # Decline
    # -----------------------
    delta = score_w2 - score_w1

    y = (delta > 0).astype(int)

    return y