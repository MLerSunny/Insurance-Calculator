"""
Tests for the database connection and models
"""
import pytest
from sqlalchemy.sql import text
from app.models.insurance import InsuranceApplication


def test_database_connection(test_db):
    """Test that we can connect to the database and run queries"""
    # Execute a simple query
    result = test_db.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_insurance_application_model(test_db):
    """Test that we can create and query InsuranceApplication models"""
    # Create a test application
    test_application = InsuranceApplication(
        applicant_name="Test User",
        applicant_age=45,
        email="test@example.com",
        phone="555-123-4567",
        medical_history={"conditions": ["hypertension"]},
        risk_factors={"smoking": True, "alcohol_consumption": False},
        coverage_amount=500000,
        premium_amount=1275.50,
        is_approved=True,
        ai_recommendation="Approve with standard rates"
    )
    
    # Add to database
    test_db.add(test_application)
    test_db.commit()
    
    # Query back
    queried_app = test_db.query(InsuranceApplication).filter_by(
        applicant_name="Test User").first()
    
    # Assert values match
    assert queried_app is not None
    assert queried_app.applicant_name == "Test User"
    assert queried_app.applicant_age == 45
    assert queried_app.coverage_amount == 500000
    assert queried_app.premium_amount == 1275.50
    assert queried_app.is_approved is True
    assert queried_app.medical_history.get("conditions") == ["hypertension"]
    assert queried_app.risk_factors.get("smoking") is True 