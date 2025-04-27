import datetime
from unittest.mock import AsyncMock
import pytest

from src.client.main import HHruClient
from src.client.schemas import Resume
from src.config.main import Config
from src.service.main import HHruService
from src.service.schemas import BumpResult


@pytest.fixture
def mock_config() -> Config:
    return Config(
        url="https://hh.ru",
        verify_ssl=True,
        proxy=None,
        folder_tokens="./tokens",
        username="test_user",
        password="test_password",
        black_list_company=[],
        black_words=[],
    )


@pytest.fixture
def mock_hh_client(mock_config):
    client = AsyncMock(spec=HHruClient(mock_config))

    client.get_resumes.return_value = [
        Resume(
            title="Test1",
            href="1",
            updated=int((datetime.datetime.now() + datetime.timedelta(days=-1)).timestamp()),
            bump_at=int((datetime.datetime.now() + datetime.timedelta(days=-1, hours=4)).timestamp()),
        ), Resume(
            title="Test1",
            href="1",
            updated=int((datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()),
            bump_at=int((datetime.datetime.now() + datetime.timedelta(days=1, hours=4)).timestamp()),
        )
    ]

    client.bump_resume.return_value = True

    yield client


@pytest.fixture
def mock_hhservice(mock_hh_client):
    service = HHruService()
    service.client = mock_hh_client
    yield service


@pytest.mark.asyncio
async def test_bump(mock_hhservice):
    result = await mock_hhservice.bump_resume()

    assert result == BumpResult(need_to_bump=["1"], bumped=["1"])
