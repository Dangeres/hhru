from enum import Enum
import string
from typing import Dict
from pydantic import BaseModel, Field


class Resume(BaseModel):
    title: str = Field(description="Название резюме")
    href: str = Field(description="Токен для ссылки на резюме")
    updated: int = Field(description="Время последнего поднятия")
    bump_at: int = Field(description="Когда нужно его поднять в поиске")


class MethodEnum(Enum):
    head = "head"
    post = "post"
    get = "get"


class Tokens(BaseModel):
    xsrf: str = Field()
    hhtoken: str = Field()


class Config(BaseModel):
    username: str = Field(description="Логин авторизации")
    password: str = Field(description="Пароль авторизации")
    folder_tokens: str = Field(default="tokens", description="Токены сессии")
    url: str = Field(default=str("https://hh.ru/"), description="Урлина сайта hh")
    count_requests: int = Field(
        default=10,
        description="Количество попыток сделать запрос",
    )
    verify_ssl: bool = Field(default=False)
    proxy: Dict[str, str] | None = Field(default=None)
