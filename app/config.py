from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    base_url: str = "http://localhost:8000"
    code_length: int = 7
    app_env: str = "production"

    class Config:
        env_file = ".env"


settings = Settings()
