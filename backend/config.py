from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Safe Roads API"
    debug: bool = False
    cors_origins: list[str] = ["http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1:5500", "http://localhost:5500"]


settings = Settings()
