from pydantic_settings import BaseSettings
from pydantic import ConfigDict 
class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db/scava-db"

    model_config = ConfigDict(env_file=".env")

# Cria uma instância única das configurações para ser importada
settings = Settings()