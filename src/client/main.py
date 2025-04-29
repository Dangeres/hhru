import json
import os
from urllib.parse import urljoin

import aiosonic
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from starlette import status

from src.client.exceptions import InvalidCaptcha
from src.client.schemas import Captcha, MethodEnum, Resume, SearchResponse, Tokens
from src.config.main import config


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

    async def _request(
        self,
        method: MethodEnum,
        path: str,
        headers: dict[str, str] | None = None,
        data: str | bytes = None,
        params: dict[str, str] | None = None,
    ) -> aiosonic.HttpResponse:
        """Сделаем запросы в сторону сайта"""

        url = self.build_url(path)

        async with aiosonic.HTTPClient(
            verify_ssl=self.config.verify_ssl,
            proxy=self.config.proxy,
        ) as session:
            match method:
                case MethodEnum.post:
                    result = await session.post(
                        url=url,
                        headers=headers,
                        data=data,
                        params=params,
                    )

                    return result

                case MethodEnum.get:
                    result = await session.get(
                        url=url,
                        headers=headers,
                        params=params,
                    )

                    return result

                case MethodEnum.head:
                    result = await session.post(
                        url=url,
                        headers=headers,
                        data=data,
                        params=params,
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

        xsrf = (
            response.cookies.get("_xsrf").value
            if response.cookies.get("_xsrf")
            else None
        )

        hhtoken = (
            response.cookies.get("hhtoken").value
            if response.cookies.get("hhtoken")
            else None
        )

        return Tokens(
            xsrf=xsrf,
            hhtoken=hhtoken,
        )

    # async def get_captcha(self): # TODO
    #     response = await self._request(method=MethodEnum.post, path="captcha")

    #     result = await response.json()

    #     return result

    async def _get_headers(self) -> dict[str, str]:
        """Получаем заголовки для запросов"""

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

        xsrf = (
            response.cookies.get("_xsrf").value
            if response.cookies.get("_xsrf")
            else None
        )

        hhtoken = (
            response.cookies.get("hhtoken").value
            if response.cookies.get("hhtoken")
            else None
        )

        try:
            tokens = Tokens(
                xsrf=xsrf,
                hhtoken=hhtoken,
            )
        except Exception as err:
            print(await response.text())
            raise err

        return tokens

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

    async def search_vacancy(self, params: dict[str, str]) -> SearchResponse:
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

        response = await response.json()

        result = SearchResponse.model_validate(response)

        return result
