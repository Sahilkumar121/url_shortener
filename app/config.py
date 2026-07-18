from pydantic_settings import BaseSettings, SettingsConfigDict


class Setting(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DB_URL: str
    SECRETE_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_TIME: int


setting = Setting()
