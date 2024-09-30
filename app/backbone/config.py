"""Settings for the project."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    dbdie_main_fd: str
    fastapi_host: str
    db_hostname: str
    db_port: str
    db_name: str
    db_username: str
    db_password: str
    ml_host: str
    check_rps: str

    class Config:
        env_file = ".env"


ST = Settings()
