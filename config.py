from pydantic_settings import BaseSettings, SettingsConfigDict

# Класс Settings (извлечение переменных окружения из .env файла)
class Settings(BaseSettings):
    DB_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int



    model_config = SettingsConfigDict(env_file='.env')


settings = Settings()

