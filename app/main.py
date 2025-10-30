from fastapi import FastAPI, Depends # Adiciona 'Depends'
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession # Adiciona 'AsyncSession'
from sqlalchemy.ext.asyncio import AsyncEngine # <-- ADICIONE ESTA LINHA
from typing import List # Adiciona 'List' para o tipo de retorno
from . import crud, schemas, scraper # Adiciona 'scraper' aqui
# Importa a 'engine' e 'Base' do nosso arquivo database.py
from .database import engine, Base, get_db # Adiciona 'get_db'
from . import crud, schemas # Adiciona importações de 'crud' e 'schemas'
import asyncio # Para o 'await asyncio.sleep(3)'
from sqlalchemy.exc import OperationalError # O erro que o SQLAlchemy nos dá

# -----
# Função 'lifespan'
# -----
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("API está iniciando... tentando conectar ao banco de dados...")
    
    connected = False
    for _ in range(10): # Tenta 10 vezes (total 30 seg)
        try:
            # --- MUDANÇA IMPORTANTE AQUI ---
            # Checa se o 'engine' é o de produção (Async) ou o de teste (Sync)
            if isinstance(engine, AsyncEngine):
                # Caminho de Produção (com Docker)
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            else:
                # Caminho de Teste (com Pytest)
                # Usa o engine síncrono de forma síncrona
                with engine.begin() as conn:
                     Base.metadata.create_all(bind=engine)
            
            connected = True
            print("Conexão com banco de dados e tabelas criadas com sucesso!")
            break # Sai do loop se conectar
        except OperationalError as e:
            # Se der erro (ex: ConnectionRefused), avisa e espera
            print(f"Erro ao conectar ao banco. Tentando novamente em 3 segundos...")
            await asyncio.sleep(3) # Espera 3 segundos antes de tentar de novo
    
    if not connected:
        print("Não foi possível conectar ao banco de dados após as tentativas. Desligando.")
        
    yield # Este 'yield' é o ponto onde a API fica rodando
    
    print("API está desligando...")

# -----
# Cria a instância da aplicação
# -----
app = FastAPI(
    title="ScavaDados API",
    description="API para coleta e consulta de datasets públicos.",
    version="0.1.0",
    lifespan=lifespan
)

# --- Endpoint Raiz (como estava antes) ---
@app.get("/")
async def read_root():
    return {"message": "Olá, Escavador! API 'ScavaDados' no ar."}

# --- Endpoint para criar um novo dataset ---
@app.post("/datasets/", response_model=schemas.Dataset)
async def create_new_dataset(
    dataset: schemas.DatasetCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Usa a função 'Depends(get_db)' para injetar a sessão do banco
    # Chama nossa função crud para criar o dataset
    return await crud.create_dataset(db=db, dataset=dataset)

# --- Endpoint para ler todos os datasets ---
@app.get("/datasets/", response_model=List[schemas.Dataset])
async def read_all_datasets(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    # Chama nossa função crud para buscar os datasets
    datasets = await crud.get_datasets(db=db, skip=skip, limit=limit)
    return datasets

# --- Endpoint para rodar o scraper e popular o banco ---
@app.post("/scrape/", response_model=dict)
async def run_scraper(db: AsyncSession = Depends(get_db)):
    print("Endpoint /scrape/ acionado...")

    # 1. Chama nosso scraper para buscar os dados do site
    # Isso cumpre o diferencial de 'Web Scraping'
    scraped_data_list = await scraper.scrape_gov_data()

    if not scraped_data_list:
        return {"message": "Scraping falhou ou não encontrou dados."}

    new_datasets_count = 0

    # 2. Itera sobre cada item raspado
    for scraped_item in scraped_data_list:
        # 3. Verifica se o item já existe no banco
        existing_dataset = await crud.get_dataset_by_source_url(
            db=db, source_url=scraped_item.source_url
        )

        # 4. Se não existir, cria o novo item
        if not existing_dataset:
            await crud.create_dataset(db=db, dataset=scraped_item)
            new_datasets_count += 1
        else:
            # Opcional: logar que o item foi pulado
            print(f"Dataset já existe, pulando: {scraped_item.title}")

    print(f"Scraping concluído. {new_datasets_count} novos datasets adicionados.")

    # 5. Retorna uma mensagem de sucesso
    return {
        "message": "Scraping concluído com sucesso!",
        "new_datasets_added": new_datasets_count,
        "total_datasets_found": len(scraped_data_list)
    }