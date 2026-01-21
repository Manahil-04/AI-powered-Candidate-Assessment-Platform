from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    GOOGLE_API_KEY: str
    GITHUB_API_BASE: str = "https://api.github.com"

    class Config:
        env_file = ".env"

settings = Settings()
