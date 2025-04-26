import os
import logging
from dotenv import load_dotenv
from app.database.vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def seed_vector_database():
    """Seed the vector database with insurance underwriting guidelines and knowledge."""
    
    # Initialize vector store
    collection_name = os.getenv("VECTOR_COLLECTION_NAME", "insurance_data")
    persist_directory = os.getenv("VECTOR_DB_PATH", "./vector_db")
    
    logger.info(f"Initializing vector store with collection '{collection_name}' at '{persist_directory}'")
    vector_store = VectorStore(collection_name=collection_name, persist_directory=persist_directory)
    
    # Sample insurance underwriting guidelines
    insurance_guidelines = [
        {
            "text": """
            Age-Based Life Insurance Underwriting Guidelines:
            - Age 18-30: Lowest risk category, standard rates apply with minimal health requirements
            - Age 31-45: Low risk category, may require basic health screening
            - Age 46-60: Medium risk category, requires comprehensive health screening
            - Age 61-70: Higher risk category, requires detailed medical examination and history
            - Age 71-80: High risk category, specialized underwriting required
            - Age 81+: Very high risk, may be declined based on health assessment
            """,
            "metadata": {"category": "underwriting", "subcategory": "age_guidelines"}
        },
        {
            "text": """
            Medical Risk Factors in Life Insurance:
            - Cardiovascular conditions: Heart disease, hypertension, stroke history
            - Respiratory conditions: Asthma, COPD, sleep apnea
            - Metabolic disorders: Diabetes (Type 1 and 2), thyroid disorders
            - Cancer: Current diagnosis, history of cancer, family history
            - Autoimmune disorders: Lupus, rheumatoid arthritis, multiple sclerosis
            - Neurological conditions: Epilepsy, Parkinson's, Alzheimer's
            - Mental health conditions: Depression, anxiety, bipolar disorder, schizophrenia
            - Substance use: Tobacco, alcohol, recreational drugs
            """,
            "metadata": {"category": "underwriting", "subcategory": "medical_risk"}
        },
        {
            "text": """
            Premium Calculation Methodology:
            Base Premium = Coverage Amount * Base Rate
            Where:
            - Base Rate varies by product type (term, whole life, etc.)
            - Modified by age factor: increases with age
            - Modified by health factor: based on medical history and current conditions
            - Modified by lifestyle factor: occupation, hobbies, habits
            - Modified by policy term: longer terms have higher rates
            - Modified by payment frequency: monthly payments have small surcharge
            """,
            "metadata": {"category": "underwriting", "subcategory": "premium_calculation"}
        },
        {
            "text": """
            High-Risk Occupations Assessment:
            - Military personnel in active combat roles: 200% base premium
            - Commercial fishermen: 150-175% base premium
            - Mining and extraction workers: 150-200% base premium
            - Construction workers (high-rise): 125-150% base premium
            - Law enforcement officers: 125-150% base premium
            - Firefighters: 125-150% base premium
            - Professional athletes (contact sports): 125-175% base premium
            - Aviation professionals (pilots): 125-150% base premium
            - Offshore oil rig workers: 150-175% base premium
            """,
            "metadata": {"category": "underwriting", "subcategory": "occupation_risk"}
        },
        {
            "text": """
            Underwriting Decision Categories:
            - Approve Standard: Applicant meets all standard criteria
            - Approve Preferred: Applicant exceeds standard health requirements
            - Approve Substandard: Approved with higher premiums due to risk factors
            - Refer to Underwriter: Requires additional review by senior underwriter
            - Postpone: Temporary delay of decision pending additional information
            - Decline: Application does not meet minimum requirements for approval
            
            Reasons for decline may include:
            - Terminal illness with short life expectancy
            - Recent major cardiac event
            - Active cancer treatment with poor prognosis
            - Multiple severe chronic conditions
            - History of fraud on insurance applications
            """,
            "metadata": {"category": "underwriting", "subcategory": "decision_categories"}
        },
        {
            "text": """
            Special Coverage Considerations:
            - Hazardous activities or hobbies may require riders or exclusions
            - Foreign travel or residence may affect eligibility or rates
            - Aviation activities may require additional premium or exclusion
            - Military deployment may affect coverage or require special provisions
            - Certain medical treatments or procedures may require waiting periods
            - Family history of hereditary conditions may affect risk classification
            """,
            "metadata": {"category": "underwriting", "subcategory": "special_considerations"}
        },
        {
            "text": """
            Medical Examination Requirements By Coverage Amount:
            - Under $100,000: Basic questionnaire, no exam for applicants under 45
            - $100,000 - $250,000: Basic health measurements and blood test
            - $250,001 - $500,000: Full blood panel and urine analysis
            - $500,001 - $1,000,000: Above plus ECG and more detailed medical history
            - Over $1,000,000: Comprehensive medical exam including stress test and specialized lab work
            
            Age increases requirements at each coverage level.
            """,
            "metadata": {"category": "underwriting", "subcategory": "medical_requirements"}
        },
        {
            "text": """
            Terminal Illness Policy:
            Any applicant diagnosed with a terminal illness with life expectancy under 24 months should be declined for standard coverage. Alternative products like guaranteed issue policies with appropriate limitations may be offered instead.
            
            Applications indicating active hospice care, end-stage disease, or palliative treatment should be declined with explanation of alternative options available.
            """,
            "metadata": {"category": "underwriting", "subcategory": "terminal_illness"}
        }
    ]
    
    # Extract texts and metadatas
    texts = [item["text"] for item in insurance_guidelines]
    metadatas = [item["metadata"] for item in insurance_guidelines]
    
    # Add documents to vector store
    logger.info(f"Adding {len(texts)} insurance guideline documents to vector store")
    try:
        document_ids = vector_store.add_documents(texts=texts, metadatas=metadatas)
        logger.info(f"Successfully added {len(document_ids)} documents to vector store")
        logger.info(f"Document IDs: {document_ids}")
        
        # Test retrieval
        logger.info("Testing vector store retrieval...")
        query = "insurance underwriting for elderly applicants with health conditions"
        results = vector_store.similarity_search(query, k=2)
        
        logger.info(f"Retrieved {len(results)} results for test query")
        for i, result in enumerate(results):
            logger.info(f"Result {i+1}: {result['content'][:100]}... (score: {result['similarity']})")
        
        return True
    except Exception as e:
        logger.error(f"Error seeding vector database: {e}")
        return False

if __name__ == "__main__":
    success = seed_vector_database()
    if success:
        logger.info("Vector database seeding completed successfully")
    else:
        logger.error("Vector database seeding failed") 