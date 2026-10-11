from __future__ import annotations

import pandas as pd
from simulation.aging_simulator import simulate_forward_risk


def estimate_time_to_independence_loss(
    base_features: pd.DataFrame,
    decline_model,
    frailty: pd.Series,
    age: pd.Series,
    threshold: float = 0.75,
    horizons=(1, 2, 3, 5, 7, 10),
) -> int | str:
    """
    Estimate the time to loss of independence based on pseudo-longitudinal forward simulations.
    Returns the earliest simulated horizon year where mean risk exceeds the threshold,
    or "Low long-term risk" if the threshold is never met.
    """
    sim_df = simulate_forward_risk(
        base_features=base_features,
        model=decline_model,
        frailty=frailty,
        age=age,
        horizons=horizons,
        n_simulations=500,
    )

    for _, row in sim_df.iterrows():
        if row["mean_risk"] >= threshold:
            return int(row["horizon_years"])

    return "Low long-term risk"
