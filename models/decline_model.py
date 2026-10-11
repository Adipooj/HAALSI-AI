from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    brier_score_loss,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from xgboost import XGBClassifier

from config.haalsi_config import RANDOM_STATE


@dataclass
class TrainedModelBundle:
    model: Any
    feature_columns: list[str]
    metrics: dict[str, float]


def build_model(random_state: int = RANDOM_STATE) -> Pipeline:
    base = XGBClassifier(
        n_estimators=250,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_lambda=1.0,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=random_state,
        tree_method="hist",
    )

    # XGBoost handles missing values directly, but the imputer keeps the pipeline explicit.
    model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler(with_mean=False)),
            ("clf", base),
        ]
    )
    return model


def calibrate_model(model: Pipeline, X_train: pd.DataFrame, y_train: pd.Series) -> CalibratedClassifierCV:
    calibrator = CalibratedClassifierCV(model, method="sigmoid", cv=3)
    calibrator.fit(X_train, y_train)
    return calibrator


def train_decline_model(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = RANDOM_STATE,
) -> TrainedModelBundle:
    feature_columns = list(X.columns)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        stratify=y if y.nunique() > 1 else None,
        random_state=random_state,
    )

    model = build_model(random_state=random_state)
    calibrated = calibrate_model(model, X_train, y_train)

    proba = calibrated.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, proba) if y_test.nunique() > 1 else float("nan")
    brier = brier_score_loss(y_test, proba) if len(np.unique(y_test)) > 1 else float("nan")

    preds = (proba >= 0.5).astype(int)
    report = classification_report(y_test, preds, output_dict=True, zero_division=0)

    metrics = {
        "auc": float(auc) if auc == auc else np.nan,
        "brier": float(brier) if brier == brier else np.nan,
        "precision": float(report.get("1", {}).get("precision", np.nan)),
        "recall": float(report.get("1", {}).get("recall", np.nan)),
        "f1": float(report.get("1", {}).get("f1-score", np.nan)),
    }

    return TrainedModelBundle(model=calibrated, feature_columns=feature_columns, metrics=metrics)


def save_model_bundle(bundle: TrainedModelBundle, model_path, feature_columns_path=None):
    joblib.dump(bundle.model, model_path)
    if feature_columns_path is not None:
        import json
        from pathlib import Path

        feature_columns_path = Path(feature_columns_path)
        feature_columns_path.parent.mkdir(parents=True, exist_ok=True)
        feature_columns_path.write_text(json.dumps(bundle.feature_columns, indent=2), encoding="utf-8")