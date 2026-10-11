from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor


def _safe_predict_labels(model: XGBClassifier, X_test: pd.DataFrame) -> np.ndarray:
    probs = model.predict_proba(X_test)

    # Multiclass: shape = (n_samples, n_classes)
    if getattr(probs, "ndim", 1) == 2:
        return probs.argmax(axis=1)

    # Binary fallback
    return (probs > 0.5).astype(int)


def train_trajectory_model(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42,
) -> XGBRegressor:
    y = pd.Series(y, index=X.index)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=random_state,
        stratify=None,
    )

    model = XGBRegressor(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    from sklearn.metrics import r2_score, mean_squared_error

    print("\n[INFO] Trajectory Regression Performance:")
    print("R2:", r2_score(y_test, preds))
    print("RMSE:", mean_squared_error(y_test, preds)**0.5)

    return model