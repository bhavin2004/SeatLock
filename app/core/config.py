from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8"
    )
    APP_NAME : str = "Cinebook"
    APP_ENV : str = "development"
    DEBUG : bool = False
    DATABASE_URL: str
    JWT_SECRET_KEY: SecretStr


settings = Settings()