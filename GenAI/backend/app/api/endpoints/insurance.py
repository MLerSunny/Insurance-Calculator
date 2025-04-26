from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.models.insurance import InsuranceApplication
from app.schemas.insurance import (
    InsuranceApplicationCreate, 
    InsuranceApplicationResponse,
    PremiumCalculationRequest,
    PremiumCalculationResponse
)
from app.services.premium_calculator import calculate_premium
from app.services.medical_risk_analysis import analyze_medical_risk

router = APIRouter()

@router.post("/applications/", response_model=InsuranceApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(application: InsuranceApplicationCreate, db: Session = Depends(get_db)):
    # Calculate premium using AI
    premium_data = calculate_premium({
        "applicant_age": application.applicant_age,
        "coverage_amount": application.coverage_amount,
        "medical_history": application.medical_history.dict(),
        "risk_factors": application.risk_factors.dict()
    })
    
    # Create new application
    db_application = InsuranceApplication(
        applicant_name=application.applicant_name,
        applicant_age=application.applicant_age,
        email=application.email,
        phone=application.phone,
        medical_history=application.medical_history.dict(),
        risk_factors=application.risk_factors.dict(),
        coverage_amount=application.coverage_amount,
        premium_amount=premium_data["premium_amount"],
        ai_recommendation=premium_data["ai_recommendation"]
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

@router.get("/applications/", response_model=List[InsuranceApplicationResponse])
def get_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    applications = db.query(InsuranceApplication).offset(skip).limit(limit).all()
    return applications

@router.get("/applications/{application_id}", response_model=InsuranceApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    db_application = db.query(InsuranceApplication).filter(InsuranceApplication.id == application_id).first()
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application

@router.post("/calculate-premium/", response_model=PremiumCalculationResponse)
def premium_calculation(request: PremiumCalculationRequest):
    # Analyze medical risk
    risk_analysis = analyze_medical_risk(request.medical_history.dict())
    
    # Calculate premium
    premium_data = calculate_premium({
        "applicant_age": request.applicant_age,
        "coverage_amount": request.coverage_amount,
        "medical_history": request.medical_history.dict(),
        "risk_factors": request.risk_factors.dict(),
        "risk_analysis": risk_analysis
    })
    
    return {
        "premium_amount": premium_data["premium_amount"],
        "risk_assessment": premium_data["risk_assessment"],
        "ai_recommendation": premium_data["ai_recommendation"]
    } 