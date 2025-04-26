"""
Tests for the FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
import json


def test_root_endpoint(client):
    """Test the root endpoint returns proper response"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Insurance Calculator API is running"}


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_system_status(client, monkeypatch):
    """Test the system status endpoint"""
    # Mock the LLM and vector store services for the test
    def mock_get_llm_service():
        return "mocked_llm_service"
    
    def mock_get_vector_store():
        return "mocked_vector_store"
    
    monkeypatch.setattr("app.services.llm_service.get_llm_service", mock_get_llm_service)
    monkeypatch.setattr("app.database.vector_store.get_vector_store", mock_get_vector_store)
    
    response = client.get("/api/system-status")
    assert response.status_code == 200
    
    # Check that the response contains the expected fields
    data = response.json()
    assert "llm_service" in data
    assert "vector_store" in data
    assert "status" in data["llm_service"]
    assert "model" in data["llm_service"]
    assert "status" in data["vector_store"]
    assert "collection" in data["vector_store"]


def test_insurance_calculate_premium(client, monkeypatch):
    """Test the calculate premium endpoint"""
    # Mock the function that would normally call the LLM
    async def mock_calculate_premium(application_data):
        # Return a fixed premium calculation
        return {
            "premium": 1250.75,
            "factors": {
                "age_factor": 1.25,
                "health_factor": 1.15,
                "coverage_factor": 1.05
            },
            "explanation": "Premium calculated based on age, health, and coverage amount"
        }
    
    # Apply the mock
    import sys
    import importlib
    
    # Use monkeypatch to override the function
    monkeypatch.setattr(
        "app.services.premium_calculation.calculate_premium", 
        mock_calculate_premium
    )
    
    # Create test data
    application_data = {
        "applicant_name": "Test User",
        "applicant_age": 45,
        "email": "test@example.com",
        "phone": "555-123-4567",
        "medical_history": {
            "conditions": ["Type 2 diabetes", "High blood pressure"],
            "medications": ["Metformin", "Lisinopril"]
        },
        "risk_factors": {
            "smoking": False,
            "alcohol_consumption": True,
            "dangerous_activities": []
        },
        "coverage_amount": 500000
    }
    
    # Test the endpoint
    response = client.post(
        "/api/insurance/calculate-premium",
        json=application_data
    )
    
    # Validate the response
    assert response.status_code == 200
    result = response.json()
    assert "premium" in result
    assert "factors" in result
    assert "explanation" in result
    assert result["premium"] == 1250.75


def test_submit_application(client):
    """Test submitting an insurance application"""
    # Create test application data
    application_data = {
        "applicant_name": "Test Applicant",
        "applicant_age": 35,
        "email": "applicant@example.com",
        "phone": "555-987-6543",
        "medical_history": {
            "conditions": ["Asthma"],
            "medications": ["Albuterol"]
        },
        "risk_factors": {
            "smoking": False,
            "alcohol_consumption": False,
            "dangerous_activities": ["Rock climbing"]
        },
        "coverage_amount": 400000
    }
    
    # Submit the application
    response = client.post(
        "/api/insurance/applications/",
        json=application_data
    )
    
    # Validate response
    assert response.status_code == 201
    result = response.json()
    assert "id" in result
    assert result["applicant_name"] == "Test Applicant"
    assert result["applicant_age"] == 35
    assert result["coverage_amount"] == 400000
    
    # Get the created application
    application_id = result["id"]
    get_response = client.get(f"/api/insurance/applications/{application_id}")
    
    # Verify the retrieved application matches what we submitted
    assert get_response.status_code == 200
    retrieved = get_response.json()
    assert retrieved["applicant_name"] == "Test Applicant"
    assert retrieved["email"] == "applicant@example.com"


def test_get_all_applications(client):
    """Test retrieving all applications"""
    # Create multiple applications
    applications = [
        {
            "applicant_name": "User One",
            "applicant_age": 30,
            "email": "user1@example.com",
            "phone": "555-111-1111",
            "medical_history": {"conditions": []},
            "risk_factors": {"smoking": False},
            "coverage_amount": 250000
        },
        {
            "applicant_name": "User Two",
            "applicant_age": 45,
            "email": "user2@example.com",
            "phone": "555-222-2222",
            "medical_history": {"conditions": ["Hypertension"]},
            "risk_factors": {"smoking": True},
            "coverage_amount": 500000
        }
    ]
    
    # Submit all applications
    for app in applications:
        client.post("/api/insurance/applications/", json=app)
    
    # Retrieve all applications
    response = client.get("/api/insurance/applications/")
    
    # Validate response
    assert response.status_code == 200
    result = response.json()
    assert isinstance(result, list)
    assert len(result) >= 2  # Could be more if other tests added applications
    
    # Check if our applications are in the list
    emails = [app["email"] for app in result]
    assert "user1@example.com" in emails
    assert "user2@example.com" in emails 