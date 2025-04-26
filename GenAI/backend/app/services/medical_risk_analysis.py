import json
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """
    Simulated vector store for medical condition embeddings
    In a real implementation, this would use a proper vector database
    such as Pinecone, Weaviate, or FAISS
    """
    def __init__(self):
        # Pre-defined medical conditions with risk scores
        self.medical_conditions = {
            "diabetes": {
                "risk_score": 0.75,
                "description": "Chronic condition affecting how the body processes blood sugar",
                "complications": ["kidney disease", "heart disease", "vision problems"]
            },
            "hypertension": {
                "risk_score": 0.65,
                "description": "Persistently elevated blood pressure in the arteries",
                "complications": ["heart attack", "stroke", "kidney failure"]
            },
            "asthma": {
                "risk_score": 0.45,
                "description": "Chronic condition affecting the airways in the lungs",
                "complications": ["respiratory failure", "pneumonia"]
            },
            "heart disease": {
                "risk_score": 0.85,
                "description": "Various conditions affecting heart function",
                "complications": ["heart attack", "heart failure"]
            },
            "cancer": {
                "risk_score": 0.90,
                "description": "Group of diseases involving abnormal cell growth",
                "complications": ["organ failure", "metastasis"]
            },
            "depression": {
                "risk_score": 0.30,
                "description": "Mental health disorder characterized by persistent sadness",
                "complications": ["anxiety", "substance abuse"]
            },
            "anxiety": {
                "risk_score": 0.25,
                "description": "Mental health disorder characterized by excessive worry",
                "complications": ["depression", "insomnia"]
            },
            "arthritis": {
                "risk_score": 0.40,
                "description": "Inflammation of one or more joints",
                "complications": ["mobility issues", "chronic pain"]
            },
            "obesity": {
                "risk_score": 0.60,
                "description": "Excess body fat accumulation that presents a health risk",
                "complications": ["diabetes", "heart disease", "sleep apnea"]
            },
            "allergies": {
                "risk_score": 0.20,
                "description": "Immune system response to substances that are usually harmless",
                "complications": ["anaphylaxis", "asthma"]
            }
        }
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for similar medical conditions"""
        results = []
        query = query.lower()
        
        for condition, data in self.medical_conditions.items():
            # Exact match
            if query in condition or condition in query:
                results.append({
                    "condition": condition,
                    "similarity": 0.9,
                    "data": data
                })
            # Partial match
            elif any(word in condition for word in query.split()):
                results.append({
                    "condition": condition,
                    "similarity": 0.7,
                    "data": data
                })
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

# Initialize the vector store
vector_store = VectorStore()

def analyze_medical_risk(medical_history: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze medical risk factors using vector similarity search
    
    This is an agentic AI component that:
    1. Takes medical history data
    2. Searches for similar conditions in the vector store
    3. Analyzes the risk level based on the conditions
    """
    logger.info("Analyzing medical risk factors")
    
    conditions = medical_history.get("conditions", [])
    
    # Initialize result
    result = {
        "risk_score": 0.0,
        "identified_conditions": [],
        "risk_assessment": ""
    }
    
    # If no conditions, return minimal risk
    if not conditions:
        result["risk_assessment"] = "No medical conditions reported. Minimal risk."
        return result
    
    # Analyze each condition
    total_risk_score = 0.0
    max_risk_score = 0.0
    matched_conditions = []
    
    for condition in conditions:
        # Search for similar conditions in vector store
        matches = vector_store.search(condition)
        
        if matches:
            # Use the top match
            top_match = matches[0]
            risk_score = top_match["data"]["risk_score"]
            
            matched_conditions.append({
                "reported_condition": condition,
                "matched_condition": top_match["condition"],
                "risk_score": risk_score,
                "description": top_match["data"]["description"],
                "complications": top_match["data"]["complications"]
            })
            
            total_risk_score += risk_score
            max_risk_score = max(max_risk_score, risk_score)
    
    # Calculate average risk score
    avg_risk_score = total_risk_score / len(conditions) if conditions else 0.0
    
    # Determine overall risk assessment
    if max_risk_score >= 0.8:
        risk_assessment = "High risk due to serious medical conditions."
    elif max_risk_score >= 0.5 or avg_risk_score >= 0.4:
        risk_assessment = "Moderate risk. Standard medical review recommended."
    else:
        risk_assessment = "Low risk. Routine underwriting sufficient."
    
    # Populate result
    result["risk_score"] = avg_risk_score
    result["identified_conditions"] = matched_conditions
    result["risk_assessment"] = risk_assessment
    
    return result 