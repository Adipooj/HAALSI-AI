from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    organization_id: str
    role: str
    full_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "clinician"
    organization_id: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    organization_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# Participant Schemas
class ParticipantCreate(BaseModel):
    participant_code: str = Field(..., description="Unique participant or patient MRN")
    age: int = Field(..., ge=40, le=120)
    gender: str = Field(..., description="Male, Female, or Other")
    contact_phone: Optional[str] = None
    caregiver_name: Optional[str] = None
    caregiver_phone: Optional[str] = None
    is_demo: bool = False

class ParticipantResponse(BaseModel):
    id: str
    organization_id: str
    participant_code: str
    age: int
    gender: str
    contact_phone: Optional[str]
    caregiver_name: Optional[str]
    caregiver_phone: Optional[str]
    is_demo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Assessment Input & Response Schemas
class AssessmentCreate(BaseModel):
    participant_id: str
    assessment_date: Optional[datetime] = None
    height_cm: Optional[float] = Field(None, ge=50, le=250)
    weight_kg: Optional[float] = Field(None, ge=20, le=300)
    systolic_bp: Optional[float] = Field(None, ge=60, le=260)
    diastolic_bp: Optional[float] = Field(None, ge=40, le=160)
    pulse_bpm: Optional[float] = Field(None, ge=30, le=220, description="Resting heart rate / pulse in BPM")
    spo2_pct: Optional[float] = Field(None, ge=50, le=100, description="Oxygen saturation SpO2 %")
    temperature_c: Optional[float] = Field(None, ge=30, le=45, description="Body temperature in Celsius")
    respiratory_rate: Optional[float] = Field(None, ge=8, le=60, description="Breaths per minute")
    
    # Body Anthropometric Measurements
    waist_cm: Optional[float] = Field(None, ge=30, le=200, description="Waist circumference in cm")
    hip_cm: Optional[float] = Field(None, ge=30, le=200, description="Hip circumference in cm")
    mid_upper_arm_circ_cm: Optional[float] = Field(None, ge=10, le=60, description="Bicep / MUAC circumference in cm")
    chest_cm: Optional[float] = Field(None, ge=40, le=200, description="Chest circumference in cm")
    
    has_diabetes: bool = False
    has_hypertension: bool = False
    has_stroke: bool = False
    has_heart_disease: bool = False
    walking_difficulty: int = Field(0, ge=0, le=2, description="0=None, 1=Some, 2=Severe")
    stairs_difficulty: int = Field(0, ge=0, le=2)
    chair_rise_difficulty: int = Field(0, ge=0, le=2)
    memory_score: float = Field(10.0, ge=0, le=20)
    recall_score: float = Field(10.0, ge=0, le=20)
    
    # Medication Tracking
    medications_count: int = Field(0, ge=0, le=50)
    medications_list: Optional[List[str]] = []

class AssessmentResponse(BaseModel):
    id: str
    participant_id: str
    assessor_id: str
    assessment_date: datetime
    
    # Measurements
    height_cm: Optional[float]
    weight_kg: Optional[float]
    bmi: Optional[float]
    systolic_bp: Optional[float]
    diastolic_bp: Optional[float]
    pulse_bpm: Optional[float]
    spo2_pct: Optional[float]
    temperature_c: Optional[float]
    respiratory_rate: Optional[float]
    waist_cm: Optional[float]
    hip_cm: Optional[float]
    mid_upper_arm_circ_cm: Optional[float]
    chest_cm: Optional[float]
    
    has_diabetes: bool
    has_hypertension: bool
    has_stroke: bool
    has_heart_disease: bool
    walking_difficulty: int
    stairs_difficulty: int
    chair_rise_difficulty: int
    memory_score: float
    recall_score: float
    
    # Polypharmacy
    medications_count: int
    medications_list: Optional[List[str]]
    is_polypharmacy: bool
    
    # Model Predictions
    frailty_index: float
    decline_probability: float
    trajectory_score: float
    trajectory_category: str
    overall_risk_score: float
    risk_tier: str
    estimated_years_to_independence_loss: Optional[int]
    
    # Model Metadata & Explainability
    model_version: str
    schema_version: str
    shap_contributions: Optional[Dict[str, float]]
    clinical_recommendations: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard Metrics
class DashboardMetrics(BaseModel):
    total_participants: int
    total_assessments: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    polypharmacy_alert_count: int
    average_frailty_index: float
    recent_assessments: List[AssessmentResponse]
