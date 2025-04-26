from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database.database import Base

class ApplicationStatus(str, enum.Enum):
    """
    Enum for application status tracking
    """
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    REVIEW = "review"
    EXPIRED = "expired"

class User(Base):
    """
    User model for authentication and application ownership
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship - one user can have many applications
    applications = relationship("InsuranceApplication", back_populates="user")

class InsuranceApplication(Base):
    """
    Insurance application model
    
    Stores all application data including medical history and risk factors as JSON
    for flexibility. Also tracks application status and AI recommendations.
    """
    __tablename__ = "insurance_applications"

    id = Column(Integer, primary_key=True, index=True)
    applicant_name = Column(String, index=True)
    applicant_age = Column(Integer)
    email = Column(String, index=True)
    phone = Column(String)
    medical_history = Column(JSON)
    risk_factors = Column(JSON)
    coverage_amount = Column(Float)
    premium_amount = Column(Float, nullable=True)
    is_approved = Column(Boolean, default=False)
    ai_recommendation = Column(String, nullable=True)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationship to user
    user = relationship("User", back_populates="applications")
    
    # Relationship to risk score (one-to-one)
    risk_score = relationship("RiskScore", uselist=False, back_populates="application", cascade="all, delete-orphan")

class RiskScore(Base):
    """
    Risk score model
    
    Stores detailed risk assessment factors for an application
    """
    __tablename__ = "risk_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("insurance_applications.id"), unique=True)
    overall_score = Column(Float)
    medical_factor = Column(Float)
    age_factor = Column(Float)
    lifestyle_factor = Column(Float)
    assessment_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship back to application
    application = relationship("InsuranceApplication", back_populates="risk_score")

class MedicalCondition(Base):
    """
    Medical condition reference data
    
    Contains known medical conditions and their associated risk scores
    """
    __tablename__ = "medical_conditions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    base_risk_score = Column(Float, default=0.0)
    category = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 