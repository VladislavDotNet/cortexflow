# =============================================
# ФАЙЛ: config.py
# НАЗНАЧЕНИЕ: Конфигурация проекта CortexFlow
# ОПИСАНИЕ: Хранит все настройки подключения
#           к базам данных и параметры проекта
# =============================================

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()


# ============================================
# PostgreSQL (Source / Raw Layer)
# ============================================
POSTGRES_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5435"),       # Наш порт!
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "database": os.getenv("POSTGRES_DB", "cortexflow_raw"),
}

# Формируем URL для SQLAlchemy
POSTGRES_URL = (
    f"postgresql://{POSTGRES_CONFIG['user']}:{POSTGRES_CONFIG['password']}"
    f"@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"
)


# ============================================
# ClickHouse (Target / Analytics Layer)
# ============================================
CLICKHOUSE_CONFIG = {
    "host": os.getenv("CLICKHOUSE_HOST", "localhost"),
    "port": os.getenv("CLICKHOUSE_PORT", "8123"),      # HTTP порт
    "user": os.getenv("CLICKHOUSE_USER", "default"),
    "password": os.getenv("CLICKHOUSE_PASSWORD", ""),
    "database": os.getenv("CLICKHOUSE_DB", "cortexflow_analytics"),
}

CLICKHOUSE_URL = (
    f"clickhouse://{CLICKHOUSE_CONFIG['user']}:{CLICKHOUSE_CONFIG['password']}"
    f"@{CLICKHOUSE_CONFIG['host']}:{CLICKHOUSE_CONFIG['port']}/{CLICKHOUSE_CONFIG['database']}"
)


# ============================================
# Qdrant (Vector Store / AI Memory)
# ============================================
QDRANT_CONFIG = {
    "host": os.getenv("QDRANT_HOST", "localhost"),
    "port": int(os.getenv("QDRANT_PORT", "6333")),
}