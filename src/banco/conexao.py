import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from src.banco.modelos import Base

# Carrega as variáveis do arquivo .env (útil para quando for rodar testes locais)
load_dotenv()

# Lê a variável de ambiente injetada pelo docker-compose da infraestrutura
db_url_raw = os.getenv("M4_DATABASE_URL")

if not db_url_raw:
    # Fallback para execução isolada (quando não estiver rodando no docker-compose geral)
    user = os.getenv("PG_USER", "prisma")
    password = os.getenv("PG_PASSWORD", "prisma_secret")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5436")
    db_name = os.getenv("DB_NAME", "recorrencia")
    db_url_raw = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

# A infraestrutura injeta o driver '+asyncpg', mas o nosso M4 usa o driver síncrono padrão.
# O comando abaixo limpa a string para garantir compatibilidade com o GeoAlchemy.
DATABASE_URL = db_url_raw.replace("+asyncpg", "")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def criar_tabelas():
    # O contrato da infraestrutura exige que o M4 ative o PostGIS ativamente no seu schema
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    print("PostGIS ativado e tabelas criadas com sucesso no banco de dados.")


def obter_sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
