import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from src.banco.conexao import criar_tabelas
from src.mensageria.consumidor import iniciar_consumidor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de Ciclo de Vida do FastAPI.
    Tudo antes do 'yield' roda na subida do container.
    Tudo depois do 'yield' roda quando o container for desligado.
    """
    print("[M4] Iniciando preparativos do banco de dados...")
    # 1. Garante que a extensão PostGIS e as tabelas estão prontas
    criar_tabelas()

    print("[M4] Subindo o consumidor RabbitMQ em background...")
    # 2. Inicia o consumidor em uma Thread separada (daemon=True garante
    # que a thread morra automaticamente se a API cair)
    thread_consumidor = threading.Thread(target=iniciar_consumidor, daemon=True)
    thread_consumidor.start()

    yield

    print("[M4] Encerrando o módulo...")


# 3. Instancia a API de Observabilidade esperada pela infraestrutura
app = FastAPI(title="Prisma M4 - Recorrência Territorial", lifespan=lifespan)


@app.get("/")
def health_check():
    """Endpoint para a infraestrutura saber se o container está vivo."""
    return {
        "status": "operacional",
        "modulo": "M4 - Recorrência Territorial",
        "rabbit_mq": "escutando em background",
    }


if __name__ == "__main__":
    # O docker-compose mapeia a porta 8004 externa para a 8000 interna do container
    uvicorn.run(app, host="127.0.0.1", port=8000)
