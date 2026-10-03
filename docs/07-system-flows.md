# 07. System Flows

Sequence diagrams for the AI internals (K1 crew, K3 LLM review) are in
[04-ai-components.md](04-ai-components.md). This chapter covers the
end-to-end flows around them.

## 7.1 End-to-end user journey (UI)

```mermaid
flowchart TD
    start([Open app]) --> calc["/calculator<br/>Quick estimate"]
    calc -->|Calculate| est["Show monthly premium,<br/>risk tier, tip"]
    est -->|Apply for Insurance| ca
    calc -->|nav: Search Applications| search

    search["/search<br/>Search accounts"] -->|Search| found{matches?}
    found -- yes --> list[Results table]
    list -->|View| detail
    found -- no --> createBtn[Create New Account button]
    createBtn --> ca["/create-account<br/>pre-filled form"]
    ca -->|Create| saveAcc[(append to<br/>insurance_accounts)]
    saveAcc -->|after 1 s| detail
    ca -->|Cancel| search

    detail["/application/:id<br/>Account + quotes"] -->|Edit Details → Save| upd[(update account<br/>contact fields)]
    upd --> detail
    detail -->|Create Quote| quote["/quote?applicationId=id<br/>12-section questionnaire"]
    quote -->|Submit| saveQ[(append to<br/>insurance_quotes)]
    saveQ --> detail
    quote -->|Cancel| detail
    detail -->|click quote row /<br/>Quote Overview| dlg[[Quote Overview dialog]]
    dlg -->|Close| detail
    detail -->|Back| search
```

## 7.2 Navigation state machine

```mermaid
stateDiagram-v2
    [*] --> Calculator : "/" redirect
    Calculator --> Search : nav tab
    Calculator --> CreateAccount : Apply (premium dropped)
    Search --> CreateAccount : no results → Create
    Search --> ApplicationDetail : View
    CreateAccount --> ApplicationDetail : created
    CreateAccount --> Search : Cancel
    ApplicationDetail --> Quote : Create Quote
    ApplicationDetail --> QuoteOverview : row click
    QuoteOverview --> ApplicationDetail : close
    Quote --> ApplicationDetail : Submit / Cancel
    Quote --> Search : missing/unknown applicationId
    ApplicationDetail --> Search : Back
    Search --> Calculator : nav tab
    note right of ApplicationDetail
        Unknown id → snackbar error,
        page stays empty
    end note
```

## 7.3 Sequence: search → create account → detail

```mermaid
sequenceDiagram
    actor A as Agent
    participant S as InsuranceSearchComponent
    participant IS as InsuranceService
    participant LS as localStorage
    participant R as Router
    participant C as CreateAccountComponent
    participant D as ApplicationDetailComponent
    participant QS as QuoteService

    A->>S: fill fields, Search
    S->>S: atLeastOneFieldFilled()
    S->>IS: searchAccounts(form.value)
    IS->>LS: getItem('insurance_accounts')
    LS-->>IS: JSON array
    IS->>IS: filter (substring match on 8 fields)
    IS-->>S: of([])
    S->>S: showCreateButton = true
    A->>S: Create New Account
    S->>R: navigate(['/create-account'], {state:{accountData}})
    R->>C: construct
    C->>R: getCurrentNavigation().extras.state
    C->>C: accountForm.patchValue(accountData)
    A->>C: complete form, Create
    C->>IS: createAccount({...form, accountNumber, createdAt})
    IS->>IS: id = Date.now(), accountNumber = ACC-XXXXX-XX
    IS->>LS: setItem('insurance_accounts', [...accounts, new])
    IS-->>C: of(newAccount)
    C->>C: snackbar "Account created successfully!"
    C->>R: (after 1 s) navigate(['/application', id])
    R->>D: route.params {id}
    par forkJoin
        D->>IS: getApplicationById(id)
        IS->>LS: getItem('insurance_accounts')
        IS-->>D: of(account)
    and
        D->>QS: getQuotesByApplicationId(id)
        QS->>LS: getItem('insurance_quotes')
        QS-->>D: of([])
    end
    D->>D: attach quotes [] and patch editForm
```

