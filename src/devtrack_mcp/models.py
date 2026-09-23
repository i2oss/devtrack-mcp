"""Request/response shapes for the DevTrack Task REST endpoints.

Field names mirror DevTrack's own API (ProjectId, TaskId, FieldValues, ...)
rather than being renamed to Python convention, so anyone cross-referencing
the DevTrack API Explorer (http://trydevsuite.techexcel.com/DevTrackAPI/Help)
can follow along directly.

NOTE on Task/Query: the API Explorer's own page for this endpoint
(.../Help/Api/POST-api-Task-Query) has been unreachable while building this
project -- it repeatedly fails to load (robots.txt fetch timing out) even
though sibling endpoints load fine. The shape below is NOT a guess, though:
it's assembled from two confirmed sibling endpoints in the same "get tasks
by query condition" family --
.../Help/Api/POST-api-Task-GetTaskListSummary and
.../Help/Api/POST-api-Task-GroupedTaskListByOwner -- both of which take an
identical ProjectId + Condition(StandardQueryCondition) + FieldIds +
PageIndex/PageSize envelope and share the exact "Get Tasks base on query
condition" description DevTrack uses for Task/Query itself. High confidence,
but still worth a final check against Task/Query's own page directly once
it loads, or against a real token's behavior.
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


# -- Task/Query's condition family -------------------------------------
# Confirmed shape (see module docstring), shared by Task/Query,
# Task/GetTaskListSummary and Task/GroupedTaskListByOwner.


class SubprojectFilter(BaseModel):
    SubIds: list[int] = Field(default_factory=list)
    IncludeChildren: bool = True
    IncludeClosed: bool = False
    IncludeBacklog: bool = True


class IdOption(BaseModel):
    """Shape used for both Status and Owner filter entries."""

    Id: int
    Option: int = 0


class DateTimeFieldQuery(BaseModel):
    FieldId: int
    From: str | None = None
    To: str | None = None


class NumericFieldQuery(BaseModel):
    FieldId: int
    From: float | None = None
    To: float | None = None
    Values: list[float] = Field(default_factory=list)
    OperationType: int | None = None


class TextFieldQuery(BaseModel):
    FieldId: int
    Word: str
    NotInclude: bool = False


class DropdownFieldQuery(BaseModel):
    FieldId: int
    ChoiceIds: list[int] = Field(default_factory=list)
    NotInclude: bool = False


class StandardQueryCondition(BaseModel):
    """DevTrack's shared task-filter object.

    Everything is optional -- an empty condition matches all tasks in the
    project (subject to PageIndex/PageSize).
    """

    TaskId: str | None = None
    StoryId: str | None = None
    Keyword: str | None = None
    Subproject: SubprojectFilter | None = None
    Status: list[IdOption] = Field(default_factory=list)
    Owner: list[IdOption] = Field(default_factory=list)
    IssueType: list[int] = Field(default_factory=list)
    DateTimeFields: list[DateTimeFieldQuery] = Field(default_factory=list)
    NumericFields: list[NumericFieldQuery] = Field(default_factory=list)
    TextFields: list[TextFieldQuery] = Field(default_factory=list)
    DropdownFields: list[DropdownFieldQuery] = Field(default_factory=list)
    DefinedQueryId: int | None = None


class TaskQueryRequest(BaseModel):
    ProjectId: int
    Condition: StandardQueryCondition = Field(default_factory=StandardQueryCondition)
    FieldIds: list[int] = Field(default_factory=list)
    PageIndex: int = 1
    PageSize: int = 25


# -- SubProject endpoints ------------------------------------------------
# SubProjectRequest / SubProjectInfoModel confirmed against the live API
# Explorer (.../Help/Api/POST-api-SubProject). SubProject/GetTree's own
# docs page has been unreachable (same intermittent-page issue as
# Task/Query) -- GetTreeRequest below reuses the confirmed
# ProjectId+SubProjectId binder shape (GetTree's one-line description,
# "Get the SubProject and its child SubProjects based on SubProject ID",
# is nearly identical to the confirmed single-SubProject endpoint's), and
# the tree's node shape is assumed to extend SubProjectInfoModel with a
# Children list -- standard DevTrack/REST tree convention, but NOT
# independently confirmed. Verify against a live token before relying on
# the nesting shape specifically.
#
# Note: DevTrack's classic REST API has no confirmed "list all projects"
# endpoint -- every endpoint takes a ProjectId you already have (typically
# read off the DevTrack web UI/URL). The only lead for project enumeration
# is the separate "Project One" family (api/projectone/P1Projects), whose
# docs page has also been unreachable and whose relationship to the
# classic Task/SubProject endpoints used elsewhere in this client is
# unconfirmed -- left as backlog rather than guessed at.


class SubProjectRequest(BaseModel):
    ProjectId: int
    SubProjectId: int = 0
    """0 means "root" when used for SubProject/GetTree; a real SubProject/Get
    call needs a genuine SubProjectId."""
