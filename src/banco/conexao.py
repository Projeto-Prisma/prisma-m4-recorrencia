import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from src.banco.modelos import Base

# Carrega as variáveis do arquivo .env
load_dotenv()

# 1. Tenta pegar a URL completa primeiro (Padrão de Produção/Render/Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Se não existir (Padrão Local/Docker), monta a URL com as variáveis soltas
if not DATABASE_URL:
    # O segundo argumento no getenv é o valor padrão (fallback) caso a variável não exista no .env
    user = os.getenv("DB_USER", "prisma")
    password = os.getenv("DB_PASS", "prisma_password")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "recorrencia_db")

    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

# Cria o motor de conexão
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def criar_tabelas():
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas e criadas com sucesso no banco de dados.")


def obter_sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
