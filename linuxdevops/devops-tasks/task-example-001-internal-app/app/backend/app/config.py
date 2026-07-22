from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://app:app@db:5432/messages"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60 * 24


settings = Settings()
