# HAALSI AI — Operations Runbook & Local Setup

## Quickstart Instructions

### 1. Backend Setup & Run
Activate the virtual environment and initialize the database:
```powershell
# Set Python path to project root
$env:PYTHONPATH="."

# Seed database with demo participants and clinician credentials
.\venv\Scripts\python -m backend.app.db.seed

# Start the FastAPI Server (Port 8000)
.\venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Frontend Setup & Run
```powershell
cd frontend
npm install
npm run dev
# The frontend will start on http://localhost:3000
```

### 3. Test Credentials
- **Email:** `doctor@haalsi.ai`
- **Password:** `doctor123`

### 4. Running Automated Tests
```powershell
$env:PYTHONPATH="."
.\venv\Scripts\pytest -v tests/test_api.py
```
