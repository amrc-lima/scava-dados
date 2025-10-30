from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session # <-- Adicione esta
from sqlalchemy.future import select
from . import models, schemas
from typing import Union # <-- Adicione esta

# --- Função para LER datasets ---
async def get_datasets(db: Union[AsyncSession, Session], skip: int = 0, limit: int = 100):
    query = select(models.Dataset).offset(skip).limit(limit)
    
    # Checa se o 'db' é async ou sync
    if isinstance(db, AsyncSession):
        result = await db.execute(query)
    else:
        result = db.execute(query) # Versão síncrona
        
    return result.scalars().all()

# --- Função para CRIAR um dataset ---
async def create_dataset(db: Union[AsyncSession, Session], dataset: schemas.DatasetCreate):
    db_dataset = models.Dataset(
        title=dataset.title,
        description=dataset.description,
        source_url=dataset.source_url
    )
    db.add(db_dataset)
    
    # Checa se o 'db' é async ou sync
    if isinstance(db, AsyncSession):
        await db.commit()
        await db.refresh(db_dataset)
    else:
        db.commit() # Versão síncrona
        db.refresh(db_dataset) # Versão síncrona
        
    return db_dataset

# --- Função para Buscar um dataset pelo link ---
async def get_dataset_by_source_url(db: Union[AsyncSession, Session], source_url: str):
    query = select(models.Dataset).filter(models.Dataset.source_url == source_url)
    
    # Checa se o 'db' é async ou sync
    if isinstance(db, AsyncSession):
        result = await db.execute(query)
    else:
        result = db.execute(query) # Versão síncrona
        
    return result.scalars().first()