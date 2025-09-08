# Usar una imagen oficial de Python como base
FROM python:3.11-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
ENV POETRY_VERSION=1.8.2
RUN pip install "poetry==$POETRY_VERSION"

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero para aprovechar el cache de Docker
COPY pyproject.toml poetry.lock* /app/

# Instalar dependencias del proyecto (sin crear virtualenv)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copiar el resto del código al contenedor
COPY . /app

# Exponer el puerto (opcional, para documentación)
EXPOSE 8000

# Comando por defecto (opcional si ya lo pones en docker-compose.yml)
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]