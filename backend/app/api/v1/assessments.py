from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.entities import User, Participant, Assessment, AuditLog
from backend.app.schemas.api_schemas import AssessmentCreate, AssessmentResponse
from backend.app.ml.inference_service import ml_service

router = APIRouter()

@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment_in: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify participant belongs to user's organization
    stmt_p = select(Participant).where(
        Participant.id == assessment_in.participant_id,
        Participant.organization_id == current_user.organization_id
    )
    participant = (await db.execute(stmt_p)).scalars().first()
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found or access denied."
        )

    # Run ML Prediction & Frailty Calculation
    ml_output = ml_service.predict(assessment_in.model_dump(), age=participant.age)

    assessment = Assessment(
        participant_id=participant.id,
        assessor_id=current_user.id,
        assessment_date=assessment_in.assessment_date or datetime.utcnow(),
        height_cm=assessment_in.height_cm,
        weight_kg=assessment_in.weight_kg,
        bmi=ml_output["bmi"],
        systolic_bp=assessment_in.systolic_bp,
        diastolic_bp=assessment_in.diastolic_bp,
        pulse_bpm=assessment_in.pulse_bpm,
        spo2_pct=assessment_in.spo2_pct,
        temperature_c=assessment_in.temperature_c,
        respiratory_rate=assessment_in.respiratory_rate,
        waist_cm=assessment_in.waist_cm,
        hip_cm=assessment_in.hip_cm,
        mid_upper_arm_circ_cm=assessment_in.mid_upper_arm_circ_cm,
        chest_cm=assessment_in.chest_cm,
        has_diabetes=assessment_in.has_diabetes,
        has_hypertension=assessment_in.has_hypertension,
        has_stroke=assessment_in.has_stroke,
        has_heart_disease=assessment_in.has_heart_disease,
        walking_difficulty=assessment_in.walking_difficulty,
        stairs_difficulty=assessment_in.stairs_difficulty,
        chair_rise_difficulty=assessment_in.chair_rise_difficulty,
        memory_score=assessment_in.memory_score,
        recall_score=assessment_in.recall_score,
        medications_count=assessment_in.medications_count,
        medications_list=assessment_in.medications_list,
        is_polypharmacy=ml_output["is_polypharmacy"],
        frailty_index=ml_output["frailty_index"],
        decline_probability=ml_output["decline_probability"],
        trajectory_score=ml_output["trajectory_score"],
        trajectory_category=ml_output["trajectory_category"],
        overall_risk_score=ml_output["overall_risk_score"],
        risk_tier=ml_output["risk_tier"],
        estimated_years_to_independence_loss=ml_output["estimated_years_to_independence_loss"],
        model_version=ml_output["model_version"],
        schema_version=ml_output["schema_version"],
        shap_contributions=ml_output["shap_contributions"],
        clinical_recommendations=ml_output["clinical_recommendations"]
    )
    db.add(assessment)
    
    # Audit trail
    audit = AuditLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action="CREATE_ASSESSMENT",
        resource_type="Assessment",
        details={
            "participant_code": participant.participant_code,
            "risk_tier": ml_output["risk_tier"],
            "frailty_index": ml_output["frailty_index"]
        }
    )
    db.add(audit)
    
    await db.commit()
    await db.refresh(assessment)
    return assessment

@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Assessment).join(Participant).where(
        Assessment.id == assessment_id,
        Participant.organization_id == current_user.organization_id
    )
    assessment = (await db.execute(stmt)).scalars().first()
    if not assessment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assessment not found.")
    return assessment
