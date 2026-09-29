# =============================================
# ФАЙЛ: embedding_generator.py
# НАЗНАЧЕНИЕ: Генерация настоящих эмбеддингов из текста
# ОПИСАНИЕ: Превращает описания ситуаций в векторы
#           через модель all-MiniLM-L6-v2 (384 измерения)
# =============================================

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


class EmbeddingGenerator:
    """
    Класс для генерации эмбеддингов из текста.
    Модель понимает СМЫСЛ фразы и кодирует его в 384 числа.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # При первом запуске модель скачается с HuggingFace (~90MB)
        print(f"[EmbeddingGenerator] Загружаю модель {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("[EmbeddingGenerator] Модель загружена")

    def generate(self, text: str) -> list:
        """Генерирует эмбеддинг (вектор из 384 чисел) для одного текста."""
        vector = self.model.encode(text)
        return vector.tolist()

    def generate_batch(self, texts: list) -> list:
        """Генерирует эмбеддинги пачкой — так быстрее, чем по одному."""
        vectors = self.model.encode(texts, batch_size=8)
        return [v.tolist() for v in vectors]


# ============================================
# Быстрый тест семантики (запуск файла напрямую)
# ============================================
if __name__ == "__main__":
    gen = EmbeddingGenerator()

    texts = [
        "Robot detected obstacle and started braking",
        "Car noticed pedestrian and stopped",
        "Warehouse system generated sales report",
    ]

    # ВОТ ЭТА СТРОКА ПОТЕРЯЛАСЬ — генерируем векторы из текстов
    vectors = gen.generate_batch(texts)
    print(f"Размерность вектора: {len(vectors[0])}")

    # Правильный способ: используем встроенный метод модели
    similarity_12 = gen.model.similarity(vectors[0], vectors[1]).item()
    similarity_13 = gen.model.similarity(vectors[0], vectors[2]).item()

    print(f"Сходство 1 и 2 (обе про опасность): {similarity_12:.3f}")
    print(f"Сходство 1 и 3 (отчёт о продажах): {similarity_13:.3f}")