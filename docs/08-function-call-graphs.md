# 08. Function Call Graphs

Notation: solid arrows are calls that happen at runtime. Dashed arrows are
calls that exist in code but never execute, or are unreachable. Grey nodes
are dead code.

## 8.1 Backend module dependency graph

```mermaid
flowchart TB
    main["main.py"]
    ep_ins["api/endpoints/insurance.py"]
    ep_cx["api/endpoints/complex_cases.py"]
    db["database/database.py"]
    vs["database/vector_store.py"]
    models["models/insurance.py"]
    schemas["schemas/insurance.py"]
    llm["services/llm_service.py"]
    h1["services/premium_calculator.py (H1)"]
    h2["services/medical_risk_analysis.py (H2)"]
    k1["services/crewai_orchestration.py (K1)"]
    k3["services/ai_underwriting.py (K3)"]
    rl["middleware/rate_limiter.py"]

    main --> db & vs & llm & k3 & k1 & ep_ins & ep_cx & models
    main -.->|imported, registration commented out| rl
    ep_ins --> db & models & schemas & h1 & h2
    ep_cx --> db & models & schemas & k1 & k3
    k1 --> llm & vs
    k3 --> llm
    models --> db
    vs -->|langchain_chroma, langchain_huggingface| ext1[(Chroma / HF)]
    llm -->|langchain_ollama, langchain.chains| ext2[[Ollama]]

    classDef dead fill:#eee,stroke:#999,color:#666
    class rl dead
```

H1 and H2 import nothing from `llm_service` or `vector_store`. Each defines
its own same-named stub class.

## 8.2 Backend call tree per endpoint

### `POST /api/insurance/applications/`

```mermaid
flowchart LR
    A["create_application(application, db)"] --> B["calculate_premium(dict)"]
    B --> C["LLMService(H1 stub).generate_response(prompt, system_prompt)"]
    C --> C1[_extract_age]
    C --> C2[_extract_coverage]
    C --> C3[_extract_conditions]
    C --> C4[_calculate_age_factor]
    C --> C5[_calculate_condition_risk]
    C --> C6["_generate_assessment ✗ NameError"]
    B --> B1["fallback dict"]
    A --> D["InsuranceApplication(...)"]
    A --> E["db.add / commit / refresh"]
    A --> F["get_db() dependency"]
    style C6 fill:#fdd
```

### `POST /api/insurance/calculate-premium/`

```mermaid
flowchart LR
    A["premium_calculation(request)"] --> B["analyze_medical_risk(history)"]
    B --> B1["VectorStore(H2 stub).search(condition, top_k=3)"]
    A --> C["calculate_premium({..., risk_analysis})"]
    C --> C1["… same as above, fallback"]
```

### `GET /api/insurance/applications/` and `/{id}`

```mermaid
flowchart LR
    A["get_applications(skip, limit, db)"] --> Q1["db.query(InsuranceApplication).offset().limit().all()"]
    B["get_application(id, db)"] --> Q2["db.query(...).filter(id).first()"]
    Q2 -->|None| X["HTTPException 404"]
```

### `POST /api/evaluate-application`

```mermaid
flowchart LR
    A["evaluate_application(dict, db)"] --> B["evaluate_application_with_llm(dict)"]
    B --> C["rule_engine.evaluate_application(dict)"]
    C --> C1["rule['condition'](app) × 6"]
    B --> D["get_llm_service()"]
    B --> E["LLMService.structured_generation(vars, template, schemas)"]
    E --> E1["PromptTemplate(...)"]
    E --> E2["JsonOutputParser()"]
    E --> E3["LLMChain(...).ainvoke(vars)"]
    E3 --> E4["OllamaLLM → HTTP /api/generate"]
    B --> F["llm_evaluation['decision'] ✗ KeyError"]
    F --> G["fallback: rule decision + formula premium"]
    style F fill:#fdd
```

### `POST /api/complex/apply-underwriting-rules/`

```mermaid
flowchart LR
    A["apply_underwriting_rules(dict)"] --> B["UnderwritingRuleEngine()"]
    B --> C["evaluate_application(dict)"]
```

### `POST /api/complex/complex-application/` and `POST /api/process-complex-application`

