"""Database models and initialization using SQLAlchemy."""

import json
from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.types import TypeDecorator, VARCHAR

from .models import RunStatus


Base = declarative_base()


class GUID(TypeDecorator):
    """Platform-independent GUID type for SQLite."""
    impl = VARCHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        else:
            return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return value


class JSONType(TypeDecorator):
    """JSON type that stores JSON as TEXT in SQLite."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value


class Project(Base):
    """Database model for a deployed project."""
    __tablename__ = "projects"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    config_yaml = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to runs
    runs = relationship("Run", back_populates="project", cascade="all, delete-orphan")


class Run(Base):
    """Database model for a workflow run."""
    __tablename__ = "runs"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid4()))
    project_id = Column(GUID, ForeignKey("projects.id"), nullable=False)
    status = Column(SQLEnum(RunStatus), nullable=False, default=RunStatus.PENDING)
    context = Column(JSONType, nullable=True)  # The blackboard state
    input_context = Column(JSONType, nullable=True)  # Initial input from trigger
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationship to project
    project = relationship("Project", back_populates="runs")
    
    # Relationship to trace events
    trace_events = relationship("TraceEvent", back_populates="run", cascade="all, delete-orphan")


class TraceEvent(Base):
    """Database model for a trace event (execution step log)."""
    __tablename__ = "trace_events"

    id = Column(GUID, primary_key=True, default=lambda: str(uuid4()))
    run_id = Column(GUID, ForeignKey("runs.id"), nullable=False)
    step_id = Column(String, nullable=False)
    status = Column(String, nullable=False)  # COMPLETED or FAILED
    input = Column(JSONType, nullable=True)
    output = Column(JSONType, nullable=True)
    metrics = Column(JSONType, nullable=True)  # latency_ms, cost_usd
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to run
    run = relationship("Run", back_populates="trace_events")


# Database initialization
def init_db(database_url: str = "sqlite:///holon.db"):
    """Initialize the database and create all tables."""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine


def get_session_maker(engine):
    """Create a session maker for database operations."""
    return sessionmaker(bind=engine)
