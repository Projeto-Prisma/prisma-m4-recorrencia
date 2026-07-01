import json
import pika
import os

# Lê as credenciais injetadas pelo docker-compose da infra
RABBITMQ_URL = os.getenv(
    "M4_RABBITMQ_URL", "amqp://prisma:prisma_password@localhost:5672/"
)
EXCHANGE = os.getenv("M4_EXCHANGE", "denuncias")
ROUTING_OUT = os.getenv("M4_ROUTING_OUT", "padrao.recorrencia")


class PublicadorRabbitMQ:
    def __init__(self):
        parameters = pika.URLParameters(RABBITMQ_URL)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Cumpre o contrato de resiliência: exchange 'topic' e durável
        self.channel.exchange_declare(
            exchange=EXCHANGE, exchange_type="topic", durable=True
        )

    def publicar(self, payload: dict):
        mensagem = json.dumps(payload)
        self.channel.basic_publish(
            exchange=EXCHANGE,
            routing_key=ROUTING_OUT,
            body=mensagem,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Torna a mensagem persistente no disco do RabbitMQ
                content_type="application/json",
            ),
        )
        print(
            f"[x] Publicado {ROUTING_OUT}: cluster {payload['payload']['regiao']['cluster_id']} com {payload['payload']['contagem']} ocorrências."
        )
