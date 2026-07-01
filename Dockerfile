# 1. Imagem base do Python
FROM python:3.11-slim

# 2. Criação de um usuário não-root por segurança (Best Practice)
RUN adduser --disabled-password --gecos '' prismauser

# 3. Diretório de trabalho no container
WORKDIR /app

# 4. Instala dependências do sistema operacional (necessárias para o PostGIS/psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copia as dependências do Python e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copia todo o código da sua aplicação para dentro do container
COPY . .

# 7. Passa a posse dos arquivos da aplicação para o novo usuário
RUN chown -R prismauser:prismauser /app

# 8. MUDANÇA DE CONTEXTO: A partir daqui, o container roda como usuário comum
USER prismauser

# 9. Expõe a porta 8000
EXPOSE 8000

# 10. Comando que liga o módulo (FastAPI + Consumer RabbitMQ em background)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]