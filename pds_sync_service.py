from uuid import UUID
import json
from sqlalchemy.orm import Session
from datetime import datetime
from models import Config, TableColumn, Connection
import logging
import requests
from typing import Any, Dict
import base64

logger = logging.getLogger(__name__)

class PDSSyncService:
    def __init__(self, db: Session, table_id: UUID):
        self.db = db
        self.table_id = table_id
        self.table = db.query(Config).filter(Config.id == table_id).first()
        if not self.table:
            raise ValueError(f"Table configuration not found for ID: {table_id}")
        
        # Get source connection (PDS)
        self.source_connection = db.query(Connection).filter(
            Connection.id == self.table.source_connection_id
        ).first()
        if not self.source_connection:
            raise ValueError("Source connection not found")
        
        # Parse connection config
        self.pds_config = json.loads(self.source_connection.connection_config)
        if not self.pds_config.get('url'):
            raise ValueError("PDS URL not configured")
        
        # Use the base URL as is, since it already includes the client-specific path
        self.pds_url = f"{self.pds_config['url']}rest-service/dataservice/runquery?configCode=ds_unifier"
        
        # Get active columns
        self.columns = db.query(TableColumn).filter(
            TableColumn.pds_table_id == table_id,
            TableColumn.active == True
        ).all()
        if not self.columns:
            raise ValueError(f"No active columns found for table: {self.table.table_name}")

    def get_auth_header(self) -> Dict[str, str]:
        """Generate Basic Auth header for PDS API"""
        auth_string = f"{self.pds_config['username']}:{self.pds_config['password']}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}

    def build_payload(self) -> Dict[str, Any]:
        """Build the payload for the PDS API request"""
        return {
            "name": self.table.table_name,
            "pageSize": str(self.table.page_size),
            "tables": [
                {
                    "tableName": self.table.table_name,
                    "columns": [col.column_name for col in self.columns]
                }
            ]
        }

    def run_sync(self):
        """Run the complete sync process"""
        try:
            # Build the payload
            payload = self.build_payload()
            
            # Log the request details (without sensitive info)
            logger.info(f"Making request to PDS API at: {self.pds_url}")
            logger.info(f"With payload: {json.dumps(payload, indent=2)}")
            
            # Get auth header
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {base64.b64encode(f'{self.pds_config["username"]}:{self.pds_config["password"]}'.encode()).decode()}"
            }
            
            try:
                # Make the request to PDS API
                response = requests.post(
                    self.pds_url,
                    json=payload,
                    headers=headers,
                    timeout=30  # Add timeout
                )
                
                # Check response
                if response.status_code != 200:
                    error_msg = f"PDS API returned error {response.status_code}"
                    try:
                        error_detail = response.json()
                        error_msg += f": {json.dumps(error_detail, indent=2)}"
                    except:
                        error_msg += f": {response.text}"
                    raise ValueError(error_msg)
                
                # Process the response
                data = response.json()
                logger.info(f"Successfully synced table: {self.table.table_name}")
                return data
                
            except requests.exceptions.ConnectionError as e:
                raise ValueError(f"Failed to connect to PDS API. Please check if the URL is correct and accessible: {self.pds_url}. Error: {str(e)}")
            except requests.exceptions.Timeout:
                raise ValueError("Request to PDS API timed out. Please try again or check the server status.")
            except requests.exceptions.RequestException as e:
                raise ValueError(f"Error making request to PDS API: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in sync process: {str(e)}")
            raise

    def check_destination_table(self, pds_table: Config) -> bool:
        """Check if the destination table exists and has the correct structure"""
        try:
            cursor = self.destination_conn.cursor()

            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    AND table_name = %s
                );
            """, (pds_table.table_name.lower(),))
            
            table_exists = cursor.fetchone()[0]

            if not table_exists:
                # Create table if it doesn't exist
                columns = self.db.query(TableColumn).filter(
                    TableColumn.pds_table_id == pds_table.id,
                    TableColumn.active == True
                ).all()

                if not columns:
                    raise ValueError(f"No active columns defined for table {pds_table.table_name}")

                # Generate CREATE TABLE statement
                column_definitions = []
                for col in columns:
                    # Map PDS data types to PostgreSQL data types
                    pg_type = self._map_data_type(col.data_type)
                    column_definitions.append(f'"{col.column_name}" {pg_type}')

                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS "{pds_table.table_name}" (
                        id SERIAL PRIMARY KEY,
                        {', '.join(column_definitions)}
                    );
                """
                
                cursor.execute(create_table_sql)
                logger.info(f"Created destination table {pds_table.table_name}")

            cursor.close()
            return True

        except Exception as e:
            logger.error(f"Error checking destination table: {str(e)}")
            raise

    def _map_data_type(self, pds_type: str) -> str:
        """Map PDS data types to destination database types"""
        type_mapping = {
            'string': 'TEXT',
            'integer': 'INTEGER',
            'float': 'DOUBLE PRECISION',
            'boolean': 'BOOLEAN',
            'date': 'DATE',
            'datetime': 'TIMESTAMP',
            'json': 'JSONB'
        }
        return type_mapping.get(pds_type.lower(), 'TEXT')

    def get_table_columns(self, pds_table_id: UUID) -> list:
        """Get all columns defined for a specific PDS table"""
        return self.db.query(TableColumn).filter(
            TableColumn.pds_table_id == pds_table_id,
            TableColumn.active == True
        ).all()

    def fetch_pds_data(self, offset: int = 0) -> dict:
        """Fetch data from PDS API"""
        auth_header = self.get_auth_header()
        
        params = {
            'limit': self.table.page_size,
            'offset': offset
        }
        
        return requests.get(
            self.pds_url,
            headers=auth_header,
            params=params
        ).json()

    def process_items(self, items: list, pds_table: Config):
        """Process a batch of items"""
        try:
            cursor = self.destination_conn.cursor()

            for item_data in items:
                try:
                    # Get column names from TableColumn
                    columns = self.get_table_columns(pds_table.id)
                    column_names = [col.column_name for col in columns]
                    
                    # Filter item data to only include defined columns
                    filtered_data = {k: v for k, v in item_data.items() if k in column_names}
                    
                    # Generate upsert SQL
                    columns_str = ', '.join(f'"{col}"' for col in filtered_data.keys())
                    values_str = ', '.join(['%s'] * len(filtered_data))
                    update_str = ', '.join(f'"{col}" = EXCLUDED."{col}"' for col in filtered_data.keys())
                    
                    upsert_sql = f"""
                        INSERT INTO "{pds_table.table_name}" ({columns_str})
                        VALUES ({values_str})
                        ON CONFLICT (id) DO UPDATE
                        SET {update_str};
                    """
                    
                    cursor.execute(upsert_sql, list(filtered_data.values()))

                except Exception as e:
                    logger.error(f"Error processing item {item_data.get('record_id')}: {str(e)}")
                    continue

            self.destination_conn.commit()
            cursor.close()

        except Exception as e:
            logger.error(f"Error in process_items: {str(e)}")
            raise 