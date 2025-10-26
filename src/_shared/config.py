from typing import Optional

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class DBConfig(BaseModel):
    host: str
    port: int
    password: str
    username: str
    dbname: str


class TestConfig(BaseModel):
    username: str
    password: str


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="--", env_file=(".env", ".env.prod")
    )

    test: Optional[TestConfig]
    db: DBConfig

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings, env_settings, dotenv_settings, file_secret_settings)


def get_settings():
    return Settings()  # type: ignore
