import json
from unittest.mock import patch, MagicMock
from src.mensageria.publicador import PublicadorRabbitMQ
from src.mensageria.consumidor import iniciar_consumidor


# 1. Testando o Publicador
@patch("src.mensageria.publicador.pika.BlockingConnection")
def test_publicador_formata_e_envia_mensagem(mock_blocking_connection):
    # Simula a conexão e o canal do RabbitMQ
    mock_conexao = MagicMock()
    mock_canal = MagicMock()
    mock_conexao.channel.return_value = mock_canal
    mock_blocking_connection.return_value = mock_conexao

    # Instancia o publicador (que usará o mock no lugar da conexão real)
    publicador = PublicadorRabbitMQ()

    # Cria um payload de mentira simulando o retorno do motor de regras
    payload_teste = {
        "evento": "padrao.recorrencia",
        "payload": {
            "regiao": {
                "cluster_id": "uuid-falso-123",
                "centroide": {"latitude": 0, "longitude": 0},
            },
            "categoria": "Manutenção e Limpeza Urbana",
            "contagem": 5,
            "janela_de_tempo": "30 dias",
        },
    }

    # Executa a ação
    publicador.publicar(payload_teste)

    # Verifica se o método basic_publish foi chamado exatamente 1 vez
    mock_canal.basic_publish.assert_called_once()

    # Captura os argumentos que foram passados para o basic_publish
    _, kwargs = mock_canal.basic_publish.call_args

    # Valida se a mensagem foi transformada em JSON corretamente
    corpo_enviado = json.loads(kwargs["body"])
    assert corpo_enviado["evento"] == "padrao.recorrencia"
    assert corpo_enviado["payload"]["contagem"] == 5
    assert kwargs["routing_key"] == "padrao.recorrencia"


# 2. Testando a inicialização do Consumidor
@patch("src.mensageria.consumidor.pika.BlockingConnection")
def test_consumidor_declara_filas_e_escuta(mock_blocking_connection):
    mock_conexao = MagicMock()
    mock_canal = MagicMock()
    mock_conexao.channel.return_value = mock_canal
    mock_blocking_connection.return_value = mock_conexao

    # Executa a função que liga o consumidor
    iniciar_consumidor()

    # Garante que as declarações de infraestrutura foram feitas
    mock_canal.exchange_declare.assert_called_with(
        exchange="denuncias", exchange_type="topic", durable=True
    )
    mock_canal.queue_declare.assert_called_with(queue="m4.recorrencia", durable=True)
    mock_canal.queue_bind.assert_called_with(
        exchange="denuncias",
        queue="m4.recorrencia",
        routing_key="denuncia.classificada",
    )

    # Garante que ele entrou no modo de escuta
    mock_canal.basic_consume.assert_called_once()
    mock_canal.start_consuming.assert_called_once()
