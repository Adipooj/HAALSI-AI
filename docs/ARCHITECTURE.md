# HAALSI AI — Architecture Overview

## 1. High-Level Architecture
HAALSI AI is structured as a decoupled, multi-tier clinical analytics system:

1. **Frontend Tier (Vite / React 18 / TypeScript / Tailwind CSS):**
   - High-performance Single Page Application (SPA).
   - Multi-view navigation (Landing Page, Clinician Login, Dashboard, Participants Directory, Longitudinal Profile, Assessment Form).
   - Bilingual i18n support (English and Hindi).
   - Real-time BMI calculation and polypharmacy warnings.

2. **Backend API Tier (FastAPI / Pydantic / SQLAlchemy Async):**
   - Versioned REST API under `/api/v1/`.
   - JWT-based authentication and role-based access control (`clinician`, `admin`, `researcher`).
   - Strict organization-level tenant isolation.
   - Comprehensive audit logging for all clinical modifications.

3. **Machine Learning & Inference Tier (`backend/app/ml/inference_service.py`):**
   - In-memory cached model loading (Calibrated XGBoost Decline Model, Trajectory Model, Quantile Scaler).
   - Deficit-accumulation Frailty Index calculator (11 clinical and functional domains).
   - Composite risk fusion engine ($40\%$ Decline $+ 40\%$ Frailty $+ 20\%$ Age factor).
   - Forward Monte Carlo aging trajectory simulation.
   - Per-assessment SHAP risk driver contributions.

4. **Persistence Tier (SQLite for development / PostgreSQL for production):**
   - Organizations, Users, Participants, Assessments, and Audit Logs.
