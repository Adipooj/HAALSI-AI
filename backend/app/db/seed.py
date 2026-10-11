import asyncio
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

        print("[Seed] Creating Demo Participants & Longitudinal Assessments...")
        demo_patients = [
            {
                "code": "HAALSI-IND-001",
                "age": 74,
                "gender": "Female",
                "phone": "+91 98765 43210",
                "caregiver": "Rohan Sharma (Son)",
                "data": {
                    "height_cm": 156.0,
                    "weight_kg": 72.0,
                    "systolic_bp": 145.0,
                    "diastolic_bp": 88.0,
                    "has_diabetes": True,
                    "has_hypertension": True,
                    "walking_difficulty": 1,
                    "stairs_difficulty": 2,
                    "chair_rise_difficulty": 1,
                    "memory_score": 7.5,
                    "recall_score": 6.0,
                    "medications_count": 6,
                    "medications_list": ["Metformin", "Amlodipine", "Atorvastatin", "Aspirin", "Pantoprazole", "Paracetamol"]
                }
            },
            {
                "code": "HAALSI-IND-002",
                "age": 68,
                "gender": "Male",
                "phone": "+91 98123 45678",
                "caregiver": "Ananya Sen (Daughter)",
                "data": {
                    "height_cm": 170.0,
                    "weight_kg": 65.0,
                    "systolic_bp": 125.0,
                    "diastolic_bp": 80.0,
                    "has_diabetes": False,
                    "has_hypertension": False,
                    "walking_difficulty": 0,
                    "stairs_difficulty": 0,
                    "chair_rise_difficulty": 0,
                    "memory_score": 10.0,
                    "recall_score": 9.5,
                    "medications_count": 1,
                    "medications_list": ["Multivitamin"]
                }
            },
            {
                "code": "HAALSI-IND-003",
                "age": 82,
                "gender": "Female",
                "phone": "+91 98345 67890",
                "caregiver": "Suresh Patel (Husband)",
                "data": {
                    "height_cm": 150.0,
                    "weight_kg": 44.0,
                    "systolic_bp": 160.0,
                    "diastolic_bp": 95.0,
                    "has_diabetes": True,
                    "has_hypertension": True,
                    "has_stroke": True,
                    "walking_difficulty": 2,
                    "stairs_difficulty": 2,
                    "chair_rise_difficulty": 2,
                    "memory_score": 4.5,
                    "recall_score": 4.0,
                    "medications_count": 7,
                    "medications_list": ["Clopidogrel", "Telmisartan", "Hydrochlorothiazide", "Glimepiride", "Metformin", "Donepezil", "Calcium-D3"]
                }
            }
        ]

        for p_info in demo_patients:
            p = Participant(
                organization_id=org.id,
                participant_code=p_info["code"],
                age=p_info["age"],
                gender=p_info["gender"],
                contact_phone=p_info["phone"],
                caregiver_name=p_info["caregiver"],
                caregiver_phone=p_info["phone"],
                is_demo=True
            )
            session.add(p)
            await session.flush()

            # Predict and create assessment
            pred = ml_service.predict(p_info["data"], age=p_info["age"])
            d = p_info["data"]
            
            a = Assessment(
                participant_id=p.id,
                assessor_id=user.id,
                height_cm=d["height_cm"],
                weight_kg=d["weight_kg"],
                bmi=pred["bmi"],
                systolic_bp=d["systolic_bp"],
                diastolic_bp=d["diastolic_bp"],
                has_diabetes=d["has_diabetes"],
                has_hypertension=d["has_hypertension"],
                has_stroke=d.get("has_stroke", False),
                has_heart_disease=d.get("has_heart_disease", False),
                walking_difficulty=d["walking_difficulty"],
                stairs_difficulty=d["stairs_difficulty"],
                chair_rise_difficulty=d["chair_rise_difficulty"],
                memory_score=d["memory_score"],
                recall_score=d["recall_score"],
                medications_count=d["medications_count"],
                medications_list=d["medications_list"],
                is_polypharmacy=pred["is_polypharmacy"],
                frailty_index=pred["frailty_index"],
                decline_probability=pred["decline_probability"],
                trajectory_score=pred["trajectory_score"],
                trajectory_category=pred["trajectory_category"],
                overall_risk_score=pred["overall_risk_score"],
                risk_tier=pred["risk_tier"],
                estimated_years_to_independence_loss=pred["estimated_years_to_independence_loss"],
                model_version=pred["model_version"],
                schema_version=pred["schema_version"],
                shap_contributions=pred["shap_contributions"],
                clinical_recommendations=pred["clinical_recommendations"]
            )
            session.add(a)

        await session.commit()
        print("[Seed] Seed data successfully generated!")

if __name__ == "__main__":
    asyncio.run(seed_data())
