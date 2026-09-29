# =============================================
# ФАЙЛ: clickhouse_loader.py
# НАЗНАЧЕНИЕ: Загрузка данных в ClickHouse
# ОПИСАНИЕ: Загружает очищенную телеметрию
#           в аналитическую таблицу
# =============================================

import pandas as pd
from clickhouse_driver import Client
from src.utils.config import CLICKHOUSE_CONFIG


class ClickHouseLoader:
    """
    Класс для загрузки данных в ClickHouse.
    Использует clickhouse-driver для нативного подключения.
    """

    def __init__(self):
        # Создаем клиент ClickHouse
        self.client = Client(
            host=CLICKHOUSE_CONFIG['host'],
            port=9000,  # Нативный порт (не HTTP!)
            user=CLICKHOUSE_CONFIG['user'],
            password=CLICKHOUSE_CONFIG['password'],
            database=CLICKHOUSE_CONFIG['database'],
        )
        print(f"[ClickHouseLoader] Подключено к {CLICKHOUSE_CONFIG['host']}:9000")

    def load_telemetry(self, df: pd.DataFrame) -> int:
        """
        Загружает DataFrame телеметрии в ClickHouse.
        Возвращает количество загруженных записей.
        """
        # Преобразуем DataFrame в список кортежей
        # ClickHouse driver принимает данные в таком формате
        data = [
            (
                row['timestamp'],
                str(row['vehicle_id']),
                float(row['latitude']),
                float(row['longitude']),
                float(row['altitude']),
                float(row['speed']),
                row['sensor_id'],
                row['speed_zone'],
                float(row['sensor_accuracy']) if pd.notna(row['sensor_accuracy']) else 0.0,
            )
            for _, row in df.iterrows()
        ]

        # SQL запрос на вставку
        query = """
            INSERT INTO telemetry_analytics (
                timestamp, vehicle_id, latitude, longitude, altitude,
                speed, sensor_id, speed_zone, sensor_accuracy
            ) VALUES
        """

        # Выполняем вставку
        self.client.execute(query, data)

        print(f"[ClickHouseLoader] Загружено {len(data)} записей в telemetry_analytics")
        return len(data)

    def verify_load(self) -> int:
        """Проверяет количество записей в таблице."""
        result = self.client.execute("SELECT count() FROM telemetry_analytics")
        count = result[0][0]
        print(f"[ClickHouseLoader] В таблице telemetry_analytics: {count} записей")
        return count

    def clean_telemetry(self):
        """Очищает таблицу перед загрузкой (идемпотентность)."""
        self.client.execute("TRUNCATE TABLE telemetry_analytics")
        print(f"[ClickHouseLoader] Таблица telemetry_analytics очищена")