# =============================================
# ФАЙЛ: main.py
# НАЗНАЧЕНИЕ: Точка входа в проект CortexFlow
# ОПИСАНИЕ: Запускает ETL пайплайн
# =============================================

from src.extract.postgres_extractor import PostgresExtractor
from src.transform.clean import clean_telemetry, clean_events
from src.load.clickhouse_loader import ClickHouseLoader
from src.load.qdrant_loader import QdrantLoader


def main():
    print("=" * 50)
    print("CortexFlow — ETL Pipeline Start")
    print("=" * 50)

    # Шаг 1: Extract — извлекаем данные из PostgreSQL
    print("\n[1/3] EXTRACT: Читаем данные из PostgreSQL...")
    extractor = PostgresExtractor()

    telemetry_df = extractor.extract_telemetry()
    events_df = extractor.extract_events()
    embeddings_df = extractor.extract_embeddings()

    # Показываем, что получили
    print("\n=== Телеметрия (первые 3 строки) ===")
    print(telemetry_df.head(3))

    print("\n=== События (первые 3 строки) ===")
    print(events_df.head(3))

    print("\n=== Эмбеддинги (первые 3 строки) ===")
    print(embeddings_df.head(3))

    # Шаг 2: Transform — пока просто выводим инфо
    print("\n[2/3] TRANSFORM: (будет добавлено позже)")

    # Шаг 3: Load — пока просто выводим инфо
    print("\n[3/3] LOAD: (будет добавлено позже)")

    print("\n" + "=" * 50)
    print("ETL Pipeline — завершён (пока только Extract)")
    print("=" * 50)

# Шаг 2: Transform
    print("\n[2/3] TRANSFORM: Очищаем данные...")
    telemetry_clean = clean_telemetry(telemetry_df)
    events_clean = clean_events(events_df)

    print("\n=== Телеметрия после очистки ===")
    print(telemetry_clean[['timestamp', 'vehicle_id', 'speed', 'speed_zone', 'sensor_accuracy']].head())


# Шаг 3: Load в ClickHouse
    print("\n[3/4] LOAD: Загружаем данные в ClickHouse...")
    ch_loader = ClickHouseLoader()
    ch_loader.clean_telemetry()  # <--- ДОБАВЬ ЭТУ СТРОКУ
    ch_loader.load_telemetry(telemetry_clean)
    ch_loader.verify_load()


# Шаг 4: Load в Qdrant (векторная память для AI)
    print("\n[4/4] LOAD: Загружаем эмбеддинги в Qdrant...")
    qdrant_loader = QdrantLoader()
    qdrant_loader.create_collection(vector_size=4)  # У нас векторы из 4 чисел
    qdrant_loader.load_embeddings(embeddings_df)
    qdrant_loader.verify_load()

    # Шаг 5: Демонстрация семантического поиска
    print("\n[DEMO] Семантический поиск: 'робот увидел опасность'")
    # Имитируем эмбеддинг "опасной ситуации" (похож на obstacle_detected)
    danger_query = [0.90, 0.15, 0.40, 0.70]
    qdrant_loader.search_similar(danger_query, top_k=2)



if __name__ == "__main__":
    main()
