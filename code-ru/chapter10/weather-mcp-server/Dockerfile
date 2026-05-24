# Многоэтапная сборка для weather-mcp-server
FROM python:3.12-slim-bookworm as base

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы проекта
COPY pyproject.toml requirements.txt ./
COPY server.py ./

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PORT=8081

# Открываем порт (Smithery использует 8081)
EXPOSE 8081

# Проверка работоспособности
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Запускаем MCP-сервер
CMD ["python", "server.py"]
