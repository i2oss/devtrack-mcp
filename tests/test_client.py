import pytest
import respx
from httpx import Response

from devtrack_mcp.client import DevTrackAPIError, DevTrackClient

BASE = "http://trydevsuite.techexcel.com/DevTrackAPI"


@respx.mock
async def test_create_task_returns_new_id(client: DevTrackClient):
    respx.post(f"{BASE}/api/Task/Create").mock(
        return_value=Response(200, json={"Success": True, "Error": None, "Data": 42})
    )
    task_id = await client.create_task(
        project_id=1, template_id=1, field_values=[{"FieldId": 101, "FieldValue": "Title"}]
    )
    assert task_id == 42


@respx.mock
async def test_create_task_raises_on_devtrack_error(client: DevTrackClient):
    respx.post(f"{BASE}/api/Task/Create").mock(
        return_value=Response(
            200,
            json={
                "Success": False,
                "Error": {"ErrorCode": 7, "ErrorMessage": "Invalid TemplateId"},
                "Data": None,
            },
        )
    )
    with pytest.raises(DevTrackAPIError) as exc_info:
        await client.create_task(project_id=1, template_id=999)
    assert exc_info.value.error_code == 7
    assert "Invalid TemplateId" in str(exc_info.value)


@respx.mock
async def test_get_task_returns_data(client: DevTrackClient):
    respx.post(f"{BASE}/api/Task/Get").mock(
        return_value=Response(
            200,
            json={
                "Success": True,
                "Error": None,
                "Data": {"TaskId": 42, "IfClosed": 0, "Values": []},
            },
        )
    )
    result = await client.get_task(project_id=1, task_id=42)
    assert result["TaskId"] == 42
    assert result["IfClosed"] == 0


@respx.mock
async def test_update_task_returns_result(client: DevTrackClient):
    respx.post(f"{BASE}/api/Task/Update").mock(
        return_value=Response(
            200,
            json={
                "Success": True,
                "Error": None,
                "Data": {"Id": 42, "Success": True, "IfClosed": 1},
            },
        )
    )
    result = await client.update_task(project_id=1, task_id=42, transition_id=3)
    assert result["Id"] == 42
    assert result["IfClosed"] == 1


@respx.mock
async def test_query_tasks_returns_results(client: DevTrackClient):
    respx.post(f"{BASE}/api/Task/Query").mock(
        return_value=Response(
            200, json={"Success": True, "Error": None, "Data": {"Total": 1, "Items": [{"TaskId": 42}]}}
        )
    )
    result = await client.query_tasks(
        project_id=1, conditions=[{"FieldId": 601, "Operator": "=", "Value": "Active"}]
    )
    assert result["Total"] == 1
    assert result["Items"][0]["TaskId"] == 42


@respx.mock
async def test_http_error_raised_as_devtrack_error(client: DevTrackClient):
    respx.post(f"{BASE}/api/Task/Get").mock(return_value=Response(500))
    with pytest.raises(DevTrackAPIError, match="HTTP 500"):
        await client.get_task(project_id=1, task_id=1)
