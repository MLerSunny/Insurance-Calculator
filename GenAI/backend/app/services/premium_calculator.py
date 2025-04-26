import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In a production environment, you would use a proper LLM API client
# For this example, we're creating a simulated LLM service
class LLMService:
    def generate_response(self, prompt, system_prompt=None):
        """Simulate an LLM response for premium calculations"""
        logger.info(f"LLM Prompt: {prompt}")
        
        # Extract data from prompt using simple parsing
        age = self._extract_age(prompt)
        coverage = self._extract_coverage(prompt)
        smoking = "smoking: true" in prompt.lower()
        medical_conditions = self._extract_conditions(prompt)
            
        # Calculate premium based on simple rules
        base_premium = 500  # Base premium
        age_factor = self._calculate_age_factor(age)
        coverage_factor = coverage / 100000 if coverage else 1.0  # $100k = factor of 1
        
        # Risk factors
        risk_multiplier = 1.5 if smoking else 1.0
            
        # Medical conditions impact
        condition_risk = self._calculate_condition_risk(medical_conditions)
        
        # Calculate final premium
        premium = base_premium * age_factor * coverage_factor * risk_multiplier * condition_risk
        premium = round(premium, 2)
        
        # Generate risk assessment and recommendation
        risk, recommendation = self._generate_assessment(condition_risk, smoking, age)
        
        return {
            "premium_amount": premium,
            "risk_assessment": risk,
            "ai_recommendation": recommendation
        }
    
    def _extract_age(self, prompt):
        try:
            if "age" in prompt:
                age_text = prompt.split("age")[1].split(",")[0].strip(": ")
                return int(''.join(filter(str.isdigit, age_text)))
        except Exception as e:
            logger.error(f"Error extracting age: {e}")
        return 40  # Default age
        
    def _extract_coverage(self, prompt):
        try:
            if "coverage" in prompt:
                coverage_text = prompt.split("coverage")[1].split(",")[0].strip(": $")
                return float(''.join(filter(lambda x: x.isdigit() or x == '.', coverage_text)))
        except Exception as e:
            logger.error(f"Error extracting coverage: {e}")
        return 100000  # Default coverage
    
    def _extract_conditions(self, prompt):
        try:
            if "conditions" in prompt:
                conditions_text = prompt.split("conditions")[1].split("]")[0].strip(": [")
                return [c.strip().strip('"\'') for c in conditions_text.split(",")]
        except Exception as e:
            logger.error(f"Error extracting conditions: {e}")
        return []  # Default empty list
    
    def _calculate_age_factor(self, age):
        if age < 30:
            return 1.0
        elif age < 45:
            return 1.5
        elif age < 60:
            return 2.0
        else:
            return 3.0
    
    def _calculate_condition_risk(self, medical_conditions):
        condition_risk = 1.0
        high_risk_conditions = ["diabetes", "heart disease", "cancer", "stroke", "hypertension"]
        medium_risk_conditions = ["asthma", "depression", "anxiety", "obesity"]
        
        for condition in medical_conditions:
            if any(high_risk in condition.lower() for high_risk in high_risk_conditions):
                condition_risk *= 1.3
            elif any(medium_risk in condition.lower() for medium_risk in medium_risk_conditions):
                condition_risk *= 1.1
        
        return condition_risk
    
    def _generate_assessment(self, condition_risk, smoking, age):
        # Calculate final premium
        premium = base_premium * age_factor * coverage_factor * risk_multiplier * condition_risk
        premium = round(premium, 2)
        
        # Generate risk assessment
        if condition_risk > 1.5 or (smoking and age > 50):
            risk = "high"
            recommendation = "Applicant has significant risk factors. Consider additional medical examination before approval."
        elif condition_risk > 1.2 or smoking or age > 60:
            risk = "medium"
            recommendation = "Moderate risk profile. Standard approval process recommended."
        else:
            risk = "low"
            recommendation = "Low risk profile. Fast-track approval recommended."
        
        return {
            "premium_amount": premium,
            "risk_assessment": risk,
            "ai_recommendation": recommendation
        }

# Initialize the LLM service
llm_service = LLMService()

def calculate_premium(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate insurance premium using AI
    
    This is an agentic AI component that:
    1. Takes application data
    2. Formats it for LLM processing
    3. Sends it to the LLM for premium calculation
    4. Processes the response
    """
    logger.info("Calculating premium with AI")
    
    # Format data for LLM
    prompt = f"""
    Calculate an insurance premium for an applicant with the following details:
    - Age: {data['applicant_age']}
    - Coverage amount: ${data['coverage_amount']}
    - Medical history:
        - Conditions: {data['medical_history'].get('conditions', [])}
        - Medications: {data['medical_history'].get('medications', [])}
    - Risk factors:
        - Smoking: {data['risk_factors'].get('smoking', False)}
        - Alcohol consumption: {data['risk_factors'].get('alcohol_consumption', False)}
        - Occupation risk: {data['risk_factors'].get('occupation_risk', 'low')}
    
    Provide the premium amount, risk assessment (low, medium, high), and a recommendation.
    """
    
    # System prompt that would instruct the LLM on how to respond
    system_prompt = """
    You are an expert insurance underwriter AI. Analyze the applicant information and determine:
    1. An appropriate premium amount based on age, coverage, and risk factors
    2. A risk assessment categorized as low, medium, or high
    3. A recommendation for the underwriting team
    Format your response as JSON with keys: premium_amount, risk_assessment, ai_recommendation
    """
    
    # Get response from LLM
    try:
        response = llm_service.generate_response(prompt, system_prompt)
        return response
    except Exception as e:
        logger.error(f"Error calculating premium: {e}")
        # Fallback to basic calculation if LLM fails
        return {
            "premium_amount": data['coverage_amount'] * 0.05,
            "risk_assessment": "medium",
            "ai_recommendation": "Error in AI calculation. Manual review recommended."
        } 