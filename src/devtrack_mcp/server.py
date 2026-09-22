"""MCP server exposing DevTrack task/issue operations as tools.

v1 scope is intentionally narrow: create, get, update and query tasks.
Project/subproject browsing, reporting, and workflow-chaining SKILL.md
files are tracked as backlog for a v2 (see README).
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from devtrack_mcp.client import DevTrackAPIError, DevTrackClient
from devtrack_mcp.config import DevTrackConfig

mcp = MCPServer(
    "devtrack",
    instructions=(
        "Tools for reading and managing tasks/issues in TechExcel DevTrack. "
        "Every tool needs a DevTrack ProjectId; ask the user for it if you "
        "don't already know it. FieldIds/FieldValues are DevTrack's internal "
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
    conditions: list[dict[str, Any]] | None = None,
    field_ids: list[int] | None = None,
    page_index: int = 1,
    page_size: int = 25,
) -> dict[str, Any]:
    """Search for tasks/issues in a DevTrack project matching filter conditions.

    Args:
        project_id: DevTrack project ID to search within.
        conditions: List of {"FieldId": int, "Operator": str, "Value": any}
            filters, e.g. [{"FieldId": 601, "Operator": "=", "Value": "Active"}].
            Omit to return all tasks (paginated).
        field_ids: Optional list of field IDs to include per result.
        page_index: 1-based page number.
        page_size: Results per page.
    """
    async with _client() as client:
        try:
            result = await client.query_tasks(
                project_id, conditions, field_ids, page_index, page_size
            )
            return {"results": result}
        except DevTrackAPIError as exc:
            return {"error": str(exc), "error_code": exc.error_code}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
