from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    DEBUG: bool = Field(default=False, alias="DEBUG")
    _APP_API_URL: str = Field(default="", alias="API_URL")
    _SELENIUM_HOST: str = Field(default="localhost", alias="SELENIUM_HOST")
    _SELENIUM_PORT: int = Field(default=4444, alias="SELENIUM_PORT")

    @property
    def API_URL(self) -> str:
        return self._APP_API_URL
    
    @property
    def SELENIUM_HOST(self) -> str:
        return self._SELENIUM_HOST

    @property
    def SELENIUM_PORT(self) -> str:
        return f"{self.SELENIUM_HOST}:{self._SELENIUM_PORT}"
    

settings = Settings()

