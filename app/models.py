from sqlalchemy import Column, Integer, String
from .database import Base # Importa a Base que acabamos de criar

# Modelo da tabela 'datasets'
class Dataset(Base):
    __tablename__ = "datasets" # Nome da tabela no banco

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    source_url = Column(String, unique=True, index=True)