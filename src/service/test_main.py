import datetime
from unittest.mock import AsyncMock, patch
import pytest

from src.client.schemas import Resume, Tokens
from src.config.main import Config
from src.service.main import HHruService
from src.service.schemas import BumpResult


@pytest.fixture
def mock_config():
    with patch("src.service.main.config") as ptch:
        cfg = Config(
            url="https://hh.ru",
            verify_ssl=True,
            proxy=None,
            folder_tokens="./tokens",
            username="test_user",
            password="test_password",
            black_list_company=[],
            bump_resume=True,
            vacancy_find_delay=14400,
            search=[],
        )

        ptch.return_value = cfg

        yield cfg


@pytest.fixture
def mock_tokens() -> Tokens:
    return Tokens(
        xsrf="real_xsrf",
        hhtoken="real_hhtoken",
    )


@pytest.fixture
def mock_hh_client(mock_config, mock_tokens):
    with patch("src.service.main.HHruClient") as MockedClient:
        client = AsyncMock()

        client.tokens.return_value = mock_tokens

        client.get_resumes.return_value = [
            Resume(
                title="Test1",
                href="1",
                updated=int(
                    (datetime.datetime.now() + datetime.timedelta(days=-1)).timestamp()
                ),
                bump_at=int(
                    (
                        datetime.datetime.now() + datetime.timedelta(days=-1, hours=4)
                    ).timestamp()
                ),
            ),
            Resume(
                title="Test1",
                href="1",
                updated=int(
                    (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()
                ),
                bump_at=int(
                    (
                        datetime.datetime.now() + datetime.timedelta(days=1, hours=4)
                    ).timestamp()
                ),
            ),
        ]

        client.bump_resume.return_value = True

        client.get_tokens_anonymous.return_value = Tokens(
            xsrf="anon_xsrf_token",
            hhtoken="anon_hhtoken",
        )

        # Мокаем метод login
        client.login.return_value = Tokens(
            xsrf="login_xsrf_token",
            hhtoken="login_hhtoken",
        )

        MockedClient.return_value = client

        yield client


@pytest.fixture
def mock_hhservice(mock_hh_client, mock_config, mock_tokens):
    service = HHruService()

    get_tokens_mock = AsyncMock()
    get_tokens_mock.return_value = mock_tokens

    save_tokens_mock = AsyncMock()
    save_tokens_mock.return_value = None

    service.config = mock_config
    service.client = mock_hh_client

    service.get_tokens = get_tokens_mock
    service.save_tokens = save_tokens_mock

    return service


@pytest.mark.asyncio
async def test_login(mock_hhservice, mock_hh_client):
    tokens = await mock_hhservice.login()

    # Проверяем, что set_tokens был вызван с новыми токенами
    mock_hh_client.set_tokens.assert_called_with(
        tokens=Tokens(xsrf="real_xsrf", hhtoken="real_hhtoken")
    )

    assert tokens == Tokens(
        xsrf="real_xsrf",
        hhtoken="real_hhtoken",
    )


@pytest.mark.asyncio
async def test_bump(mock_hhservice):
    result = await mock_hhservice.bump_resume()

    assert result == BumpResult(need_to_bump=["1"], bumped=["1"])
