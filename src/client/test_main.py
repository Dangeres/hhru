from http.cookies import SimpleCookie
import pytest
from unittest.mock import AsyncMock, patch
from src.client.main import HHruClient
from src.client.schemas import MethodEnum, Resume, Tokens
from src.config.main import Config

path = "src.client"


@pytest.fixture
def mock_config():
    with patch("src.config.main.config") as ptch:
        ptch.return_value = Config(
            url="https://hh.ru",
            verify_ssl=True,
            proxy=None,
            folder_tokens="./tokens",
            username="test_user",
            password="test_password",
            black_list_company=[],
            black_words=[],
        )

        yield ptch


@pytest.fixture
def hh_instance(mock_config) -> HHruClient:
    client = HHruClient(
        tokens=Tokens(
            xsrf="mocked_xsrf_token",
            hhtoken="mocked_hhtoken",
        ),
    )

    return client


@pytest.fixture
def mock_request():
    with patch(f"{path}.main.HHruClient._request") as request:
        mock = AsyncMock()

        mock.cookies = SimpleCookie(
            {
                "_xsrf": "test_xsrf_token",
                "hhtoken": "test_hhtoken",
            }
        )

        mock.status_code = 200

        request.return_value = mock

        yield mock


@pytest.mark.asyncio
@patch(f"{path}.main.aiosonic.HTTPClient")
async def test_request(mock_http_client, hh_instance):
    """Тестирование метода _request."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_http_client.return_value.__aenter__.return_value.get.return_value = (
        mock_response
    )

    response = await hh_instance._request(MethodEnum.get, "/test-path")

    assert response.status_code == 200
    mock_http_client.assert_called_once()


@pytest.mark.asyncio
async def test_get_tokens_anonymous(mock_request, hh_instance):
    """Тестирование метода _get_cookie_anonymous."""

    tokens = await hh_instance.get_tokens_anonymous()

    assert tokens.xsrf == "test_xsrf_token"
    assert tokens.hhtoken == "test_hhtoken"


@pytest.mark.asyncio
async def test_set_tokens(mock_request, hh_instance):
    """Тестирование метода _get_cookie_anonymous."""

    assert hh_instance.tokens.xsrf == "mocked_xsrf_token"
    assert hh_instance.tokens.hhtoken == "mocked_hhtoken"

    await hh_instance.set_tokens(
        tokens=Tokens(
            xsrf="new_xsrf_token",
            hhtoken="new_hhtoken",
        ),
    )

    assert hh_instance.tokens.xsrf == "new_xsrf_token"
    assert hh_instance.tokens.hhtoken == "new_hhtoken"


@pytest.mark.asyncio
async def test_login(mock_request, hh_instance):
    """Тестирование метода login."""

    tokens = await hh_instance.login()

    assert tokens.xsrf == "test_xsrf_token"
    assert tokens.hhtoken == "test_hhtoken"


@pytest.mark.asyncio
async def test_bump_resume(mock_request, hh_instance):
    """Тестирование метода bump_resume."""

    hh_instance.resume = [
        Resume(
            title="test",
            href="resume_id",
            updated=0,
            bump_at=0,
        )
    ]

    result = await hh_instance.bump_resume("resume_id")

    assert result is True


@pytest.mark.asyncio
async def test_get_resumes(mock_request, hh_instance):
    """Тестирование метода get_resumes."""
    mock_request.text.return_value = """
    <html>
        <noindex>
            <template>
                {"applicantResumes": [{"title": [{"string": "Test Resume"}], "_attributes": {"hash": "resume_id", "updated": 1745662140000, "update_timeout": 14400000}}]}
            </template>
        </noindex>
    </html>
    """

    resumes = await hh_instance.get_resumes()

    assert len(resumes) == 1
    assert resumes[0].title == "Test Resume"
    assert resumes[0].href == "resume_id"
    assert resumes[0].updated == 1745662140
    assert resumes[0].bump_at == 1745662140 + 14400


@pytest.mark.asyncio
async def test_search_vacancy(mock_request, hh_instance):
    """Тестирование метода search_vacancy."""
    mock_request.json.return_value = {
        "searchClustersOrder": {
            "work_schedule_by_days": ["fullDay"],
            "employment_form": ["full"],
            "work_format": ["office"],
            "experience": ["noExperience"],
            "industry": ["IT"],
            "area": ["Moscow"],
            "professional_role": ["developer"],
            "education": ["higher"],
            "working_hours": ["day"],
            "label": ["new"],
            "search_field": ["name"],
            "excluded_text": ["spam"],
            "resume": ["resume_id"],
        },
        "searchCounts": {
            "isLoad": True,
            "value": 100,
            "usedResumeId": 12345,
            "isSuitableSearch": True,
        },
        "vacancySearchResult": {
            "savedSearches": {
                "isSavedSearch": False,
                "email": "",
                "isFormOpen": False,
                "isShowButton": False,
                "position": 0,
            },
            "criteria": {
                "page": 1,
                "limit": 20,
                "offset": 0,
                "clusters": True,
                "currency_code": "RUR",
                "search_debug": False,
                "control_flag": [],
                "saved_search_id": None,
                "search_session_id": "session_123",
                "vacancy_id": None,
                "resume": "resume_id",
                "no_magic": False,
                "ored_clusters": True,
                "cache_ttl_sec": None,
                "text": "Python developer",
                "date_from": None,
                "date_to": None,
                "items_on_page": 20,
                "order_by": "relevance",
                "search_field": ["name"],
                "enable_snippets": True,
                "only_with_salary": False,
                "is_part_time_clusters_enabled": False,
                "exclude_archived": True,
                "exclude_closed": True,
                "search_period": None,
                "salary": None,
                "bottom_left_lat": None,
                "bottom_left_lng": None,
                "top_right_lat": None,
                "top_right_lng": None,
                "sort_point_lat": None,
                "sort_point_lng": None,
                "employer_id": None,
                "excluded_employer_id": None,
                "employer_manager_id": None,
                "precision": None,
                "geocode_type": None,
                "geohash": None,
                "recommended_by_uid": False,
                "excluded_text": "",
                "accept_temporary": None,
                "use_relations_for_similar": None,
            },
            "totalUsedFilters": 5,
            "vacancies": [
                {
                    "vacancyId": 1,
                    "name": "Python Developer",
                    "type": "open",
                    "acceptTemporary": False,
                    "metallic": "silver",
                    "creationSite": "hh.ru",
                    "creationSiteId": 1,
                    "displayHost": "hh.ru",
                    "creationTime": "2023-10-01T12:00:00Z",
                    "canBeShared": True,
                    "inboxPossibility": True,
                    "chatWritePossibility": "allowed",
                    "notify": True,
                    "acceptIncompleteResumes": False,
                    "workExperience": "between3And6",
                    "closedForApplicants": False,
                    "userTestPresent": False,
                    "employmentForm": "full",
                    "internship": False,
                    "nightShifts": False,
                    "contactInfo": None,
                    "responsesCount": 10,
                    "totalResponsesCount": 15,
                    "show_question_input": True,
                    "allowChatWithManager": True,
                    "searchRid": "rid_123",
                }
            ],
            "hasVacanciesWithAddress": True,
            "isClustersEnabled": True,
            "totalResults": 100,
            "enableSimilarSavedSearch": False,
            "showSwipeTeaser": False,
            "proxiedSearchFormParams": {
                "search_session_id": "session_123",
                "resume": "resume_id",
                "ored_clusters": True,
                "text": "Python developer",
                "enable_snippets": True,
                "excluded_text": "",
            },
            "vacancyHint": None,
        },
    }

    params = {"text": "Python Developer"}
    result = await hh_instance.search_vacancy(params)

    assert len(result.vacancySearchResult.vacancies) == 1
    assert result.vacancySearchResult.vacancies[0].name == "Python Developer"
    assert result.vacancySearchResult.vacancies[0].vacancyId == 1
