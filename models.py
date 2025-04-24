from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from database import Base
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ConnectionOptions(Base):
    __tablename__ = "CONNECTIONOPTIONS"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    connections = relationship("Connection", back_populates="connection_type")

class Connection(Base):
    __tablename__ = "CONNECTIONS"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    connection_name = Column(String, nullable=False)
    connection_description = Column(String, nullable=True)
    connection_config = Column(LargeBinary, nullable=False)  # Store JSON as BLOB
    connection_type_id = Column(UUID(as_uuid=True), ForeignKey('CONNECTIONOPTIONS.id'), nullable=False)
    direction = Column(Boolean, nullable=False)  # True for source, False for destination
    connection_type = relationship("ConnectionOptions", back_populates="connections")
    source_tables = relationship("Config", foreign_keys="Config.source_connection_id", back_populates="source_connection")
    destination_tables = relationship("Config", foreign_keys="Config.destination_connection_id", back_populates="destination_connection")

class Config(Base):
    __tablename__ = "PDSTABLES"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    table_name = Column(String, nullable=False)
    config_name = Column(String, nullable=False)
    source_connection_id = Column(UUID(as_uuid=True), ForeignKey('CONNECTIONS.id'), nullable=False)
    destination_connection_id = Column(UUID(as_uuid=True), ForeignKey('CONNECTIONS.id'), nullable=False)
    active = Column(Boolean, default=True)
    page_size = Column(Integer, default=10000)  # Default to max page size
    
    # Relationships
    source_connection = relationship("Connection", foreign_keys=[source_connection_id], back_populates="source_tables")
    destination_connection = relationship("Connection", foreign_keys=[destination_connection_id], back_populates="destination_tables")
    columns = relationship("TableColumn", back_populates="pds_table", cascade="all, delete-orphan")

class TableColumn(Base):
    __tablename__ = "TABLECOLLUMNS"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pds_table_id = Column(UUID(as_uuid=True), ForeignKey('PDSTABLES.id'), nullable=False)
    column_name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)
    active = Column(Boolean, default=True)
    pds_table = relationship("Config", back_populates="columns") 