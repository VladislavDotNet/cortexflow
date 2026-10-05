import pandas as pd
import sys
import os

# Добавляем корень проекта в путь, чтобы видеть src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.transform.clean import clean_telemetry


def test_clean_telemetry_fills_na_and_zones():
    # 1. Arrange (Подготовка тестовых данных с пропусками)
    df = pd.DataFrame({
        'timestamp': ['2023-01-01', '2023-01-02'],
        'vehicle_id': ['v1', 'v2'],
        'latitude': [None, 55.0],
        'longitude': [None, 37.0],
        'altitude': [100.0, 100.0],
        'speed': [0.0, 90.0],
        'sensor_id': ['gps', 'gps'],
        'reading_json': ['{"accuracy": 2.5}', None]
    })

    # 2. Act (Вызов функции)
    result_df = clean_telemetry(df)

    # 3. Assert (Проверка результата)
    # Пропуски заполнены нулями
    assert result_df['latitude'].iloc[0] == 0.0
    # Зоны скорости определены верно
    assert result_df['speed_zone'].iloc[0] == 'stopped'
    assert result_df['speed_zone'].iloc[1] == 'fast'
    # JSON распарсен корректно
    assert result_df['sensor_accuracy'].iloc[0] == 2.5