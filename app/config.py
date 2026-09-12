from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PORT: int = 8001
    LOG_LEVEL: str = "info"
    ENV: str = "local"

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    MS2_BASE_URL: str = "http://localhost:8002"
    HTTP_TIMEOUT_SECONDS: int = 3
    HTTP_RETRIES: int = 2

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()