from pydantic import BaseModel, Field


class BumpResult(BaseModel):
    need_to_bump: list[str] = Field(default=[])
    bumped: list[str] = Field(default=[])