```mermaid
flowchart LR
    A1["process_complex_case(application, db)"] --> S
    A2["process_complex_app(dict, db)"] --> S
    S["process_complex_application_sync(dict)"] --> L["asyncio.get_event_loop() / new_event_loop()"]
    S --> P["loop.run_until_complete(process_complex_application(dict))"]
    P --> AG["Agent(name, role, goal) × 3"]
    AG --> AG1["get_llm_service()"]
    AG --> AG2["get_vector_store()"]
    P --> CR["Crew(agents, tasks).run(context)"]
    CR --> M["next(a for a in agents if a.role == task.get('role')) → None"]
    CR -.->|never reached| X["_execute_agent_task(agent, task, ctx, results)"]
    X -.-> ET["Agent.execute_task(description, ctx)"]
    ET -.-> U["_process_underwriter_task"]
    ET -.-> R["_process_risk_analyst_task"]
    ET -.-> ME["_process_medical_expert_task"]
    U -.-> VSS["vector_store.similarity_search(k=3)"]
    U -.-> SG1["structured_generation"]
    R -.-> SG2["structured_generation"]
    ME -.-> SG3["structured_generation"]
    U -.-> FU["_fallback_underwriter_response"]
    R -.-> FR["_fallback_risk_analyst_response"]
    ME -.-> FM["_fallback_medical_expert_response"]
    A1 --> DB["InsuranceApplication(...); db.add/commit/refresh"]
    style M fill:#fdd
```

### `GET /health`, `GET /api/system-status`, startup

```mermaid
flowchart LR
    H["health_check()"] --> G["next(get_db())"] --> Q["db.execute(text('SELECT 1'))"]
    SS["system_status()"] --> GL["get_llm_service()"]
    SS --> GV["get_vector_store()"]
    SS --> ENV["os.getenv(OLLAMA_MODEL, VECTOR_COLLECTION_NAME)"]
    ST["startup_db_client()"] --> CA["Base.metadata.create_all(engine)"]
    ST --> G2["next(get_db()) → SELECT 1"]
```

## 8.3 Backend function index

| Function / method | File | Called by | Calls | Status |
|-------------------|------|-----------|-------|--------|
| `startup_db_client` | main.py | FastAPI startup | `create_all`, `get_db` | live |
| `global_exception_handler` | main.py | FastAPI on unhandled error | `JSONResponse` | live |
| `read_root`, `health_check`, `system_status` | main.py | HTTP | see 8.2 | live |
| `evaluate_application` | main.py | HTTP | `evaluate_application_with_llm` | live |
| `process_complex_app` | main.py | HTTP | `process_complex_application_sync` | live |
| `create_application`, `get_applications`, `get_application`, `premium_calculation` | endpoints/insurance.py | HTTP | see 8.2 | live |
| `process_complex_case`, `apply_underwriting_rules` | endpoints/complex_cases.py | HTTP | see 8.2 | live |
| `get_db` | database.py | every DB endpoint, startup, health | `SessionLocal` | live |
| `db_session` | database.py | nobody | | dead |
| `check_database_connection` | database.py | `check_db.py` script | `engine.connect` | script only |
| `VectorStore.__init__` | vector_store.py | module import, `seed_vector_db.py` | `HuggingFaceEmbeddings`, `Chroma` | live |
| `VectorStore.add_documents` | vector_store.py | `seed_vector_db.py`, tests | `Chroma.add_texts` | script only |
| `VectorStore.similarity_search` | vector_store.py | K1 underwriter (unreachable), tests | `similarity_search_with_score` | unreachable at runtime |
| `VectorStore.delete_collection` | vector_store.py | nobody | | dead |
| `LLMService.generate_text` | llm_service.py | tests only | `llm.agenerate` | dead at runtime |
| `LLMService.structured_generation` | llm_service.py | K3, K1 agents | `LLMChain.ainvoke` | live (K3) |
| `calculate_premium` | premium_calculator.py | `create_application`, `premium_calculation` | stub `generate_response` | live (always falls back) |
| `analyze_medical_risk` | medical_risk_analysis.py | `premium_calculation` | stub `search` | live (output unused) |
| `UnderwritingRuleEngine.evaluate_application` | ai_underwriting.py | K3, `apply_underwriting_rules` | 6 lambdas | live |
| `evaluate_application_with_llm` | ai_underwriting.py | `/api/evaluate-application` | rules, `structured_generation` | live (always falls back) |
| `process_complex_application_sync` | crewai_orchestration.py | 2 endpoints | `process_complex_application` | live |
| `process_complex_application` | crewai_orchestration.py | the sync wrapper | `Crew.run` | live (returns `{}`) |
| `Crew.run` | crewai_orchestration.py | above | `_execute_agent_task` (never) | live |
| `Agent.*` handlers and fallbacks | crewai_orchestration.py | `Crew._execute_agent_task` | LLM, vector store | unreachable |
| `RateLimiter.*` | rate_limiter.py | nobody | | dead |
| `RiskFactorsBase.calculate_risk_contribution` | schemas | nobody | | dead |
| `InsuranceApplicationResponse.from_orm` | schemas | nobody (FastAPI uses `model_validate`) | | dead |
| `PremiumCalculationResponse.to_application_response` | schemas | nobody | | dead |

