import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app import database
from app import main

# --- Configuração do Banco de Dados de Teste (VERSÃO SÍNCRONA) ---
# Usaremos um banco SQLite em memória, síncrono
TEST_DATABASE_URL = "sqlite:///./test_temp.db"

# Engine SÍNCRONA
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
# Session SÍNCRONA
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# --- Sobrescrevendo a dependência 'get_db' ---
# Esta função é SÍNCRONA e retorna uma sessão SÍNCRONA
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Aplica a substituição
app.dependency_overrides[get_db] = override_get_db

# --- Fixture do Pytest (Setup e Teardown SÍNCRONO) ---
@pytest.fixture(scope="function")
def client():
    # --- MONKEYPATCHING (O "ENGANO") ---
    # 1. Guarda os engines de produção originais
    original_db_engine = database.engine
    original_main_engine = main.engine # <-- NOVO

    # 2. Substitui os engines em AMBOS os lugares
    database.engine = test_engine
    main.engine = test_engine # <-- NOVO E CRUCIAL

    # ANTES de cada teste:
    # Agora o lifespan() vai usar o test_engine (SQLite)
    Base.metadata.create_all(bind=test_engine)

    # Disponibiliza o TestClient
    with TestClient(app) as c:
        yield c

    # DEPOIS de cada teste:
    # Limpa o banco de dados
    Base.metadata.drop_all(bind=test_engine)

    # --- RESTAURAÇÃO ---
    # 3. Coloca os engines de produção de volta no lugar
    database.engine = original_db_engine
    main.engine = original_main_engine # <-- NOVO

    
# --- Nossos Testes (SÍNCRONOS) ---

def test_read_root(client: TestClient):
    """Testa se a rota raiz (/) está funcionando."""
    # Sem 'async' e sem 'await'
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Olá, Escavador! API 'ScavaDados' no ar."}

def test_create_and_read_dataset(client: TestClient):
    """Testa se conseguimos criar e depois ler um dataset."""
    # 1. Criar um dataset
    test_data = {
        "title": "Livro de Teste",
        "description": "R$ 10,00",
        "source_url": "http://teste.com/livro"
    }
    # Sem 'async' e sem 'await'
    create_response = client.post("/datasets/", json=test_data)
    
    assert create_response.status_code == 200
    assert create_response.json()["title"] == "Livro de Teste"
    assert create_response.json()["id"] is not None
    
    # 2. Ler o dataset
    # Sem 'async' e sem 'await'
    read_response = client.get("/datasets/")
    assert read_response.status_code == 200
    assert len(read_response.json()) == 1
    assert read_response.json()[0]["title"] == "Livro de Teste"