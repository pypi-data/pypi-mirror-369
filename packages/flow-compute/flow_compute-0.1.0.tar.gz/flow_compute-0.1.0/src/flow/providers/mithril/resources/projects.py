"""Project resolution component for the Mithril provider.

Resolves human-readable project names to IDs with a small in-memory cache and
clear errors when a project cannot be found.
"""

import logging

from flow.providers.mithril.api.client import MithrilApiClient
from flow.errors import FlowError
from flow.providers.mithril.api.types import ProjectModel as Project
from flow.utils.instance_parser import is_uuid

logger = logging.getLogger(__name__)


class ProjectNotFoundError(FlowError):
    """Raised when a project cannot be resolved."""

    def __init__(self, project_name: str, available_projects: list[str]):
        self.project_name = project_name
        self.available_projects = available_projects

        msg = f"Project '{project_name}' not found."
        if available_projects:
            msg += "\n\nAvailable projects:\n"
            for project in available_projects[:5]:
                msg += f"  • {project}\n"
            if len(available_projects) > 5:
                msg += f"  ... and {len(available_projects) - 5} more"

        super().__init__(msg)


class ProjectResolver:
    """Resolves project names to IDs with caching and error handling."""

    def __init__(self, api_client: MithrilApiClient):
        """Initialize project resolver.

        Args:
            http_client: HTTP client for API requests
        """
        # Centralized API client only (no raw HTTP fallback)
        self._api: MithrilApiClient = api_client
        self._cache: dict[str, tuple[str, float]] = {}  # name -> (ID, ts)
        self._projects_cache: tuple[list[Project], float] | None = None
        self._ttl_seconds: float = 300.0  # 5 minutes

    def resolve(self, project_identifier: str) -> str:
        """Resolve project name or ID to project ID.

        Args:
            project_identifier: Project name or UUID

        Returns:
            Project ID (UUID)

        Raises:
            ProjectNotFoundError: If project cannot be resolved
        """
        if not project_identifier:
            raise FlowError("Project identifier is required")

        # If already a UUID, return as is
        if is_uuid(project_identifier):
            logger.debug(f"Project identifier is already a UUID: {project_identifier}")
            return project_identifier

        # Check cache first (TTL)
        try:
            item = self._cache.get(project_identifier)
            if item is not None:
                pid, ts = item
                import time as _t

                if _t.time() - ts < self._ttl_seconds:
                    logger.debug(f"Resolved project '{project_identifier}' from cache")
                    return pid
                else:
                    self._cache.pop(project_identifier, None)
        except Exception:
            pass

        # Fetch and resolve
        project_id = self._resolve_from_api(project_identifier)
        if project_id:
            # Cache with TTL timestamp
            try:
                import time as _t

                self._cache[project_identifier] = (project_id, _t.time())
            except Exception:
                pass
            logger.info(f"Resolved project '{project_identifier}' to ID: {project_id}")
            return project_id

        # Not found - provide helpful error
        available_names = [p.name for p in self._get_all_projects()]
        raise ProjectNotFoundError(project_identifier, available_names)

    def list_projects(self) -> list[Project]:
        """List all available projects.

        Returns:
            List of Project objects
        """
        return self._get_all_projects()

    def invalidate_cache(self):
        """Clear the cache, forcing fresh lookups."""
        self._cache.clear()
        self._projects_cache = None
        logger.debug("Project resolver cache invalidated")

    def _resolve_from_api(self, project_name: str) -> str | None:
        """Resolve project name using API.

        Args:
            project_name: Project name to resolve

        Returns:
            Project ID if found, None otherwise
        """
        projects = self._get_all_projects()

        # Exact match first
        for project in projects:
            if project.name == project_name:
                return project.fid

        # Case-insensitive match
        name_lower = project_name.lower()
        for project in projects:
            if project.name.lower() == name_lower:
                logger.warning(
                    f"Found case-insensitive match: '{project.name}' for query '{project_name}'"
                )
                return project.fid

        return None

    def _get_all_projects(self) -> list[Project]:
        """Get all projects from API with caching.

        Returns:
            List of Project objects
        """
        if self._projects_cache is not None:
            try:
                projects, ts = self._projects_cache
                import time as _t

                if _t.time() - ts < self._ttl_seconds:
                    return projects
            except Exception:
                pass

        try:
            response = self._api.list_projects()

            # API returns list directly
            projects_data = response if isinstance(response, list) else []

            projects_list = [
                Project(
                    fid=p["fid"],
                    name=p["name"],
                    created_at=p["created_at"],
                )
                for p in projects_data
                if "fid" in p and "name" in p and "created_at" in p
            ]

            logger.debug(f"Loaded {len(projects_list)} projects from API")
            try:
                import time as _t

                self._projects_cache = (projects_list, _t.time())
            except Exception:
                self._projects_cache = (projects_list, 0.0)
            return projects_list

        except Exception as e:
            logger.error(f"Failed to fetch projects: {e}")
            # Return empty list instead of failing completely
            return []
