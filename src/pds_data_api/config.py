"""Production configuration for PDS Data API."""
import os
from pathlib import Path

# Base directory of the application
BASE_DIR = Path(__file__).parent.parent.parent.absolute()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/pds_data.db')

# Server configuration
HOST = os.getenv('PDS_HOST', '127.0.0.1')  # Default to localhost for security
PORT = int(os.getenv('PDS_PORT', '8000'))

# Security configuration
SECRET_KEY = os.getenv('SECRET_KEY', None)
if not SECRET_KEY:
    import secrets
    SECRET_KEY = secrets.token_hex(32)

# Logging configuration
LOG_FILE = os.getenv('LOG_FILE', 'pds_data_api.log')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'WARNING')

# API configuration
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))  # 30 seconds default timeout
MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '1000'))

# File paths
TEMPLATE_DIR = os.path.join(BASE_DIR, 'src', 'pds_data_api', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'src', 'pds_data_api', 'static')

# Production settings
DEBUG = False
TESTING = False 