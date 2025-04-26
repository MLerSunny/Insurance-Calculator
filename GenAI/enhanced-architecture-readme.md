# Enhanced Insurance Application Architecture

This document describes the architecture of the enhanced AI-powered insurance application, as visualized in the accompanying Mermaid diagram (`enhanced-architecture.mmd`).

## Architecture Overview

The enhanced architecture integrates advanced AI capabilities into the existing Angular-FastAPI application, creating a comprehensive system that leverages LLMs, vector databases, and agent-based orchestration for intelligent insurance underwriting.

## Key Components

### Client-Side
- **Angular Application**: The frontend remains largely unchanged while being enhanced with capabilities to display AI-generated insights.
  - **Quote Overview Dialog**: Enhanced to display AI-generated risk analyses and premium explanations.
  - **AI Insight Service**: New Angular service to fetch AI-generated insights from the backend.

### Server-Side
#### FastAPI Application
- **API Endpoints**: Enhanced with a new AI Analysis API endpoint.
- **Services**:
  - **Premium Calculator**: Calculates insurance premiums based on application data and AI insights.
  - **Medical Risk Analysis**: Analyzes medical conditions for risk assessment.
  - **Vector Store**: Interface for vector database operations.
  - **Application & Quote Services**: Handle CRUD operations for insurance applications and quotes.

#### AI Processing Layer
- **LLM Inference Service**: Handles interactions with LLM APIs for text generation and analysis.
- **Vector Database**: Stores embeddings of medical conditions, applications, and precedent cases.
- **CrewAI Orchestration**: Coordinates specialized AI agents to collaboratively analyze insurance applications.
- **Langchain Pipelines**: Implements retrieval-augmented generation and maintains context across multi-step reasoning.

#### Agent System
- **Medical Specialist Agent**: Evaluates medical conditions and their impact on risk.
- **Actuarial Agent**: Determines premium calculations based on risk profiles.
- **Fraud Detection Agent**: Identifies potential inconsistencies or fraud indicators.
- **Underwriting Agent**: Makes final recommendations based on all available information.

### External Services
- **OpenAI API**: Provides the foundation models for LLM inference.
- **Cloud Storage**: Stores backup data and model artifacts.

## Data Flow

1. Users interact with the Angular application to submit insurance applications or request quotes.
2. Application data is sent to the FastAPI backend via service calls.
3. For AI-powered analysis:
   - Application data is processed by the AI Analysis API
   - Medical conditions are embedded and queried against the Vector Database
   - The CrewAI system orchestrates specialized agents to analyze different aspects
   - LLM inference generates explanations and recommendations
4. Results are returned to the frontend and displayed in the Quote Overview Dialog.

## Technical Implementation

The architecture follows a modular design that allows for:
- **Progressive Enhancement**: AI capabilities can be added incrementally without disrupting existing functionality.
- **Scalability**: AI components can be independently scaled based on demand.
- **Flexibility**: Different LLM providers can be swapped in without changing the overall architecture.
- **Observability**: Clear separation of concerns enables targeted monitoring and troubleshooting.

This enhanced architecture delivers significant improvements in risk assessment accuracy, premium personalization, fraud detection, and customer experience while maintaining the familiar user interface. 