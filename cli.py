import asyncio


from dynaconf import Dynaconf

from src.service.main import HHru
from src.service.schemas import Config


async def main():
    settings = Dynaconf(
        settings_files=["settings.yaml"],
        environments=True,
        merge_enabled=True,
        default_env='default',
        env_switcher='hh_env',
        envvar_prefix='hh',
        lowercase_read=True,
    )

    settings = {key.lower(): value for key, value in settings.to_dict().items()}

    config = Config(
        **settings
    )

    hh_service = HHru(config=config)

    await hh_service.login()

    print(
        await hh_service.search_vacancy(
            {
                "ored_clusters": True,
                "enable_snippets": True,
                "hhtmFrom": "vacancy_search_list",
                "hhtmFromLabel": "vacancy_search_line",
                "excluded_text": "django,node js",
                "resume": "dd41fba3ff0c4a4ee60039ed1f5a56586a576e",
                "search_field": "name",
                "search_field": "company_name",
                "search_field": "description",
                "text": "python senior",
                "forceFiltersSaving": True,
            }
        )
    )

    resumes = await hh_service.get_resumes()
    print(resumes)
    res = await hh_service.bump_resume(resume=resumes[0].href)
    print(res)


if __name__ == "__main__":
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(main())
