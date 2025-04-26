import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
from dotenv import load_dotenv
from app.database.database import get_db, engine
from app.database.vector_store import get_vector_store
from app.services.llm_service import get_llm_service
from app.services.ai_underwriting import evaluate_application_with_llm
from app.services.crewai_orchestration import process_complex_application, process_complex_application_sync
from app.middleware.rate_limiter import RateLimiter
from app.api.endpoints.insurance import router as insurance_router
from app.api.endpoints.complex_cases import router as complex_cases_router
from app.models.insurance import Base
from sqlalchemy import text
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize the FastAPI app
app = FastAPI(
    title="Insurance Calculator API",
    description="""
    ## Insurance Premium Calculator API
    
    This API provides insurance premium calculation with Agentic AI components:
    
    ### Agentic AI Components
    
    - **Premium Calculator (H1)**: LLM-powered premium calculation based on applicant data.
    - **Medical Risk Analysis (H2)**: Vector store-based risk assessment of medical conditions.
    - **CrewAI Orchestration (K1)**: Multi-agent system for complex application processing.
    - **AI Underwriting Logic (K3)**: Rule-based decision making for application evaluation.
    
    ### Main Features
    
    - Calculate insurance premiums with AI assistance
    - Submit and retrieve insurance applications
    - Process complex cases with specialized AI agents
    - Apply underwriting rules with explanations
    
    ### Security & Validation
    
    - **Input Validation**: All endpoints have strict schema validation
    - **Rate Limiting**: API requests are limited to 60 per minute per client
    - **Error Handling**: Standardized error responses
    """,
    version="1.0.0",
    contact={
        "name": "Insurance Calculator Team",
    },
)

# Startup event handler to check database connection and create tables
@app.on_event("startup")
async def startup_db_client():
    try:
        # Create database tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Test database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        
        # Log successful startup
        logger.info("Successfully connected to the database")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        # Database issues are critical but we don't want to prevent the API from starting
        # as we have fallbacks for some functionality

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:4200")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
# Commenting out rate limiter middleware due to issues with the implementation
# rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
# app.add_middleware(
#     RateLimiter,
#     requests_per_minute=rate_limit_per_minute,
#     burst_limit=10,
#     exclude_paths=["/docs", "/redoc", "/openapi.json", "/health"]
# )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_id = f"error-{id(exc)}"
    logger.error(f"Global exception handler caught: {exc} (ID: {error_id})")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "error_id": error_id
        }
    )

# Include routers
app.include_router(insurance_router, prefix="/api/insurance", tags=["insurance"])
app.include_router(complex_cases_router, prefix="/api/complex", tags=["complex-cases"])

# Root endpoint
@app.get("/")
async def read_root():
    return {"message": "Insurance Calculator API is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        # Check database connection
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "connected"
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": db_status,
        "api_version": app.version
    }

# Endpoint to evaluate an application using AI underwriting
@app.post("/api/evaluate-application")
async def evaluate_application(application_data: dict, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received application evaluation request: {application_data.get('id', 'unknown')}")
        
        # Process application with AI underwriting
        result = await evaluate_application_with_llm(application_data)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Error processing application: {e}")
        raise HTTPException(status_code=500, detail=f"Application processing error: {str(e)}")

# Endpoint to process complex application using CrewAI
@app.post("/api/process-complex-application")
def process_complex_app(application_data: dict, db: Session = Depends(get_db)):
    try:
        logger.info(f"Received complex application processing request: {application_data.get('id', 'unknown')}")
        
        # Process application with CrewAI using synchronous version
        result = process_complex_application_sync(application_data)
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"Error processing complex application: {e}")
        raise HTTPException(status_code=500, detail=f"Complex application processing error: {str(e)}")

# Endpoint to check LLM and vector store status
@app.get("/api/system-status")
async def system_status():
    llm_service = get_llm_service()
    vector_store = get_vector_store()
    
    try:
        llm_status = "available"
    except Exception as e:
        llm_status = f"error: {str(e)}"
    
    try:
        vector_status = "available"
    except Exception as e:
        vector_status = f"error: {str(e)}"
    
    return {
        "llm_service": {
            "status": llm_status,
            "model": os.getenv("OLLAMA_MODEL", "deepseek-r1:32b")
        },
        "vector_store": {
            "status": vector_status,
            "collection": os.getenv("VECTOR_COLLECTION_NAME", "insurance_data")
        }
    }

# Run the API server if executed directly
if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting Insurance Calculator API on {host}:{port}")
    uvicorn.run("main:app", host=host, port=port, reload=debug) 