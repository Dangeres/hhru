import json
import os
from urllib.parse import urljoin

import aiosonic
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from src.client.schemas import MethodEnum, Resume, SearchResponse, Tokens
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

    async def _request(
        self,
        method: MethodEnum,
        path: str,
        headers: dict[str, str] | None = None,
        data: str | bytes = None,
        params: dict[str, str] | None = None,
    ) -> aiosonic.HttpResponse:
        """Сделаем запросы в сторону сайта"""

        url = urljoin(self.config.url, path)

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

    async def _get_headers(self) -> dict[str, str]:
        """Получаем заголовки для запросов"""

        return {
            "content-type": f"multipart/form-data; boundary={self.boundary}",
            "cookie": f"_xsrf={self.tokens.xsrf}; hhtoken={self.tokens.hhtoken};",
            "user-agent": self.user_agent,
            "x-xsrftoken": f"{self.tokens.xsrf}",
        }

    async def _get_request_data(self) -> str:
        """Сгенерим все нужные заголовки и хедеры"""

        return (
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="_xsrf"\r\n\r\n{self.tokens.xsrf}\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="backUrl"\r\n\r\nhttps://hh.ru/\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="failUrl"\r\n\r\n/account/login\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="remember"\r\n\r\nyes\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="username"\r\n\r\n{self.config.username}\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="password"\r\n\r\n{self.config.password}\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="username"\r\n\r\n{self.config.username}\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="isBot"\r\n\r\nfalse\r\n--{self.boundary}--\r\n'
        )

    async def _get_request_data_resume_bump(self, resume_href: str = None) -> str:
        """Сгенерим все нужные данные для поднятия резюме"""

        return (
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="resume"\r\n\r\n{resume_href}\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="undirectable"\r\n\r\ntrue\r\n'
            f"--{self.boundary}--\r\n"
        )

    async def login(self) -> Tokens:
        """Функция для авторизации аккаунта"""

        path = "login"

        headers = await self._get_headers()
        data = await self._get_request_data()

        response = await self._request(
            method=MethodEnum.post,
            path=path,
            headers=headers,
            data=data,
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

    async def bump_resume(self, resume_href: str) -> bool:
        """Поднять резюме в поиске для эйчаров"""

        path = "applicant/resumes/touch"

        headers = await self._get_headers()

        data = await self._get_request_data_resume_bump(resume_href=resume_href)

        response = await self._request(
            method=MethodEnum.post,
            path=path,
            headers=headers,
            data=data,
        )

        return response.status_code == 200

    async def get_resumes(self) -> list[Resume]:
        """Получить все резюме с залогиненого аккаунта"""

        path = "applicant/resumes"

        headers = await self._get_headers()

        response = await self._request(
            method=MethodEnum.get, path=path, headers=headers
        )

        result = []

        if response.status_code == 200:
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
