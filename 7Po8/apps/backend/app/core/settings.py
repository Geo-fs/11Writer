from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "7Po8 API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    database_url: str = "sqlite:///./data/7po8.db"
    allowed_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    def ensure_data_dir(self) -> None:
        Path("data").mkdir(parents=True, exist_ok=True)


settings = Settings()