## 8.4 Frontend component → service → storage graph

```mermaid
flowchart LR
    subgraph Components
        SC[InsuranceSearchComponent]
        CAC[CreateAccountComponent]
        ADC[ApplicationDetailComponent]
        QOD[QuoteOverviewDialogComponent]
        QC[QuoteComponent]
        ICC[InsuranceCalculatorComponent]
    end
    subgraph InsuranceService
        sa[searchAccounts]
        ca[createAccount]
        ga[getApplication]
        gab[getApplicationById]
        ua[updateApplication]
        cp[calculatePremium]
        gsa[getStoredAccounts]
        ssa[saveAccountsToStorage]
        gun[generateUniqueAccountNumber]
        h_list[getApplications]
        h_comp[getCompleteApplicationById]
        h_create[createApplication]
        h_save[saveApplication]
        h_cx[processComplexApplication]
        h_rules[applyUnderwritingRules]
        he[handleError]
    end
    subgraph QuoteService
        gq[getQuotesByApplicationId]
        cq[createQuote]
        gqi[getQuoteById]
        uqs[updateQuoteStatus]
        gsq[getStoredQuotes]
        ssq[saveQuotesToStorage]
        gqn[generateUniqueQuoteNumber]
    end
    LSA[(localStorage<br/>insurance_accounts)]
    LSQ[(localStorage<br/>insurance_quotes)]
    API[[FastAPI :8000]]

    SC -->|searchApplications| sa
    CAC -->|submitForm| ca
    ADC -->|loadApplication| gab
    ADC -->|loadApplication| gq
    ADC -->|saveChanges| ua
    ADC -->|openQuoteOverview| QOD
    QC -->|loadApplicantData| ga
    QC -->|submitForm| cq
    ICC -->|calculatePremium| cp

    sa & ga & ua & ca --> gsa --> LSA
    ca & ua --> ssa --> LSA
    ca --> gun
    gab --> ga
    gq & cq --> gsq --> LSQ
    cq --> ssq --> LSQ
    cq --> gqn
    gqi --> gsq
    uqs --> gsq & ssq

    h_list -.-> API
    h_comp -.-> API
    h_create -.-> API
    h_save -.-> API
    h_cx -.-> API
    h_rules -.-> API
    h_list & h_comp & h_create & h_save & h_cx & h_rules -.-> he

    classDef dead fill:#eee,stroke:#999,color:#666
    class h_list,h_comp,h_create,h_save,h_cx,h_rules,he,gqi,uqs dead
```

## 8.5 Frontend component method maps

### `InsuranceSearchComponent`

```mermaid
flowchart TD
    ctor["constructor → fb.group(9 controls)"]
    S["searchApplications()"] --> F["atLeastOneFieldFilled()"]
    S --> IS["insuranceService.searchAccounts(value)"]
    S --> SB["snackBar.open (empty / error)"]
    CA["createAccount()"] --> RN1["router.navigate('/create-account', state.accountData)"]
    RS["resetForm()"] --> FR["searchForm.reset() → nulls"]
    VD["viewDetails(id)"] --> RN2["router.navigate('/application', id)"]
```

### `CreateAccountComponent`