## 7.4 Sequence: create quote → overview

```mermaid
sequenceDiagram
    actor A as Agent
    participant D as ApplicationDetailComponent
    participant Q as QuoteComponent
    participant IS as InsuranceService
    participant QS as QuoteService
    participant LS as localStorage
    participant DLG as QuoteOverviewDialogComponent

    A->>D: Create Quote
    D->>Q: /quote?applicationId=id
    Q->>IS: getApplication(id)
    IS-->>Q: account
    Q->>Q: populateApplicantInfo() + QAP-XXXXX-XXX
    A->>Q: answer questions (selectionChange → updateConditionalFields)
    A->>Q: Submit
    Q->>Q: valid? calculatePremium() = 500 + loadings
    Q->>Q: determineCoverageAmount() = 100000
    Q->>QS: createQuote({applicationId, premium, coverageAmount, quoteDetails})
    QS->>QS: id = Date.now(), QT-XXXXXX-XX, status Pending
    QS->>LS: setItem('insurance_quotes', ...)
    QS-->>Q: quote
    Q->>D: navigate /application/id (snackbar with quote number)
    D->>QS: getQuotesByApplicationId(id)
    A->>D: click quote row
    D->>DLG: dialog.open({quote, application}, width 700px)
    DLG->>DLG: analyzeQuote() → analyzeRiskFactors() + analyzeUnderwritingConcerns()
    DLG-->>A: premium, factors, concerns, breakdown bars
```

## 7.5 Sequence: quick calculator

```mermaid
sequenceDiagram
    actor P as Prospect
    participant C as InsuranceCalculatorComponent
    participant IS as InsuranceService
    participant R as Router
    P->>C: age, smoker, coverage, conditions → Calculate
    C->>C: form valid?
    C->>IS: calculatePremium(form.value)
    Note over IS: pure TypeScript, no HTTP
    IS-->>C: of({premium, riskAssessment, recommendation, coverageAmount})
    C-->>P: result card (innerHTML)
    P->>C: Apply for Insurance
    C->>R: navigate(['/create-account'], {state:{premiumData}})
    Note over R: CreateAccountComponent reads only state.accountData,<br/>so premiumData is discarded
```

## 7.6 Backend request lifecycle

```mermaid
flowchart TD
    subgraph Import["Process start (import main.py, top to bottom)"]
        i1["import database.py →<br/>logging.basicConfig(INFO) (first call wins)<br/>engine = sqlite:///./app_database.db"] --> i2["import vector_store →<br/>VectorStore() singleton:<br/>download/load MiniLM, open Chroma"]
        i2 --> i3["import llm_service →<br/>reads OLLAMA_HOST / OLLAMA_MODEL from os.environ<br/>LLMService() singleton (no network yet)"]
        i3 --> i4["import ai_underwriting, crewai_orchestration,<br/>rate_limiter, routers →<br/>premium_calculator / medical_risk stubs"]
        i4 --> i5["load_dotenv() — too late for values read above"]
        i5 --> i6["logging.basicConfig(FileHandler('logs/api.log'))<br/>handler is constructed (fails if logs/ missing)<br/>but basicConfig is a no-op, so nothing is written to it"]
        i6 --> i7["FastAPI app, CORS(FRONTEND_URL),<br/>exception handler, routers"]
    end
    subgraph Startup["@app.on_event('startup')"]
        s1["Base.metadata.create_all(engine)"] --> s2["SELECT 1"]
        s2 -->|fail| s3[log error, continue]
    end
    subgraph Request["Per request"]
        r1[CORSMiddleware] --> r2["Route match"]
        r2 --> r3["Pydantic body validation<br/>(422 on failure)"]
        r3 --> r4["Depends(get_db) → SessionLocal()"]
        r4 --> r5[Handler → services]
        r5 --> r6{exception?}
        r6 -- HTTPException --> r7[4xx/5xx detail]
        r6 -- other --> r8["global handler → 500<br/>{error, detail, error_id}"]
        r6 -- no --> r9[response_model serialization]
        r9 --> r10["finally: db.close()"]
    end
    Import --> Startup --> Request
```

