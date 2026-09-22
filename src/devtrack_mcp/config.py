"""Configuration for the DevTrack MCP server.

All settings come from environment variables (optionally loaded from a
.env file), so the same code can point at TechExcel's public sandbox
today and a real DevTrack instance later just by changing env vars --
no code changes needed.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# TechExcel's public trydevsuite sandbox. Used as the default base URL so
# the server works out of the box for demos/portfolio use without a real
# DevTrack instance. Point DEVTRACK_BASE_URL at a real instance (e.g. a GA
# DevTrack server) to use this against production data.
DEFAULT_BASE_URL = "http://trydevsuite.techexcel.com/DevTrackAPI"


@dataclass(frozen=True)
class DevTrackConfig:
    base_url: str
    token: str | None
    language_id: int

    @classmethod
    def from_env(cls) -> DevTrackConfig:
        base_url = os.environ.get("DEVTRACK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        token = os.environ.get("DEVTRACK_TOKEN") or None
        language_id = int(os.environ.get("DEVTRACK_LANGUAGE_ID", "1"))
        return cls(base_url=base_url, token=token, language_id=language_id)
