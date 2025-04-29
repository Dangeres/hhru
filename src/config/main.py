from typing import Dict
from dynaconf import Dynaconf
from pydantic import BaseModel, Field


class Search(BaseModel):
    params: Dict = Field(description="Данные для поиска")
    resume_href: str = Field(description="Каким резюме откликаться")
    letter: str = Field(
        default="", description="Какое сопроводительное письмо пушить при отклике"
    )


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
    bump_resume: bool = Field(description="Нужно ли поднимать резюме в поиске")
    apply_vacancy: bool = Field(
        description="Нужно ли искать вакансии и откликаться на них"
    )
    vacancy_find_delay: int = Field(
        description="Задержка перед поиском и откликом на вакансии (секунды)"
    )
    search: list[Search] = Field(
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
