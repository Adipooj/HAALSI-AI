import numpy as np
import pandas as pd


def compute_combined_risk(decline_model, trajectory_model, label_encoder, X):

    # -----------------------
    # Decline probability
    # -----------------------
    decline_probs = decline_model.predict_proba(X)[:, 1]

    # -----------------------
    # Trajectory prediction
    # -----------------------
    traj_score = trajectory_model.predict(X)

    # normalize between 0 and 1
    traj_score = (traj_score - traj_score.min()) / (traj_score.max() - traj_score.min())

    # -----------------------
    # Combine risk
    # -----------------------
    combined = 0.6 * decline_probs + 0.4 * traj_score

    # Normalize
    combined = np.clip(combined, 0, 1)

    return pd.DataFrame({
        "decline_risk": decline_probs,
        "trajectory_score": traj_score,
        "combined_risk": combined
    })