from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr,Field,model_validator


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
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(gt=0)
    RAZORPAY_KEY_ID: str | None = None
    RAZORPAY_KEY_SECRET: SecretStr | None = None
    RAZORPAY_WEBHOOK_SECRET: SecretStr | None = None
    TEST_DATABASE_URL: SecretStr | None = None
    REDIS_URL: SecretStr | None = None

    
    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.APP_ENV.lower() == "production":
            
            if len(self.JWT_SECRET_KEY.get_secret_value())<32:
                raise ValueError(
                "JWT_SECRET_KEY must be at least 32 characters in production"
            )
            if self.DEBUG:
                raise ValueError(
                "DEBUG must be false in production"
            )
        return self

settings = Settings() # type: ignore