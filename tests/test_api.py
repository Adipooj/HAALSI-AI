import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["database"] == "connected"
    assert data["models_loaded"] is True

@pytest.mark.asyncio
async def test_auth_login_and_participants():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Login
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "doctor@haalsi.ai",
            "password": "doctor123"
        })
        assert login_res.status_code == 200
        token_data = login_res.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List Participants
        parts_res = await ac.get("/api/v1/participants/", headers=headers)
        assert parts_res.status_code == 200
        participants = parts_res.json()
        assert len(participants) >= 3

        # Create New Participant
        new_part = await ac.post("/api/v1/participants/", headers=headers, json={
            "participant_code": "HAALSI-TEST-999",
            "age": 75,
            "gender": "Male",
            "contact_phone": "+91 99999 88888"
        })
        assert new_part.status_code == 201
        p_id = new_part.json()["id"]

        # Run Real ML Assessment
        assess_res = await ac.post("/api/v1/assessments/", headers=headers, json={
            "participant_id": p_id,
            "height_cm": 165.0,
            "weight_kg": 68.0,
            "systolic_bp": 140.0,
            "diastolic_bp": 85.0,
            "has_diabetes": True,
            "has_hypertension": True,
            "walking_difficulty": 1,
            "stairs_difficulty": 1,
            "chair_rise_difficulty": 1,
            "memory_score": 8.0,
            "recall_score": 7.5,
            "medications_count": 5,
            "medications_list": ["DrugA", "DrugB", "DrugC", "DrugD", "DrugE"]
        })
        assert assess_res.status_code == 201
        ass_data = assess_res.json()
        assert "frailty_index" in ass_data
        assert "decline_probability" in ass_data
        assert "overall_risk_score" in ass_data
        assert "risk_tier" in ass_data
        assert ass_data["is_polypharmacy"] is True
        assert ass_data["risk_tier"] in ["Low", "Moderate", "High"]

@pytest.mark.asyncio
async def test_dashboard_metrics():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "doctor@haalsi.ai",
            "password": "doctor123"
        })
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        dash_res = await ac.get("/api/v1/dashboard/metrics", headers=headers)
        assert dash_res.status_code == 200
        metrics = dash_res.json()
        assert metrics["total_participants"] >= 3
        assert metrics["total_assessments"] >= 3
