from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Merq API"
    VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+psycopg2://merq:merq123@db:5432/merqdb"

    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
