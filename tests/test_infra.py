import pytest
from src.banco.conexao import criar_tabelas, engine
from src.main import app
from fastapi.testclient import TestClient


def test_conexao_e_criacao_tabelas():
    """Valida se a conexão com o banco é válida e se as tabelas são criadas."""
    try:
        criar_tabelas()
        assert engine is not None
    except Exception as e:
        pytest.fail(f"Erro ao conectar ou criar tabelas: {e}")


def test_api_startup():
    """Valida se o app FastAPI foi instanciado e se a rota de health_check funciona."""
    client = TestClient(app)

    # Testa a rota que criamos no main.py
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "operacional"
    assert response.json()["modulo"] == "M4 - Recorrência Territorial"
