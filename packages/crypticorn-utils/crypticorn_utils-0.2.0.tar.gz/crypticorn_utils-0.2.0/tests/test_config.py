import pytest
import pytest_asyncio
from crypticorn import AsyncClient
from crypticorn_utils.enums import BaseUrl
from crypticorn_utils.auth import apikey_header
from crypticorn.hive import Configuration as HiveConfig
from crypticorn_utils._migration import has_migrated


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(base_url=BaseUrl.LOCAL, api_key="test") as client:
        yield client


@pytest.mark.asyncio
async def test_client_config(client: AsyncClient):
    client.configure(config=HiveConfig(host="something"), service='hive-v1' if has_migrated else 'hive')
    assert client.hive.config.host == "something"  # overriden
    assert client.hive.config.api_key == {
        apikey_header.scheme_name: "test"
    }  # not overriden
