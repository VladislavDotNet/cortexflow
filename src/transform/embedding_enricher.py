# =============================================
# ФАЙЛ: embedding_enricher.py
# НАЗНАЧЕНИЕ: Замена фейковых эмбеддингов на настоящие
# ОПИСАНИЕ: Берёт текст context, прогоняет через ML-модель
#           и обновляет векторы в PostgreSQL и пайплайне
# =============================================

import json
import pandas as pd
from sqlalchemy import create_engine, text
from src.utils.config import POSTGRES_URL
from src.transform.embedding_generator import EmbeddingGenerator


class EmbeddingEnricher:
    """
    Класс-обогатитель: превращает текст в настоящие эмбеддинги.
    Это ключевой мост между классическим DE и Data for AI.
    """

    def __init__(self):
        self.engine = create_engine(POSTGRES_URL)
        self.generator = EmbeddingGenerator()  # Модель грузится один раз

    def enrich(self, embeddings_df: pd.DataFrame) -> pd.DataFrame:
        """
        Берёт колонку context, генерирует векторы пачкой
        и заменяет ими фейковую колонку embedding.
        """
        df = embeddings_df.copy()

        # Все тексты разом — batch намного быстрее по одному
        contexts = df['context'].tolist()
        vectors = self.generator.generate_batch(contexts)

        # Подменяем фейковые векторы [0.85, ...] на настоящие (384 числа)
        df['embedding'] = vectors

        print(f"[EmbeddingEnricher] Сгенерировано {len(vectors)} настоящих эмбеддингов (384 dim)")
        return df

    def update_postgres(self, df: pd.DataFrame):
        """
        Обновляет колонку embedding в PostgreSQL.
        Source of truth должен хранить настоящие векторы, а не заглушки.
        """
        with self.engine.connect() as conn:
            for _, row in df.iterrows():
                conn.execute(
                    text("UPDATE embeddings SET embedding = :emb WHERE id = :id"),
                    {"emb": json.dumps(row['embedding']), "id": str(row['id'])},
                )
            conn.commit()
        print(f"[EmbeddingEnricher] PostgreSQL обновлён: {len(df)} записей")