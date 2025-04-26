# Insurance Calculator Backend API

The backend API for the Insurance Premium Calculator application, built with FastAPI, SQLAlchemy and various Agentic AI components.

## Features

- RESTful API for insurance premium calculations
- Application submission and retrieval
- Integration with agentic AI components:
  - Premium Calculator (LLM integration)
  - Medical Risk Analysis (Vector Store)
  - CrewAI Orchestration
  - AI Underwriting Logic

## Agentic AI Components

### Premium Calculator
Uses LLM integration to calculate premiums based on applicant data. The service formats the request for the LLM, processes the response, and returns the calculated premium.

### Medical Risk Analysis
Leverages a vector store to analyze medical conditions and assess risk levels. Compares reported conditions against known conditions to determine similarity and risk factors.

### CrewAI Orchestration
Coordinates multiple specialized AI agents to process complex insurance applications. Agents include underwriters, risk analysts, and medical experts, each with specific tasks and responsibilities.

### AI Underwriting Logic
Implements rule-based decision-making for insurance applications. Evaluates applications against predefined rules to determine approval, referral, or decline status.

## Production Readiness Features

This backend has been developed with production readiness in mind, incorporating the following features:

### Testing Infrastructure

- **Unit Tests**: Comprehensive test suite for all key components
  - Database models and connections
  - Vector store operations
  - LLM service integration
  - API endpoints
- **Test Coverage Reports**: Generated via pytest-cov
- **Mocking**: Test fixtures for external dependencies (LLM, vector store)

### Security & Validation

- **Input Validation**: Pydantic models with strict validation rules
  - Field-level validation
  - Custom validators for complex fields
  - Clear error messages
- **Rate Limiting**: Token bucket algorithm implementation
  - Configurable limits per client IP
  - Burst handling
  - Exclusion paths for documentation
- **Error Handling**: Standardized error responses

### Monitoring & Logging

- **Structured Logging**: Consistent format across all components
- **Request Tracking**: Log correlation for tracing requests
- **Performance Metrics**: Timing for AI component operations

### Resilience Features

- **Retry Mechanisms**: For LLM service calls with exponential backoff
- **Fallback Strategies**: Backup logic when AI components fail
- **Database Connection Pooling**: Efficient database connection management

## Running Tests

To run the test suite:

```bash
# Run the test script
./run_tests.ps1

# Or manually
python -m pytest tests/ -v --cov=app
```

## API Documentation

When the backend is running, documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./insurance.db` |
| `OLLAMA_HOST` | Ollama API host | `http://localhost:11434` |
| `OLLAMA_MODEL` | LLM model name | `deepseek-r1:32b` |
| `FRONTEND_URL` | CORS allowed origin | `http://localhost:4200` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit per client | `60` |

## Development Setup

1. Ensure Python 3.9+ is installed
2. Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.fixed.txt
   ```
4. Run the application:
   ```bash
   python -m uvicorn main:app --reload
   ```

## Production Deployment Considerations

- Use HTTPS in production
- Set appropriate rate limits
- Configure database connection pooling
- Enable application monitoring
- Set up health check endpoints for container orchestration

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the database:
- Create a PostgreSQL database named `insurance`
- Update the connection string in `app/database/database.py` if needed

## Running the Application

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000

API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

- `GET /api/insurance/applications/` - List all applications
- `POST /api/insurance/applications/` - Create a new application
- `GET /api/insurance/applications/{id}` - Get application details
- `POST /api/insurance/calculate-premium/` - Calculate premium for given parameters 