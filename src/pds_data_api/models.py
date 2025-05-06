from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime, LargeBinary, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, backref
import uuid
from .database import Base
from datetime import datetime
from sqlalchemy import UniqueConstraint

class ConnectionOptions(Base):
    __tablename__ = "connection_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    connections = relationship("Connection", back_populates="connection_type")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

class Connection(Base):
    __tablename__ = "connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_name = Column(String, nullable=False)
    connection_description = Column(String, nullable=True)
    connection_config = Column(LargeBinary, nullable=False)  # Store JSON as BLOB
    connection_type_id = Column(UUID(as_uuid=True), ForeignKey('connection_options.id'), nullable=False)
    direction = Column(Boolean, nullable=False)  # True for source, False for destination
    connection_type = relationship("ConnectionOptions", back_populates="connections")
    source_tables = relationship("Config", foreign_keys="Config.source_connection_id", back_populates="source_connection")
    destination_tables = relationship("Config", foreign_keys="Config.destination_connection_id", back_populates="destination_connection")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

class Config(Base):
    __tablename__ = "pds_tables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_name = Column(String, nullable=False)
    source_connection_id = Column(UUID(as_uuid=True), ForeignKey('connections.id'), nullable=False)
    destination_connection_id = Column(UUID(as_uuid=True), ForeignKey('connections.id'), nullable=False)
    table_name = Column(String, nullable=False)
    title = Column(String, nullable=True)
    page_size = Column(Integer, default=1000)
    qdrant_batch_size = Column(Integer, nullable=True, server_default='100')
    active = Column(Boolean, default=True)
    source_connection = relationship("Connection", foreign_keys=[source_connection_id], back_populates="source_tables")
    destination_connection = relationship("Connection", foreign_keys=[destination_connection_id], back_populates="destination_tables")
    columns = relationship("TableColumn", back_populates="pds_table")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

class TableColumn(Base):
    __tablename__ = "table_columns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pds_table_id = Column(UUID(as_uuid=True), ForeignKey('pds_tables.id'), nullable=False)
    column_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    is_primary_key = Column(Boolean, default=False)
    pds_table = relationship("Config", back_populates="columns")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

class SyncHistory(Base):
    __tablename__ = "sync_history"

    sync_guid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pds_table_id = Column(UUID(as_uuid=True), ForeignKey('pds_tables.id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    total_columns = Column(Integer, nullable=True)
    total_updates = Column(Integer, nullable=True)
    total_creates = Column(Integer, nullable=True)
    status = Column(String, nullable=False)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QdrantCollection(Base):
    __tablename__ = "qdrant_collection_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    vector_size = Column(Integer, nullable=False)
    distance = Column(String, nullable=False)
    on_disk_payload = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

class QdrantPoint(Base):
    __tablename__ = "qdrant_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(UUID(as_uuid=True), ForeignKey('qdrant_collection_configs.id', ondelete='CASCADE'), nullable=False)
    point_id = Column(String, nullable=False)
    vector = Column(ARRAY(Float), nullable=False)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)

    collection = relationship("QdrantCollection", backref=backref("points", cascade="all, delete-orphan"))

    __table_args__ = (
        UniqueConstraint('collection_id', 'point_id', name='uq_collection_point_id'),
    ) 