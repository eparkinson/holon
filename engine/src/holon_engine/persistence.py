import json
import logging
import os
from datetime import datetime
from typing import List, Optional
from uuid import UUID

import fsspec
from pydantic import ValidationError

from .models import Project, Run


# Set up logging
logger = logging.getLogger(__name__)


class PersistenceService:
    def __init__(self, storage_uri: str):
        self.storage_uri = storage_uri
        # Parse protocol
        if "://" in storage_uri:
            self.protocol, self.root_path = storage_uri.split("://", 1)
        else:
            self.protocol = "file"
            self.root_path = storage_uri

        # Initialize filesystem
        # s3fs/fsspec might require kwargs for credentials if not in env
        self.fs = fsspec.filesystem(self.protocol, auto_mkdir=True)

        # Ensure structure exists
        if self.protocol == "file":
            os.makedirs(os.path.join(self.root_path, "projects"), exist_ok=True)
            os.makedirs(os.path.join(self.root_path, "runs"), exist_ok=True)

    def _path(self, *parts):
        """Construct a path compatible with the filesystem."""
        # Force forward slashes for fsspec compatibility across protocols
        clean_parts = [str(p).strip("/") for p in parts]
        return f"{self.root_path}/{'/'.join(clean_parts)}"

    def save_project(self, project: Project):
        """Save a project configuration."""
        path = self._path("projects", f"{project.id}.json")
        with self.fs.open(path, "w") as f:
            f.write(project.model_dump_json())

    def get_project(self, project_id: UUID) -> Optional[Project]:
        """Retrieve a project by ID."""
        path = self._path("projects", f"{project_id}.json")
        if not self.fs.exists(path):
            return None
        try:
            with self.fs.open(path, "r") as f:
                data = json.load(f)
                return Project(**data)
        except (json.JSONDecodeError, ValidationError):
            return None

    def list_projects(self) -> List[Project]:
        """List all deployed projects."""
        projects_dir = self._path("projects")

        # Ensure projects directory exists
        if not self.fs.exists(projects_dir):
            return []

        # glob returns full paths including protocol prefix sometimes, or just path
        # fsspec's fs.glob usually returns paths relative to fs root or absolute paths
        try:
            files = self.fs.glob(f"{projects_dir}/*.json")
        except (OSError, IOError, PermissionError) as e:
            # If glob fails due to filesystem errors, return empty list
            logger.error(f"Failed to glob projects directory: {e}")
            return []

        projects = []
        for file_path in files:
            # Re-add protocol if glob strips it, or just open directly
            # fs.open usually accepts what fs.glob returns
            try:
                with self.fs.open(file_path, "r") as f:
                    projects.append(Project(**json.load(f)))
            except Exception:
                continue

        # Safely sort projects by created_at, handling None values
        try:
            return sorted(
                projects,
                key=lambda p: p.created_at or datetime.min,
                reverse=True,
            )
        except (TypeError, AttributeError) as e:
            # If sorting fails due to type errors, return unsorted list
            logger.warning(f"Failed to sort projects by created_at: {e}")
            return projects

    def save_run(self, run: Run):
        """Save or update a workflow run."""
        path = self._path("runs", f"{run.id}.json")
        with self.fs.open(path, "w") as f:
            f.write(run.model_dump_json())

    def get_run(self, run_id: UUID) -> Optional[Run]:
        """Retrieve a run configuration and state."""
        path = self._path("runs", f"{run_id}.json")
        if not self.fs.exists(path):
            return None
        try:
            with self.fs.open(path, "r") as f:
                data = json.load(f)
                return Run(**data)
        except Exception:
            return None


def get_persistence() -> PersistenceService:
    """Factory to get the persistence service instance."""
    uri = os.getenv("HOLON_STORAGE_URI", "file://./holon_data")
    return PersistenceService(uri)
