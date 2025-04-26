# Insurance Premium Calculator

An AI-powered insurance premium calculator application with FastAPI backend and Angular frontend.

## Project Structure

- **backend/** - FastAPI backend application
- **frontend/insurance-calculator/** - Angular frontend application

## Agentic AI Components

This application incorporates multiple Agentic AI components:

1. **Premium Calculator (H1)**: LLM-powered premium calculation based on applicant data
2. **Medical Risk Analysis (H2)**: Vector store-based risk assessment of medical conditions
3. **CrewAI Orchestration (K1)**: Multi-agent system for complex application processing
4. **AI Underwriting Logic (K3)**: Rule-based decision making for application evaluation

## Production Readiness Features

The application has been enhanced with several production readiness features:

### Testing Infrastructure
- **Comprehensive Tests**: Unit tests for critical backend components
- **Test Coverage Reports**: Generated via pytest-cov
- **Test Fixtures**: Mocking external dependencies for reliable testing

### Security Enhancements
- **Input Validation**: Strict schema validation with Pydantic
- **Rate Limiting**: Token bucket algorithm to prevent API abuse
- **Error Handling**: Standardized error responses

### Monitoring & Logging
- **Structured Logging**: Consistent logging format
- **Performance Tracking**: Timing metrics for AI operations

### Resilience Features
- **Retry Mechanisms**: For LLM calls with exponential backoff
- **Fallback Strategies**: When AI components fail
- **SQLite Fallback**: For database operations

## Running the Backend

To run the backend API:

```powershell
# Run with the convenience script
.\run_backend.ps1
```

Or manually:

```powershell
cd backend
python -m uvicorn main:app --reload
```

The API will be available at http://localhost:8000

## Testing Ollama Integration

To test the Ollama LLM integration:

```powershell
# Run with the convenience script
.\test_ollama_integration.ps1
```

Or manually:

```powershell
cd backend
python test_ollama.py
```

## Running Tests

To run the backend test suite:

```powershell
cd backend
.\run_tests.ps1
```

## Running the Frontend

To start the Angular frontend:

```powershell
cd frontend/insurance-calculator
ng serve
```

The frontend will be available at http://localhost:4200

## API Documentation

Once the backend is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Next Steps for Full Production Readiness

While many production readiness features have been implemented, the following are still needed:

1. **Frontend Error Handling Components**: Add UI components to display errors
2. **Authentication System**: Implement JWT/OAuth authentication
3. **Metrics Dashboard**: Set up Prometheus/Grafana for monitoring
4. **Deployment Pipeline**: CI/CD automation for testing and deployment
5. **Load Testing**: Performance testing under stress conditions