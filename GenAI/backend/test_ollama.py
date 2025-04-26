import os
import logging
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "deepseek-r1:32b")

def test_ollama():
    """Test Ollama integration with DeepSeek-R1."""
    
    logger.info(f"Initializing Ollama client with model: {MODEL_NAME}")
    
    try:
        # Initialize Ollama client
        client = OllamaLLM(
            model=MODEL_NAME,
            base_url=OLLAMA_HOST,
            temperature=0.1,
            num_predict=256
        )
        
        # Test prompt
        prompt = """You are an expert insurance underwriter.
        Please analyze this applicant profile:
        - Age: 65
        - Medical history: hypertension, type 2 diabetes
        - Coverage requested: $500,000
        
        Provide a brief underwriting recommendation.
        """
        
        logger.info(f"Sending prompt to {MODEL_NAME}")
        response = client.invoke(prompt)
        
        logger.info(f"Received response from {MODEL_NAME}")
        logger.info(f"Response: {response[:500]}...")
        
        return response
    except Exception as e:
        logger.error(f"Error testing Ollama: {e}")
        logger.info("Attempting to list available models...")
        try:
            import requests
            models_response = requests.get(f"{OLLAMA_HOST}/api/tags")
            if models_response.status_code == 200:
                models = models_response.json()
                logger.info(f"Available models: {models}")
            else:
                logger.error(f"Failed to list models: {models_response.status_code}")
        except Exception as list_error:
            logger.error(f"Error listing models: {list_error}")
        
        raise

if __name__ == "__main__":
    logger.info("Starting Ollama test with DeepSeek-R1")
    test_ollama()
    logger.info("Ollama test completed") 