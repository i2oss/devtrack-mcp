"""Tests for the MCP tool functions in server.py.

@mcp.tool() in this SDK version registers the function but returns it
unchanged, so these call the tool functions directly with the DevTrack
HTTP layer mocked via respx, rather than spinning up a full MCP client/
server transport.
"""

import respx
from httpx import Response

from devtrack_mcp import server

BASE = "http://trydevsuite.techexcel.com/DevTrackAPI"


@respx.mock
async def test_create_task_tool_success(monkeypatch):
    monkeypatch.setenv("DEVTRACK_TOKEN", "test-token")
    respx.post(f"{BASE}/api/Task/Create").mock(
        return_value=Response(200, json={"Success": True, "Error": None, "Data": 99})
    )
    result = await server.create_task(project_id=1, template_id=1)
    assert result == {"task_id": 99}


@respx.mock
async def test_get_task_tool_surfaces_devtrack_error(monkeypatch):
    monkeypatch.setenv("DEVTRACK_TOKEN", "test-token")
    respx.post(f"{BASE}/api/Task/Get").mock(
        return_value=Response(
            200,
            json={
                "Success": False,
                "Error": {"ErrorCode": 4, "ErrorMessage": "Task not found"},
                "Data": None,
            },
        )
    )
    result = await server.get_task(project_id=1, task_id=12345)
    assert result["error"] == "Task not found"
    assert result["error_code"] == 4


@respx.mock
async def test_query_tasks_tool_wraps_results(monkeypatch):
    monkeypatch.setenv("DEVTRACK_TOKEN", "test-token")
    respx.post(f"{BASE}/api/Task/Query").mock(
        return_value=Response(200, json={"Success": True, "Error": None, "Data": {"Total": 0, "Items": []}})
    )
    result = await server.query_tasks(project_id=1)
    assert result == {"results": {"Total": 0, "Items": []}}
