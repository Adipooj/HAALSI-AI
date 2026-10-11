import asyncio
from datetime import datetime, timedelta
from backend.app.db.session import AsyncSessionLocal, engine, Base
from backend.app.models.entities import Organization, User, Participant, Assessment
from backend.app.core.security import get_password_hash
from backend.app.ml.inference_service import ml_service

async def seed_data():
    print("[Seed] Initializing database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        print("[Seed] Creating Demo Organization...")
        org = Organization(
            name="AIIMS Delhi Geriatric Medicine Department",
            slug="aiims-geriatrics"
        )
        session.add(org)
        await session.flush()

        print("[Seed] Creating Clinician User...")
        user = User(
            organization_id=org.id,
            email="doctor@haalsi.ai",
            full_name="Dr. Priya Sharma, MD",
            hashed_password=get_password_hash("doctor123"),
            role="clinician"
        )
        session.add(user)
        await session.flush()

        print("[Seed] Creating Longitudinal Nursing Home Patients with Multiple Timepoints...")
        
        # Patient 1: Smt. Kamla Devi (76y) tracked across 3 months showing accelerated decline
        now = datetime.utcnow()
        p1 = Participant(
            organization_id=org.id,
            participant_code="HAALSI-IND-001",
            age=76,
            gender="Female",
            contact_phone="+91 98765 43210",
            caregiver_name="Rohan Sharma (Son)",
            caregiver_phone="+91 98765 43210",
            is_demo=True
        )
        session.add(p1)
        await session.flush()

        # P1 - Wave 1: 3 months ago (Relatively stable)
        p1_m1 = {
            "height_cm": 154.0, "weight_kg": 68.0, "systolic_bp": 132.0, "diastolic_bp": 82.0,
            "pulse_bpm": 74.0, "spo2_pct": 97.0, "temperature_c": 36.7, "respiratory_rate": 16.0,
            "waist_cm": 86.0, "hip_cm": 98.0, "mid_upper_arm_circ_cm": 26.5, "chest_cm": 92.0,
            "has_diabetes": True, "has_hypertension": True,
            "walking_difficulty": 0, "stairs_difficulty": 1, "chair_rise_difficulty": 0,
            "memory_score": 9.0, "recall_score": 8.0, "medications_count": 3,
            "medications_list": ["Metformin", "Amlodipine", "Atorvastatin"]
        }
        pred_p1_m1 = ml_service.predict(p1_m1, age=76)
        a1 = Assessment(
            participant_id=p1.id, assessor_id=user.id, assessment_date=now - timedelta(days=90),
            **p1_m1, **{k: v for k, v in pred_p1_m1.items() if k != "is_polypharmacy"},
            is_polypharmacy=pred_p1_m1["is_polypharmacy"]
        )
        session.add(a1)

        # P1 - Wave 2: 1.5 months ago (Moderate decline after fall)
        p1_m2 = {
            "height_cm": 154.0, "weight_kg": 64.5, "systolic_bp": 142.0, "diastolic_bp": 88.0,
            "pulse_bpm": 82.0, "spo2_pct": 95.0, "temperature_c": 36.8, "respiratory_rate": 18.0,
            "waist_cm": 84.0, "hip_cm": 96.0, "mid_upper_arm_circ_cm": 24.8, "chest_cm": 90.0,
            "has_diabetes": True, "has_hypertension": True,
            "walking_difficulty": 1, "stairs_difficulty": 2, "chair_rise_difficulty": 1,
            "memory_score": 7.5, "recall_score": 6.5, "medications_count": 5,
            "medications_list": ["Metformin", "Amlodipine", "Atorvastatin", "Aspirin", "Pantoprazole"]
        }
        pred_p1_m2 = ml_service.predict(p1_m2, age=76)
        a2 = Assessment(
            participant_id=p1.id, assessor_id=user.id, assessment_date=now - timedelta(days=45),
            **p1_m2, **{k: v for k, v in pred_p1_m2.items() if k != "is_polypharmacy"},
            is_polypharmacy=pred_p1_m2["is_polypharmacy"]
        )
        session.add(a2)

        # P1 - Wave 3: Current assessment (High risk / rapid decline)
        p1_m3 = {
            "height_cm": 154.0, "weight_kg": 61.0, "systolic_bp": 155.0, "diastolic_bp": 94.0,
            "pulse_bpm": 88.0, "spo2_pct": 93.0, "temperature_c": 37.1, "respiratory_rate": 20.0,
            "waist_cm": 82.0, "hip_cm": 93.0, "mid_upper_arm_circ_cm": 22.2, "chest_cm": 88.0,
            "has_diabetes": True, "has_hypertension": True, "has_heart_disease": True,
            "walking_difficulty": 2, "stairs_difficulty": 2, "chair_rise_difficulty": 2,
            "memory_score": 6.0, "recall_score": 5.0, "medications_count": 7,
            "medications_list": ["Metformin", "Amlodipine", "Atorvastatin", "Aspirin", "Pantoprazole", "Torsemide", "Paracetamol"]
        }
        pred_p1_m3 = ml_service.predict(p1_m3, age=76)
        a3 = Assessment(
            participant_id=p1.id, assessor_id=user.id, assessment_date=now - timedelta(days=2),
            **p1_m3, **{k: v for k, v in pred_p1_m3.items() if k != "is_polypharmacy"},
            is_polypharmacy=pred_p1_m3["is_polypharmacy"]
        )
        session.add(a3)

        # Patient 2: Shri Ramesh Sen (68y) stable longitudinal trajectory over 2 months
        p2 = Participant(
            organization_id=org.id,
            participant_code="HAALSI-IND-002",
            age=68,
            gender="Male",
            contact_phone="+91 98123 45678",
            caregiver_name="Ananya Sen (Daughter)",
            caregiver_phone="+91 98123 45678",
            is_demo=True
        )
        session.add(p2)
        await session.flush()

        p2_m1 = {
            "height_cm": 170.0, "weight_kg": 66.0, "systolic_bp": 124.0, "diastolic_bp": 78.0,
            "pulse_bpm": 70.0, "spo2_pct": 98.0, "temperature_c": 36.6, "respiratory_rate": 15.0,
            "waist_cm": 88.0, "hip_cm": 96.0, "mid_upper_arm_circ_cm": 28.0, "chest_cm": 96.0,
            "has_diabetes": False, "has_hypertension": False,
            "walking_difficulty": 0, "stairs_difficulty": 0, "chair_rise_difficulty": 0,
            "memory_score": 10.0, "recall_score": 9.5, "medications_count": 1,
            "medications_list": ["Multivitamin"]
        }
        pred_p2_m1 = ml_service.predict(p2_m1, age=68)
        b1 = Assessment(
            participant_id=p2.id, assessor_id=user.id, assessment_date=now - timedelta(days=60),
            **p2_m1, **{k: v for k, v in pred_p2_m1.items() if k != "is_polypharmacy"},
            is_polypharmacy=pred_p2_m1["is_polypharmacy"]
        )
        session.add(b1)

        p2_m2 = {
            "height_cm": 170.0, "weight_kg": 66.5, "systolic_bp": 122.0, "diastolic_bp": 76.0,
            "pulse_bpm": 68.0, "spo2_pct": 98.0, "temperature_c": 36.5, "respiratory_rate": 14.0,
            "waist_cm": 87.5, "hip_cm": 96.0, "mid_upper_arm_circ_cm": 28.2, "chest_cm": 96.0,
            "has_diabetes": False, "has_hypertension": False,
            "walking_difficulty": 0, "stairs_difficulty": 0, "chair_rise_difficulty": 0,
            "memory_score": 10.0, "recall_score": 9.5, "medications_count": 1,
            "medications_list": ["Multivitamin"]
        }
        pred_p2_m2 = ml_service.predict(p2_m2, age=68)
        b2 = Assessment(
            participant_id=p2.id, assessor_id=user.id, assessment_date=now - timedelta(days=5),
            **p2_m2, **{k: v for k, v in pred_p2_m2.items() if k != "is_polypharmacy"},
            is_polypharmacy=pred_p2_m2["is_polypharmacy"]
        )
        session.add(b2)

        # Patient 3: Smt. Meena Patel (82y)
        p3 = Participant(
            organization_id=org.id,
            participant_code="HAALSI-IND-003",
            age=82,
            gender="Female",
            contact_phone="+91 98345 67890",
            caregiver_name="Suresh Patel (Husband)",
            caregiver_phone="+91 98345 67890",
            is_demo=True
        )
        session.add(p3)
        await session.flush()

        p3_m1 = {
            "height_cm": 150.0, "weight_kg": 44.0, "systolic_bp": 158.0, "diastolic_bp": 94.0,
            "pulse_bpm": 86.0, "spo2_pct": 94.0, "temperature_c": 36.8, "respiratory_rate": 18.0,
            "waist_cm": 78.0, "hip_cm": 88.0, "mid_upper_arm_circ_cm": 21.0, "chest_cm": 82.0,
            "has_diabetes": True, "has_hypertension": True, "has_stroke": True,
            "walking_difficulty": 2, "stairs_difficulty": 2, "chair_rise_difficulty": 2,
            "memory_score": 4.5, "recall_score": 4.0, "medications_count": 7,
            "medications_list": ["Clopidogrel", "Telmisartan", "Hydrochlorothiazide", "Glimepiride", "Metformin", "Donepezil", "Calcium-D3"]
        }
        pred_p3_m1 = ml_service.predict(p3_m1, age=82)
        c1 = Assessment(
            participant_id=p3.id, assessor_id=user.id, assessment_date=now - timedelta(days=1),
            **p3_m1, **{k: v for k, v in pred_p3_m1.items() if k != "is_polypharmacy"},
            is_polypharmacy=pred_p3_m1["is_polypharmacy"]
        )
        session.add(c1)

        await session.commit()
        print("[Seed] Longitudinal multi-wave seed data generated successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
