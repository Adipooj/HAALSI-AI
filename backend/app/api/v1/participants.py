from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from backend.app.db.session import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.entities import User, Participant, Assessment
from backend.app.schemas.api_schemas import ParticipantCreate, ParticipantResponse, AssessmentResponse

router = APIRouter()

@router.get("/", response_model=List[ParticipantResponse])
async def list_participants(
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Participant).where(Participant.organization_id == current_user.organization_id)
    if search:
        stmt = stmt.where(Participant.participant_code.ilike(f"%{search}%"))
    stmt = stmt.order_by(desc(Participant.created_at)).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def create_participant(
    participant_in: ParticipantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check uniqueness within organization
    stmt = select(Participant).where(
        Participant.organization_id == current_user.organization_id,
        Participant.participant_code == participant_in.participant_code
    )
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Participant code '{participant_in.participant_code}' already exists in this organization."
        )

    participant = Participant(
        organization_id=current_user.organization_id,
        participant_code=participant_in.participant_code,
        age=participant_in.age,
        gender=participant_in.gender,
        contact_phone=participant_in.contact_phone,
        caregiver_name=participant_in.caregiver_name,
        caregiver_phone=participant_in.caregiver_phone,
        is_demo=participant_in.is_demo
    )
    db.add(participant)
    await db.commit()
    await db.refresh(participant)
    return participant

@router.get("/{participant_id}", response_model=ParticipantResponse)
async def get_participant(
    participant_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Participant).where(
        Participant.id == participant_id,
        Participant.organization_id == current_user.organization_id
    )
    participant = (await db.execute(stmt)).scalars().first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found.")
    return participant

@router.get("/{participant_id}/assessments", response_model=List[AssessmentResponse])
async def get_participant_assessments(
    participant_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Enforce tenant isolation
    stmt_p = select(Participant).where(
        Participant.id == participant_id,
        Participant.organization_id == current_user.organization_id
    )
    participant = (await db.execute(stmt_p)).scalars().first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found.")

    stmt = select(Assessment).where(
        Assessment.participant_id == participant_id
    ).order_by(desc(Assessment.assessment_date))
    result = await db.execute(stmt)
    return result.scalars().all()
