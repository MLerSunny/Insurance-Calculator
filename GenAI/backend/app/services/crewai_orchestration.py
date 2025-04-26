import logging
import json
from typing import Dict, Any, List, Optional
import asyncio
from .llm_service import get_llm_service, ResponseSchema
from ..database.vector_store import get_vector_store
from langchain_core.output_parsers.json import JsonOutputParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Agent:
    """
    Production Agent class for CrewAI integration with DeepSeek-R1
    Represents a specialized AI agent with a specific role and goal
    """
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.llm_service = get_llm_service()
        self.vector_store = get_vector_store()
    
    async def execute_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the DeepSeek-R1 model
        
        Args:
            task: Description of the task to perform
            context: Dictionary of context data needed for the task
            
        Returns:
            Dictionary containing the task results
        """
        logger.info(f"Agent {self.name} executing task: {task}")
        
        # Route task to appropriate handler
        if self.role == "underwriter":
            return await self._process_underwriter_task(task, context)
        elif self.role == "risk_analyst":
            return await self._process_risk_analyst_task(task, context)
        elif self.role == "medical_expert":
            return await self._process_medical_expert_task(task, context)
        else:
            return {"status": "error", "message": f"Unknown role: {self.role}"}
    
    async def _process_underwriter_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process tasks specific to the underwriter role"""
        if "evaluate_application" in task.lower():
            # Fetch relevant underwriting guidelines from vector store
            search_results = self.vector_store.similarity_search(
                query="insurance underwriting guidelines for determining premium and eligibility",
                k=3
            )
            
            # Extract relevant guidelines
            guidelines = "\n".join([result["content"] for result in search_results])
            
            # Define output schema
            output_schemas = [
                ResponseSchema(name="decision", description="The underwriting decision: 'approve', 'refer', or 'decline'"),
                ResponseSchema(name="reason", description="Detailed reasoning explaining the underwriting decision"),
                ResponseSchema(name="premium_amount", description="If approved, the calculated premium amount"),
                ResponseSchema(name="underwriting_notes", description="Additional notes about the underwriting decision")
            ]
            
            # Create prompt
            prompt = f"""
            You are {self.name}, an experienced insurance underwriter with the goal: {self.goal}.
            
            Your task is to evaluate an insurance application with the following details:
            Applicant Age: {context.get('applicant_age', 'Unknown')}
            Coverage Amount: ${context.get('coverage_amount', 'Unknown')}
            Risk Score: {context.get('risk_score', 'Unknown')}
            Medical History: {json.dumps(context.get('medical_history', {}), indent=2)}
            Risk Factors: {json.dumps(context.get('risk_factors', {}), indent=2)}
            
            Consider these relevant underwriting guidelines:
            {guidelines}
            
            Based on the application details and guidelines, please determine:
            1. Whether to approve, refer for further review, or decline the application
            2. The reasoning behind your decision
            3. If approved, calculate an appropriate premium amount
            4. Any additional notes or concerns
            
            Think step by step through your underwriting process.
            """
            
            try:
                # Generate structured output using LLM
                result = await self.llm_service.structured_generation(
                    input_variables={},  # No variables needed since prompt is complete
                    prompt_template=prompt,
                    output_schemas=output_schemas
                )
                
                # Calculate premium if needed
                premium = result.get("premium_amount")
                if premium is None and result["decision"] == "approve":
                    # Basic premium calculation as fallback
                    base_premium = context.get("coverage_amount", 100000) * 0.01
                    age_factor = 1.0 + (context.get("applicant_age", 40) / 100)
                    risk_factor = 1.0 + (context.get("risk_score", 0.3) * 2)
                    premium = round(base_premium * age_factor * risk_factor, 2)
                    result["premium_amount"] = premium
                
                return result
            except Exception as e:
                logger.error(f"Error in underwriter LLM evaluation: {e}")
                # Fallback response if LLM fails
                return self._fallback_underwriter_response(context)
        
        return {"status": "error", "message": "Unknown task for underwriter"}
    
    def _fallback_underwriter_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a fallback response if LLM processing fails"""
        risk_score = context.get("risk_score", 0.5)
        coverage_amount = context.get("coverage_amount", 100000)
        applicant_age = context.get("applicant_age", 40)
        
        # Simple decision logic
        if risk_score > 0.8:
            decision = "decline"
            reason = "High risk profile exceeds underwriting guidelines"
        elif risk_score > 0.6:
            decision = "refer"
            reason = "Elevated risk requires additional review"
            if coverage_amount > 500000:
                reason += " and potential coverage limit"
        else:
            decision = "approve"
            reason = "Risk profile within acceptable parameters"
        
        # Premium calculation
        base_premium = coverage_amount * 0.01
        age_factor = 1.0 + (applicant_age / 100)
        risk_factor = 1.0 + risk_score
        premium = base_premium * age_factor * risk_factor
        
        return {
            "decision": decision,
            "reason": reason,
            "premium_amount": round(premium, 2),
            "underwriting_notes": f"Application evaluated by automated underwriting fallback. Risk score: {risk_score}."
        }
    
    async def _process_risk_analyst_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process tasks specific to the risk analyst role"""
        if "analyze_risk" in task.lower():
            # Define output schema
            output_schemas = [
                ResponseSchema(name="risk_score", description="The overall risk score as a decimal between 0 and 1"),
                ResponseSchema(name="risk_assessment", description="Detailed assessment of the applicant's risk profile"),
                ResponseSchema(name="risk_factors", description="Breakdown of individual risk factors and their contributions"),
                ResponseSchema(name="analysis_notes", description="Additional notes about the risk analysis")
            ]
            
            # Create prompt
            prompt = f"""
            You are {self.name}, a skilled risk assessment specialist with the goal: {self.goal}.
            
            Your task is to analyze the risk profile of an insurance applicant with the following details:
            Applicant Age: {context.get('applicant_age', 'Unknown')}
            Medical History: {json.dumps(context.get('medical_history', {}), indent=2)}
            Risk Factors: {json.dumps(context.get('risk_factors', {}), indent=2)}
            
            Based on this information, please provide:
            1. An overall risk score (0.0 to 1.0, where 1.0 is highest risk)
            2. A detailed assessment of the applicant's risk profile
            3. Breakdown of individual risk factors and their contributions
            4. Additional notes or concerns about your analysis
            
            Consider both medical and lifestyle factors in your assessment.
            """
            
            try:
                # Generate structured output using LLM
                return await self.llm_service.structured_generation(
                    input_variables={},  # No variables needed since prompt is complete
                    prompt_template=prompt,
                    output_schemas=output_schemas
                )
            except Exception as e:
                logger.error(f"Error in risk analyst LLM evaluation: {e}")
                # Fallback response if LLM fails
                return self._fallback_risk_analyst_response(context)
        
        return {"status": "error", "message": "Unknown task for risk analyst"}
    
    def _fallback_risk_analyst_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a fallback response if LLM processing fails"""
        medical_history = context.get("medical_history", {})
        risk_factors = context.get("risk_factors", {})
        
        conditions = medical_history.get("conditions", [])
        
        # Risk categories
        high_risk_conditions = ["diabetes", "heart disease", "cancer", "stroke"]
        medium_risk_conditions = ["hypertension", "asthma", "depression", "obesity"]
        
        # Calculate condition risk
        condition_risk = 0.0
        for condition in conditions:
            if any(hr in condition.lower() for hr in high_risk_conditions):
                condition_risk += 0.2
            elif any(mr in condition.lower() for mr in medium_risk_conditions):
                condition_risk += 0.1
        
        # Calculate lifestyle risk
        lifestyle_risk = 0.0
        if risk_factors.get("smoking", False):
            lifestyle_risk += 0.3
        if risk_factors.get("alcohol_consumption", False):
            lifestyle_risk += 0.2
        
        # Dangerous activities
        activities = risk_factors.get("dangerous_activities", [])
        if activities:
            lifestyle_risk += len(activities) * 0.1
        
        # Overall risk score
        overall_risk = min(0.95, condition_risk + lifestyle_risk)
        
        # Risk assessment
        if overall_risk > 0.7:
            assessment = "High risk profile due to medical conditions and lifestyle factors"
        elif overall_risk > 0.4:
            assessment = "Moderate risk profile with some concerning factors"
        else:
            assessment = "Low risk profile with minimal concerns"
        
        return {
            "risk_score": round(overall_risk, 2),
            "risk_assessment": assessment,
            "risk_factors": {
                "medical_risk": round(condition_risk, 2),
                "lifestyle_risk": round(lifestyle_risk, 2)
            },
            "analysis_notes": "Automated risk analysis based on self-reported conditions and lifestyle factors"
        }
    
    async def _process_medical_expert_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process tasks specific to the medical expert role"""
        if "evaluate_medical" in task.lower():
            # Define output schema
            output_schemas = [
                ResponseSchema(name="consistency_check", description="Assessment of the consistency of the medical information provided"),
                ResponseSchema(name="recommendation", description="Medical recommendation based on the evaluation"),
                ResponseSchema(name="notes", description="Detailed notes about the medical evaluation"),
                ResponseSchema(name="review_level", description="Recommended level of medical review (standard or detailed)")
            ]
            
            # Create prompt
            prompt = f"""
            You are {self.name}, a medical expert with the goal: {self.goal}.
            
            Your task is to evaluate the medical information of an insurance applicant with the following details:
            Applicant Age: {context.get('applicant_age', 'Unknown')}
            Medical History: {json.dumps(context.get('medical_history', {}), indent=2)}
            
            Based on this information, please provide:
            1. An assessment of the consistency and completeness of the medical information
            2. Medical recommendation for the underwriting process
            3. Detailed notes about your medical evaluation
            4. Recommended level of medical review (standard or detailed)
            
            Focus on identifying any inconsistencies, missing information, or concerning medical conditions.
            """
            
            try:
                # Generate structured output using LLM
                return await self.llm_service.structured_generation(
                    input_variables={},  # No variables needed since prompt is complete
                    prompt_template=prompt,
                    output_schemas=output_schemas
                )
            except Exception as e:
                logger.error(f"Error in medical expert LLM evaluation: {e}")
                # Fallback response if LLM fails
                return self._fallback_medical_expert_response(context)
        
        return {"status": "error", "message": "Unknown task for medical expert"}
    
    def _fallback_medical_expert_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Provide a fallback response if LLM processing fails"""
        medical_history = context.get("medical_history", {})
        applicant_age = context.get("applicant_age", 40)
        
        conditions = medical_history.get("conditions", [])
        medications = medical_history.get("medications", [])
        
        # Age-related condition assessment
        age_appropriate = True
        age_notes = ""
        
        if applicant_age > 60 and not any("hypertension" in c.lower() for c in conditions):
            age_appropriate = False
            age_notes = "Absence of common age-related conditions is unusual and requires verification"
        
        # Medication-condition correlation
        medication_match = True
        medication_notes = ""
        
        # Diabetes medications check
        diabetes_meds = ["insulin", "metformin", "glipizide"]
        has_diabetes = any("diabetes" in c.lower() for c in conditions)
        taking_diabetes_meds = any(any(med.lower() in m.lower() for med in diabetes_meds) for m in medications)
        
        if has_diabetes and not taking_diabetes_meds:
            medication_match = False
            medication_notes += "Diabetes reported but no diabetes medication listed. "
        
        if taking_diabetes_meds and not has_diabetes:
            medication_match = False
            medication_notes += "Diabetes medication listed but condition not reported. "
        
        # Overall assessment
        if not age_appropriate or not medication_match:
            recommendation = "Medical review required. Inconsistencies detected."
        else:
            recommendation = "Medical information appears consistent. Standard processing recommended."
        
        return {
            "consistency_check": {
                "age_appropriate": age_appropriate,
                "medication_match": medication_match
            },
            "recommendation": recommendation,
            "notes": f"{age_notes} {medication_notes}".strip(),
            "review_level": "detailed" if not age_appropriate or not medication_match else "standard"
        }


class Crew:
    """
    Production-ready Crew class for orchestrating multiple agents
    """
    def __init__(self, agents: List[Agent], tasks: List[Dict[str, Any]]):
        self.agents = agents
        self.tasks = tasks
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all tasks with the assigned agents asynchronously
        
        Args:
            context: Shared context for all agents
            
        Returns:
            Dictionary of task results
        """
        logger.info("CrewAI Orchestration starting")
        results = {}
        
        # Execute tasks asynchronously
        tasks = []
        for task in self.tasks:
            agent = next((a for a in self.agents if a.role == task.get("role")), None)
            if agent:
                # Create task for asyncio.gather
                tasks.append(self._execute_agent_task(agent, task, context, results))
            else:
                logger.error(f"No agent found for role: {task.get('role')}")
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        return results
    
    async def _execute_agent_task(
        self, 
        agent: Agent, 
        task: Dict[str, Any], 
        context: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """Execute a single agent task and add result to results dict"""
        try:
            task_result = await agent.execute_task(task.get("description"), context)
            results[task.get("name")] = task_result
        except Exception as e:
            logger.error(f"Error executing task {task.get('name')}: {e}")
            results[task.get("name")] = {"status": "error", "message": str(e)}


async def process_complex_application(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a complex insurance application using specialized AI agents
    
    Args:
        application_data: Dictionary containing application details
        
    Returns:
        Dictionary with processing results, recommendation, and premium
    """
    logger.info("Processing complex application with CrewAI orchestration")
    try:
        # Create specialized agents
        agents = [
            Agent("Risk Analyzer", "risk_analyst", "Accurately assess risk profiles"),
            Agent("Medical Expert", "medical_expert", "Evaluate medical information for consistency and risk"),
            Agent("Underwriter", "underwriter", "Make appropriate underwriting decisions")
        ]
        
        # Define tasks
        tasks = [
            {
                "agent": "Risk Analyzer",
                "task": "analyze_risk",
                "description": "Analyze the risk profile of the applicant"
            },
            {
                "agent": "Medical Expert",
                "task": "evaluate_medical",
                "description": "Evaluate the medical information provided"
            },
            {
                "agent": "Underwriter",
                "task": "evaluate_application",
                "description": "Make final underwriting decision"
            }
        ]
        
        # Create and run crew
        crew = Crew(agents, tasks)
        result = await crew.run(application_data)
        
        # Ensure premium amount is a number if approved
        if result.get("approved", False) and isinstance(result.get("premium_amount"), str):
            try:
                # Try to convert string to number if needed
                result["premium_amount"] = float(result["premium_amount"].replace("$", "").replace(",", ""))
            except:
                # Fallback premium calculation
                result["premium_amount"] = application_data.get("coverage_amount", 100000) * 0.02
        
        logger.info(f"Complex application processing complete: {result}")
        return result
    
    except Exception as e:
        logger.error(f"Error in complex application processing: {e}")
        # Fallback response
        return {
            "approved": False,
            "premium_amount": None,
            "recommendation": f"Application processing error: {str(e)}. Please review manually.",
            "risk_score": None,
            "error": str(e)
        }

# Add a synchronous version for use in non-async endpoints
def process_complex_application_sync(application_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Synchronous wrapper for process_complex_application
    
    Args:
        application_data: Dictionary containing application details
        
    Returns:
        Dictionary with processing results, recommendation, and premium
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If no event loop is set for the current thread, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(process_complex_application(application_data)) 