from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    DEBUG: bool = Field(default=False, alias="DEBUG")
    _API_URL: str = Field(default="", alias="API_URL")

    @property
    def API_URL(self):
        return self._API_URL
    

settings = Settings()

