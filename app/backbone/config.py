from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    fastapi_host: str
    cvat_host: str
    cvat_mail: str
    cvat_password: str
    db_hostname: str
    db_port: str
    db_name: str
    db_username: str
    db_password: str
    dbdie_main_fd: str

    class Config:
        env_file = ".env"


ST = Settings()


def endp(endpoint: str) -> str:
    """Get full URL of the endpoint"""
    return ST.fastapi_host + endpoint
