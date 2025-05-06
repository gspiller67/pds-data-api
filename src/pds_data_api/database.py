from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://pdsapi:pdsapi@db:5432/pds_data_api')

def create_db_engine(max_retries=3, retry_interval=2):
    """Create database engine with retry mechanism"""
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_pre_ping=True,  # Enable connection health checks
                pool_size=5,  # Set a reasonable pool size
                max_overflow=10  # Allow some overflow connections
            )
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                raise

# Create SQLAlchemy engine with retry mechanism
engine = create_db_engine()

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get database session
def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_db_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False

def init_db_connection():
    """Initialize database connection with retries."""
    max_retries = 3
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                return False 