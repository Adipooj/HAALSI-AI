import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    participants = relationship("Participant", back_populates="organization", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="clinician", nullable=False)  # admin, clinician, researcher, reviewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="users")
    assessments = relationship("Assessment", back_populates="assessor")

class Participant(Base):
    __tablename__ = "participants"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    participant_code = Column(String(100), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)  # Male, Female, Other
    contact_phone = Column(String(50), nullable=True)
    caregiver_name = Column(String(255), nullable=True)
    caregiver_phone = Column(String(50), nullable=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="participants")
    assessments = relationship("Assessment", back_populates="participant", cascade="all, delete-orphan")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    participant_id = Column(String(36), ForeignKey("participants.id"), nullable=False, index=True)
    assessor_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Clinical Raw Inputs
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    systolic_bp = Column(Float, nullable=True)
    diastolic_bp = Column(Float, nullable=True)
    has_diabetes = Column(Boolean, default=False)
    has_hypertension = Column(Boolean, default=False)
    has_stroke = Column(Boolean, default=False)
    has_heart_disease = Column(Boolean, default=False)
    walking_difficulty = Column(Integer, default=0) # 0=none, 1=some, 2=severe
    stairs_difficulty = Column(Integer, default=0)
    chair_rise_difficulty = Column(Integer, default=0)
    memory_score = Column(Float, default=10.0)
    recall_score = Column(Float, default=10.0)
    
    # Medication Review
    medications_count = Column(Integer, default=0)
    medications_list = Column(JSON, nullable=True) # list of med names
    is_polypharmacy = Column(Boolean, default=False) # count >= 5
    
    # ML Computed Outputs
    frailty_index = Column(Float, nullable=False)
    decline_probability = Column(Float, nullable=False)
    trajectory_score = Column(Float, nullable=False)
    trajectory_category = Column(String(50), nullable=False)  # Stable, Moderate Decline, Rapid Decline
    overall_risk_score = Column(Float, nullable=False)
    risk_tier = Column(String(50), nullable=False)  # Low, Moderate, High
    estimated_years_to_independence_loss = Column(Integer, nullable=True)
    
    # Model Lineage & Explanations
    model_version = Column(String(50), default="1.0.0")
    schema_version = Column(String(50), default="1.0.0")
    shap_contributions = Column(JSON, nullable=True)
    clinical_recommendations = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    participant = relationship("Participant", back_populates="assessments")
    assessor = relationship("User", back_populates="assessments")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    organization_id = Column(String(36), nullable=False, index=True)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False) # e.g. "CREATE_ASSESSMENT", "LOGIN", "EXPORT_REPORT"
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
