# Insurance Calculator Models
# Initialized models module 

from app.database.database import Base
from app.models.insurance import User, InsuranceApplication, RiskScore, MedicalCondition, ApplicationStatus

__all__ = [
    "Base",
    "User",
    "InsuranceApplication",
    "RiskScore",
    "MedicalCondition",
    "ApplicationStatus"
] 