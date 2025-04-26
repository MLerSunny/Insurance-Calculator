import logging
from typing import Dict, Any, List
import json
from .llm_service import get_llm_service, ResponseSchema

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define rules for the underwriting process
# These will be used both by the rule engine and communicated to the LLM
UNDERWRITING_RULES = [
    # Age-based rules
    {
        "name": "max_age_limit",
        "description": "Applicants over 80 years old are declined automatically",
        "condition": lambda app: app.get("applicant_age", 0) > 80,
        "action": "decline",
        "reason": "Applicant exceeds maximum age limit"
    },
    # Coverage amount rules
    {
        "name": "high_coverage_medical_review",
        "description": "Coverage > $1M requires medical review",
        "condition": lambda app: app.get("coverage_amount", 0) > 1000000,
        "action": "refer",
        "reason": "High coverage amount requires additional review"
    },
    # Risk score rules
    {
        "name": "high_risk_decline",
        "description": "Risk score > 0.85 is declined",
        "condition": lambda app: app.get("risk_score", 0) > 0.85,
        "action": "decline",
        "reason": "Risk score exceeds acceptable threshold"
    },
    {
        "name": "medium_risk_refer",
        "description": "Risk score > 0.65 is referred for review",
        "condition": lambda app: app.get("risk_score", 0) > 0.65,
        "action": "refer",
        "reason": "Elevated risk requires manual review"
    },
    # Medical condition rules
    {
        "name": "terminal_illness_decline",
        "description": "Terminal illnesses are declined",
        "condition": lambda app: any(
            "terminal" in condition.lower() or "stage 4" in condition.lower()
            for condition in app.get("medical_history", {}).get("conditions", [])
        ),
        "action": "decline",
        "reason": "Terminal illness present"
    },
    # Combination rules
    {
        "name": "senior_high_coverage",
        "description": "Seniors (>65) with high coverage (>$500k) require review",
        "condition": lambda app: app.get("applicant_age", 0) > 65 and app.get("coverage_amount", 0) > 500000,
        "action": "refer",
        "reason": "Senior applicant with high coverage amount"
    }
]

