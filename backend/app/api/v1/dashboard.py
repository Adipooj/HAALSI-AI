from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.entities import User, Participant, Assessment
from backend.app.schemas.api_schemas import DashboardMetrics, AssessmentResponse

router = APIRouter()

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    org_id = current_user.organization_id

    # Count participants
    stmt_p = select(func.count(Participant.id)).where(Participant.organization_id == org_id)
    total_participants = (await db.execute(stmt_p)).scalar() or 0

    # Count assessments
    stmt_a = select(func.count(Assessment.id)).join(Participant).where(Participant.organization_id == org_id)
    total_assessments = (await db.execute(stmt_a)).scalar() or 0

    # Tiers
    stmt_high = select(func.count(Assessment.id)).join(Participant).where(
        Participant.organization_id == org_id, Assessment.risk_tier == "High"
    )
    high_count = (await db.execute(stmt_high)).scalar() or 0

    stmt_mod = select(func.count(Assessment.id)).join(Participant).where(
        Participant.organization_id == org_id, Assessment.risk_tier == "Moderate"
    )
    mod_count = (await db.execute(stmt_mod)).scalar() or 0

    stmt_low = select(func.count(Assessment.id)).join(Participant).where(
        Participant.organization_id == org_id, Assessment.risk_tier == "Low"
    )
    low_count = (await db.execute(stmt_low)).scalar() or 0

    # Polypharmacy
    stmt_poly = select(func.count(Assessment.id)).join(Participant).where(
        Participant.organization_id == org_id, Assessment.is_polypharmacy == True
    )
    poly_count = (await db.execute(stmt_poly)).scalar() or 0

    # Average frailty
    stmt_frail = select(func.avg(Assessment.frailty_index)).join(Participant).where(
        Participant.organization_id == org_id
    )
    avg_frailty = (await db.execute(stmt_frail)).scalar() or 0.0

    # Recent assessments
    stmt_recent = select(Assessment).join(Participant).where(
        Participant.organization_id == org_id
    ).order_by(desc(Assessment.assessment_date)).limit(10)
    recent = (await db.execute(stmt_recent)).scalars().all()

    return DashboardMetrics(
        total_participants=total_participants,
        total_assessments=total_assessments,
        high_risk_count=high_count,
        moderate_risk_count=mod_count,
        low_risk_count=low_count,
        polypharmacy_alert_count=poly_count,
        average_frailty_index=round(float(avg_frailty), 3),
        recent_assessments=[AssessmentResponse.from_orm(a) for a in recent]
    )
