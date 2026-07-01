import pytest
from sqlalchemy.orm import Session
from src.banco.conexao import criar_tabelas, engine

# Adicionamos a importação do Base aqui
from src.banco.modelos import Base, CategoriaM2, Denuncia
from src.servicos.calculo_espacial import processar_nova_denuncia


@pytest.fixture(scope="module")
def db_session():
    # Derruba as tabelas antigas (com o schema defasado sem a coluna 'resolvido')
    Base.metadata.drop_all(bind=engine)

    # Cria as tabelas novamente com o schema atualizado
    criar_tabelas()

    with Session(engine) as session:
        yield session
        session.query(Denuncia).delete()
        session.commit()


def test_denuncia_inedita_gera_novo_cluster(db_session):
    resultado = processar_nova_denuncia(
        db=db_session,
        latitude=-8.047562,
        longitude=-34.876964,
        categoria_texto=CategoriaM2.MANUTENCAO_LIMPEZA.value,
    )

    assert resultado["evento"] == "padrao.recorrencia"
    payload = resultado["payload"]
    assert payload["contagem"] == 1
    assert payload["regiao"]["cluster_id"] is not None
    assert payload["categoria"] == CategoriaM2.MANUTENCAO_LIMPEZA.value


def test_denuncia_recorrente_herda_cluster(db_session):
    resultado = processar_nova_denuncia(
        db=db_session,
        latitude=-8.047562,
        longitude=-34.876964,
        categoria_texto=CategoriaM2.MANUTENCAO_LIMPEZA.value,
    )

    payload = resultado["payload"]
    assert payload["contagem"] == 2
    assert payload["regiao"]["cluster_id"] is not None
