from sqlalchemy import text
from database import engine
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_db():
    """Migrate the database schema while preserving data"""
    try:
        with engine.connect() as connection:
            # Start a transaction
            with connection.begin():
                # Add data_type column if it doesn't exist
                connection.execute(text("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_name = 'TABLECOLLUMNS' 
                            AND column_name = 'data_type'
                        ) THEN
                            ALTER TABLE "TABLECOLLUMNS" 
                            ADD COLUMN data_type VARCHAR(50) NOT NULL DEFAULT 'string';
                        END IF;
                    END $$;
                """))
                
                logger.info("Database migration completed successfully!")
                
    except Exception as e:
        logger.error(f"Error during migration: {str(e)}")
        raise

if __name__ == "__main__":
    migrate_db() 