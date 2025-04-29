from typing import Dict
from dynaconf import Dynaconf
from pydantic import BaseModel, Field


class Config(BaseModel):
    username: str = Field(description="Логин авторизации")
    password: str = Field(description="Пароль авторизации")
    folder_tokens: str = Field(description="Токены сессии")
    url: str = Field(description="Урлина сайта hh")
    verify_ssl: bool = Field(description="SSL")
    proxy: Dict[str, str] | None = Field(description="Прокся для запросов")
    black_list_company: list[int] = Field(
        description="Черный список компаний, все вакансии будут скипаться"
    )
    black_words: list[str] = Field(description="Черные слова для поиска вакансий")
    bump_resume: bool = Field(description="Нужно ли поднимать резюме в поиске")
    vacancy_find_delay: int = Field(
        description="Задержка перед поиском и откликом на вакансии (секунды)"
    )
    params_search: dict = Field(
        description="Параметры для поиска вакансии",
    )


def init_config() -> Config:
    settings = Dynaconf(
        settings_files=["settings.yaml"],
        environments=True,
        merge_enabled=True,
        default_env="default",
        env_switcher="hh_env",
        envvar_prefix="hh",
        lowercase_read=True,
    )

    settings = {key.lower(): value for key, value in settings.to_dict().items()}

    config = Config(**settings)

    return config


config = init_config()
