"""
Tests for the LLM service component
"""
import pytest
import asyncio
from app.services.llm_service import LLMService, ResponseSchema


def test_llm_service_initialization(mock_llm_service):
    """Test that the LLM service initializes correctly"""
    assert mock_llm_service is not None
    assert mock_llm_service.llm is not None


def test_generate_text_sync(mock_llm_service, monkeypatch):
    """Test synchronous text generation"""
    # Mock the invoke method
    def mock_invoke(self, prompt):
        return f"Test response for: {prompt}"
    
    monkeypatch.setattr(mock_llm_service.llm.__class__, "invoke", mock_invoke)
    
    # Test prompt
    test_prompt = "Calculate insurance premium for a 45-year-old with diabetes"
    
    # Generate text
    response = mock_llm_service.llm.invoke(test_prompt)
    
    # Verify response
    assert "Test response for:" in response
    assert "Calculate insurance premium" in response


def test_structured_generation(mock_llm_service, monkeypatch):
    """Test structured generation with schema"""
    # Define a mock ainvoke method that returns structured data
    async def mock_ainvoke(self, input_vars):
        return {
            "premium": 1250.75,
            "risk_assessment": "Moderate risk due to medical history",
            "recommendation": "Standard coverage with slight premium increase"
        }
    
    # Apply the mock
    monkeypatch.setattr(mock_llm_service.llm.__class__, "ainvoke", mock_ainvoke)
    
    # Create a mock chain class
    class MockChain:
        async def ainvoke(self, input_vars):
            return {
                "premium": 1250.75,
                "risk_assessment": "Moderate risk due to medical history",
                "recommendation": "Standard coverage with slight premium increase"
            }
    
    # Test structured generation
    async def run_test():
        # Schema definition
        output_schemas = [
            ResponseSchema(name="premium", description="Calculated premium amount"),
            ResponseSchema(name="risk_assessment", description="Risk assessment text"),
            ResponseSchema(name="recommendation", description="Recommendation for coverage")
        ]
        
        # Override the LLMChain with our mock
        monkeypatch.setattr("langchain.chains.LLMChain", lambda **kwargs: MockChain())
        
        # Test input
        input_vars = {
            "age": 45,
            "medical_conditions": ["Type 2 diabetes", "High blood pressure"],
            "coverage_amount": 500000
        }
        
        # Generate structured output
        result = await mock_llm_service.structured_generation(
            input_variables=input_vars,
            prompt_template="Calculate premium for a {age}-year-old with {medical_conditions} requesting ${coverage_amount} coverage",
            output_schemas=output_schemas
        )
        
        # Verify the structure and content
        assert "premium" in result
        assert "risk_assessment" in result
        assert "recommendation" in result
        assert result["premium"] == 1250.75
        assert "Moderate risk" in result["risk_assessment"]
    
    # Run the async test
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test())


def test_generate_text_with_retry(mock_llm_service, monkeypatch):
    """Test that retries work when generation fails initially"""
    # Configure a counter to track call attempts
    call_count = {"count": 0}
    
    # Create a mock agenerate method that fails twice then succeeds
    async def mock_agenerate(self, prompts):
        call_count["count"] += 1
        if call_count["count"] < 3:
            raise ConnectionError("Simulated connection error")
        
        class MockGenerations:
            generations = [[MockGeneration()]]
        
        class MockGeneration:
            text = f"Success on attempt {call_count['count']}"
        
        return MockGenerations()
    
    # Apply the mock
    monkeypatch.setattr(mock_llm_service.llm.__class__, "agenerate", mock_agenerate)
    
    # Test the retry mechanism
    async def run_test():
        # Test prompt
        test_prompt = "Test retry mechanism"
        
        # Generate text with retries
        response = await mock_llm_service.generate_text(test_prompt)
        
        # Should succeed on the third attempt
        assert call_count["count"] == 3
        assert "Success on attempt 3" in response.generations[0].text
    
    # Run the async test
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test())


def test_error_handling_exceeded_retries(mock_llm_service, monkeypatch):
    """Test that an error is raised when max retries is exceeded"""
    # Create a mock agenerate method that always fails
    async def mock_agenerate(self, prompts):
        raise ConnectionError("Simulated persistent connection error")
    
    # Apply the mock
    monkeypatch.setattr(mock_llm_service.llm.__class__, "agenerate", mock_agenerate)
    
    # Test the retry mechanism
    async def run_test():
        # Test prompt
        test_prompt = "Test max retries exceeded"
        
        # Should raise an error after max retries
        with pytest.raises(ConnectionError):
            await mock_llm_service.generate_text(test_prompt)
    
    # Run the async test
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_test()) 