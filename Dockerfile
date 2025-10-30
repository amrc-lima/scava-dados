# 1. Imagem Base: Começa com uma imagem Python oficial
FROM python:3.11-slim

# 2. Define o diretório de trabalho dentro do container
WORKDIR /code

# 3. Copia o arquivo de requisitos para o container
COPY requirements.txt .

# 4. Instala as dependências
# --no-cache-dir economiza espaço
# psycopg2-binary é o driver Postgres que o SQLAlchemy precisa
RUN pip install --no-cache-dir -r requirements.txt psycopg2-binary

# 5. Copia o código da sua aplicação (tudo da pasta 'app')
COPY ./app /code/app

# 6. Comando para rodar a aplicação quando o container iniciar
# Expõe a API na porta 8000 para o mundo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]