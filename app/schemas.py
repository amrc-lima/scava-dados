from pydantic import BaseModel, ConfigDict # <-- MUDANÇA AQUI
# Schema base para um dataset (dados comuns)
class DatasetBase(BaseModel):
    title: str
    description: str | None = None # Permite que a descrição seja opcional (None)
    source_url: str

# Schema para criar um dataset (o que recebemos da API)
class DatasetCreate(DatasetBase):
    pass # Por enquanto, é igual ao Base

# Schema para ler um dataset (o que enviamos da API)
# Inclui o 'id' e habilita o 'from_attributes'
class Dataset(DatasetBase):
    id: int

    # --- MUDANÇA AQUI ---
    model_config = ConfigDict(from_attributes=True)