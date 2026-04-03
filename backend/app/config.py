from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    supabase_jwt_secret: str
    supabase_url: str
    backend_cors_origins: str = "http://localhost:3000"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",")]


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
