import pytest
from sqlalchemy.orm import Session
from src.banco.conexao import criar_tabelas, engine
from src.banco.modelos import CategoriaDenuncia, Denuncia
from src.servicos.calculo_espacial import processar_nova_denuncia


# Usamos um banco em memória ou a nossa conexão de testes
@pytest.fixture(scope="module")
def db_session():
    criar_tabelas()
    with Session(engine) as session:
        yield session
        # Limpa as tabelas após o teste
        session.query(Denuncia).delete()
        session.commit()


def test_denuncia_inedita_gera_novo_cluster(db_session):
    resultado = processar_nova_denuncia(
        db=db_session,
        latitude=-8.047562,  # Recife (Exemplo)
        longitude=-34.876964,
        categoria=CategoriaDenuncia.BURACO_VIA,
    )

    assert resultado["is_recorrente"] is False
    assert resultado["cluster_id"] is not None


def test_denuncia_recorrente_herda_cluster(db_session):
    # Insere a segunda denúncia exatamente no mesmo local da primeira
    resultado = processar_nova_denuncia(
        db=db_session,
        latitude=-8.047562,
        longitude=-34.876964,
        categoria=CategoriaDenuncia.BURACO_VIA,
    )

    assert resultado["is_recorrente"] is True
