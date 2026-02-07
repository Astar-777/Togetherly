from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    db_username: str
    db_password: str
    db_name: str
    db_host: str
    db_port: str


    secret_key: str
    algorithm: str
    access_token_expire_minutes: int


    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8"
    )


    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_username}:"
            f"{self.db_password}@{self.db_host}:"
            f"{self.db_port}/{self.db_name}"
        )
    

settings = Settings()
