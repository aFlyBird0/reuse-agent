from pydantic import BaseSettings, Field
from functools import lru_cache


class CustomBaseSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class LLMSettings(CustomBaseSettings):
    api_base: str = Field(env="OPENAI_API_BASE", default="https://api.openai.com")
    api_key: str = Field(env="OPENAI_API_KEY")
    default_model: str = Field(env="DEFAULT_MODEL", default="gpt-4")


class DatabaseSettings(CustomBaseSettings):
    url: str = Field(env="DATABASE_URL", default="mongodb://localhost:27017")
    db_name: str = Field(env="DATABASE_NAME", default="cluster0")


class Settings(BaseSettings):
    llm: LLMSettings = Field(default_factory=LLMSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)


@lru_cache
def get_settings():
    settings = Settings()
    return settings


if __name__ == '__main__':
    print(get_settings().json(indent=2))