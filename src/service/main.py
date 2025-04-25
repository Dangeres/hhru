from datetime import datetime
import hashlib
import json
import os
from urllib.parse import urljoin

import aiosonic
import aiofiles
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from src.service.schemas import Config, MethodEnum, Resume, SearchResponse, Tokens


class HHru:
    def __init__(self, config: Config):
        """Получаем обьект который дальше делает магию"""

        self.user_agent = UserAgent().chrome
        self.tokens = None
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

    async def _get_cookie_anonymous(self) -> Tokens:
        """Получаем печеньки от анонима"""

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

        self.tokens = Tokens(
            xsrf=xsrf,
            hhtoken=hhtoken,
        )

        return self.tokens

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

    async def _get_request_data_resume_bump(self, resume: str = None) -> str:
        """Сгенерим все нужные данные для поднятия резюме"""

        return (
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="resume"\r\n\r\n{resume}\r\n'
            f"--{self.boundary}\r\nContent-Disposition: form-data; "
            f'name="undirectable"\r\n\r\ntrue\r\n'
            f"--{self.boundary}--\r\n"
        )

    def __hash_username(self) -> str:
        """Захешируем юзернейм что бы был id у него"""
        return hashlib.md5(self.config.username.encode("utf-8")).hexdigest()

    async def save_tokens(self, tokens: Tokens):
        """Сохраняем токен в файл что бы не делать миллион перелогинов"""
        async with aiofiles.open(
            f"{self.config.folder_tokens}/{self.__hash_username()}.json", "w+"
        ) as file:
            await file.write(tokens.model_dump_json())

    async def get_tokens(self) -> Tokens | None:
        """Получаем токен из файла"""

        try:
            async with aiofiles.open(
                f"{self.config.folder_tokens}/{self.__hash_username()}.json", "r+"
            ) as file:
                self.tokens = Tokens.model_validate_json(await file.read())

                return self.tokens
        except Exception as err:
            print(err)

        return None

    async def login(self) -> None:
        """Функция для авторизации аккаунта"""

        path = "login"

        tokens = await self.get_tokens()

        if not tokens:
            tokens = await self._get_cookie_anonymous()

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

        self.tokens = Tokens(
            xsrf=xsrf,
            hhtoken=hhtoken,
        )

        await self.save_tokens(tokens=self.tokens)

    async def bump_resume(self, resume: str) -> bool:
        """Поднять резюме в поиске для эйчаров"""

        path = "applicant/resumes/touch"

        for rsme in self.resume:
            if rsme.href == resume:
                if rsme.bump_at < int(datetime.now().timestamp()):
                    continue

                return False

        headers = await self._get_headers()

        data = await self._get_request_data_resume_bump(resume=resume)

        response = await self._request(
            method=MethodEnum.post,
            path=path,
            headers=headers,
            data=data,
        )

        return response.status_code == 200

    async def return_data_resume(self, resume_href: str) -> Resume | None:
        """Возвращает резюме из списка в кеше"""

        for resume in self.resume:
            if resume.href == resume_href:
                return resume

        return None

    async def get_resumes(self) -> list[Resume]:
        """Получить все резюме с залогиненого аккаунта"""

        path = "applicant/resumes"

        headers = await self._get_headers()
        response = await self._request(
            method=MethodEnum.get, path=path, headers=headers
        )

        if response.status_code == 200:
            soup = BeautifulSoup(await response.text(), "lxml")

            noindexes = soup.select("noindex>template")

            self.resume: list[Resume] = []

            resumes = json.loads(noindexes[-1].text)

            for resume in resumes.get("applicantResumes", []):
                title = resume.get("title")[0]["string"]
                link = resume.get("_attributes", {}).get("hash", "")
                updated = resume.get("_attributes", {}).get("updated", 0)

                self.resume.append(
                    Resume(
                        title=title,
                        href=link,
                        updated=updated,
                        bump_at=(
                            updated
                            + resume.get("_attributes", {}).get("update_timeout", 0)
                        ),
                    )
                )

        return self.resume

    async def search_vacancy(self, params: dict[str, str]) -> SearchResponse:
        """
        Функция поиска открытых вакансий на сайте hh.ru

        :param params: dict - запрос с поиском работы на сайт

        :returns: dict - результат выполнения запроса
        """

        path = "shards/vacancy/search"

        headers = await self._get_headers()
        response = await self._request(
            method=MethodEnum.get, path=path, headers=headers, params=params
        )
        response = await response.json()

        result = SearchResponse.model_validate(response)

        return result
