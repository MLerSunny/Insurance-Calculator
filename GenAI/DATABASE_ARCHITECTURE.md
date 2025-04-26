# Insurance Application Database Architecture

## Table of Contents
1. [Overview](#overview)
2. [Database Schema](#database-schema)
3. [Table Relationships](#table-relationships)
4. [Data Access Patterns](#data-access-patterns)
5. [Optimization Strategies](#optimization-strategies)

## Overview

The insurance application uses a hybrid database approach:
- PostgreSQL for structured data (applications, quotes, users)
- ChromaDB for vector storage (similar cases, medical conditions)
- Redis for caching and session management

## Database Schema

### Core Tables

#### Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    role VARCHAR(50) DEFAULT 'user'
);

CREATE INDEX idx_users_email ON users(email);
```

#### Insurance Applications
```sql
CREATE TABLE insurance_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    coverage_type VARCHAR(100) NOT NULL,
    coverage_amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP WITH TIME ZONE,
    
    -- Personal Information
    applicant_name VARCHAR(255) NOT NULL,
    applicant_email VARCHAR(255) NOT NULL,
    applicant_phone VARCHAR(50),
    applicant_dob DATE NOT NULL,
    
    -- Address Information
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    postal_code VARCHAR(20) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'USA',
    
    CONSTRAINT fk_user
        FOREIGN KEY(user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

CREATE INDEX idx_applications_user ON insurance_applications(user_id);
CREATE INDEX idx_applications_status ON insurance_applications(status);
CREATE INDEX idx_applications_created ON insurance_applications(created_at);
```

#### Medical History
```sql
CREATE TABLE medical_conditions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL,
    condition_name VARCHAR(255) NOT NULL,
    diagnosis_date DATE,
    treatment_status VARCHAR(50),
    severity VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_application
        FOREIGN KEY(application_id)
        REFERENCES insurance_applications(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_conditions_application ON medical_conditions(application_id);
```

#### Risk Assessments
```sql
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL UNIQUE,
    risk_score DECIMAL(5,2) NOT NULL,
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    assessor_type VARCHAR(50) NOT NULL, -- 'AI' or 'HUMAN'
    confidence_score DECIMAL(5,2),
    
    -- Risk Factors
    medical_risk_factor DECIMAL(5,2),
    lifestyle_risk_factor DECIMAL(5,2),
    occupation_risk_factor DECIMAL(5,2),
    age_risk_factor DECIMAL(5,2),
    
    -- AI Processing Results
    ai_insights JSONB,
    similar_cases JSONB,
    
    CONSTRAINT fk_application
        FOREIGN KEY(application_id)
        REFERENCES insurance_applications(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_assessments_application ON risk_assessments(application_id);
CREATE INDEX idx_assessments_score ON risk_assessments(risk_score);
```

#### Insurance Quotes
```sql
CREATE TABLE insurance_quotes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    premium_amount DECIMAL(12,2) NOT NULL,
    coverage_amount DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP WITH TIME ZONE,
    
    -- Premium Calculation Factors
    base_premium DECIMAL(12,2) NOT NULL,
    risk_multiplier DECIMAL(5,2) NOT NULL,
    age_factor DECIMAL(5,2) NOT NULL,
    medical_factor DECIMAL(5,2) NOT NULL,
    lifestyle_factor DECIMAL(5,2) NOT NULL,
    
    -- Additional Coverage Options
    riders JSONB,
    discounts JSONB,
    
    CONSTRAINT fk_application
        FOREIGN KEY(application_id)
        REFERENCES insurance_applications(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_quotes_application ON insurance_quotes(application_id);
CREATE INDEX idx_quotes_status ON insurance_quotes(status);
```

### AI-Related Tables

#### Vector Embeddings
```sql
CREATE TABLE vector_embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reference_id UUID NOT NULL, -- ID of the referenced entity (application, condition, etc.)
    reference_type VARCHAR(50) NOT NULL, -- Type of the referenced entity
    embedding VECTOR(1536), -- For storing OpenAI embeddings
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_embeddings_reference ON vector_embeddings(reference_id);
CREATE INDEX idx_embeddings_type ON vector_embeddings(reference_type);
```

#### AI Processing History
```sql
CREATE TABLE ai_processing_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL,
    processing_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    result JSONB,
    error_message TEXT,
    
    CONSTRAINT fk_application
        FOREIGN KEY(application_id)
        REFERENCES insurance_applications(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_ai_history_application ON ai_processing_history(application_id);
CREATE INDEX idx_ai_history_type ON ai_processing_history(processing_type);
```

## Table Relationships

### Primary Relationships

1. **User -> Applications (1:N)**
   - One user can have multiple insurance applications
   - Each application belongs to one user

2. **Application -> Medical Conditions (1:N)**
   - One application can have multiple medical conditions
   - Each medical condition belongs to one application

3. **Application -> Risk Assessment (1:1)**
   - Each application has exactly one risk assessment
   - Each risk assessment belongs to one application

4. **Application -> Quotes (1:N)**
   - One application can have multiple quotes
   - Each quote belongs to one application

### Secondary Relationships

1. **Application -> Vector Embeddings (1:N)**
   - Applications and their components are embedded for similarity search
   - Multiple embeddings can reference the same application

2. **Application -> AI Processing History (1:N)**
   - Each application can have multiple AI processing records
   - Tracks all AI interactions with the application

## Data Access Patterns

### Application Creation Flow
```python
async def create_application(db: Session, application_data: ApplicationCreate) -> Application:
    """Creates a new insurance application with related records"""
    async with db.begin():
        # Create application
        application = InsuranceApplication(**application_data.dict())
        db.add(application)
        await db.flush()
        
        # Create medical conditions
        medical_conditions = [
            MedicalCondition(application_id=application.id, **condition.dict())
            for condition in application_data.medical_conditions
        ]
        db.add_all(medical_conditions)
        
        # Generate and store embeddings
        embeddings = await generate_embeddings(application)
        db.add(VectorEmbedding(
            reference_id=application.id,
            reference_type='application',
            embedding=embeddings
        ))
        
        # Create initial risk assessment
        risk_assessment = await create_risk_assessment(application)
        db.add(risk_assessment)
        
        await db.commit()
        return application
```

### Quote Generation Flow
```python
async def generate_quote(db: Session, application_id: UUID) -> Quote:
    """Generates a new quote for an application"""
    async with db.begin():
        # Get application with risk assessment
        application = await db.query(InsuranceApplication)\
            .options(
                joinedload(InsuranceApplication.risk_assessment),
                joinedload(InsuranceApplication.medical_conditions)
            )\
            .filter(InsuranceApplication.id == application_id)\
            .first()
        
        if not application:
            raise ApplicationNotFoundError()
        
        # Calculate premium
        premium_calculator = PremiumCalculator()
        premium_details = await premium_calculator.calculate_premium(
            application,
            application.risk_assessment
        )
        
        # Create quote
        quote = Quote(
            application_id=application_id,
            premium_amount=premium_details.final_amount,
            coverage_amount=application.coverage_amount,
            base_premium=premium_details.base_premium,
            risk_multiplier=premium_details.risk_multiplier,
            age_factor=premium_details.age_factor,
            medical_factor=premium_details.medical_factor,
            lifestyle_factor=premium_details.lifestyle_factor
        )
        
        db.add(quote)
        await db.commit()
        return quote
```

### Similarity Search Flow
```python
async def find_similar_cases(
    db: Session,
    vector_store: VectorStore,
    application_id: UUID
) -> List[SimilarCase]:
    """Finds similar cases using vector similarity"""
    # Get application embedding
    embedding = await db.query(VectorEmbedding)\
        .filter(
            VectorEmbedding.reference_id == application_id,
            VectorEmbedding.reference_type == 'application'
        )\
        .first()
    
    if not embedding:
        raise EmbeddingNotFoundError()
    
    # Perform similarity search
    similar_embeddings = await vector_store.similarity_search(
        embedding.embedding,
        n_results=5
    )
    
    # Get similar applications
    similar_cases = await db.query(InsuranceApplication)\
        .options(
            joinedload(InsuranceApplication.risk_assessment),
            joinedload(InsuranceApplication.quotes)
        )\
        .filter(
            InsuranceApplication.id.in_([
                e.reference_id for e in similar_embeddings
            ])
        )\
        .all()
    
    return similar_cases
```

## Optimization Strategies

### Indexing Strategy

1. **B-tree Indexes**
   - Primary keys (UUID)
   - Foreign keys
   - Status fields
   - Email addresses
   - Created/updated timestamps

2. **Vector Indexes**
   - Embeddings for similarity search
   - Using HNSW index type for fast approximate nearest neighbor search

### Caching Strategy

1. **Application Cache**
```python
class ApplicationCache:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = timedelta(minutes=30)
    
    async def get_application(self, application_id: UUID) -> Optional[Application]:
        """Gets application from cache or database"""
        cache_key = f"application:{application_id}"
        
        # Try cache first
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return Application.parse_raw(cached_data)
        
        # Get from database
        application = await get_application_from_db(application_id)
        if application:
            # Cache for future use
            await self.redis.set(
                cache_key,
                application.json(),
                ex=self.ttl
            )
        
        return application
```

2. **Risk Assessment Cache**
```python
class RiskAssessmentCache:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.ttl = timedelta(hours=1)
    
    async def get_risk_assessment(
        self,
        application_id: UUID
    ) -> Optional[RiskAssessment]:
        """Gets risk assessment from cache or database"""
        cache_key = f"risk_assessment:{application_id}"
        
        # Try cache first
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return RiskAssessment.parse_raw(cached_data)
        
        # Get from database
        assessment = await get_risk_assessment_from_db(application_id)
        if assessment:
            # Cache for future use
            await self.redis.set(
                cache_key,
                assessment.json(),
                ex=self.ttl
            )
        
        return assessment
```

### Query Optimization

1. **Eager Loading**
```python
async def get_application_details(application_id: UUID) -> ApplicationDetails:
    """Gets application details with all related data"""
    application = await db.query(InsuranceApplication)\
        .options(
            joinedload(InsuranceApplication.user),
            joinedload(InsuranceApplication.medical_conditions),
            joinedload(InsuranceApplication.risk_assessment),
            joinedload(InsuranceApplication.quotes.filter(
                Quote.status.in_(['active', 'accepted'])
            ))
        )\
        .filter(InsuranceApplication.id == application_id)\
        .first()
    
    return ApplicationDetails.from_orm(application)
```

2. **Pagination**
```python
async def get_applications_page(
    page: int,
    page_size: int,
    filters: Dict[str, Any]
) -> ApplicationPage:
    """Gets paginated applications with filters"""
    query = db.query(InsuranceApplication)\
        .options(
            joinedload(InsuranceApplication.risk_assessment),
            joinedload(InsuranceApplication.quotes)
        )
    
    # Apply filters
    for field, value in filters.items():
        query = query.filter(getattr(InsuranceApplication, field) == value)
    
    # Get total count
    total = await query.count()
    
    # Get page
    applications = await query\
        .order_by(InsuranceApplication.created_at.desc())\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    return ApplicationPage(
        items=applications,
        total=total,
        page=page,
        page_size=page_size
    )
```

This database architecture provides a robust foundation for the insurance application, supporting both traditional relational data and AI-specific requirements. The schema is designed for scalability, performance, and maintainability. 