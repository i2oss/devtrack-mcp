import pytest

from devtrack_mcp.client import DevTrackClient
from devtrack_mcp.config import DevTrackConfig


@pytest.fixture
def config() -> DevTrackConfig:
    return DevTrackConfig(
        base_url="http://trydevsuite.techexcel.com/DevTrackAPI",
        token="test-token",
        language_id=1,
    )


@pytest.fixture
async def client(config: DevTrackConfig):
    c = DevTrackClient(config)
    yield c
    await c.aclose()
