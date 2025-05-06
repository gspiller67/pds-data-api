from sqlalchemy import inspect, text, update
from database import engine, Base, SessionLocal
import models
import logging
from models import ConnectionOptions, Connection, Config
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def add_connection_types(db):
    """Add any missing connection types"""
    # Define connection types that should exist
    connection_types = ['PDS', 'PostgreSQL', 'Oracle', 'Qdrant']
    
    # Get existing connection types
    existing_types = {type.name for type in db.query(ConnectionOptions).all()}
    logger.info(f"Found existing connection types: {existing_types}")
    
    # Add any missing types
    for type_name in connection_types:
        if type_name not in existing_types:
            conn_type = ConnectionOptions(name=type_name)
            db.add(conn_type)
            logger.info(f"Added missing connection type: {type_name}")
    
    try:
        db.commit()
    except Exception as e:
        logger.error(f"Error adding connection types: {str(e)}")
        db.rollback()

def init_db():
    """Initialize the database by ensuring tables and connection types exist"""
    try:
        # Create tables if they don't exist (won't modify existing tables)
        logger.info("Creating any missing tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables check complete")
            
        # Test the connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful!")
            
        # Create a new session
        db = SessionLocal()
        
        try:
            # Add any missing connection types
            add_connection_types(db)
            
            # Verify current connection types
            current_types = db.query(ConnectionOptions).all()
            logger.info("Current connection types:")
            for conn_type in current_types:
                logger.info(f"- {conn_type.name}")
            
        except Exception as e:
            logger.error(f"Error in database operations: {str(e)}")
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_db() 