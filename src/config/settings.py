from pydantic import BaseSettings

class Settings(BaseSettings):
    google_calendar_api_key: str
    google_calendar_client_id: str
    google_calendar_client_secret: str
    openai_api_key: str
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()