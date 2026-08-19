from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # No default — same reasoning as docker-compose.yml's required POSTGRES_PASSWORD: a
    # weak default here is one a real deploy could silently inherit. Set it in .env.
    database_url: str
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
