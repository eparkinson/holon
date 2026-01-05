"""Tests for the workflow execution engine."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from holon_engine.database import Base, Run
from holon_engine.engine import WorkflowEngine
from holon_engine.models import RunStatus


TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Create a test database session."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionMaker = sessionmaker(bind=engine)
    session = SessionMaker()
    
    yield session
    
    session.close()
    Base.metadata.drop_all(engine)


def test_parse_config(db_session):
    """Test parsing a valid holon.yaml configuration."""
    config_yaml = """
version: "1.0"
project: "Test-Project"

resources:
  - id: researcher
    provider: perplexity
    model: sonar-reasoning

workflow:
  type: sequential
  steps:
    - id: research
      agent: researcher
      instruction: "Research ${trigger.input.topic}"
"""
    
    engine = WorkflowEngine(db_session)
    config = engine.parse_config(config_yaml)
    
    assert config.version == "1.0"
    assert config.project == "Test-Project"
    assert len(config.resources) == 1
    assert config.resources[0].id == "researcher"
    assert config.workflow.type.value == "sequential"
    assert len(config.workflow.steps) == 1


def test_parse_invalid_config(db_session):
    """Test parsing an invalid configuration."""
    invalid_yaml = """
version: "1.0"
# Missing required fields
"""
    
    engine = WorkflowEngine(db_session)
    with pytest.raises(Exception):
        engine.parse_config(invalid_yaml)


def test_execute_sequential_workflow(db_session):
    """Test executing a sequential workflow."""
    config_yaml = """
version: "1.0"
project: "Test-Project"

resources:
  - id: test_agent
    provider: anthropic
    model: claude-3-5-sonnet

workflow:
  type: sequential
  steps:
    - id: step1
      agent: test_agent
      instruction: "Step 1"
    - id: step2
      agent: test_agent
      instruction: "Step 2"
"""
    
    # Create a run
    run = Run(
        id="test-run-001",
        project_id="test-project-001",
        status=RunStatus.PENDING,
        input_context={"topic": "AI"}
    )
    db_session.add(run)
    db_session.commit()
    
    # Execute the run
    engine = WorkflowEngine(db_session)
    engine.execute_run(run, config_yaml)
    
    # Refresh the run from DB
    db_session.refresh(run)
    
    # Check that the run completed successfully
    assert run.status == RunStatus.COMPLETED
    assert run.context is not None
    assert "steps" in run.context
    assert "step1" in run.context["steps"]
    assert "step2" in run.context["steps"]


def test_template_resolution(db_session):
    """Test that template variables are resolved correctly."""
    config_yaml = """
version: "1.0"
project: "Test-Project"

resources:
  - id: test_agent
    provider: anthropic
    model: claude-3-5-sonnet

workflow:
  type: sequential
  steps:
    - id: step1
      agent: test_agent
      instruction: "Research ${trigger.input.topic} in ${trigger.input.language}"
"""
    
    # Create a run with input context
    run = Run(
        id="test-run-002",
        project_id="test-project-002",
        status=RunStatus.PENDING,
        input_context={"topic": "Quantum Computing", "language": "Python"}
    )
    db_session.add(run)
    db_session.commit()
    
    # Execute the run
    engine = WorkflowEngine(db_session)
    engine.execute_run(run, config_yaml)
    
    # Refresh and check
    db_session.refresh(run)
    
    assert run.status == RunStatus.COMPLETED
    # The resolved instruction should be in the trace events
    # which are stored separately, but we can check the context was set up
    assert run.context["trigger"]["input"]["topic"] == "Quantum Computing"
    assert run.context["trigger"]["input"]["language"] == "Python"


def test_workflow_error_handling(db_session):
    """Test that errors are handled properly."""
    # Invalid workflow type to trigger an error
    invalid_config = """
version: "1.0"
project: "Test-Project"

resources:
  - id: test_agent
    provider: anthropic
    model: claude-3-5-sonnet

workflow:
  type: scatter-gather
  steps: []
"""
    
    run = Run(
        id="test-run-003",
        project_id="test-project-003",
        status=RunStatus.PENDING,
        input_context={}
    )
    db_session.add(run)
    db_session.commit()
    
    # Execute - should fail due to unsupported workflow type
    engine = WorkflowEngine(db_session)
    
    with pytest.raises(NotImplementedError):
        engine.execute_run(run, invalid_config)
    
    # Refresh and check that run is marked as FAILED
    db_session.refresh(run)
    assert run.status == RunStatus.FAILED
