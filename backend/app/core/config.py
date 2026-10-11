import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "HAALSI AI Geriatric Decision Support"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "haalsi_production_super_secret_jwt_key_2026_clinical")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./haalsi.db")
    SYNC_DATABASE_URL: str = os.getenv("SYNC_DATABASE_URL", "sqlite:///./haalsi.db")
    
    # Paths to ML artifacts
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
    OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
    MODELS_DIR: Path = OUTPUTS_DIR / "models"
    ARTIFACTS_DIR: Path = OUTPUTS_DIR / "artifacts"
    
    DECLINE_MODEL_PATH: Path = MODELS_DIR / "haalsi_decline_model.joblib"
    TRAJECTORY_MODEL_PATH: Path = MODELS_DIR / "trajectory_model.joblib"
    TRAJECTORY_SCALER_PATH: Path = MODELS_DIR / "trajectory_scaler.joblib"
    TRAJECTORY_THRESHOLDS_PATH: Path = MODELS_DIR / "trajectory_thresholds.json"
    SCHEMA_PATH: Path = ARTIFACTS_DIR / "schema.json"
    
    # Research vs Clinical Mode
    DEPLOYMENT_MODE: str = os.getenv("DEPLOYMENT_MODE", "clinical_evaluation")  # research | clinical_evaluation | demo

    class Config:
        env_file = ".env"

settings = Settings()
