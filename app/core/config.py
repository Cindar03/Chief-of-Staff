from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    database_url: str = "sqlite:///./data/chief_of_staff.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    initiative_review_hours: int = 6

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
