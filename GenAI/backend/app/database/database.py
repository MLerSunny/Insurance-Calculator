import os
import logging
from sqlalchemy import create_engine, event, exc, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager

# Create declarative base for models
Base = declarative_base()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force SQLite database URL instead of using environment variable
DATABASE_URL = "sqlite:///./app_database.db"
logger.info(f"Using database: {DATABASE_URL}")

# Connection settings for SQLite
connect_args = {"check_same_thread": False}

# Create engine with appropriate parameters for SQLite
# SQLite doesn't support connection pooling, so we don't pass those parameters
engine = create_engine(
    DATABASE_URL, 
    connect_args=connect_args
)

# Add engine event listeners for debugging and connection management
@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    logger.debug("Database connection established")

@event.listens_for(engine, "checkout")
def checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Database connection checked out from pool")

@event.listens_for(engine, "checkin")
def checkin(dbapi_connection, connection_record):
    logger.debug("Database connection returned to pool")

# Create a scoped session to ensure thread safety
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# Session dependency for FastAPI
def get_db():
    """
    FastAPI dependency that provides a database session
    
    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_session():
    """
    Context manager for database sessions
    
    Usage:
        with db_session() as db:
            # Use db session here
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()

def check_database_connection():
    """
    Check if database is accessible
    
    Returns:
        tuple: (is_connected, error_message)
    """
    try:
        # Create a connection and execute a simple query
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "Connected to database"
    except exc.SQLAlchemyError as e:
        logger.error(f"Database connection error: {str(e)}")
        return False, str(e) 