## 7.7 Sequence: submit application via API (H1)

```mermaid
sequenceDiagram
    participant Cl as API Client
    participant F as FastAPI
    participant EP as insurance.create_application
    participant H1 as premium_calculator.calculate_premium
    participant Sim as local LLMService (stub)
    participant DB as SQLite
    Cl->>F: POST /api/insurance/applications/
    F->>F: validate InsuranceApplicationCreate
    alt invalid
        F-->>Cl: 422
    end
    F->>EP: application, db
    EP->>H1: {age, coverage, medical_history, risk_factors}
    H1->>Sim: generate_response(prompt, system_prompt)
    Sim->>Sim: parse prompt, compute premium
    Sim--xH1: NameError (base_premium)
    H1-->>EP: {coverage × 0.05, "medium", "Error in AI calculation…"}
    EP->>DB: INSERT insurance_applications
    EP->>DB: COMMIT, REFRESH
    EP-->>F: ORM object
    F-->>Cl: 201 InsuranceApplicationResponse
```

## 7.8 Sequence: calculate premium with medical risk (H2 → H1)

```mermaid
sequenceDiagram
    participant Cl as API Client
    participant EP as insurance.premium_calculation
    participant H2 as analyze_medical_risk
    participant VS as local VectorStore (dict)
    participant H1 as calculate_premium
    Cl->>EP: POST /api/insurance/calculate-premium/
    EP->>H2: medical_history
    loop each condition
        H2->>VS: search(condition)
        VS-->>H2: top matches (0.9 / 0.7)
    end
    H2-->>EP: {risk_score, identified_conditions, risk_assessment}
    EP->>H1: {..., risk_analysis}
    Note over H1: risk_analysis ignored,<br/>NameError → fallback
    H1-->>EP: {premium_amount, risk_assessment, ai_recommendation}
    EP-->>Cl: 200 PremiumCalculationResponse
```

## 7.9 Sequence: complex application with persistence (K1)

```mermaid
sequenceDiagram
    participant Cl as API Client
    participant EP as complex_cases.process_complex_case
    participant K1 as process_complex_application_sync
    participant DB as SQLite
    Cl->>EP: POST /api/complex/complex-application/
    EP->>K1: application_data (dicts)
    K1->>K1: event loop → Crew.run → {} (no agent matched)
    K1-->>EP: {}
    EP->>DB: INSERT (premium NULL, is_approved false, ai_recommendation "")
    EP-->>Cl: 201 {"application_id": n}
```

## 7.10 AI fallback decision flow (all components)

```mermaid
flowchart LR
    req[AI request] --> try{primary path}
    try -->|H1| h1x[NameError] --> h1f["coverage × 5%"]
    try -->|K3| k3a["LLM call ×3 retries"] --> k3b{"parsed and<br/>result[decision] found?"}
    k3b -- no (always today) --> k3f["rule decision +<br/>cov×1%×(1+age/100)×(1+2r)"]
    k3b -- yes --> k3ok[LLM decision]
    try -->|K1 agent| k1a{task routed?}
    k1a -- no (today) --> k1e["{}"]
    k1a -- yes --> k1b["LLM ×3 retries"] --> k1c{prompt formats?}
    k1c -- no (JSON braces) --> k1f[role-specific fallback]
    k1c -- yes --> k1ok[LLM output]
    style h1f fill:#ffd
    style k3f fill:#ffd
    style k1e fill:#fdd
    style k1f fill:#ffd
```

## 7.11 Quote and application lifecycles

```mermaid
stateDiagram-v2
    state "Browser quote (QuoteService)" as BQ {
        [*] --> Pending : createQuote()
        Pending --> Approved : updateQuoteStatus() — no UI calls it
        Pending --> Rejected : updateQuoteStatus() — no UI calls it
    }
    state "Backend application (SQLite)" as BA {
        [*] --> pending : INSERT
        pending --> pending : no update endpoint exists
    }
```
