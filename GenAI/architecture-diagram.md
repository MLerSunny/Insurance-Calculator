# Insurance Calculator Architecture Diagram

```mermaid
graph TB
    %% Client Side
    subgraph "Frontend (Angular)"
        A[Browser] --> B[Angular App]
        B --> C1[App Component]
        C1 --> C2[Insurance Calculator Component]
        
        subgraph "Angular Services"
            D1[Insurance Service]
            D2[Auth Service]
        end
        
        C2 --> D1
        C2 --> D2
    end
    
    %% Server Side
    subgraph "Backend (FastAPI)"
        E[FastAPI App] --> F1[CORS Middleware]
        E --> F2[Rate Limit Middleware]
        E --> F3[Cache Middleware]
        
        subgraph "API Endpoints"
            G1[Calculate Premium]
            G2[Health Check]
            G3[Auth Endpoints]
        end
        
        E --> G1
        E --> G2
        E --> G3
        
        subgraph "Services"
            H1[Premium Calculator]
            H2[Medical Risk Analysis]
            H3[Authentication]
        end
        
        G1 --> H1
        H1 --> H2
        G3 --> H3
        
        subgraph "Data Layer"
            I1[Database]
            I2[Vector Store]
        end
        
        H1 --> I1
        H2 --> I2
    end
    
    %% Communication
    D1 -->|HTTP Requests| G1
    D2 -->|HTTP Requests| G3
    
    %% Configuration and Utilities
    subgraph "Configuration & Utilities"
        J1[Config]
        J2[Utils]
        J3[Environment Variables]
    end
    
    E --> J1
    H1 --> J2
    H2 --> J2
    E --> J3
    
    %% Styling
    classDef frontend fill:#f9f,stroke:#333,stroke-width:2px
    classDef backend fill:#bbf,stroke:#333,stroke-width:2px
    classDef data fill:#bfb,stroke:#333,stroke-width:2px
    classDef config fill:#fbb,stroke:#333,stroke-width:2px
    
    class A,B,C1,C2,D1,D2 frontend
    class E,F1,F2,F3,G1,G2,G3,H1,H2,H3 backend
    class I1,I2 data
    class J1,J2,J3 config
```

## How to Generate a High-Definition PNG

You can generate a high-definition PNG of this diagram using one of the following methods:

### Method 1: Using Mermaid Live Editor

1. Go to [Mermaid Live Editor](https://mermaid.live/)
2. Copy and paste the mermaid code above into the editor
3. Customize the theme if desired
4. Click on "Download PNG" in the menu

### Method 2: Using VS Code with Mermaid Extension

1. Install the "Markdown Preview Mermaid Support" extension in VS Code
2. Open this markdown file in VS Code
3. Click the "Open Preview" button
4. Right-click on the rendered diagram and select "Save image as..."

### Method 3: Using GitHub

GitHub natively supports mermaid diagrams in markdown files. Simply commit this file to a GitHub repository, and the diagram will be rendered automatically.

## Architecture Overview

This diagram illustrates the complete architecture of the Insurance Calculator application:

1. **Frontend Layer**:
   - Angular application with components and services
   - Communication with backend via HTTP requests

2. **Backend Layer**:
   - FastAPI application with middleware
   - API endpoints for calculating premiums and authentication
   - Business logic services for premium calculation and risk analysis

3. **Data Layer**:
   - Database for storing user and application data
   - Vector store for medical risk analysis

4. **Configuration & Utilities**:
   - Configuration settings
   - Utility functions
   - Environment variables 