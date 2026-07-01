import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.banco.conexao import criar_tabelas, engine
from src.main import app


def test_conexao_e_criacao_tabelas():
    try:
        criar_tabelas()
        assert engine is not None
    except Exception as e:
        pytest.fail(f"Erro ao conectar ou criar tabelas: {e}")


# Adicionamos o patch aqui para "calar" o consumidor durante o teste do FastAPI
@patch("src.main.iniciar_consumidor")
def test_api_startup(mock_consumidor):
    # O TestClient aciona automaticamente o "lifespan" do main.py
    with TestClient(app) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert response.json()["status"] == "operacional"
        assert response.json()["modulo"] == "M4 - Recorrência Territorial"
