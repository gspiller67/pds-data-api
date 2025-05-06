import json
import psycopg2
import cx_Oracle
import requests
from typing import Any, Dict, Union
import logging

logger = logging.getLogger(__name__)

class ConnectionHandler:
    @staticmethod
    def get_connection(config: Dict[str, Any]) -> Any:
        """Get a connection based on the configuration type"""
        connection_type = config.get('type', '').lower()
        
        if connection_type == 'postgresql':
            return PostgreSQLHandler.get_connection(config)
        elif connection_type == 'oracle':
            return OracleHandler.get_connection(config)
        elif connection_type == 'pds':
            return PDSHandler.get_connection(config)
        else:
            raise ValueError(f"Unsupported connection type: {connection_type}")

class PostgreSQLHandler:
    @staticmethod
    def get_connection(config: Dict[str, Any]) -> psycopg2.extensions.connection:
        """Get a PostgreSQL connection"""
        try:
            conn = psycopg2.connect(
                host=config.get('host'),
                port=config.get('port'),
                database=config.get('database'),
                user=config.get('username'),
                password=config.get('password')
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {str(e)}")
            raise

class OracleHandler:
    @staticmethod
    def get_connection(config: Dict[str, Any]) -> cx_Oracle.Connection:
        """Get an Oracle connection"""
        try:
            dsn = cx_Oracle.makedsn(
                host=config.get('host'),
                port=config.get('port'),
                service_name=config.get('service_name')
            )
            conn = cx_Oracle.connect(
                user=config.get('username'),
                password=config.get('password'),
                dsn=dsn
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to Oracle: {str(e)}")
            raise

class PDSHandler:
    @staticmethod
    def get_connection(config: Dict[str, Any]) -> Dict[str, Any]:
        """Get PDS API configuration"""
        required_fields = ['URL', 'username', 'password']
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Missing required PDS configuration fields: {', '.join(missing_fields)}")
            
        return {
            'url': config['URL'],
            'username': config['username'],
            'password': config['password']
        }

    @staticmethod
    def get_auth_header(username: str, password: str) -> str:
        """Generate Basic Authentication header for PDS"""
        import base64
        credentials = f"{username}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return f"Basic {encoded_credentials}"

    @staticmethod
    def make_request(url: str, auth_header: str, method: str = 'GET', params: Dict = None, data: Dict = None) -> Dict:
        """Make a request to the PDS API"""
        headers = {
            'Authorization': auth_header,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making PDS request: {str(e)}")
            raise 