from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    DB_URL: str

    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()
print(f"Current directory: {os.getcwd()}")  # Добавьте эту строку
print(f"DB_URL: {settings.DB_URL}")  # И эту