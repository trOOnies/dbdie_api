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

    class Config:
        env_file = "../env_files/fastapi.env"


settings = Settings()
# settings = Settings(
#     db_hostname=os.environ["DB_HOSTNAME"],
#     db_port=os.environ["DB_PORT"],
#     db_password=os.environ["DB_PASSWORD"],
#     db_name=os.environ["DB_NAME"],
#     db_username=os.environ["DB_USERNAME"],
# )
# print(settings)
