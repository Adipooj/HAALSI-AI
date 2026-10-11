from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from config.haalsi_config import (
    DATA_PATH,
    MODEL_FILE,
    FEATURE_COLUMNS_FILE,
    FEATURE_DEFAULTS_FILE,
    SCHEMA_FILE,
    ARTIFACT_DIR,
)

from data.loader import load_haalsi_data
from data.preprocessing import clean_missing_values, standardize_column_names

from features.feature_builder import (
    build_domain_variable_lists,
    build_feature_table,
)
from features.frailty_index import compute_frailty_index

from targets.decline_label import compute_decline_label
from pipeline.trajectory_pipeline import build_trajectory_labels

from models.decline_model import train_decline_model
from models.trajectory_model import train_trajectory_model

from inference.schema import SchemaArtifact


def ensure_dirs() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)


def _coerce_numeric_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def build_training_matrices(df, domain_varlists):

    # -----------------------
    # BASELINE FEATURES (W1 ONLY)
    # -----------------------
    X = build_feature_table(df, domain_varlists, wave="W1")

    if X.empty:
        raise ValueError("No W1 features found.")

    # -----------------------
    # NUMERIC CLEAN
    # -----------------------
    for c in X.columns:
        X[c] = pd.to_numeric(X[c], errors="coerce")

    # -----------------------
    # DOMAIN GROUPING
    # -----------------------
    domain_map = {}
    for col in X.columns:
        if "__" not in col:
            continue
        domain = col.split("__")[0]
        domain_map.setdefault(domain, []).append(col)

    # -----------------------
    # DOMAIN-LEVEL FEATURES (HIGH IMPACT)
    # -----------------------
    for d, cols in domain_map.items():

        block = X[cols]

        # Mean health
        X[f"{d}_mean"] = block.mean(axis=1)

        # Variability within domain
        if len(cols) > 1:
            X[f"{d}_std"] = block.std(axis=1)

        # Missingness
        X[f"{d}_missing_frac"] = block.isna().mean(axis=1)

        # Impairment proxy (below median)
        median_val = block.median().median()
        X[f"{d}_impairment"] = (block.mean(axis=1) < median_val).astype(int)

        X[f"{d}_count"] = block.notna().sum(axis=1)

    # -----------------------
    # GLOBAL FEATURES
    # -----------------------
    X["global_mean"] = X.mean(axis=1)
    X["global_missing"] = X.isna().mean(axis=1)

    global_std = X.std(axis=1)
    X["health_index"] = X["global_mean"] / (1 + global_std)

    # Frailty
    X["frailty_index"] = compute_frailty_index(X)

    # -----------------------
    # INTERACTIONS (VERY IMPORTANT)
    # -----------------------
    if "age_proxy" in X.columns:
        X["age_frailty"] = X["age_proxy"] * X["frailty_index"]

    # -----------------------
    # FOLLOW-UP (ONLY FOR LABEL)
    # -----------------------
    follow = build_feature_table(df, domain_varlists, wave="W2")

    y_decline = compute_decline_label(X, follow)

    # -----------------------
    # TRAJECTORY
    # -----------------------
    y_trajectory, traj_cluster_model = build_trajectory_labels(df, domain_varlists)

    # -----------------------
    # FINAL CLEAN
    # -----------------------
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median(numeric_only=True))

    y_decline = y_decline.reindex(X.index).fillna(0).astype(int)
    y_trajectory = y_trajectory.reindex(X.index)

    return X, y_decline, y_trajectory, traj_cluster_model


