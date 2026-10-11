from pathlib import Path

# Absolute source paths you provided
DATA_PATH = Path(r"T:\HAALSI\ICPSR_36633\DS0001\36633-0001-Data.dta")
CROSSWALK_PATH = Path(r"T:\HAALSI\ICPSR_36633\DS0001\36633-0001-Documentation-crosswalk.xlsx")

# Project-local paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "outputs"
MODEL_DIR = OUTPUT_DIR / "models"
ARTIFACT_DIR = OUTPUT_DIR / "artifacts"
REPORT_DIR = OUTPUT_DIR / "reports"

WAVES = ("W1", "W2", "W3")
MISSING_VALUES = (-97, -98, -99)

# Conservative defaults for the first implementation
TARGET_WAVE_PAIR = ("W1", "W2")
RANDOM_STATE = 42

# Risk fusion weights; retrain/recalibrate later if needed
FRAILTY_WEIGHT = 0.40
DECLINE_WEIGHT = 0.40
AGE_WEIGHT = 0.20

# Core outputs
MODEL_FILE = MODEL_DIR / "haalsi_decline_model.joblib"
CALIBRATOR_FILE = MODEL_DIR / "haalsi_calibrator.joblib"
FEATURE_COLUMNS_FILE = ARTIFACT_DIR / "feature_columns.json"
FEATURE_DEFAULTS_FILE = ARTIFACT_DIR / "feature_defaults.json"
SCHEMA_FILE = ARTIFACT_DIR / "schema.json"
CROSSWALK_CACHE_FILE = ARTIFACT_DIR / "crosswalk_cache.parquet"