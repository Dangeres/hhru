import asyncio
from datetime import datetime, timedelta
import hashlib

import aiofiles
from src.client.exceptions import InvalidCaptcha
from src.client.main import HHruClient
from src.client.schemas import Resume, Tokens, Vacancie
from src.config.main import config
from src.service.schemas import BumpResult


def log(text):
    print(text)


class HHruService:
    def __init__(self):
        self.client = HHruClient(
            tokens=None,
        )
        self.config = config
        self.resumes: list[Resume] = []

    def __hash_username(self) -> str:
        """Захешируем юзернейм что бы у него был id"""

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
                tokens = Tokens.model_validate_json(await file.read())

                return tokens
        except Exception as err:
            print(err)

        return None

    async def return_data_resume(self, resume_href: str) -> Resume | None:
        """Возвращает резюме из списка в кеше"""

        for resume in self.resumes:
            if resume.href == resume_href:
                return resume

        return None

    async def login(self) -> Tokens:
        """Функция для логина, имеет в себе получение токенов, сохранение их и прочее"""

        tokens = await self.get_tokens()

        if tokens is None:
            tokens = await self.client.get_tokens_anonymous()

            try:
                tokens = await self.client.login()
            except InvalidCaptcha as err:
                # captcha = await self.client.get_captcha()

                log(
                    self.client.build_url(
                        f"captcha/picture?key={err.captcha.hhcaptcha.captchaKey}"
                    )
                )

                raise err

            # TODO если тут ошибка, давай перезапросим токены начиная с анонимных и сделаем авторизацию по новой

        await self.client.set_tokens(tokens=tokens)

        await self.save_tokens(tokens=tokens)

        return tokens

    async def bump_resume(self) -> BumpResult:
        """Бампим все резюме которые активны для поднятия в поиске"""

        result = BumpResult()

        for resume in await self.client.get_resumes():
            if resume.bump_at < int(datetime.now().timestamp()):
                result.need_to_bump.append(resume.href)

        for resume_href in result.need_to_bump:
            response = await self.client.bump_resume(resume_href=resume.href)

            if response:
                result.bumped.append(resume_href)

        return result

    async def idle_resume_bump(self):
        log(f"{self.idle_resume_bump.__name__} flag {self.config.bump_resume=}")

        while self.config.bump_resume:
            log(f"{self.idle_resume_bump.__name__}")

            resumes = await self.client.get_resumes()

            log(f"{self.idle_resume_bump.__name__} get resume {resumes}")

            for resume in resumes:
                if resume.bump_at < int(datetime.now().timestamp()):
                    result = await self.client.bump_resume(resume_href=resume.href)

                    log(f"{self.idle_resume_bump.__name__} bumped {resume=} {result=}")

            resumes = await self.client.get_resumes()

            minimal_time = int((datetime.now() + timedelta(days=1)).timestamp())

            for resumt in resumes:
                if resume.bump_at < minimal_time:
                    minimal_time = resume.bump_at

            sleep_time = minimal_time - int(datetime.now().timestamp())

            log(f"{self.idle_resume_bump.__name__} sleep {sleep_time} seconds")

            await asyncio.sleep(sleep_time)

    async def idle_vacancy_apply(self):
        log(f"{self.idle_vacancy_apply.__name__} flag {self.config.apply_vacancy=}")

        while self.config.apply_vacancy:
            log(f"{self.idle_vacancy_apply.__name__}")

            for search in self.config.search:
                response = await self.client.search_vacancy(search.params)
                raw_vacancy = response.vacancySearchResult.vacancies

                vacancy: list[Vacancie] = []

                for vac in raw_vacancy:
                    if vac.company.id in self.config.black_list_company:
                        continue

                    if vac.userTestId is not None:
                        continue

                    if len(vac.userLabels) > 0:
                        continue

                    vacancy.append(vac)

                print(vacancy)

                for vac in vacancy:
                    result = await self.client.apply_vacancy(
                        vacancy_id=vac.vacancyId,
                        resume_href=search.resume_href,
                        letter=search.letter,
                    )
                    # TODO

                    log(f"<{result}> [{vac.company.name}]: {vac.name}")

            await asyncio.sleep(self.config.vacancy_find_delay)

    async def run(self):
        await self.login()

        await asyncio.gather(
            self.idle_resume_bump(),
            self.idle_vacancy_apply(),
        )
