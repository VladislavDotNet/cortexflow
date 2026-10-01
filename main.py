# =============================================
# ФАЙЛ: main.py
# НАЗНАЧЕНИЕ: Точка входа в проект CortexFlow
# ОПИСАНИЕ: Запускает ETL пайплайн
# =============================================

from src.extract.postgres_extractor import PostgresExtractor
from src.transform.clean import clean_telemetry, clean_events
from src.transform.embedding_enricher import EmbeddingEnricher
from src.load.clickhouse_loader import ClickHouseLoader
from src.load.qdrant_loader import QdrantLoader


def main():
    print("=" * 50)
    print("CortexFlow — ETL Pipeline Start")
    print("=" * 50)

    # Шаг 1: Extract
    print("\n[1/4] EXTRACT: Читаем данные из PostgreSQL...")
    extractor = PostgresExtractor()
    telemetry_df = extractor.extract_telemetry()
    events_df = extractor.extract_events()
    embeddings_df = extractor.extract_embeddings()

    # Шаг 2: Transform (очистка)
    print("\n[2/4] TRANSFORM: Очищаем данные...")
    telemetry_clean = clean_telemetry(telemetry_df)
    events_clean = clean_events(events_df)

    # Шаг 2.5: Transform (генерация настоящих эмбеддингов)
    print("\n[2.5/4] TRANSFORM: Генерируем настоящие эмбеддинги из context...")
    enricher = EmbeddingEnricher()
    embeddings_real = enricher.enrich(embeddings_df)
    enricher.update_postgres(embeddings_real)

    # Шаг 3: Load в ClickHouse
    print("\n[3/4] LOAD: Загружаем телеметрию в ClickHouse...")
    ch_loader = ClickHouseLoader()
    ch_loader.clean_telemetry()
    ch_loader.load_telemetry(telemetry_clean)
    ch_loader.verify_load()

    # Шаг 4: Load в Qdrant (векторная память, теперь 384 dim)
    print("\n[4/4] LOAD: Загружаем эмбеддинги в Qdrant...")
    qdrant_loader = QdrantLoader()
    qdrant_loader.create_collection(vector_size=384)
    qdrant_loader.load_embeddings(embeddings_real)
    qdrant_loader.verify_load()

    # Демо: семантический поиск ТЕКСТОВЫМ запросом
    print("\n[DEMO] Семантический поиск: 'robot sees danger on the road'")
    danger_query = enricher.generator.generate("robot sees danger on the road")
    qdrant_loader.search_similar(danger_query, top_k=2)

    print("\n" + "=" * 50)
    print("ETL Pipeline — завершён")
    print("=" * 50)


if __name__ == "__main__":
    main()