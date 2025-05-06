from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from .database import engine, Base, SessionLocal
from .models import ConnectionOptions, Connection, Config
import logging
from datetime import datetime
import psycopg2
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database and create necessary tables."""
    try:
        # Create database if it doesn't exist
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "db"),
            port=os.getenv("DB_PORT", "5432"),
            user=os.getenv("DB_USER", "pdsapi"),
            password=os.getenv("DB_PASSWORD", "pdsapi"),
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'pds_data_api'")
        if not cursor.fetchone():
            cursor.execute('CREATE DATABASE pds_data_api')
            logger.info("Created new database: pds_data_api")
        
        cursor.close()
        conn.close()
        
        # Connect to the application database
        engine = create_engine(
            f"postgresql://{os.getenv('DB_USER', 'pdsapi')}:{os.getenv('DB_PASSWORD', 'pdsapi')}@{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT', '5432')}/pds_data_api"
        )
        
        # Create tables
        Base.metadata.create_all(engine)
        
        # Initialize connection types if needed
        with Session(engine) as session:
            existing_types = {ct.name for ct in session.query(ConnectionOptions).all()}
            if not existing_types:
                # Add default connection types
                default_types = ['PDS', 'PostgreSQL', 'Oracle', 'Qdrant']
                for type_name in default_types:
                    session.add(ConnectionOptions(name=type_name))
                session.commit()
                logger.info("Initialized default connection types")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise 