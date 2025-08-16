from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    host: str = "localhost"
    port: int | str = 5432
    name: str = ""
    password: Optional[str] = None
    username: Optional[str] = None
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        env_prefix="db_",
    )

    def get_url(self) -> str:
        return f"postgresql+psycopg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class Context:
    settings: Optional[PostgresSettings] = None


__ctx = Context()


def init_settings(root: Path):
    PostgresSettings.model_config.update(env_file=root / ".env")
    __ctx.settings = PostgresSettings()


def get_settings() -> PostgresSettings:
    if __ctx.settings is None:
        msg = "Settings are not initialized -- call init_settings()"
        raise Exception(msg)
    return __ctx.settings


if __name__ == "__main__":
    settings = PostgresSettings(port="443", name="fake")
    print(settings.port)
