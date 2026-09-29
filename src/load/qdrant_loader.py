# =============================================
# ФАЙЛ: qdrant_loader.py
# НАЗНАЧЕНИЕ: Загрузка эмбеддингов в Qdrant
# ОПИСАНИЕ: Создаёт коллекцию и загружает векторы
#           для семантического поиска (AI память)
# =============================================

import json
import pandas as pd
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from src.utils.config import QDRANT_CONFIG


class QdrantLoader:
    """
    Класс для работы с векторной БД Qdrant.
    Хранит эмбеддинги роботов для AI-поиска.
    """

    def __init__(self):
        # Подключаемся к Qdrant
        self.client = QdrantClient(
            host=QDRANT_CONFIG['host'],
            port=QDRANT_CONFIG['port'],
        )
        self.collection_name = "robot_memory"
        print(f"[QdrantLoader] Подключено к {QDRANT_CONFIG['host']}:{QDRANT_CONFIG['port']}")

    def create_collection(self, vector_size: int = 4):
        """
        Создаёт коллекцию для хранения эмбеддингов.

        vector_size: размерность вектора (у нас 4 из тестовых данных)
        В реальных проектах обычно 768, 1024 или 1536 (OpenAI embeddings)
        """
        # Проверяем, существует ли коллекция
        collections = [c.name for c in self.client.get_collections().collections]

        if self.collection_name in collections:
            print(f"[QdrantLoader] Коллекция '{self.collection_name}' уже существует — удаляем для чистой загрузки")
            self.client.delete_collection(self.collection_name)

        # Создаём новую коллекцию
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE  # Косинусное расстояние — стандарт для эмбеддингов
            ),
        )
        print(f"[QdrantLoader] Коллекция '{self.collection_name}' создана (размерность: {vector_size})")

    def load_embeddings(self, df) -> int:
        """
        Загружает DataFrame с эмбеддингами в Qdrant.

        Каждая запись превращается в "точку" (Point):
        - id: уникальный номер
        - vector: сам эмбеддинг [0.85, 0.12, ...]
        - payload: метаданные (context, vehicle_id, event_id)
        """
        points = []

        for idx, row in df.iterrows():
            # Парсим вектор из JSON строки '[0.85, 0.12, 0.45, 0.67]'
            embedding_str = row['embedding']
            if isinstance(embedding_str, str):
                vector = json.loads(embedding_str)
            else:
                vector = embedding_str

            # Формируем метаданные (payload)
            payload = {
                "vehicle_id": str(row['vehicle_id']),
                "context": row['context'],
                "timestamp": str(row['timestamp']),
            }

            # Добавляем event_id, если колонка существует и значение не пустое (не NaN)
            if 'event_id' in row.index and pd.notna(row['event_id']):
                payload["event_id"] = str(row['event_id'])

            # Создаём точку
            points.append(
                PointStruct(
                    id=idx + 1,  # Qdrant требует int id, не UUID
                    vector=vector,
                    payload=payload,
                )
            )

        # Загружаем пачкой в Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

        print(f"[QdrantLoader] Загружено {len(points)} эмбеддингов в '{self.collection_name}'")
        return len(points)

    def search_similar(self, query_vector: list, top_k: int = 3) -> list:
        """
        Семантический поиск: найти самые похожие "воспоминания" робота.
        (новый API qdrant-client 1.12+: query_points вместо search)
        """
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
        )
        results = response.points  # Новый API возвращает объект, у которого точки лежат в .points

        print(f"\n[QdrantLoader] Найдено {len(results)} похожих воспоминаний:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. Score: {result.score:.4f} | Context: {result.payload['context']}")

        return results

    def verify_load(self) -> int:
        """Проверяет количество точек в коллекции."""
        info = self.client.get_collection(self.collection_name)
        count = info.points_count
        print(f"[QdrantLoader] В коллекции '{self.collection_name}': {count} векторов")
        return count

