import json
from unittest.mock import patch, MagicMock
from src.mensageria.publicador import PublicadorRabbitMQ
from src.mensageria.consumidor import iniciar_consumidor


# 1. Testando o Publicador
@patch("src.mensageria.publicador.pika.BlockingConnection")
def test_publicador_formata_e_envia_mensagem(mock_blocking_connection):
    mock_conexao = MagicMock()
    mock_canal = MagicMock()
    mock_conexao.channel.return_value = mock_canal
    mock_blocking_connection.return_value = mock_conexao

    publicador = PublicadorRabbitMQ()
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

    publicador.publicar(payload_teste)
    mock_canal.basic_publish.assert_called_once()

    _, kwargs = mock_canal.basic_publish.call_args
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

    iniciar_consumidor()

    mock_canal.exchange_declare.assert_called_with(
        exchange="denuncias", exchange_type="topic", durable=True
    )
    mock_canal.queue_declare.assert_called_with(queue="m4.recorrencia", durable=True)
    mock_canal.queue_bind.assert_called_with(
        exchange="denuncias",
        queue="m4.recorrencia",
        routing_key="denuncia.classificada",
    )

    mock_canal.basic_consume.assert_called_once()
    mock_canal.start_consuming.assert_called_once()


# 3. Testando o tratamento de erro no Consumidor (Cobre o 'except' para o SonarCloud)
@patch("src.mensageria.consumidor.pika.BlockingConnection")
def test_consumidor_trata_erro_de_processamento(mock_blocking_connection):
    mock_conexao = MagicMock()
    mock_canal = MagicMock()
    mock_conexao.channel.return_value = mock_canal
    mock_blocking_connection.return_value = mock_conexao

    # Inicia o consumidor para registrar o callback
    iniciar_consumidor()
    callback = mock_canal.basic_consume.call_args[1]["on_message_callback"]

    # Payload corrompido (não é um JSON válido)
    body = b"json_invalido"

    # Intercepta a função print para verificar se o erro foi pego e logado
    with patch("src.mensageria.consumidor.print") as mock_print:
        callback(mock_canal, MagicMock(delivery_tag=1), None, body)

        # Garante que ele acionou o basic_nack rejeitando a mensagem problemática
        mock_canal.basic_nack.assert_called_with(delivery_tag=1, requeue=False)
        mock_print.assert_called()
