"""Thin async client over the TechExcel DevTrack REST API.

Handles auth, the base envelope every DevTrack response is wrapped in
({"Success", "Error", "Data"}), and translation into a small exception
type so callers (the MCP tools in server.py) don't have to think about
HTTP or DevTrack's envelope at all.
"""

from __future__ import annotations

import sys
from typing import Any

import httpx

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from devtrack_mcp.config import DevTrackConfig
from devtrack_mcp.models import (
    FieldValue,
    StandardQueryCondition,
    TaskCreateRequest,
    TaskGetRequest,
    TaskQueryRequest,
    TaskUpdateRequest,
)


class DevTrackAPIError(Exception):
    """Raised when DevTrack returns Success: false, or the HTTP call fails."""

    def __init__(self, message: str, error_code: int | None = None):
        super().__init__(message)
        self.error_code = error_code


class DevTrackClient:
    def __init__(self, config: DevTrackConfig, http_client: httpx.AsyncClient | None = None):
        self._config = config
        self._owns_client = http_client is None
        self._http = http_client or httpx.AsyncClient(base_url=config.base_url, timeout=30.0)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._config.token:
            headers["Authorization"] = f"bearer {self._config.token}"
        return headers

    def _params(self) -> dict[str, Any]:
        return {"LanguageID": self._config.language_id}

    async def _request(self, method: str, path: str, json: dict[str, Any] | None = None) -> Any:
        try:
            response = await self._http.request(
                method,
                path,
                json=json,
                headers=self._headers(),
                params=self._params(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise DevTrackAPIError(
                f"DevTrack API returned HTTP {exc.response.status_code} for {method} {path}"
            ) from exc
        except httpx.HTTPError as exc:
            raise DevTrackAPIError(f"Could not reach DevTrack API at {path}: {exc}") from exc

        body = response.json()
        if not body.get("Success", False):
            error = body.get("Error") or {}
            raise DevTrackAPIError(
                error.get("ErrorMessage", "Unknown DevTrack API error"),
                error_code=error.get("ErrorCode"),
            )
        return body.get("Data")

    # -- Task endpoints -----------------------------------------------

    async def create_task(
        self, project_id: int, template_id: int, field_values: list[dict[str, Any]] | None = None
    ) -> int:
        """Create a task/issue. Returns the new task's ID."""
        req = TaskCreateRequest(
            ProjectId=project_id,
            TemplateId=template_id,
            FieldValues=[FieldValue(**fv) for fv in (field_values or [])],
        )
        return await self._request("POST", "/api/Task/Create", json=req.model_dump())

    async def get_task(
        self, project_id: int, task_id: int, field_ids: list[int] | None = None
    ) -> dict[str, Any]:
        """Fetch a task/issue's details."""
        req = TaskGetRequest(ProjectId=project_id, TaskId=task_id, FieldIds=field_ids or [])
        return await self._request("POST", "/api/Task/Get", json=req.model_dump())

    async def update_task(
        self,
        project_id: int,
        task_id: int,
        field_values: list[dict[str, Any]] | None = None,
        transition_id: int | None = None,
    ) -> dict[str, Any]:
        """Update a task/issue's fields and/or move it through a workflow transition."""
        req = TaskUpdateRequest(
            ProjectId=project_id,
            TaskId=task_id,
            TransitionId=transition_id,
            FieldValues=[FieldValue(**fv) for fv in (field_values or [])],
        )
        return await self._request("POST", "/api/Task/Update", json=req.model_dump())

    async def query_tasks(
        self,
        project_id: int,
        condition: dict[str, Any] | None = None,
        field_ids: list[int] | None = None,
        page_index: int = 1,
        page_size: int = 25,
    ) -> Any:
        """Search tasks/issues matching a DevTrack StandardQueryCondition.

        See the caveat in models.TaskQueryRequest for how this shape was
        derived (high-confidence, assembled from confirmed sibling
        endpoints -- Task/Query's own docs page has been unreachable).
        """
        req = TaskQueryRequest(
            ProjectId=project_id,
            Condition=StandardQueryCondition(**(condition or {})),
            FieldIds=field_ids or [],
            PageIndex=page_index,
            PageSize=page_size,
        )
        return await self._request("POST", "/api/Task/Query", json=req.model_dump())
