from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CELERY_BROKER_URL: str = "redis://localhost:6380/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6380/0"
    OPENAI_API_KEY: str
    OPENAI_ENDPOINT: str
    GITHUB_TOKEN: str

    class Config:
        env_file = ".env"

settings = Settings()