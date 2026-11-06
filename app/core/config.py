from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "To-dos Application"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/todos"

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    FIRST_ADMIN_EMAIL: str | None = None
    FIRST_ADMIN_USERNAME: str | None = None
    FIRST_ADMIN_PASSWORD: str | None = None


settings = Settings()  # type: ignore[call-arg]
