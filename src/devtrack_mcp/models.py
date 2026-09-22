"""Request/response shapes for the DevTrack Task REST endpoints.

Field names mirror DevTrack's own API (ProjectId, TaskId, FieldValues, ...)
rather than being renamed to Python convention, so anyone cross-referencing
the DevTrack API Explorer (http://trydevsuite.techexcel.com/DevTrackAPI/Help)
can follow along directly.

NOTE: Task/Create, Task/Get and Task/Update schemas below were confirmed
against the live API Explorer. Task/Query's exact request shape could not
be fetched while scaffolding this project (the docs page timed out) -- the
TaskQueryBinder shape here is a reasonable inference from the other three
endpoints and DevTrack's documented query conventions. Verify and adjust
against http://trydevsuite.techexcel.com/DevTrackAPI/Help/Api/POST-api-Task-Query
once you have a working token, and update this docstring when confirmed.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class FieldValue(BaseModel):
    """One field's value, used in both create and update requests."""

    FieldId: int
    Option: int = 0
    FieldValue: Any = None


class TaskCreateRequest(BaseModel):
    ProjectId: int
    TemplateId: int
    FieldValues: list[FieldValue] = Field(default_factory=list)


class TaskGetRequest(BaseModel):
    ProjectId: int
    TaskId: int
    FieldIds: list[int] = Field(default_factory=list)


class TaskUpdateRequest(BaseModel):
    ProjectId: int
    TaskId: int
    TransitionId: int | None = None
    FieldValues: list[FieldValue] = Field(default_factory=list)


class QueryCondition(BaseModel):
    """A single filter condition, e.g. {"FieldId": 601, "Operator": "=", "Value": "Active"}."""

    FieldId: int
    Operator: str = "="
    Value: Any = None


class TaskQueryRequest(BaseModel):
    """Best-effort shape -- see module docstring. Confirm against live docs."""

    ProjectId: int
    Conditions: list[QueryCondition] = Field(default_factory=list)
    FieldIds: list[int] = Field(default_factory=list)
    PageIndex: int = 1
    PageSize: int = 25
