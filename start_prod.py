#!/usr/bin/env python3
"""Production startup script for PDS Data API."""

import os
import sys
import logging
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Add the src directory to the Python path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

# Load environment variables
load_dotenv()

def setup_logging():
    """Configure production logging."""
    log_file = os.getenv('LOG_FILE', 'pds_data_api.log')
    log_level = os.getenv('LOG_LEVEL', 'WARNING')
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def check_environment():
    """Verify all required environment variables and paths."""
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Check database path
    db_url = os.getenv('DATABASE_URL')
    if db_url.startswith('sqlite:///'):
        db_path = db_url.replace('sqlite:///', '')
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Database file not found: {db_path}")

def main():
    """Main entry point for the application."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting PDS Data API")
        
        # Check environment
        check_environment()
        
        # Get configuration from environment
        host = os.getenv('PDS_HOST', '127.0.0.1')
        port = int(os.getenv('PDS_PORT', '8000'))
        workers = int(os.getenv('WORKERS', '4'))
        
        # Start the application
        uvicorn.run(
            "pds_data_api.main:app",
            host=host,
            port=port,
            workers=workers,
            log_level="warning",
            reload=False,
            access_log=False
        )
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 