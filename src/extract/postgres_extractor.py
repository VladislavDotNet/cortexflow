# =============================================
# ФАЙЛ: postgres_extractor.py
# НАЗНАЧЕНИЕ: Извлечение данных из PostgreSQL
# ОПИСАНИЕ: Читает сырую телеметрию и возвращает
#           DataFrame для дальнейшей обработки
# =============================================

import pandas as pd
from sqlalchemy import create_engine, text
from src.utils.config import POSTGRES_URL


class PostgresExtractor:
    """
    Класс для извлечения данных из PostgreSQL.
    Использует SQLAlchemy для подключения и pandas для чтения.
    """

    def __init__(self):
        # Создаем движок подключения (engine) — это объект SQLAlchemy
        # Он управляет пулом соединений и диалектом БД
        self.engine = create_engine(POSTGRES_URL)

    def extract_telemetry(self) -> pd.DataFrame:
        """
        Извлекает все данные из таблицы robot_telemetry.
        Возвращает pandas DataFrame.
        """
        query = text("SELECT * FROM robot_telemetry ORDER BY timestamp")

        # pd.read_sql — читает SQL запрос и сразу возвращает DataFrame
        # conn — контекстный менеджер, автоматически закрывает соединение
        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn)

        print(f"[PostgresExtractor] Извлечено {len(df)} записей из robot_telemetry")
        return df

    def extract_events(self) -> pd.DataFrame:
        """Извлекает все события из таблицы robot_events."""
        query = text("SELECT * FROM robot_events ORDER BY timestamp")

        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn)

        print(f"[PostgresExtractor] Извлечено {len(df)} записей из robot_events")
        return df

    def extract_embeddings(self) -> pd.DataFrame:
        """Извлекает эмбеддинги из таблицы embeddings."""
        query = text("SELECT * FROM embeddings ORDER BY timestamp")

        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn)

        print(f"[PostgresExtractor] Извлечено {len(df)} записей из embeddings")
        return df


# ============================================
# Быстрый тест (если запустить файл напрямую)
# ============================================
if __name__ == "__main__":
    extractor = PostgresExtractor()
    df = extractor.extract_telemetry()
    print("\n=== Первые 5 строк телеметрии ===")
    print(df.head())
    print("\n=== Информация о DataFrame ===")
    print(df.info())