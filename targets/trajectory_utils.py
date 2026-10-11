import pandas as pd
import numpy as np


def zscore(series):
    mean = series.mean()
    std = series.std()
    if std == 0 or pd.isna(std):
        return pd.Series(0, index=series.index)
    return (series - mean) / std


def compute_domain_score(df, columns):
    """
    Standardized domain score (robust)
    """

    subset = df[columns].apply(pd.to_numeric, errors="coerce")

    # Normalize each variable
    subset = subset.apply(zscore)

    # Average
    score = subset.mean(axis=1)

    return score