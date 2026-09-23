# devtrack-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes [TechExcel
DevTrack](https://techexcel.com/products/devtrack/) issue/task operations as
tools an AI assistant (Claude, or any other MCP client) can call directly.

Part of a series of MCP portfolio projects — see also
[s1000d-mcp](https://github.com/i2oss/s1000d-mcp).

## What it does (v1)

Six tools, backed by DevTrack's REST API:

| Tool | DevTrack endpoint | Purpose |
|---|---|---|
| `create_task` | `POST /api/Task/Create` | File a new task/issue |
| `get_task` | `POST /api/Task/Get` | Fetch a task's fields, comments, time tracking |
| `update_task` | `POST /api/Task/Update` | Edit fields and/or move a task through a workflow transition |
| `query_tasks` | `POST /api/Task/Query` | Search tasks in a project by filter conditions |
| `get_subproject` | `POST /api/SubProject` | Fetch a single subproject's info |
| `list_subprojects` | `POST /api/SubProject/GetTree` | Browse a project's subproject structure as a tree |

Reporting tools (sprint scores, work summaries) and a SKILL.md that
chains these into a workflow (e.g. triaging a batch of new issues) are
backlog for v2 — same "core first, then expand" approach as the S1000D
MCP project.

`query_tasks` takes a simple `keyword` for free-text search, or a full
DevTrack `condition` dict (status, owner, date ranges, custom fields —
DevTrack's `StandardQueryCondition` shape) for anything more targeted.

**Note:** there's no `list_projects` tool. DevTrack's classic REST API
has no confirmed endpoint for enumerating all projects a token can
access — every endpoint here takes a `ProjectId` you already have
(typically read off the DevTrack web UI's URL). A separate "Project One"
family (`api/projectone/P1Projects`) looks like it might cover this, but
its docs page — like `Task/Query`'s before it — has been unreachable
while building this, and its relationship to the classic endpoints used
here is unconfirmed. Left as backlog rather than guessed at.

## Why it points at a public sandbox by default

This server ships configured against TechExcel's public
`trydevsuite.techexcel.com` sandbox, so it's runnable and demoable without
needing a real DevTrack license or admin-issued token. Point it at a real
instance — including a GA-internal one — by setting `DEVTRACK_BASE_URL` and
`DEVTRACK_TOKEN`; no code changes required. See [Configuration](#configuration).

## Install

```bash
git clone https://github.com/i2oss/devtrack-mcp.git
cd devtrack-mcp
pip install -e ".[dev]"
```

## Configuration

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Default | Notes |
|---|---|---|
| `DEVTRACK_BASE_URL` | `http://trydevsuite.techexcel.com/DevTrackAPI` | Base URL of the DevTrack REST API. Point this at a real instance to use real data. |
| `DEVTRACK_TOKEN` | *(unset)* | User token from a DevTrack admin. Required for any authenticated instance. |
| `DEVTRACK_LANGUAGE_ID` | `1` | 1=English, 2=Chinese, 3=Japanese. |

## Running

```bash
devtrack-mcp
```

Or add it to a Claude Desktop / Claude Code MCP config:

```json
{
  "mcpServers": {
    "devtrack": {
      "command": "devtrack-mcp",
      "env": {
        "DEVTRACK_BASE_URL": "http://trydevsuite.techexcel.com/DevTrackAPI",
        "DEVTRACK_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Development

```bash
pytest        # run tests (HTTP calls are mocked, no live DevTrack needed)
ruff check .  # lint
```

## A note on the Task/Query request shape

DevTrack's `Task/Create`, `Task/Get` and `Task/Update` request/response
schemas were confirmed directly against the live [API
Explorer](http://trydevsuite.techexcel.com/DevTrackAPI/Help). `Task/Query`'s
own docs page has been consistently unreachable (fails to load even on
repeated tries, while every other endpoint's page loads fine) — but its
request shape is now backed by two *confirmed* sibling endpoints in the
same "get tasks by query condition" family, `Task/GetTaskListSummary` and
`Task/GroupedTaskListByOwner`, which share Task/Query's exact API
description and both take an identical `ProjectId` + `Condition`
(DevTrack's `StandardQueryCondition`) + `FieldIds` + `PageIndex`/`PageSize`
envelope. `models.py` implements that confirmed `StandardQueryCondition`
shape (keyword, status, owner, issue type, date/numeric/text/dropdown
field filters). High confidence, but still worth a final check against a
real token or Task/Query's own page directly if you hit a mismatch.

`SubProject/GetTree`'s docs page has the same unreachable-page issue.
Its request binder is confirmed (reused from the plain `SubProject`
endpoint, which does load), but the tree response's exact nesting shape
under `Children` is inferred, not independently confirmed.

## License

MIT
