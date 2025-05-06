from uuid import UUID
import json
from sqlalchemy.orm import Session
from datetime import datetime
from .models import Config, TableColumn, Connection, SyncHistory
import logging
import requests
from typing import Any, Dict, Optional, List
import base64
from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extras import execute_values
import uuid
import time
from .config_loader import load_secrets
import os
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastapi import HTTPException
import inspect
import httpx

logger = logging.getLogger(__name__)

def log_args(cls):
    sig = inspect.signature(cls.__init__)
    logger.info(f"[DEBUG] QdrantClient.__init__ accepted args:\n{sig}")

class PDSSyncService:
    def __init__(self, db: Session, table_id: UUID):
        """Initialize the sync service with database session and table ID."""
        self.db = db
        self.table_id = table_id
        self._initialize_table()
        self._initialize_connections()
        self._initialize_clients()

    def _initialize_table(self):
        """Initialize table configuration."""
        self.table = self.db.query(Config).filter(Config.id == self.table_id).first()
        if not self.table:
            raise ValueError(f"Table configuration not found for ID: {self.table_id}")
        
        # Get active columns
        self.columns = self.db.query(TableColumn).filter(
            TableColumn.pds_table_id == self.table_id,
            TableColumn.active == True
        ).all()
        if not self.columns:
            raise ValueError(f"No active columns found for table: {self.table.table_name}")

    def _initialize_connections(self):
        """Initialize source and destination connections."""
        # Initialize source connection (PDS)
        self.source_connection = self.db.query(Connection).filter(
            Connection.id == self.table.source_connection_id
        ).first()
        if not self.source_connection:
            raise ValueError("Source connection not found")
        
        # Initialize destination connection
        self.dest_connection = self.db.query(Connection).filter(
            Connection.id == self.table.destination_connection_id
        ).first()
        if not self.dest_connection:
            raise ValueError("Destination connection not found")

        # Parse connection configs
        self.source_config = self._parse_connection_config(self.source_connection.connection_config)
        self.dest_config = self._parse_connection_config(self.dest_connection.connection_config)

        # Construct PDS API URL
        base_url = self.source_config['url'].rstrip('/')
        if base_url.endswith('/pds'):
            base_url = base_url[:-4]
        self.pds_url = f"{base_url}/pds/rest-service/dataservice/runquery?configCode=ds_unifier"

    def _parse_connection_config(self, connection_config: bytes) -> Dict[str, Any]:
        """Parse connection configuration from bytes."""
        try:
            logger.info("Starting to parse connection configuration...")
            config = json.loads(connection_config.decode('utf-8'))
            logger.info(f"Raw connection config: {json.dumps(config, default=str)}")
            
            # Define allowed parameters for each connection type
            allowed_params = {
                'PDS': ['url', 'username', 'password'],
                'PostgreSQL': ['host', 'port', 'database', 'username', 'password'],
                'Oracle': ['host', 'port', 'service_name', 'username', 'password'],
                'Qdrant': ['host', 'port', 'api_key', 'batch_size']
            }
            
            # Get connection type
            connection = self.db.query(Connection).filter(
                Connection.connection_config == connection_config
            ).first()
            connection_type = connection.connection_type.name
            logger.info(f"Connection type: {connection_type}")
            
            # Filter out any parameters not in the allowed list
            filtered_config = {
                k: v for k, v in config.items() 
                if k in allowed_params.get(connection_type, [])
            }
            logger.info(f"Filtered config for {connection_type}: {json.dumps(filtered_config, default=str)}")
            
            return filtered_config
        except Exception as e:
            logger.error(f"Error parsing connection config: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _initialize_clients(self):
        """Initialize destination clients based on connection type."""
        self.qdrant_client = None
        self.dest_engine = None

        if self.dest_connection.connection_type.name.lower() == "qdrant":
            self._initialize_qdrant_client()
        elif self.dest_connection.connection_type.name.lower() in ["postgresql", "oracle"]:
            self._initialize_sql_client()

    def _initialize_qdrant_client(self):
        """Initialize Qdrant client."""
        try:
            logger.info("Starting Qdrant client initialization...")
            
            # Log the full dest_config
            logger.info(f"Full dest_config: {json.dumps(self.dest_config, default=str)}")
            
            # Get only the essential parameters
            host = self.dest_config.get('host', 'localhost')
            # Strip any http:// or https:// prefix if present
            host = host.replace('http://', '').replace('https://', '')
            logger.info(f"Extracted host (after stripping protocol): {host}")
            
            port = self.dest_config.get('port', 6333)
            logger.info(f"Extracted port: {port}")
            
            api_key = self.dest_config.get('api_key')
            logger.info(f"Extracted api_key: {'*' * len(api_key) if api_key else None}")
            
            # Construct URL with http:// scheme
            url = f"http://{host}:{port}"
            logger.info(f"Constructed URL: {url}")
            
            # Log the exact parameters being passed to QdrantClient
            client_params = {
                'url': url,
                'api_key': api_key,
                'timeout': 300  # Increased timeout to 5 minutes
            }
            logger.info(f"Parameters being passed to QdrantClient: {json.dumps(client_params, default=str)}")
            
            # Initialize with URL and API key only
            logger.info("Attempting to initialize QdrantClient...")
            self.qdrant_client = QdrantClient(
                url=url,
                api_key=api_key,
                timeout=300  # Increased timeout to 5 minutes
            )
            logger.info("QdrantClient initialized successfully")
            
            # Log the type and attributes of the initialized client
            logger.info(f"QdrantClient type: {type(self.qdrant_client)}")
            logger.info(f"QdrantClient attributes: {dir(self.qdrant_client)}")
            
            # Test the client with a simple operation
            logger.info("Testing QdrantClient with get_collections...")
            collections = self.qdrant_client.get_collections()
            logger.info(f"Successfully retrieved collections: {collections}")
            
        except Exception as e:
            logger.error(f"Error initializing Qdrant client: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _initialize_sql_client(self):
        """Initialize SQL database client."""
        self._ensure_database_exists()
        self.dest_engine = create_engine(
            f"postgresql://{self.dest_config['username']}:{self.dest_config['password']}@{self.dest_config['host']}:{self.dest_config['port']}/{self.dest_config['database']}"
        )

    def _ensure_database_exists(self):
        """Create the database if it doesn't exist."""
        try:
            conn = psycopg2.connect(
                host=self.dest_config['host'],
                port=self.dest_config['port'],
                user=self.dest_config['username'],
                password=self.dest_config['password'],
                database='postgres'
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.dest_config['database']}'")
            if not cursor.fetchone():
                cursor.execute(f'CREATE DATABASE "{self.dest_config["database"]}"')
                logger.info(f"Created database: {self.dest_config['database']}")
            
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error ensuring database exists: {str(e)}")
            raise

    def get_auth_header(self) -> Dict[str, str]:
        """Generate Basic Auth header for PDS API."""
        username = self.source_config.get("username", "")
        password = self.source_config.get("password", "")
        auth_string = f"{username}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}

    def build_payload(self) -> Dict[str, Any]:
        """Build the payload for the PDS API request."""
        table_name = self._ensure_unifier_prefix(self.table.table_name)
        return {
            "name": table_name,
            "pageSize": str(self.table.page_size),
            "tables": [
                {
                    "tableName": table_name,
                    "columns": [col.column_name for col in self.columns]
                }
            ]
        }

    def _ensure_unifier_prefix(self, table_name: str) -> str:
        """Ensure the table name has the UNIFIER_ prefix."""
        if not table_name.startswith("UNIFIER_"):
            return f"UNIFIER_{table_name}"
        return table_name

    def run_sync(self):
        """Run the sync process based on destination type."""
        try:
            dest_type = self.dest_connection.connection_type.name.lower()
            
            if dest_type == "qdrant":
                return self.sync_to_qdrant(self.table.table_name)
            elif dest_type in ["postgresql", "oracle"]:
                return self.run_sql_sync()
            else:
                raise ValueError(f"Unsupported destination type: {dest_type}")
        except Exception as e:
            logger.error(f"Error in sync process: {str(e)}")
            raise

    def sync_to_qdrant(self, table_name: str, collection_name: str = None) -> Dict[str, Any]:
        """Sync data to Qdrant with embeddings."""
        try:
            logger.info(f"Starting sync_to_qdrant for table: {table_name}")
            logger.info(f"Current qdrant_client state: {self.qdrant_client}")
            logger.info(f"Qdrant client type: {type(self.qdrant_client)}")
            logger.info(f"Qdrant client attributes: {dir(self.qdrant_client)}")
            
            # Create sync history record
            sync_history = self._create_sync_history()
            
            # Load OpenAI API key
            secrets = load_secrets(os.getenv("SECRETS_PATH", "secrets.json"))
            openai_api_key = secrets.get("openai_api_key")
            if not openai_api_key:
                raise ValueError("OpenAI API key not found in secrets.json")
            
            # Initialize OpenAI client
            openai_client = OpenAI(
                api_key=openai_api_key,
                http_client=httpx.Client(transport=httpx.HTTPTransport(retries=3))
            )
            
            # Set collection name
            collection_name = collection_name or table_name.lower()
            logger.info(f"Using collection name: {collection_name}")
            
            # Ensure collection exists
            self._ensure_qdrant_collection(collection_name)
            
            # Get and process data
            total_items = self._process_qdrant_data(
                table_name=table_name,
                collection_name=collection_name,
                openai_client=openai_client,
                sync_history=sync_history
            )
            
            # Update sync history
            self._update_sync_history(sync_history, total_items)
            
            return {
                "status": "success",
                "message": f"Successfully synced {total_items} items to Qdrant collection '{collection_name}'"
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in sync_to_qdrant: {error_msg}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            if 'sync_history' in locals():
                self._update_sync_history(sync_history, 0, error_msg)
            return {"status": "error", "message": f"Error in sync_to_qdrant: {error_msg}"}

    def _create_sync_history(self) -> SyncHistory:
        """Create a new sync history record."""
        sync_history = SyncHistory(
            pds_table_id=self.table_id,
            start_time=datetime.now(),
            total_columns=len(self.columns),
            status='IN_PROGRESS'
        )
        self.db.add(sync_history)
        self.db.commit()
        return sync_history

    def _update_sync_history(self, sync_history: SyncHistory, total_items: int, error_msg: str = None):
        """Update sync history record."""
        sync_history.status = 'FAILED' if error_msg else 'COMPLETED'
        sync_history.total_creates = total_items
        sync_history.error_message = error_msg
        sync_history.end_time = datetime.now()
        self.db.commit()

    def _ensure_qdrant_collection(self, collection_name: str):
        """Ensure Qdrant collection exists."""
        try:
            logger.info(f"Checking if collection '{collection_name}' exists...")
            try:
                # Try to get collection info
                self.qdrant_client.get_collection(collection_name)
                logger.info(f"Collection '{collection_name}' exists")
                return
            except Exception as e:
                error_str = str(e)
                logger.info(f"Collection check error: {error_str}")
                
                # Check if collection already exists
                if "already exists" in error_str:
                    logger.info(f"Collection '{collection_name}' already exists")
                    return
                
                # Check if collection not found
                if "Not found" in error_str or "validation" in error_str.lower():
                    logger.info(f"Creating collection '{collection_name}'...")
                    try:
                        self.qdrant_client.create_collection(
                            collection_name=collection_name,
                            vectors_config=models.VectorParams(
                                size=1536,  # OpenAI embedding size
                                distance=models.Distance.COSINE
                            )
                        )
                        logger.info(f"Collection '{collection_name}' created successfully")
                    except Exception as create_error:
                        if "already exists" in str(create_error):
                            logger.info(f"Collection '{collection_name}' already exists (from create)")
                            return
                        raise
                else:
                    logger.error(f"Error checking collection: {error_str}")
                    raise
        except Exception as e:
            logger.error(f"Error in _ensure_qdrant_collection: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def _process_qdrant_data(self, table_name: str, collection_name: str, 
                           openai_client: OpenAI, sync_history: SyncHistory) -> int:
        """Process data for Qdrant sync."""
        total_items = 0
        # Use default batch size of 100
        batch_size = 100
        logger.info(f"Using batch size: {batch_size}")
        
        # Get data from PDS
        table_name = self._ensure_unifier_prefix(table_name)
        payload = self.build_payload()
        next_key = None
        
        while True:
            if next_key is not None:
                payload["nextKey"] = next_key
            
            # Get data from PDS
            response = self._make_pds_request(payload)
            if not response:
                break
                
            # Process data in batches
            items = response.get("data", {}).get(table_name, [])
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                total_items += self._process_qdrant_batch(
                    batch=batch,
                    collection_name=collection_name,
                    openai_client=openai_client
                )
            
            # Check pagination
            next_key = self._get_next_key(response)
            if not next_key:
                break
            
            time.sleep(1)  # Rate limiting
        
        return total_items

    def _make_pds_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a request to the PDS API."""
        try:
            # Create a new session for each request
            with requests.Session() as session:
                session.trust_env = False  # Don't use environment proxy settings
                
                # If proxies are configured, add them to the session
                # if 'proxies' in self.source_config:
                #     session.proxies = self.source_config['proxies']
                
                response = session.post(
                    self.pds_url,
                    headers=self.get_auth_header(),
                    json=payload,
                    timeout=300  # Increased timeout to 5 minutes
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error making PDS request: {str(e)}")
            return None

    def _get_next_key(self, response: Dict[str, Any]) -> Optional[int]:
        """Get next key from pagination data."""
        pagination = response.get("pagination", [])
        if pagination and isinstance(pagination, list) and len(pagination) > 0:
            pagination_data = pagination[0]
            next_table_name = str(pagination_data.get("nextTableName", "-1"))
            next_key = int(pagination_data.get("nextKey", 0))
            if next_key != 0 and next_table_name != "-1":
                return next_key
        return None

    def _process_qdrant_batch(self, batch: List[Dict[str, Any]], 
                            collection_name: str, openai_client: OpenAI) -> int:
        """Process a batch of items for Qdrant."""
        logger.info(f"Processing Qdrant batch of size {len(batch)} for collection {collection_name}")
        
        # Get primary key columns
        primary_key_columns = [col.column_name for col in self.columns if col.is_primary_key]
        if not primary_key_columns:
            logger.warning("No primary key columns found, using UUID for point IDs")
        
        # Prepare text for embeddings
        texts_to_embed = []
        point_ids = []
        source_ids = []  # Store source identifiers for tracking
        
        for item in batch:
            # Generate source identifier from primary keys
            if primary_key_columns:
                # Create a deterministic ID from primary key values
                pk_values = []
                source_pk = {}  # Store original primary key values
                for col in primary_key_columns:
                    value = item.get(col)
                    if value is not None:
                        pk_values.append(f"{col}:{value}")
                        source_pk[col] = value
                
                # Create a deterministic string that includes table name and primary keys
                # Format: table_name:pk1:value1:pk2:value2:...
                name_parts = [self.table.table_name] + pk_values
                name = ":".join(name_parts)
                
                # Use UUID5 (deterministic) based on the table name and primary key values
                namespace = uuid.NAMESPACE_DNS  # Using DNS namespace for consistency
                point_id = str(uuid.uuid5(namespace, name))
                source_id = "_".join(pk_values)  # Store the original identifier
            else:
                point_id = str(uuid.uuid4())
                source_id = point_id
                source_pk = {}
            
            point_ids.append(point_id)
            source_ids.append(source_id)
            
            # Prepare text for embedding
            text_fields = []
            for col in self.columns:
                if col.active and item.get(col.column_name):
                    text_fields.append(f"{col.column_name}: {item[col.column_name]}")
            texts_to_embed.append(" | ".join(text_fields))
        
        # Get embeddings
        try:
            logger.info("Requesting embeddings from OpenAI")
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=texts_to_embed
            )
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Received {len(embeddings)} embeddings from OpenAI")
        except Exception as e:
            logger.error(f"Error getting embeddings: {str(e)}")
            raise
        
        # Delete existing points if they exist
        try:
            if point_ids:
                logger.info(f"Deleting {len(point_ids)} existing points")
                self.qdrant_client.delete(
                    collection_name=collection_name,
                    points_selector=models.PointIdsList(
                        points=point_ids
                    )
                )
        except Exception as e:
            logger.warning(f"Error deleting existing points: {str(e)}")
        
        # Prepare points for Qdrant
        points = []
        for idx, (item, embedding, point_id, source_id) in enumerate(zip(batch, embeddings, point_ids, source_ids)):
            # Extract primary key values for this item
            source_pk = {}
            if primary_key_columns:
                for col in primary_key_columns:
                    value = item.get(col)
                    if value is not None:
                        source_pk[col] = value
            
            points.append(models.PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "table_name": self.table.table_name,
                    "original_data": item,
                    "text": texts_to_embed[idx],
                    "source_id": source_id,  # Original identifier from primary keys
                    "source_pk": source_pk,  # Original primary key values
                    "sync_timestamp": datetime.now().isoformat()  # Track when this record was synced
                }
            ))
        
        # Upsert to Qdrant
        try:
            logger.info(f"Attempting to upsert {len(points)} points to Qdrant")
            logger.info(f"Qdrant client state before upsert: {self.qdrant_client}")
            logger.info(f"Qdrant client type: {type(self.qdrant_client)}")
            logger.info(f"Qdrant client attributes: {dir(self.qdrant_client)}")
            
            self.qdrant_client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info("Successfully upserted points to Qdrant")
            return len(batch)
        except Exception as e:
            logger.error(f"Error upserting to Qdrant: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error args: {e.args}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    def run_sql_sync(self):
        """Run SQL sync process."""
        try:
            sync_history = self._create_sync_history()
            self.create_destination_table()
            
            # Get data from PDS
            all_data = self._get_table_data(self.table.table_name)
            
            # Process data
            total_updates, total_creates = self.sync_data(all_data)
            
            # Update sync history
            self._update_sync_history(sync_history, total_creates)
            
            return {
                "status": "SUCCESS",
                "message": f"Successfully synced {len(all_data)} rows",
                "total_rows": len(all_data),
                "total_updates": total_updates,
                "total_creates": total_creates,
                "sync_guid": str(sync_history.sync_guid)
            }
            
        except Exception as e:
            logger.error(f"Error in SQL sync process: {str(e)}")
            if 'sync_history' in locals():
                self._update_sync_history(sync_history, 0, str(e))
            raise

    def create_destination_table(self):
        """Create the destination table if it doesn't exist."""
        with self.dest_engine.connect() as conn:
            # Get primary key columns
            primary_key_columns = [col.column_name for col in self.columns if col.is_primary_key]
            
            # Create column definitions
            column_definitions = []
            for col in self.columns:
                pg_type = self._get_postgres_type(col.data_type)
                column_definitions.append(f'"{col.column_name}" {pg_type}')
            
            # Create table
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS "{self.table.table_name}" (
                {', '.join(column_definitions)}
                {', PRIMARY KEY (' + ', '.join([f'"{col}"' for col in primary_key_columns]) + ')' if primary_key_columns else ''}
            )
            """
            conn.execute(text(create_table_sql))
            conn.commit()

    def _get_postgres_type(self, data_type: str) -> str:
        """Convert PDS data types to PostgreSQL data types."""
        type_map = {
            'string': 'VARCHAR(255)',
            'number': 'NUMERIC',
            'date': 'DATE',
            'datetime': 'TIMESTAMP',
            'boolean': 'BOOLEAN'
        }
        return type_map.get(data_type.lower(), 'VARCHAR(255)')

    def _get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all data from PDS table."""
        table_name = self._ensure_unifier_prefix(table_name)
        payload = self.build_payload()
        all_data = []
        next_key = None
        
        while True:
            if next_key is not None:
                payload["nextKey"] = next_key
            
            response = self._make_pds_request(payload)
            if not response:
                break
            
            items = response.get("data", {}).get(table_name, [])
            all_data.extend(items)
            
            next_key = self._get_next_key(response)
            if not next_key:
                break
            
            time.sleep(1)
        
        return all_data

    def sync_data(self, data: List[Dict[str, Any]]) -> tuple[int, int]:
        """Sync data to destination table."""
        updates = 0
        creates = 0
        
        with self.dest_engine.connect() as conn:
            for row in data:
                try:
                    # Convert values to strings
                    processed_row = {k: str(v) if v is not None else None for k, v in row.items()}
                    
                    # Get primary key values
                    primary_key_columns = [col.column_name for col in self.columns if col.is_primary_key]
                    if not primary_key_columns:
                        continue
                    
                    # Build WHERE clause
                    conditions = []
                    values = {}
                    for col in primary_key_columns:
                        value = processed_row.get(col)
                        if value is not None and value.strip():
                            param_name = f"pk_{col.lower()}"
                            conditions.append(f'"{col}" = :{param_name}')
                            values[param_name] = value
                    
                    if not conditions:
                        continue
                    
                    where_clause = ' AND '.join(conditions)
                    
                    # Check if row exists
                    check_sql = f'SELECT COUNT(*) FROM "{self.table.table_name}" WHERE {where_clause}'
                    result = conn.execute(text(check_sql), values).scalar()
                    
                    if result > 0:
                        # Update existing row
                        update_columns = []
                        update_values = {}
                        for col in self.columns:
                            if col.column_name in processed_row and col.column_name not in primary_key_columns:
                                value = processed_row[col.column_name]
                                if value is not None and value.strip():
                                    param_name = f"update_{col.column_name.lower()}"
                                    update_columns.append(f'"{col.column_name}" = :{param_name}')
                                    update_values[param_name] = value
                        
                        if update_columns:
                            update_sql = f"""
                            UPDATE "{self.table.table_name}"
                            SET {', '.join(update_columns)}
                            WHERE {where_clause}
                            """
                            update_values.update(values)
                            conn.execute(text(update_sql), update_values)
                            updates += 1
                    else:
                        # Insert new row
                        columns = []
                        insert_values = {}
                        for col in self.columns:
                            if col.column_name in processed_row:
                                value = processed_row[col.column_name]
                                if value is not None and value.strip():
                                    param_name = f"insert_{col.column_name.lower()}"
                                    columns.append(f'"{col.column_name}"')
                                    insert_values[param_name] = value
                        
                        if columns:
                            placeholders = [f":{k}" for k in insert_values.keys()]
                            insert_sql = f"""
                            INSERT INTO "{self.table.table_name}" ({', '.join(columns)})
                            VALUES ({', '.join(placeholders)})
                            """
                            conn.execute(text(insert_sql), insert_values)
                            creates += 1
                
                except Exception as e:
                    logger.error(f"Error processing row: {str(e)}")
                    continue
            
            conn.commit()
            return updates, creates 