def run_training():
    print("\n[PIPELINE] Starting HAALSI training pipeline...\n")
    ensure_dirs()

    # Load and clean
    df = load_haalsi_data(DATA_PATH)
    df = standardize_column_names(df)
    df = clean_missing_values(df)
    print("[INFO] Data cleaned")

    # Build domain map directly from the dataset
    domain_varlists = build_domain_variable_lists(df)
    print(f"[INFO] Domains detected: {list(domain_varlists.keys())}")

    # Build matrices
    print("[INFO] Building training matrices...")
    X, y_decline, y_trajectory, traj_cluster_model = build_training_matrices(df, domain_varlists)
    print(f"[INFO] Feature matrix shape: {X.shape}")

    # Decline model
    print("\n[MODEL] Training decline model...")
    decline_bundle = train_decline_model(X, y_decline)
    joblib.dump(decline_bundle.model, MODEL_FILE)
    joblib.dump(decline_bundle.model, MODEL_FILE.parent / "decline_model.joblib")

    # Trajectory model
    print("\n[MODEL] Training trajectory model...")
    trajectory_model = train_trajectory_model(X, y_trajectory)
    joblib.dump(trajectory_model, MODEL_FILE.parent / "trajectory_model.joblib")
    joblib.dump(traj_cluster_model, MODEL_FILE.parent / "trajectory_cluster_model.joblib")

    # --------------------------------------------------
    # PART 1 — TRAJECTORY OUTPUT CALIBRATION & SCALING
    # --------------------------------------------------
    from sklearn.preprocessing import QuantileTransformer
    trajectory_scaler = QuantileTransformer(n_quantiles=1000, random_state=42, output_distribution='uniform')
    trajectory_scaler.fit(y_trajectory.to_numpy().reshape(-1, 1))
    joblib.dump(trajectory_scaler, MODEL_FILE.parent / "trajectory_scaler.joblib")

    # Compute percentiles on the scaled values (since the scaler transforms targets into percentiles)
    y_trajectory_scaled = trajectory_scaler.transform(y_trajectory.to_numpy().reshape(-1, 1)).flatten()
    
    # Save raw and scaled thresholds
    raw_t33 = float(np.percentile(y_trajectory, 33))
    raw_t66 = float(np.percentile(y_trajectory, 66))
    scaled_t33 = float(np.percentile(y_trajectory_scaled, 33))
    scaled_t66 = float(np.percentile(y_trajectory_scaled, 66))
    
    thresholds = {
        "raw_lower": raw_t33,
        "raw_upper": raw_t66,
        "scaled_lower": scaled_t33,
        "scaled_upper": scaled_t66
    }
    
    with open(MODEL_FILE.parent / "trajectory_thresholds.json", "w", encoding="utf-8") as f:
        json.dump(thresholds, f, indent=2)

    # --------------------------------------------------
    # PART 7 — VALIDATION IMPROVEMENT (CROSS-VALIDATION)
    # --------------------------------------------------
    from sklearn.model_selection import StratifiedKFold, KFold
    from sklearn.metrics import roc_auc_score, r2_score
    from models.decline_model import build_model, calibrate_model
    from xgboost import XGBRegressor

    print("\n[CV] Running 5-fold cross-validation...")

    # CV for decline model
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    decline_auc_scores = []
    for train_idx, test_idx in skf.split(X, y_decline):
        X_train_cv, X_test_cv = X.iloc[train_idx], X.iloc[test_idx]
        y_train_cv, y_test_cv = y_decline.iloc[train_idx], y_decline.iloc[test_idx]
        
        m_decline = build_model(random_state=42)
        calibrated_decline = calibrate_model(m_decline, X_train_cv, y_train_cv)
        
        proba = calibrated_decline.predict_proba(X_test_cv)[:, 1]
        decline_auc_scores.append(roc_auc_score(y_test_cv, proba))
        
    mean_auc = np.mean(decline_auc_scores)
    std_auc = np.std(decline_auc_scores)
    print(f"Decline Model CV AUC: {mean_auc:.4f} ± {std_auc:.4f}")

    # CV for trajectory model
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    traj_r2_scores = []
    for train_idx, test_idx in kf.split(X, y_trajectory):
        X_train_cv, X_test_cv = X.iloc[train_idx], X.iloc[test_idx]
        y_train_cv, y_test_cv = y_trajectory.iloc[train_idx], y_trajectory.iloc[test_idx]
        
        m_traj = XGBRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.03,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42
        )
        m_traj.fit(X_train_cv, y_train_cv)
        preds_cv = m_traj.predict(X_test_cv)
        traj_r2_scores.append(r2_score(y_test_cv, preds_cv))
        
    mean_r2 = np.mean(traj_r2_scores)
    std_r2 = np.std(traj_r2_scores)
    print(f"Trajectory Model CV R2: {mean_r2:.4f} ± {std_r2:.4f}")

    from models.combined_risk import compute_combined_risk

    # Load encoder
    try:
        label_encoder = joblib.load("outputs/models/trajectory_label_encoder.joblib")
    except Exception:
        label_encoder = None

    combined_df = compute_combined_risk(
        decline_bundle.model,
        trajectory_model,
        label_encoder,
        X
    )

    print("\n[INFO] Combined Risk Summary:")
    print(combined_df.describe())

    # Artifacts
    FEATURE_COLUMNS_FILE.write_text(
        json.dumps(list(X.columns), indent=2),
        encoding="utf-8",
    )

    defaults = {str(k): v for k, v in X.median(numeric_only=True).to_dict().items()}
    FEATURE_DEFAULTS_FILE.write_text(
        json.dumps(defaults, indent=2, default=str),
        encoding="utf-8",
    )

    schema = SchemaArtifact(
        feature_columns=list(X.columns),
        feature_defaults=defaults,
        metadata={
            "decline_metrics": decline_bundle.metrics,
            "cv_metrics": {
                "decline_mean_auc": mean_auc,
                "decline_std_auc": std_auc,
                "trajectory_mean_r2": mean_r2,
                "trajectory_std_r2": std_r2
            }
        },
    )
    schema.save(SCHEMA_FILE)

    print("\n[PIPELINE COMPLETE]\n")
    print("Decline Model Metrics:")
    print(json.dumps(decline_bundle.metrics, indent=2))
    print("\nTrajectory Model Saved")
    print("\nArtifacts:")
    print(f"- Model: {MODEL_FILE}")
    print(f"- Trajectory Model: {MODEL_FILE.parent / 'trajectory_model.joblib'}")
    print(f"- Schema: {SCHEMA_FILE}")


if __name__ == "__main__":
    run_training()