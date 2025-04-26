# Insurance System Architecture Diagrams

## System Overview

```mermaid
graph TB
    subgraph Frontend[Angular Frontend]
        FC[Quote Component]
        FAD[Application Detail]
        FQ[Quote Generation]
        FRA[Risk Assessment Display]
    end

    subgraph Backend[FastAPI Backend]
        BA[Application Router]
        BPC[Premium Calculator]
        BRA[Risk Assessment]
        BDB[Database Service]
    end

    subgraph AI[AI Processing Layer]
        AILS[LLM Service]
        AIVS[Vector Store]
        AICA[Crew AI Orchestrator]
        AIRA[Risk Assessment Pipeline]
    end

    subgraph DB[Databases]
        VDB[(Vector DB)]
        SQL[(PostgreSQL)]
    end

    %% Frontend to Backend connections
    FC --> BA
    FAD --> BA
    FQ --> BPC
    FRA --> BRA

    %% Backend to AI connections
    BA --> AICA
    BPC --> AIRA
    BRA --> AILS

    %% AI internal connections
    AILS --> AIVS
    AICA --> AILS
    AIRA --> AIVS

    %% Database connections
    AIVS --> VDB
    BA --> SQL
    BPC --> SQL
```

## Risk Assessment Flow

```mermaid
flowchart TD
    subgraph Input[Input Processing]
        A[Application Data] --> MH[Medical History]
        A --> LF[Lifestyle Factors]
        A --> PI[Personal Info]
    end

    subgraph RiskAnalysis[Risk Analysis]
        MH --> VEC[Vector Similarity Search]
        VEC --> RC[Risk Calculation]
        LF --> RFS[Risk Factor Scoring]
        RFS --> RC
        PI --> AGE[Age Factor Analysis]
        AGE --> RC
    end

    subgraph AI[AI Processing]
        RC --> LLM[LLM Analysis]
        LLM --> INS[Insight Extraction]
        INS --> REC[Recommendations]
    end

    subgraph Output[Results]
        RC --> RS[Risk Score]
        INS --> RA[Risk Assessment]
        REC --> PR[Premium Recommendation]
    end
```

## Premium Calculation Process

```mermaid
flowchart LR
    subgraph Input[Inputs]
        APP[Application Data]
        RA[Risk Assessment]
    end

    subgraph Calculation[Premium Calculation]
        BR[Base Rate]
        RM[Risk Multiplier]
        AF[Age Factor]
        MF[Medical Factor]
        LF[Lifestyle Factor]
    end

    subgraph Processing[Processing]
        APP --> BR
        RA --> RM
        APP --> AF
        RA --> MF
        APP --> LF
    end

    subgraph Output[Final Premium]
        BR --> FP[Final Premium]
        RM --> FP
        AF --> FP
        MF --> FP
        LF --> FP
    end
```

## Crew AI Orchestration

```mermaid
sequenceDiagram
    participant App as Application
    participant CO as Crew Orchestrator
    participant MA as Medical Agent
    participant FA as Fraud Agent
    participant AA as Actuarial Agent
    participant UA as Underwriting Agent

    App->>CO: Submit Application
    CO->>MA: Analyze Medical History
    CO->>FA: Check Fraud Patterns
    CO->>AA: Calculate Risk Metrics
    CO->>UA: Evaluate Policy Terms

    MA-->>CO: Medical Assessment
    FA-->>CO: Fraud Analysis
    AA-->>CO: Risk Calculations
    UA-->>CO: Policy Evaluation

    CO->>App: Final Assessment
```

## LLM Service Processing

```mermaid
graph TD
    subgraph Input[Input Processing]
        AD[Application Data] --> CP[Context Preparation]
        CP --> EG[Embedding Generation]
    end

    subgraph Processing[LLM Processing]
        EG --> SCR[Similar Case Retrieval]
        SCR --> AG[Analysis Generation]
        AG --> IE[Insight Extraction]
    end

    subgraph Output[Output Generation]
        IE --> RF[Risk Factors]
        IE --> MI[Medical Insights]
        IE --> LI[Lifestyle Impact]
        RF --> FR[Final Recommendations]
        MI --> FR
        LI --> FR
    end

    subgraph ErrorHandling[Error Recovery]
        AG -- Error --> FB[Fallback Processing]
        FB --> BR[Basic Risk Assessment]
        FB --> CP[Conservative Premium]
        FB --> MR[Manual Review Flag]
    end
```

These diagrams provide a visual representation of the system architecture and key processes described in the implementation guide. Each diagram focuses on a specific aspect of the system:

1. System Overview: Shows the high-level architecture and component interactions
2. Risk Assessment Flow: Details the risk assessment process
3. Premium Calculation Process: Illustrates premium calculation workflow
4. Crew AI Orchestration: Shows the interaction between AI agents
5. LLM Service Processing: Details the LLM service workflow

The diagrams use Mermaid notation, which can be rendered by many Markdown viewers and documentation systems. 