"""Tests for the Holon Engine core functionality."""

import tempfile
import shutil
from pathlib import Path

import pytest

from holon_engine.persistence import PersistenceService
from holon_engine.models import Project, Run, RunStatus
from uuid import uuid4
from datetime import datetime


@pytest.fixture
def test_storage():
    """Create a temporary storage directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def persistence(test_storage):
    """Create a persistence service with test storage."""
    return PersistenceService(f"file://{test_storage}")


def test_save_and_load_project(persistence):
    """Test saving and loading a project."""
    project = Project(
        id=uuid4(),
        name="Test-Project",
        config_yaml="version: '1.0'\nproject: Test",
        env_vars={"KEY": "value"},
        created_at=datetime.utcnow(),
    )

    persistence.save_project(project)
    loaded = persistence.get_project(project.id)

    assert loaded is not None
    assert loaded.id == project.id
    assert loaded.name == project.name
    assert loaded.env_vars == {"KEY": "value"}


def test_list_projects(persistence):
    """Test listing projects."""
    project1 = Project(
        id=uuid4(),
        name="Project-1",
        config_yaml="version: '1.0'\nproject: P1",
        created_at=datetime.utcnow(),
    )
    project2 = Project(
        id=uuid4(),
        name="Project-2",
        config_yaml="version: '1.0'\nproject: P2",
        created_at=datetime.utcnow(),
    )

    persistence.save_project(project1)
    persistence.save_project(project2)

    projects = persistence.list_projects()
    assert len(projects) >= 2
    names = [p.name for p in projects]
    assert "Project-1" in names
    assert "Project-2" in names


def test_save_and_load_run(persistence):
    """Test saving and loading a run."""
    run = Run(
        id=uuid4(),
        project_id=uuid4(),
        status=RunStatus.PENDING,
        input_context={"test": "data"},
        started_at=None,
        ended_at=None,
    )

    persistence.save_run(run)
    loaded = persistence.get_run(run.id)

    assert loaded is not None
    assert loaded.id == run.id
    assert loaded.status == RunStatus.PENDING
    assert loaded.input_context == {"test": "data"}


def test_get_nonexistent_project(persistence):
    """Test getting a project that doesn't exist."""
    fake_id = uuid4()
    project = persistence.get_project(fake_id)
    assert project is None


def test_get_nonexistent_run(persistence):
    """Test getting a run that doesn't exist."""
    fake_id = uuid4()
    run = persistence.get_run(fake_id)
    assert run is None
