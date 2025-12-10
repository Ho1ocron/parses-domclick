from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    DEBUG: bool = Field(default=False, alias="DEBUG")
    S_SELENIUM_HOST: str = Field(default="localhost", alias="SELENIUM_HOST")
    S_SELENIUM_PORT: int = Field(default=4444, alias="SELENIUM_PORT")

    @property
    def SELENIUM_HOST(self) -> str:
        return self.S_SELENIUM_HOST

    @property
    def SELENIUM_PORT(self) -> int:
        return self.S_SELENIUM_PORT
    

settings = Settings()


if __name__ == "__main__":
    print(settings.SELENIUM_HOST)
    print(settings.SELENIUM_PORT)