```mermaid
flowchart TD
    ctor["constructor"] --> FG["fb.group(9 controls + validators)"]
    ctor --> NAV["router.getCurrentNavigation().extras.state.accountData → patchValue"]
    init["ngOnInit"] --> AN["accountNumber = 'ACC' + Date.now()…"]
    SF["submitForm()"] --> V{invalid?} -->|yes| T["markAsTouched all + snackbar"]
    V -->|no| CA["insuranceService.createAccount(...)"] --> OK["snackbar → setTimeout 1 s → navigate /application/id"]
    CN["cancel()"] --> RS["navigate /search"]
```

### `ApplicationDetailComponent`

```mermaid
flowchart TD
    init["ngOnInit"] --> P["route.params → applicationId"] --> LA["loadApplication()"]
    LA --> FJ["forkJoin(getApplicationById, getQuotesByApplicationId)"]
    FJ --> LF["loadFormValues() → editForm.patchValue"]
    FJ -->|error| HE["handleError → snackbar"]
    TE["toggleEditMode()"] --> LF
    CE["cancelEdit()"] --> LF
    SV["saveChanges()"] --> V{invalid?} -->|yes| MT["markFormGroupTouched"]
    V -->|no| UA["insuranceService.updateApplication(merged)"] --> OK2["application = response; editMode = false; snackbar"]
    GB["goBack()"] --> N1["navigate /search"]
    NQ["createNewQuote()"] --> N2["navigate /quote?applicationId"]
    OQ["openQuoteOverview(quote)"] --> DLG["dialog.open(QuoteOverviewDialogComponent)"]
    D["ngOnDestroy"] --> DS["destroy$.next/complete"]
```

(`createNewQuote()` is defined, but the template uses a `routerLink` for
the same navigation.)

### `QuoteComponent`

```mermaid
flowchart TD
    init["ngOnInit"] --> QP["route.queryParams.applicationId"]
    QP -->|missing| R1["snackbar + navigate /search"]
    QP -->|present| LAD["loadApplicantData(id)"] --> GA["insuranceService.getApplication(id)"]
    GA --> PAI["populateApplicantInfo()"] --> GAN["generateApplicationNumber() QAP-…"]
    GA -->|error| R2["snackbar + navigate /search"]
    SEL["(selectionChange)"] --> UCF["updateConditionalFields()"]
    SF["submitForm()"] --> V{invalid?}
    V -->|no| CP["calculatePremium()"]
    V -->|no| DCA["determineCoverageAmount() = 100000"]
    CP & DCA --> CQ["quoteService.createQuote(...)"] --> NAV["navigate /application/id"]
    CN["cancel()"] --> NAV
```

### `QuoteOverviewDialogComponent`

```mermaid
flowchart TD
    ctor["constructor(dialogRef, data)"] --> AQ["analyzeQuote()"]
    AQ --> ARF["analyzeRiskFactors(details)"]
    ARF --> h1[checkHealthStatus] & h2[checkSmokingStatus] & h3[checkPreExistingConditions] & h4[checkFamilyMedicalHistory] & h5[checkHospitalizationHistory] & h6[checkTravelHistory]
    h6 --> hr[isHighRiskRegion]
    AQ --> AUC["analyzeUnderwritingConcerns(details)"]
    AUC --> u1[checkOccupationRisk] & u2[checkMentalHealth] & u3[checkStressLevels] & u4[checkSurgeryHistory] & u5[checkAlcoholConsumption] & u6[checkDrugUse]
    TPL["template"] --> W["calculateImpactWidth(impact)"]
    TPL --> IV["calculateImpactValue(impact, total)"] --> GIP["getImpactPercentage(impact)"]
    CL["close()"] --> DR["dialogRef.close()"]
```

### `InsuranceCalculatorComponent` and `AppComponent`

```mermaid
flowchart TD
    CP["calculatePremium()"] --> V{invalid?} -->|no| IS["insuranceService.calculatePremium(value)"] --> RES["premiumResult = result"]
    SA["saveApplication()"] --> NAV["navigate /create-account state.premiumData"]
    RF["resetForm()"] --> RST["form.reset(defaults); premiumResult = null"]
    AI["AppComponent.ngOnInit"] --> RE["router.events NavigationEnd"] --> SC["showCalculator = url has /calculator or ?"]
```
