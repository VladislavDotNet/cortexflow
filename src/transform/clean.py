# =============================================
# ФАЙЛ: clean.py
# НАЗНАЧЕНИЕ: Очистка и подготовка телеметрии
# ОПИСАНИЕ: Обрабатывает сырые данные для
#           дальнейшей загрузки в ClickHouse
# =============================================

import pandas as pd
import json


def clean_telemetry(df: pd.DataFrame) -> pd.DataFrame:
    """
    Очищает DataFrame телеметрии:
    1. Заполняет пропуски
    2. Извлекает данные из JSON
    3. Добавляет вычисляемые поля
    """
    df = df.copy()  # Не мутируем оригинал

    # 1. Заполняем пропуски в числовых полях нулями
    numeric_cols = ['latitude', 'longitude', 'altitude', 'speed']
    df[numeric_cols] = df[numeric_cols].fillna(0.0)

    # 2. Извлекаем данные из reading_json (если есть)
    # Пример: {'accuracy': 2.5} -> колонка sensor_accuracy
    if 'reading_json' in df.columns:
        # Преобразуем JSON строки в словари
        df['reading_parsed'] = df['reading_json'].apply(
            lambda x: json.loads(x) if isinstance(x, str) else x
        )

        # Извлекаем accuracy (если есть)
        df['sensor_accuracy'] = df['reading_parsed'].apply(
            lambda x: x.get('accuracy', None) if isinstance(x, dict) else None
        )

    # 3. Добавляем вычисляемое поле: зона скорости
    def get_speed_zone(speed):
        if speed == 0:
            return 'stopped'
        elif speed < 40:
            return 'slow'
        elif speed < 80:
            return 'medium'
        else:
            return 'fast'

    df['speed_zone'] = df['speed'].apply(get_speed_zone)

    # 4. Удаляем временные колонки
    if 'reading_parsed' in df.columns:
        df = df.drop(columns=['reading_parsed'])

    print(f"[Clean] Обработано {len(df)} записей")
    return df


def clean_events(df: pd.DataFrame) -> pd.DataFrame:
    """Очищает DataFrame событий."""
    df = df.copy()

    # Заполняем пропуски в description
    if 'description' in df.columns:
        df['description'] = df['description'].fillna('No description')

    print(f"[Clean] Обработано {len(df)} событий")
    return df