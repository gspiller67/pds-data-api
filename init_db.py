from sqlalchemy import inspect, text
from database import engine, Base
import models
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def drop_all_tables():
    """Drop all existing tables"""
    Base.metadata.drop_all(bind=engine)
    logger.info("All existing tables dropped successfully!")

def init_db():
    """Initialize the database by creating tables"""
    try:
        # Drop all existing tables first
        drop_all_tables()
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
            
        # Test the connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful!")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 