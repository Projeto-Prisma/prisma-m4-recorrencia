import json
import pika
import os
from sqlalchemy.orm import Session
from src.banco.conexao import engine
from src.servicos.calculo_espacial import processar_nova_denuncia
from src.mensageria.publicador import PublicadorRabbitMQ

RABBITMQ_URL = os.getenv(
    "M4_RABBITMQ_URL", "amqp://prisma:prisma_password@localhost:5672/"
)
EXCHANGE = os.getenv("M4_EXCHANGE", "denuncias")
FILA = os.getenv("M4_FILA", "m4.recorrencia")
ROUTING_IN = os.getenv("M4_ROUTING_IN", "denuncia.classificada")


def iniciar_consumidor():
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Declara a infraestrutura amarrando a fila à routing key de entrada
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    channel.queue_declare(queue=FILA, durable=True)
    channel.queue_bind(exchange=EXCHANGE, queue=FILA, routing_key=ROUTING_IN)

    publicador = PublicadorRabbitMQ()

    def callback(ch, method, properties, body):
        try:
            dados = json.loads(body)
            categoria = dados.get("categoria")
            localizacao = dados.get("localizacao")

            # Se a denúncia não tiver categoria válida ou GPS, ignoramos para não sujar o banco
            if not categoria or not localizacao:
                print(
                    f"[!] Denúncia ignorada por dados insuficientes: {dados.get('id')}"
                )
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            lat = float(localizacao.get("lat"))
            lon = float(localizacao.get("lon"))

            # Abre a sessão com o PostGIS e roda o motor de estado e espaço
            with Session(engine) as db_session:
                resultado = processar_nova_denuncia(
                    db=db_session,
                    latitude=lat,
                    longitude=lon,
                    categoria_texto=categoria,
                )

                # Despacha o JSON pronto para o Módulo 3
                publicador.publicar(resultado)

            # Confirma ao RabbitMQ que processamos a mensagem com sucesso
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"[Erro] Falha ao processar mensagem: {e}")
            # Rejeita a mensagem sem devolver para a fila (evita loops infinitos de crash)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    # Impede que o módulo puxe muitas mensagens de uma vez, garantindo estabilidade
    channel.basic_qos(prefetch_count=1)

    print(f"[*] Módulo 4 Operacional. Aguardando eventos em '{FILA}'...")
    channel.basic_consume(queue=FILA, on_message_callback=callback)
    channel.start_consuming()
