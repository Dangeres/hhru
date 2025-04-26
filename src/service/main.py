from datetime import datetime
from src.client.main import hhru_client
from src.service.schemas import BumpResult


class HHruService:
    def __init__(self):
        self.client = hhru_client

    async def bump_resume(self) -> BumpResult:
        """Бампим все резюме которые активны для поднятия в поиске"""

        result = BumpResult()

        print(self.client.tokens.hhtoken)

        for resume in await self.client.get_resumes():
            if resume.bump_at < int(datetime.now().timestamp()):
                result.need_to_bump.append(resume.href)

        for resume_href in result.need_to_bump:
            response = await self.client.bump_resume(resume_href=resume.href)

            if response:
                result.bumped.append(resume_href)

        return result
