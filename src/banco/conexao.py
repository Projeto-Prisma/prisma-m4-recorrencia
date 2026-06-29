from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.banco.modelos import Base

DATABASE_URL = "postgresql://prisma:prisma_password@127.0.0.1:5433/recorrencia_db"

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
