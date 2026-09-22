# devtrack-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes [TechExcel
DevTrack](https://techexcel.com/products/devtrack/) issue/task operations as
tools an AI assistant (Claude, or any other MCP client) can call directly.

Part of a series of MCP portfolio projects — see also
[s1000d-mcp](https://github.com/i2oss/s1000d-mcp).

## What it does (v1)

Four core tools, backed by DevTrack's REST API:

| Tool | DevTrack endpoint | Purpose |
|---|---|---|
| `create_task` | `POST /api/Task/Create` | File a new task/issue |
| `get_task` | `POST /api/Task/Get` | Fetch a task's fields, comments, time tracking |
| `update_task` | `POST /api/Task/Update` | Edit fields and/or move a task through a workflow transition |
| `query_tasks` | `POST /api/Task/Query` | Search tasks in a project by filter conditions |

Project/subproject browsing, reporting tools (sprint scores, work
summaries), and a SKILL.md that chains these into a workflow (e.g.
triaging a batch of new issues) are backlog for v2 — same "core first,
then expand" approach as the S1000D MCP project.

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
schemas were confirmed against the live [API
Explorer](http://trydevsuite.techexcel.com/DevTrackAPI/Help). The
`Task/Query` docs page timed out while this project was being scaffolded,
so `TaskQueryRequest` in `models.py` is a best-effort inference from the
other three endpoints' conventions. If you hit a schema mismatch there,
check the live Explorer and update `models.py` + `client.py` — that's
first on the backlog.

## License

MIT
