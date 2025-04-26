import asyncio

from src.client.main import hhru_client


async def main():
    await hhru_client.login()

    print(
        await hhru_client.search_vacancy(
            {
                "ored_clusters": True,
                "enable_snippets": True,
                "hhtmFrom": "vacancy_search_list",
                "hhtmFromLabel": "vacancy_search_line",
                "excluded_text": "django,node js",
                "resume": "dd41fba3ff0c4a4ee60039ed1f5a56586a576e",
                "search_field": "name",
                "text": "python senior",
                "forceFiltersSaving": True,
            }
        )
    )

    resumes = await hhru_client.get_resumes()
    print(resumes)
    res = await hhru_client.bump_resume(resume_href=resumes[0].href)
    print(res)


if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(main())
