from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080  # 7 days

    GEMINI_API_KEY: str = ""
    SEMANTIC_SCHOLAR_KEY: str = ""

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "acadeval_password"

    REDIS_URL: str = "redis://localhost:6379/0"

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 500

    APP_ENV: str = "development"
    FRONTEND_ORIGIN: str = "http://localhost:5173"


settings = Settings()
