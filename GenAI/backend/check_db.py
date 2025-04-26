import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import sys

# Add the project root directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.app.database.database import Base

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def main():
    # Check environment variables
    logger.info("Environment Variables:")
    database_url = os.getenv("DATABASE_URL")
    logger.info(f"DATABASE_URL: {database_url}")
    
    # Use SQLite as fallback
    if not database_url:
        database_url = "sqlite:///./insurance.db"
        logger.info(f"No DATABASE_URL found, using fallback: {database_url}")
    
    # Configure SQLite connect_args
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    
    # Try to create engine and connect
    try:
        logger.info(f"Creating database engine for {database_url}")
        engine = create_engine(database_url, connect_args=connect_args)
        
        # Test connection
        logger.info("Testing database connection...")
        conn = engine.connect()
        logger.info("Connection successful!")
        
        # Check if tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        logger.info(f"Existing tables: {tables}")
        
        conn.close()
        
        # Setup session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database setup complete!")
        
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        
        # If PostgreSQL failed, try SQLite
        if not database_url.startswith("sqlite"):
            logger.info("Trying SQLite as fallback...")
            sqlite_url = "sqlite:///./insurance.db"
            try:
                engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
                conn = engine.connect()
                logger.info("SQLite connection successful!")
                conn.close()
                
                # Update the DATABASE_URL in .env file
                with open(".env", "a") as f:
                    f.write(f"\nDATABASE_URL={sqlite_url}\n")
                logger.info(f"Added DATABASE_URL={sqlite_url} to .env file")
                
            except Exception as sqlite_e:
                logger.error(f"SQLite connection error: {sqlite_e}")

if __name__ == "__main__":
    main() 