from src.banco.conexao import criar_tabelas


def iniciar_modulo():
    print("Iniciando Módulo 4 - Recorrência Territorial...")

    # Conecta no banco do Docker e cria a tabela 'denuncias_historico'
    criar_tabelas()


if __name__ == "__main__":
    iniciar_modulo()
