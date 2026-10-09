from prefect import flow, task
from src.extract.postgres_extractor import PostgresExtractor
from src.transform.clean import clean_telemetry, clean_events
from src.transform.embedding_enricher import EmbeddingEnricher
from src.load.clickhouse_loader import ClickHouseLoader
from src.load.qdrant_loader import QdrantLoader


@task
def extract_data():
    extractor = PostgresExtractor()
    telemetry_df = extractor.extract_telemetry()
    events_df = extractor.extract_events()
    embeddings_df = extractor.extract_embeddings()
    return telemetry_df, events_df, embeddings_df


@task
def transform_data(telemetry_df, events_df, embeddings_df):
    telemetry_clean = clean_telemetry(telemetry_df)
    events_clean = clean_events(events_df)
    enricher = EmbeddingEnricher()
    embeddings_real = enricher.enrich(embeddings_df)
    enricher.update_postgres(embeddings_real)
    return telemetry_clean, events_clean, embeddings_real


@task
def load_data(telemetry_clean, events_clean, embeddings_real):
    ch_loader = ClickHouseLoader()
    ch_loader.clean_telemetry()
    ch_loader.load_telemetry(telemetry_clean)
    ch_loader.verify_load()

    qdrant_loader = QdrantLoader()
    qdrant_loader.create_collection(vector_size=384)
    qdrant_loader.load_embeddings(embeddings_real)
    qdrant_loader.verify_load()


@flow(name="CortexFlow ETL")
def cortexflow_etl():
    telemetry_df, events_df, embeddings_df = extract_data()
    telemetry_clean, events_clean, embeddings_real = transform_data(
        telemetry_df, events_df, embeddings_df
    )
    load_data(telemetry_clean, events_clean, embeddings_real)


if __name__ == "__main__":
    cortexflow_etl()