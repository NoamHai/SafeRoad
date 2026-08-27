from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "Safe Roads API"
    debug: bool = False
    model_path: str = "model.pkl"
    cors_origins: list = ["http://127.0.0.1:8000", "http://localhost:8000", "http://127.0.0.1:5500", "http://localhost:5500"]
    accident_type_mapping: dict[str, int] = {}
    speed_limit_mapping: dict[str, int] = {}
    district_mapping: dict[str, int] = {}


settings = Settings()
