from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_URL: str

setting = Setting()