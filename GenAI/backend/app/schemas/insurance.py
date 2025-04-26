from typing import Dict, Optional, List, Union, Any
from pydantic import BaseModel, EmailStr, Field, validator, constr, ConfigDict
from datetime import datetime
import re
from enum import Enum

class ApplicationStatus(str, Enum):
    """
    Application status enum for API responses
    """
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    REVIEW = "review"
    EXPIRED = "expired"

class MedicalHistoryBase(BaseModel):
    """
    Medical history information for an insurance application
    """
    conditions: List[str] = Field(
        default_factory=list,
        description="List of medical conditions (e.g., 'diabetes', 'hypertension')"
    )
    medications: List[str] = Field(
        default_factory=list,
        description="List of current medications"
    )
    surgeries: List[str] = Field(
        default_factory=list,
        description="List of past surgeries"
    )
    allergies: List[str] = Field(
        default_factory=list,
        description="List of known allergies"
    )
    
    @validator('conditions', 'medications', 'surgeries', 'allergies')
    def validate_string_lists(cls, value):
        if not all(isinstance(item, str) and len(item.strip()) > 0 for item in value):
            raise ValueError("All items must be non-empty strings")
        return value
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to a JSON-compatible dictionary"""
        return self.model_dump()

class RiskFactorsBase(BaseModel):
    """
    Risk factors information for an insurance application
    """
    smoking: bool = Field(
        False,
        description="Whether the applicant is a smoker"
    )
    alcohol_consumption: bool = Field(
        False,
        description="Whether the applicant consumes alcohol regularly"
    )
    dangerous_activities: List[str] = Field(
        default_factory=list,
        description="List of dangerous activities (e.g., 'skydiving', 'rock climbing')"
    )
    occupation_risk: str = Field(
        "low",
        description="Occupation risk level: 'low', 'medium', or 'high'"
    )
    
    @validator('occupation_risk')
    def validate_occupation_risk(cls, value):
        valid_values = ['low', 'medium', 'high']
        if value.lower() not in valid_values:
            raise ValueError(f"Occupation risk must be one of: {', '.join(valid_values)}")
        return value.lower()
    
    @validator('dangerous_activities')
    def validate_activities(cls, value):
        if not all(isinstance(item, str) and len(item.strip()) > 0 for item in value):
            raise ValueError("All activities must be non-empty strings")
        return value
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to a JSON-compatible dictionary"""
        return self.model_dump()
    
    def calculate_risk_contribution(self) -> float:
        """
        Calculate the risk contribution of these factors
        
        Returns a value between 0.0 and 1.0
        """
        base_risk = 0.0
        
        # Smoking is a major risk factor
        if self.smoking:
            base_risk += 0.3
        
        # Alcohol is a moderate risk factor
        if self.alcohol_consumption:
            base_risk += 0.15
        
        # Each dangerous activity adds risk
        activity_risk = min(0.4, len(self.dangerous_activities) * 0.1)
        base_risk += activity_risk
        
        # Occupation risk
        occupation_risk_map = {"low": 0.0, "medium": 0.15, "high": 0.25}
        base_risk += occupation_risk_map.get(self.occupation_risk, 0.0)
        
        # Cap at 1.0
        return min(1.0, base_risk)

class RiskScoreBase(BaseModel):
    """
    Risk score information for an insurance application
    """
    overall_score: float = Field(..., ge=0.0, le=1.0)
    medical_factor: float = Field(..., ge=0.0, le=1.0)
    age_factor: float = Field(..., ge=0.0, le=1.0)
    lifestyle_factor: float = Field(..., ge=0.0, le=1.0)
    assessment_notes: Optional[str] = None

class RiskScoreCreate(RiskScoreBase):
    """Schema for creating a new risk score"""
    application_id: int
    
