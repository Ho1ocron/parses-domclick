from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    DEBUG: bool = Field(default=False, alias="DEBUG")
    APP_API_URL: str = Field(default="", alias="API_URL")
    S_SELENIUM_HOST: str = Field(default="localhost", alias="SELENIUM_HOST")
    S_SELENIUM_PORT: int = Field(default=4444, alias="SELENIUM_PORT")

    @property
    def API_URL(self) -> str:
        return self.APP_API_URL
    
    @property
    def SELENIUM_HOST(self) -> str:
        return self.S_SELENIUM_HOST

    @property
    def SELENIUM_PORT(self) -> int:
        return self.S_SELENIUM_PORT
    

settings = Settings()


if __name__ == "__main__":
    print(settings.API_URL)
    print(settings.SELENIUM_HOST)
    print(settings.SELENIUM_PORT)