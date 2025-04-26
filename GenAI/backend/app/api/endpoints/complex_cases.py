from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.database import get_db
from app.models.insurance import InsuranceApplication
from app.schemas.insurance import InsuranceApplicationCreate, InsuranceApplicationResponse
from app.services.crewai_orchestration import process_complex_application_sync
from app.services.ai_underwriting import UnderwritingRuleEngine

router = APIRouter()

@router.post("/complex-application/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def process_complex_case(application: InsuranceApplicationCreate, db: Session = Depends(get_db)):
    """
    Process a complex insurance application using multiple AI agents
    
    This endpoint:
    1. Takes the application data
    2. Processes it through CrewAI orchestration
    3. Stores the application with the decision in the database
    """
    # Process through CrewAI orchestration
    application_data = {
        "applicant_name": application.applicant_name,
        "applicant_age": application.applicant_age,
        "email": application.email,
        "phone": application.phone,
        "medical_history": application.medical_history.dict(),
        "risk_factors": application.risk_factors.dict(),
        "coverage_amount": application.coverage_amount
    }
    
    # Process using CrewAI
    crew_result = process_complex_application_sync(application_data)
    
    # Create database entry
    db_application = InsuranceApplication(
        applicant_name=application.applicant_name,
        applicant_age=application.applicant_age,
        email=application.email,
        phone=application.phone,
        medical_history=application.medical_history.dict(),
        risk_factors=application.risk_factors.dict(),
        coverage_amount=application.coverage_amount,
        premium_amount=crew_result.get("premium_amount"),
        is_approved=crew_result.get("approved", False),
        ai_recommendation=crew_result.get("recommendation", "")
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    
    # Return the CrewAI result together with the application ID
    result = {
        "application_id": db_application.id,
        **crew_result
    }
    
    return result

@router.post("/apply-underwriting-rules/", response_model=Dict[str, Any])
def apply_underwriting_rules(application_data: Dict[str, Any]):
    """
    Apply AI underwriting rules to an application
    
    This endpoint:
    1. Takes application data
    2. Runs it through the rule-based AI underwriting service
    3. Returns the decision and explanation
    """
    # Process using AI underwriting rules
    rule_engine = UnderwritingRuleEngine()
    result = rule_engine.evaluate_application(application_data)
    return result 