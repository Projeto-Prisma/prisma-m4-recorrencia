from src.banco.conexao import criar_tabelas, engine
from src.main import iniciar_modulo
import pytest


def test_conexao_e_criacao_tabelas():
    try:
        criar_tabelas()
        assert engine is not None
    except Exception as e:
        pytest.fail(f"Erro ao conectar ou criar tabelas: {e}")


def test_iniciar_modulo():
    # P/ cobrir o código dentro do main.py
    try:
        iniciar_modulo()
    except Exception as e:
        pytest.fail(f"Erro ao iniciar módulo: {e}")