class UnderwritingRuleEngine:
    """
    Rule-based engine for insurance underwriting decisions
    """
    def __init__(self, rules=None):
        self.rules = rules or UNDERWRITING_RULES
    
    def evaluate_application(self, application: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an application against all rules
        Returns decision and reasons
        """
        logger.info(f"Evaluating application against {len(self.rules)} rules")
        
        # Default decision
        decision = "approve"
        reasons = []
        fired_rules = []
        
        # Evaluate each rule
        for rule in self.rules:
            try:
                if rule["condition"](application):
                    logger.info(f"Rule fired: {rule['name']}")
                    fired_rules.append(rule["name"])
                    
                    # Rules can decline or refer
                    if rule["action"] == "decline":
                        decision = "decline"
                        reasons.append(rule["reason"])
                    elif rule["action"] == "refer" and decision != "decline":
                        decision = "refer"
                        reasons.append(rule["reason"])
            except Exception as e:
                logger.error(f"Error evaluating rule {rule['name']}: {e}")
        
        # If no rules fired and we're still at default "approve"
        if decision == "approve" and not reasons:
            reasons.append("All underwriting criteria met")
        
        return {
            "decision": decision,
            "reasons": reasons,
            "rules_fired": fired_rules
        }

# Initialize the rule engine
rule_engine = UnderwritingRuleEngine()

async def evaluate_application_with_llm(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate an insurance application using DeepSeek-R1 LLM for enhanced decision making
    
    This combines rule-based logic with LLM-based analysis for better insights
    """
    logger.info("Evaluating application with AI underwriting logic using DeepSeek-R1")
    
    # First run the application through the rule engine for baseline decision
    rule_evaluation = rule_engine.evaluate_application(application_data)
    
    # Prepare data for the LLM
    simplified_rules = [{"name": rule["name"], "description": rule["description"]} 
                        for rule in UNDERWRITING_RULES]
    
    prompt_template = """
    You are an expert insurance underwriter. Your task is to evaluate an insurance application 
    and provide a professional underwriting decision. 
    
    The application has already been evaluated by a rule-based system with this result:
    {rule_evaluation}
    
    The underwriting rules used were:
    {rules}
    
    The applicant's information:
    - Age: {age}
    - Coverage Amount: ${coverage_amount}
    - Medical History: {medical_history}
    - Risk Factors: {risk_factors}
    - Risk Score (0-1): {risk_score}
    
    Based on both the rule system's decision and your expertise, please provide:
    1. A final underwriting decision (approve, refer, or decline)
    2. Detailed reasoning for this decision
    3. If approved, a justified premium amount
    4. Any special conditions that should apply
    
    Think step by step through your evaluation process.
    """
    
    # Define output schemas for structured generation
    output_schemas = [
        ResponseSchema(name="decision", description="The final underwriting decision: 'approve', 'refer', or 'decline'"),
        ResponseSchema(name="reasoning", description="Detailed reasoning explaining the underwriting decision"),
        ResponseSchema(name="premium_amount", description="If approved, the justified premium amount, otherwise null"),
        ResponseSchema(name="special_conditions", description="Any special conditions or exclusions that should apply to the policy")
    ]
    
    # Get service and generate structured output
    llm_service = get_llm_service()
    
    try:
        llm_evaluation = await llm_service.structured_generation(
            input_variables={
                "rule_evaluation": json.dumps(rule_evaluation, indent=2),
                "rules": json.dumps(simplified_rules, indent=2),
                "age": application_data.get("applicant_age", "Unknown"),
                "coverage_amount": application_data.get("coverage_amount", 0),
                "medical_history": json.dumps(application_data.get("medical_history", {}), indent=2),
                "risk_factors": json.dumps(application_data.get("risk_factors", {}), indent=2),
                "risk_score": application_data.get("risk_score", 0)
            },
            prompt_template=prompt_template,
            output_schemas=output_schemas
        )
        
        # Combine rule-based and LLM evaluations for final decision
        premium = None
        if llm_evaluation["decision"] == "approve":
            premium = llm_evaluation.get("premium_amount")
        
        # Prepare the final result combining both approaches
        return {
            "application_id": application_data.get("id", "unknown"),
            "decision": llm_evaluation["decision"],
            "premium_amount": premium,
            "decision_factors": llm_evaluation["reasoning"],
            "rule_engine_decision": rule_evaluation["decision"],
            "rule_engine_factors": rule_evaluation["reasons"],
            "special_conditions": llm_evaluation.get("special_conditions", []),
            "requires_review": llm_evaluation["decision"] == "refer"
        }
    except Exception as e:
        logger.error(f"Error in LLM evaluation: {e}")
        # Fallback to rule-based decision if LLM fails
        
        # Calculate basic premium if not declined
        premium = None
        if rule_evaluation["decision"] != "decline":
            # Basic premium calculation
            base_premium = application_data.get("coverage_amount", 100000) * 0.01
            age_factor = 1.0 + (application_data.get("applicant_age", 40) / 100)
            risk_factor = 1.0 + (application_data.get("risk_score", 0.3) * 2)
            
            premium = round(base_premium * age_factor * risk_factor, 2)
        
        return {
            "application_id": application_data.get("id", "unknown"),
            "decision": rule_evaluation["decision"],
            "premium_amount": premium,
            "decision_factors": rule_evaluation["reasons"],
            "rule_engine_decision": rule_evaluation["decision"],
            "rule_engine_factors": rule_evaluation["reasons"],
            "special_conditions": [],
            "requires_review": rule_evaluation["decision"] == "refer",
            "error": f"LLM evaluation failed: {str(e)}"
        } 