import logging
import os
from typing import Dict, Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_ollama import OllamaLLM
from langchain.chains import LLMChain, SequentialChain
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Model configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "deepseek-r1:32b")

# Define ResponseSchema class since it's not available in langchain_core 0.3.x
class ResponseSchema(BaseModel):
    name: str = Field(description="The name of the field to be returned")
    description: str = Field(description="The description of the field to be returned")

class LLMService:
    """
    Production-ready LLM service using DeepSeek-R1 via Ollama
    """
    def __init__(self):
        """Initialize the LLM service with DeepSeek-R1 model"""
        logger.info(f"Initializing LLM service with model: {MODEL_NAME}")
        
        try:
            self.llm = OllamaLLM(
                model=MODEL_NAME,
                base_url=OLLAMA_HOST,
                temperature=0.1,  # Low temperature for more deterministic outputs
                num_predict=2048,  # Maximum token length for predictions
                keep_alive=-1,     # Keep model loaded indefinitely
                repeat_penalty=1.1 # Slightly penalize repetition
            )
            logger.info("LLM initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def generate_text(self, prompt: str, temperature: float = 0.1) -> str:
        """
        Generate text from the LLM using a simple prompt
        
        Args:
            prompt: The prompt text to send to the model
            temperature: Controls randomness (0.0-1.0)
            
        Returns:
            Generated text response
        """
        logger.info(f"Generating text with prompt: {prompt[:50]}...")
        try:
            return await self.llm.agenerate([prompt])
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def structured_generation(
        self, 
        input_variables: Dict[str, Any],
        prompt_template: str,
        output_schemas: List[ResponseSchema]
    ) -> Dict[str, Any]:
        """
        Generate structured output from the LLM
        
        Args:
            input_variables: Dictionary of variables to fill in the prompt template
            prompt_template: Template string with placeholders for variables
            output_schemas: List of ResponseSchema objects defining the expected output
            
        Returns:
            Structured output as a dictionary
        """
        logger.info(f"Generating structured output for input: {str(input_variables)[:50]}...")
        
        try:
            # Updated implementation for structured output using newer API
            from langchain_core.output_parsers import StructuredOutputParser as SOParser
            from langchain_core.output_parsers.json import JsonOutputParser
            
            format_instructions = f"""
            Return a JSON object with the following keys:
            {', '.join([schema.name for schema in output_schemas])}
            """
            
            output_parser = JsonOutputParser()
            
            # Create prompt with format instructions
            prompt = PromptTemplate(
                template=prompt_template + "\n{format_instructions}\n",
                input_variables=list(input_variables.keys()),
                partial_variables={"format_instructions": format_instructions}
            )
            
            # Setup chain
            chain = LLMChain(llm=self.llm, prompt=prompt, output_parser=output_parser)
            
            # Run chain
            result = await chain.ainvoke(input_variables)
            
            return result
        except Exception as e:
            logger.error(f"Error in structured generation: {e}")
            raise

# Create a singleton instance for global use
llm_service = LLMService()

def get_llm_service() -> LLMService:
    """Dependency to get LLM service instance"""
    return llm_service 