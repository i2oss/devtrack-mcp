"""MCP server exposing DevTrack task/issue and subproject operations as tools.

Core v1 scope: create, get, update and query tasks. Subproject browsing
(get_subproject, list_subprojects) rounds it out. Reporting tools and a
workflow-chaining SKILL.md are still backlog for v2 (see README) -- as is
project-level enumeration (list_projects), which DevTrack's classic REST
API has no confirmed endpoint for; see the note in models.py.
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from devtrack_mcp.client import DevTrackAPIError, DevTrackClient
from devtrack_mcp.config import DevTrackConfig

mcp = MCPServer(
    "devtrack",
    instructions=(
        "Tools for reading and managing tasks/issues and subprojects in "
        "TechExcel DevTrack. Every tool needs a DevTrack ProjectId; ask the "
        "user for it if you don't already know it (DevTrack has no API for "
        "listing all projects -- it's usually read off the DevTrack web UI "
        "URL). Use list_subprojects to discover a project's subproject "
        "structure before filing or querying issues within a specific "
        "subproject. FieldIds/FieldValues are DevTrack's internal "
        "custom-field IDs (e.g. 101=Title, 108=Owner, 601=Status) and vary "
        "per DevTrack project configuration -- ask the user or use get_task "
        "on a known task to learn the field IDs in use before writing to them."
    ),
)


def _client() -> DevTrackClient:
    return DevTrackClient(DevTrackConfig.from_env())


@mcp.tool()
async def create_task(
    project_id: int, template_id: int, field_values: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Create a new task/issue in DevTrack.

    Args:
        project_id: DevTrack project ID to create the task in.
        template_id: ID of the work-item template (issue type) to use.
        field_values: List of {"FieldId": int, "Option": int, "FieldValue": any}
            entries setting the new task's fields (e.g. Title, Description).
    """
    async with _client() as client:
        try:
            task_id = await client.create_task(project_id, template_id, field_values)
            return {"task_id": task_id}
        except DevTrackAPIError as exc:
            return {"error": str(exc), "error_code": exc.error_code}


@mcp.tool()
async def get_task(
    project_id: int, task_id: int, field_ids: list[int] | None = None
) -> dict[str, Any]:
    """Fetch a task/issue's details from DevTrack.

    Args:
        project_id: DevTrack project ID the task belongs to.
        task_id: The task/issue ID to fetch.
        field_ids: Optional list of specific field IDs to return; omit for
            DevTrack's default field set.
    """
    async with _client() as client:
        try:
            return await client.get_task(project_id, task_id, field_ids)
        except DevTrackAPIError as exc:
            return {"error": str(exc), "error_code": exc.error_code}


@mcp.tool()
async def update_task(
    project_id: int,
    task_id: int,
    field_values: list[dict[str, Any]] | None = None,
    transition_id: int | None = None,
) -> dict[str, Any]:
    """Update a task/issue's fields and/or advance its workflow status.

    Args:
        project_id: DevTrack project ID the task belongs to.
        task_id: The task/issue ID to update.
        field_values: List of {"FieldId": int, "Option": int, "FieldValue": any}
            entries for fields to change.
        transition_id: Optional workflow transition ID to move the task
            through (e.g. "Start Work", "Resolve"). Get valid transitions
            from DevTrack's UI or admin config.
    """
    async with _client() as client:
        try:
            return await client.update_task(project_id, task_id, field_values, transition_id)
        except DevTrackAPIError as exc:
            return {"error": str(exc), "error_code": exc.error_code}


@mcp.tool()
async def query_tasks(
    project_id: int,
    keyword: str | None = None,
    condition: dict[str, Any] | None = None,
    field_ids: list[int] | None = None,
    page_index: int = 1,
    page_size: int = 25,
) -> dict[str, Any]:
    """Search for tasks/issues in a DevTrack project.

    Args:
        project_id: DevTrack project ID to search within.
        keyword: Quick free-text search across task fields. For anything
            beyond a keyword search, use `condition` instead (or together
            with keyword -- it's folded into the condition as Keyword).
        condition: A DevTrack StandardQueryCondition dict for advanced
            filtering, e.g. {"Status": [{"Id": 1, "Option": 2}],
            "Owner": [{"Id": 5, "Option": 1}], "IssueType": [1, 2],
            "DateTimeFields": [{"FieldId": 10, "From": "2026-01-01 00:00:00",
            "To": "2026-12-31 23:59:59"}]}. Status/Owner entries use DevTrack's
            {"Id": int, "Option": int} shape. Omit entirely to match all
            tasks in the project (paginated).
        field_ids: Optional list of field IDs to include per result.
        page_index: 1-based page number.
        page_size: Results per page.
    """
    merged_condition = dict(condition or {})
    if keyword:
        merged_condition["Keyword"] = keyword
    async with _client() as client:
        try:
            result = await client.query_tasks(
                project_id, merged_condition, field_ids, page_index, page_size
            )
            return {"results": result}
        except DevTrackAPIError as exc:
            return {"error": str(exc), "error_code": exc.error_code}


@mcp.tool()
async def get_subproject(project_id: int, subproject_id: int) -> dict[str, Any]:
    """Fetch a single subproject's info (name, status, manager, hierarchy path, etc).

    Args:
        project_id: DevTrack project ID the subproject belongs to.
        subproject_id: The subproject ID to fetch.
    """
    async with _client() as client:
        try:
            return await client.get_subproject(project_id, subproject_id)
        except DevTrackAPIError as exc:
            return {"error": str(exc), "error_code": exc.error_code}


@mcp.tool()
async def list_subprojects(project_id: int, subproject_id: int = 0) -> dict[str, Any]:
    """List a project's subproject structure as a tree.

    Useful for discovering what subprojects exist in a DevTrack project
    (and their IDs) before filing or querying tasks within one.

    Args:
        project_id: DevTrack project ID to browse.
        subproject_id: Root subproject to start from; 0 (default) starts
            from the project's top level.
    """
    async with _client() as client:
        try:
            tree = await client.list_subprojects(project_id, subproject_id)
            return {"tree": tree}
        except DevTrackAPIError as exc:
            return {"error": str(exc), "error_code": exc.error_code}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
