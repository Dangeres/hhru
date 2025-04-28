from datetime import datetime
import hashlib

import aiofiles
from src.client.main import HHruClient
from src.client.schemas import Resume, Tokens
from src.config.main import config
from src.service.schemas import BumpResult


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
        tokens = await self.get_tokens()

        if tokens is None:
            tokens = await self.client.get_tokens_anonymous()

        await self.client.set_tokens(tokens=tokens)

        tokens = await self.client.login()

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