class RiskScoreResponse(RiskScoreBase):
    """Schema for returning a risk score"""
    id: int
    application_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class InsuranceApplicationBase(BaseModel):
    """
    Base schema for insurance applications
    """
    applicant_name: constr(min_length=2, max_length=100) = Field(
        ...,
        description="Full name of the applicant (2-100 characters)"
    )
    applicant_age: int = Field(
        ..., 
        gt=17, 
        lt=120,
        description="Age of the applicant (18-119)"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    phone: str = Field(
        ...,
        description="Phone number in any format"
    )
    medical_history: MedicalHistoryBase = Field(
        ...,
        description="Medical history information"
    )
    risk_factors: RiskFactorsBase = Field(
        ...,
        description="Risk factors information"
    )
    coverage_amount: float = Field(
        ..., 
        gt=0,
        le=10000000,
        description="Requested coverage amount (1-10,000,000)"
    )
    
    @validator('phone')
    def validate_phone(cls, value):
        # Remove common separators for validation
        clean_phone = re.sub(r'[\s\-\(\)\.]+', '', value)
        # Check if it's a valid phone number (simple check)
        if not clean_phone.isdigit() or len(clean_phone) < 7:
            raise ValueError("Invalid phone number format")
        return value
    
    @validator('applicant_name')
    def validate_name(cls, value):
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', value):
            raise ValueError("Name contains invalid characters")
        return value
    
    def to_orm_model(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for ORM model creation"""
        return {
            "applicant_name": self.applicant_name,
            "applicant_age": self.applicant_age,
            "email": self.email,
            "phone": self.phone,
            "medical_history": self.medical_history.to_json(),
            "risk_factors": self.risk_factors.to_json(),
            "coverage_amount": self.coverage_amount
        }

class InsuranceApplicationCreate(InsuranceApplicationBase):
    """
    Schema for creating a new insurance application
    
    Extends the base schema and optionally associates with a user
    """
    user_id: Optional[int] = None
    notes: Optional[str] = None

class InsuranceApplicationUpdate(BaseModel):
    """
    Schema for updating an existing insurance application
    
    All fields are optional to allow partial updates
    """
    applicant_name: Optional[constr(min_length=2, max_length=100)] = None
    applicant_age: Optional[int] = Field(None, gt=17, lt=120)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    medical_history: Optional[MedicalHistoryBase] = None
    risk_factors: Optional[RiskFactorsBase] = None
    coverage_amount: Optional[float] = Field(None, gt=0, le=10000000)
    premium_amount: Optional[float] = None
    is_approved: Optional[bool] = None
    ai_recommendation: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    notes: Optional[str] = None
    
    @validator('phone')
    def validate_phone(cls, value):
        if value is None:
            return value
        # Remove common separators for validation
        clean_phone = re.sub(r'[\s\-\(\)\.]+', '', value)
        # Check if it's a valid phone number (simple check)
        if not clean_phone.isdigit() or len(clean_phone) < 7:
            raise ValueError("Invalid phone number format")
        return value

class InsuranceApplicationResponse(BaseModel):
    """
    Schema for returning an insurance application
    """
    id: int
    applicant_name: str
    applicant_age: int
    email: EmailStr
    phone: str
    medical_history: Dict[str, Any]
    risk_factors: Dict[str, Any]
    coverage_amount: float
    premium_amount: Optional[float] = None
    is_approved: bool = False
    ai_recommendation: Optional[str] = None
    status: ApplicationStatus
    notes: Optional[str] = None
    user_id: Optional[int] = None
    risk_score: Optional[RiskScoreResponse] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, db_obj):
        """Create a response model from a database model with proper handling of nested objects"""
        # Handle risk score relationship
        risk_score_data = None
        if hasattr(db_obj, 'risk_score') and db_obj.risk_score:
            risk_score_data = RiskScoreResponse.model_validate(db_obj.risk_score)
        
        # Create the response
        return cls(
            id=db_obj.id,
            applicant_name=db_obj.applicant_name,
            applicant_age=db_obj.applicant_age,
            email=db_obj.email,
            phone=db_obj.phone,
            medical_history=db_obj.medical_history,
            risk_factors=db_obj.risk_factors,
            coverage_amount=db_obj.coverage_amount,
            premium_amount=db_obj.premium_amount,
            is_approved=db_obj.is_approved,
            ai_recommendation=db_obj.ai_recommendation,
            status=db_obj.status if hasattr(db_obj, 'status') else ApplicationStatus.PENDING,
            notes=db_obj.notes if hasattr(db_obj, 'notes') else None,
            user_id=db_obj.user_id if hasattr(db_obj, 'user_id') else None,
            risk_score=risk_score_data,
            created_at=db_obj.created_at,
            updated_at=db_obj.updated_at
        )

class PremiumCalculationRequest(BaseModel):
    """
    Schema for requesting a premium calculation
    """
    applicant_age: int = Field(
        ..., 
        gt=17, 
        lt=120,
        description="Age of the applicant (18-119)"
    )
    coverage_amount: float = Field(
        ..., 
        gt=0,
        le=10000000,
        description="Requested coverage amount (1-10,000,000)"
    )
    medical_history: MedicalHistoryBase = Field(
        ...,
        description="Medical history information"
    )
    risk_factors: RiskFactorsBase = Field(
        ...,
        description="Risk factors information"
    )
    calculation_mode: Optional[str] = Field(
        "standard",
        description="Calculation mode: 'standard', 'detailed', or 'quick'"
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for API processing"""
        return {
            "applicant_age": self.applicant_age,
            "coverage_amount": self.coverage_amount,
            "medical_history": self.medical_history.to_json(),
            "risk_factors": self.risk_factors.to_json(),
            "calculation_mode": self.calculation_mode
        }

class PremiumCalculationResponse(BaseModel):
    """
    Schema for premium calculation response
    """
    premium_amount: float
    risk_assessment: str
    ai_recommendation: str
    factors: Dict[str, Any] = Field(
        default_factory=dict,
        description="Breakdown of factors affecting the premium calculation"
    )
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to a JSON-compatible dictionary"""
        return self.model_dump()
    
    def to_application_response(self, application_id: int) -> Dict[str, Any]:
        """Convert to a format suitable for application update"""
        return {
            "premium_amount": self.premium_amount,
            "ai_recommendation": self.ai_recommendation,
            "is_approved": "decline" not in self.risk_assessment.lower(),
            "status": ApplicationStatus.APPROVED if "decline" not in self.risk_assessment.lower() else ApplicationStatus.DECLINED
        }

# User-related schemas
class UserBase(BaseModel):
    """Base schema for user data"""
    username: str
    email: EmailStr
    
class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8)
    role: Optional[str] = "user"
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Ensure password meets minimum security requirements"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None
    
    @validator('password')
    def validate_password_strength(cls, v):
        if v is None:
            return v
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v

class UserResponse(BaseModel):
    """Schema for user responses"""
    id: int
    username: str
    email: EmailStr
    is_active: bool
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

# Token schemas
class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    token_type: str
    expires_in: int = 3600  # Default 1 hour expiry

class TokenData(BaseModel):
    """Schema for token payload data"""
    username: str
    expires: Optional[datetime] = None
    scopes: List[str] = []
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.expires:
            return False
        return datetime.utcnow() > self.expires 