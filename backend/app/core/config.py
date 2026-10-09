from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    INSTAGRAM_APP_ID: str
    INSTAGRAM_APP_SECRET: str
    INSTAGRAM_REDIRECT_URI: str

    FACEBOOK_APP_ID: str
    FACEBOOK_APP_SECRET: str
    FACEBOOK_REDIRECT_URI: str
    FACEBOOK_CONFIG_ID: str

    GRAPH_API_VERSION: str = "v26.0"

    ENCRYPTION_KEY: str
    PUBLIC_BASE_URL: str
    FRONTEND_BASE_URL: str

    RATE_LIMIT_LOGIN: str = "5/15min"
    RATE_LIMIT_REGISTER: str = "3/hour"
    RATE_LIMIT_OAUTH: str = "3/10min"
    RATE_LIMIT_FACEBOOK_PAGES: str = "2/hour"
    RATE_LIMIT_UPLOAD: str = "10/hour"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()