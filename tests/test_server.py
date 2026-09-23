"""Tests for the MCP tool functions in server.py.

@mcp.tool() in this SDK version registers the function but returns it
unchanged, so these call the tool functions directly with the DevTrack
HTTP layer mocked via respx, rather than spinning up a full MCP client/
server transport.
"""

import json

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


@respx.mock
async def test_query_tasks_tool_folds_keyword_into_condition(monkeypatch):
    monkeypatch.setenv("DEVTRACK_TOKEN", "test-token")
    route = respx.post(f"{BASE}/api/Task/Query").mock(
        return_value=Response(200, json={"Success": True, "Error": None, "Data": {"Total": 0, "Items": []}})
    )
    await server.query_tasks(
        project_id=1, keyword="login bug", condition={"Status": [{"Id": 1, "Option": 2}]}
    )
    payload = json.loads(route.calls.last.request.content)
    assert payload["Condition"]["Keyword"] == "login bug"
    assert payload["Condition"]["Status"] == [{"Id": 1, "Option": 2}]


@respx.mock
async def test_get_subproject_tool_success(monkeypatch):
    monkeypatch.setenv("DEVTRACK_TOKEN", "test-token")
    respx.post(f"{BASE}/api/SubProject").mock(
        return_value=Response(
            200,
            json={"Success": True, "Error": None, "Data": {"SubProjectId": 2, "SubProjectName": "QA"}},
        )
    )
    result = await server.get_subproject(project_id=1, subproject_id=2)
    assert result == {"SubProjectId": 2, "SubProjectName": "QA"}


@respx.mock
async def test_list_subprojects_tool_defaults_to_root(monkeypatch):
    monkeypatch.setenv("DEVTRACK_TOKEN", "test-token")
    route = respx.post(f"{BASE}/api/SubProject/GetTree").mock(
        return_value=Response(
            200, json={"Success": True, "Error": None, "Data": {"SubProjectId": 0, "Children": []}}
        )
    )
    result = await server.list_subprojects(project_id=1)
    assert result == {"tree": {"SubProjectId": 0, "Children": []}}
    payload = json.loads(route.calls.last.request.content)
    assert payload["SubProjectId"] == 0
