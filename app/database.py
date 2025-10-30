from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings 

# Cria a engine assíncrona usando a URL do banco de dados das configurações
engine = create_async_engine(settings.DATABASE_URL)

# Cria uma fábrica de sessões assíncronas
# autocommit=False e autoflush=False são padrões seguros
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para nossos modelos (tabelas)
Base = declarative_base()

# Função para injetar a sessão da DB na nossa API
async def get_db():
    async with SessionLocal() as session:
        yield session