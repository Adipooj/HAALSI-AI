from __future__ import annotations

from pathlib import Path
import pandas as pd

from config.haalsi_config import DATA_PATH


def load_haalsi_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_stata(path, convert_categoricals=False, preserve_dtypes=True)
    print(f"[loader] Loaded HAALSI data: {df.shape[0]:,} rows × {df.shape[1]:,} columns")
    return df