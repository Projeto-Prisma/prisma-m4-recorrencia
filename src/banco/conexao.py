import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from src.banco.modelos import Base

# Carrega as variáveis do arquivo .env
load_dotenv()

# Lê as variáveis com segurança usando os.getenv
user = os.getenv("DB_USER")
password = os.getenv("DB_PASS")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db_name = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

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