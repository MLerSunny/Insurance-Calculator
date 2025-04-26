"""
Pytest configuration and fixtures
"""
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Add the parent directory to the Python path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app
from app.database.database import Base, get_db
from app.database.vector_store import VectorStore
from app.services.llm_service import LLMService

# Create test database
TEST_DATABASE_URL = "sqlite:///./test_insurance.db"


@pytest.fixture(scope="function")
def test_db():
    """
    Create a fresh test database for each test function
    """
    # Create test database engine
    engine = create_engine(
        TEST_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """
    Create a FastAPI test client with a test database
    """
    # Override the get_db dependency to use our test database
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Remove the override after the test
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def mock_vector_store():
    """
    Create a mock vector store for testing
    """
    # Use a test-specific persist directory
    test_persist_dir = "./test_vector_db"
    test_collection = "test_insurance_data"
    
    # Create vector store with test settings
    vector_store = VectorStore(
        collection_name=test_collection,
        persist_directory=test_persist_dir
    )
    
    yield vector_store
    
    # Clean up
    try:
        vector_store.delete_collection()
        # Remove directory
        import shutil
        if os.path.exists(test_persist_dir):
            shutil.rmtree(test_persist_dir)
    except:
        pass


@pytest.fixture(scope="module")
def mock_llm_service(monkeypatch):
    """
    Create a mock LLM service that doesn't make actual API calls
    """
    class MockOllamaLLM:
        def invoke(self, prompt):
            return f"Mock response for: {prompt[:20]}..."
        
        async def ainvoke(self, prompt):
            return f"Mock async response for: {prompt[:20]}..."
        
        async def agenerate(self, prompts):
            class MockGenerations:
                generations = [[MockGeneration()]]
            
            class MockGeneration:
                text = f"Mock generation for: {prompts[0][:20]}..."
            
            return MockGenerations()
    
    # Patch the OllamaLLM initialization in LLMService
    monkeypatch.setattr("app.services.llm_service.OllamaLLM", MockOllamaLLM)
    
    # Create service with the mock
    service = LLMService()
    return service 