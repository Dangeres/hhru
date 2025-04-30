import json
import os
from urllib.parse import urljoin, quote_plus

from aiosonic import HttpResponse, HTTPClient
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from starlette import status

from src.client.exceptions import InvalidCaptcha, TokenError
from src.client.schemas import Captcha, MethodEnum, Resume, SearchResponse, Tokens
from src.config.main import ParamsDict, config


class HHruClient:
    def __init__(self, tokens: Tokens | None):
        """Клиент с осуществлением запросов к hh.ru"""

        self.user_agent = UserAgent().chrome
        self.tokens = tokens
        self.config = config
        self.boundary = "boundary"
        self.resume: list[Resume] = []

        os.makedirs(self.config.folder_tokens, exist_ok=True)

    def build_url(self, path: str) -> str:
        return urljoin(self.config.url, path)

    def build_params(self, params: list[ParamsDict] | None) -> str:
        buffer = []

        for param in params or []:
            buffer.append(f"{param.key}={param.value}")

        if len(buffer) == 0:
            return ""

        result = quote_plus("&".join(buffer))

        return f"?{result}"

    async def _request(
        self,
        method: MethodEnum,
        path: str,
        headers: dict[str, str] | None = None,
        data: str | bytes | None = None,
        params: list[ParamsDict] | None = None,
    ) -> HttpResponse:
        """Сделаем запросы в сторону сайта"""

        prapared_params = self.build_params(params)

        url = self.build_url(f"{path}{prapared_params}")

        async with HTTPClient(
            verify_ssl=self.config.verify_ssl,
            proxy=self.config.proxy,
        ) as session:
            match method:
                case MethodEnum.post:
                    result = await session.post(
                        url=url,
                        headers=headers,
                        data=data,
                    )

                    return result

                case MethodEnum.get:
                    result = await session.get(
                        url=url,
                        headers=headers,
                    )

                    return result

                case MethodEnum.head:
                    result = await session.post(
                        url=url,
                        headers=headers,
                        data=data,
                    )

                    return result

                case _:
                    raise Exception(f"{MethodEnum.__name__} has no case")

    async def set_tokens(self, tokens: Tokens) -> Tokens:
        """Установить новые токены для запросов"""

        self.tokens = tokens

        return self.tokens

    async def get_tokens_anonymous(self) -> Tokens:
        """Получаем токены от анонима"""

        path = ""

        headers = {"user-agent": self.user_agent}

        response = await self._request(
            method=MethodEnum.head, path=path, headers=headers
        )

        xsrf = response.cookies.get("_xsrf")
        hhtoken = response.cookies.get("hhtoken")

        if not xsrf or not hhtoken:
            raise TokenError("Не смог найти токен")

        return Tokens(
            xsrf=xsrf.value,
            hhtoken=hhtoken.value,
        )

    # async def get_captcha(self): # TODO
    #     response = await self._request(method=MethodEnum.post, path="captcha")

    #     result = await response.json()

    #     return result

    async def _get_headers(self) -> dict[str, str]:
        """Получаем заголовки для запросов"""

        if not self.tokens:
            raise TokenError("Не смог найти токены для генерации заголовков")

        return {
            "content-type": f"multipart/form-data; boundary={self.boundary}",
            "cookie": f"_xsrf={self.tokens.xsrf}; hhtoken={self.tokens.hhtoken};",
            "user-agent": self.user_agent,
            "x-xsrftoken": f"{self.tokens.xsrf}",
        }

    async def generate_data(self, data: dict) -> str:
        result = []

        for key, value in data.items():
            result.append(
                (
                    f"--{self.boundary}\r\nContent-Disposition: form-data; "
                    f'name="{key}"\r\n\r\n{value}\r\n'
                )
            )

        return "".join(result)

    async def login(self) -> Tokens:
        """Функция для авторизации аккаунта"""

        path = "login"

        headers = await self._get_headers()
        data = await self.generate_data(
            data={
                "_xsrf": self.tokens.xsrf,
                "backUrl": "https://hh.ru/",
                "failUrl": "/account/login",
                "remember": "yes",
                "password": self.config.password,
                "username": self.config.username,
                "isBot": False,
            }
        )

        response = await self._request(
            method=MethodEnum.post,
            path=path,
            headers=headers,
            data=data,
        )

        resp = Captcha.model_validate(await response.json())

        if resp.hhcaptcha.isBot or resp.recaptcha.isBot:
            raise InvalidCaptcha(
                "На авторизации нужна капча",
                captcha=resp,
            )

        xsrf = response.cookies.get("_xsrf")
        hhtoken = response.cookies.get("hhtoken")

        if not xsrf or not hhtoken:
            print(await response.text())
            raise TokenError("Не смог найти токен")

        return Tokens(
            xsrf=xsrf.value,
            hhtoken=hhtoken.value,
        )

    async def apply_vacancy(
        self, vacancy_id: int, resume_href: str, letter: str
    ) -> int:
        headers = await self._get_headers()

        data = await self.generate_data(
            data={
                "_xsrf": self.tokens.xsrf,
                "vacancy_id": vacancy_id,
                "resume_hash": resume_href,
                "ignore_postponed": "true",
                "incomplete": "false",
                "letter": letter,
                "lux": "true",
                "withoutTest": "no",
                "hhtmFromLabel": "undefined",
                "hhtmSourceLabel": "undefined",
            }
        )

        response = await self._request(
            method=MethodEnum.post,
            path="applicant/vacancy_response/popup",
            headers=headers,
            data=data,
        )

        return response.status_code

    async def bump_resume(self, resume_href: str) -> bool:
        """Поднять резюме в поиске для эйчаров"""

        path = "applicant/resumes/touch"

        headers = await self._get_headers()

        data = await self.generate_data(
            data={
                "resume": resume_href,
                "undirectable": True,
            }
        )

        response = await self._request(
            method=MethodEnum.post,
            path=path,
            headers=headers,
            data=data,
        )

        return response.status_code == status.HTTP_200_OK

    async def get_resumes(self) -> list[Resume]:
        """Получить все резюме с залогиненого аккаунта"""

        path = "applicant/resumes"

        headers = await self._get_headers()

        response = await self._request(
            method=MethodEnum.get, path=path, headers=headers
        )

        result = []

        if response.status_code == status.HTTP_200_OK:
            soup = BeautifulSoup(await response.text(), "lxml")

            noindexes = soup.select("noindex>template")

            resumes = json.loads(noindexes[-1].text)

            for resume in resumes.get("applicantResumes", []):
                title = resume.get("title")[0]["string"]
                link = resume.get("_attributes", {}).get("hash", "")
                updated = resume.get("_attributes", {}).get("updated", 0)

                result.append(
                    Resume(
                        title=title,
                        href=link,
                        updated=updated // 1000,
                        bump_at=(
                            updated
                            + resume.get("_attributes", {}).get("update_timeout", 0)
                        )
                        // 1000,
                    )
                )

        return result

    async def search_vacancy(self, params: list[ParamsDict]) -> SearchResponse:
        """
        Функция поиска открытых вакансий на сайте hh.ru

        :param params: dict - запрос с поиском работы на сайт

        :returns: dict - результат выполнения запроса
        """

        path = "shards/vacancy/search"

        headers = await self._get_headers()

        response = await self._request(
            method=MethodEnum.get,
            path=path,
            headers=headers,
            params=params,
        )

        resp = await response.text()

        print(resp)

        response = await response.json()

        # print(response.get("vacancySearchResult", {}).get("vacancies", []))

        with open("search_vacancy_response.json", "w+") as f:
            json.dump(response, f, indent="  ")

        result = SearchResponse.model_validate(response)

        return result
