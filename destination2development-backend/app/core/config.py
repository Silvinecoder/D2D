from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_NAME: str

    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_PASSWORD_GRANT_TYPE: str
    AUTH0_GRANT_TYPE: str
    AUTH0_MANAGEMENT_AUDIENCE: str

    AUTH0_TEST_USERNAME: str
    AUTH0_TEST_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:5432/{self.DB_NAME}"
        )


settings = Settings()
