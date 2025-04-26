import logging
import asyncio
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def test_ollama():
    """Test basic Ollama integration with DeepSeek-R1"""
    
    model = "deepseek-r1:32b"
    logger.info(f"Testing Ollama with model: {model}")
    
    try:
        # Test prompt
        prompt = """You are an expert insurance underwriter.
        Please analyze this applicant profile:
        - Age: 65
        - Medical history: hypertension, type 2 diabetes
        - Coverage requested: $500,000
        
        Provide a brief underwriting recommendation.
        """
        
        logger.info(f"Sending prompt to {model}")
        
        # Make the request (synchronously because ollama library doesn't have async methods)
        response = ollama.generate(model=model, prompt=prompt)
        
        logger.info(f"Received response from {model}")
        logger.info(f"Response: {response['response'][:500]}...")
        
        return response
    except Exception as e:
        logger.error(f"Error testing Ollama: {e}")
        raise

if __name__ == "__main__":
    logger.info("Starting basic Ollama test with DeepSeek-R1")
    asyncio.run(test_ollama())
    logger.info("Ollama test completed") 