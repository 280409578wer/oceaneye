from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "OceanEye 巨量行情"
    data_source: str = "mock"
    database_url: str = f"sqlite:///{ROOT_DIR / 'data' / 'oceaneye.db'}"
    mock_enabled: bool = True
    mock_interval_seconds: int = 10
    ai_provider: str = "rules"
    ai_api_key: str = ""
    ai_model: str = ""

    oceanengine_app_id: str = ""
    oceanengine_secret: str = ""
    oceanengine_access_token: str = ""
    oceanengine_advertiser_id: str = ""

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

