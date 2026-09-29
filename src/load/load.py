# ==============================================================================
# БЛОК 1: ИМПОРТЫ БИБЛИОТЕК И МОДУЛЕЙ
# Назначение: Подключение зависимостей для работы с ClickHouse и данными.
# ==============================================================================
import os  # Работа с переменными окружения (секреты, конфиги)
import logging  # Логирование процессов
import pandas as pd  # Работа с данными (DataFrame)
from typing import List, Dict, Any  # Типизация для списков и словарей
from clickhouse_driver import connect  # Официальный драйвер ClickHouse для Python
from clickhouse_driver.errors import Error as ClickHouseError  # Специфичные ошибки ClickHouse

# ==============================================================================
# БЛОК 2: НАСТРОЙКА ЛОГИРОВАНИЯ
# Назначение: Конфигурация логгера для отслеживания процесса загрузки.
# ==============================================================================
logging.basicConfig(  # Базовая настройка логгера
    level=logging.INFO,  # Уровень INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат вывода
    datefmt='%Y-%m-%d %H:%M:%S'  # Формат времени
)
logger = logging.getLogger(__name__)  # Создаем логгер с именем текущего модуля

# ==============================================================================
# БЛОК 3: КОНФИГУРАЦИЯ ПОДКЛЮЧЕНИЯ К CLICKHOUSE
# Назначение: Настройка параметров подключения к ClickHouse из переменных окружения.
# ==============================================================================
CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")  # Хост ClickHouse
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))  # Порт (9000 - нативный протокол, 8123 - HTTP)
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")  # Имя пользователя
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")  # Пароль (пусто по умолчанию для локалки)
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "ecommerce")  # Имя базы данных
CLICKHOUSE_TABLE = os.getenv("CLICKHOUSE_TABLE", "orders")  # Имя целевой таблицы
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100000"))  # Размер батча для вставки (ClickHouse любит большие батчи)


# ==============================================================================
# БЛОК 4: ФУНКЦИЯ ПОДКЛЮЧЕНИЯ К CLICKHOUSE
# Назначение: Создание и проверка подключения к ClickHouse.
# ==============================================================================
def get_clickhouse_connection():  # Функция возвращает объект подключения
    """  # Начало docstring
    Создает подключение к ClickHouse и проверяет его работоспособность.  # Описание
    """  # Конец docstring

    logger.info(f"Подключение к ClickHouse: {CLICKHOUSE_HOST}:{CLICKHOUSE_PORT}")  # Логируем параметры подключения

    try:  # Пытаемся подключиться
        connection = connect(  # Создаем подключение через clickhouse-driver
            host=CLICKHOUSE_HOST,  # Хост
            port=CLICKHOUSE_PORT,  # Порт
            user=CLICKHOUSE_USER,  # Пользователь
            password=CLICKHOUSE_PASSWORD,  # Пароль
            database=CLICKHOUSE_DATABASE  # База данных
        )

        # Проверяем подключение выполнением простого запроса
        connection.execute("SELECT 1")  # Если подключение работает, вернет [(1,)]
        logger.info("Подключение к ClickHouse успешно установлено")  # Логируем успех
        return connection  # Возвращаем объект подключения

    except ClickHouseError as e:  # Ловим специфичные ошибки ClickHouse
        logger.error(f"Ошибка подключения к ClickHouse: {e}")  # Логируем ошибку
        raise  # Пробрасываем исключение дальше


# ==============================================================================
# БЛОК 5: ФУНКЦИЯ ПОДГОТОВКИ ДАННЫХ ДЛЯ CLICKHOUSE
# Назначение: Конвертация pandas DataFrame в формат, подходящий для ClickHouse.
# ==============================================================================
def prepare_data_for_clickhouse(df: pd.DataFrame) -> List[Dict[str, Any]]:  # Функция возвращает список словарей
    """  # Начало docstring
    Конвертирует DataFrame в список словарей, обрабатывая специфичные типы данных.  # Описание
    """  # Конец docstring

    logger.info("Подготовка данных для ClickHouse")  # Логируем старт

    # Конвертируем DataFrame в список словарей (каждая строка = один словарь)
    records = df.to_dict(orient='records')  # orient='records' дает [{col1: val1, col2: val2}, ...]

    # Обработка специфичных типов данных для ClickHouse
    for record in records:  # Проходим по каждой записи
        # Конвертируем pandas Timestamp в Python datetime (ClickHouse понимает datetime)
        for key, value in record.items():  # Проходим по каждой колонке
            if pd.isna(value):  # Если значение NaN/None
                record[key] = None  # Заменяем на None (ClickHouse воспримет как NULL)
            elif isinstance(value, pd.Timestamp):  # Если это pandas Timestamp
                record[key] = value.to_pydatetime()  # Конвертируем в Python datetime

    logger.info(f"Подготовлено {len(records)} записей для загрузки")  # Логируем количество
    return records  # Возвращаем список словарей


# ==============================================================================
# БЛОК 6: ФУНКЦИЯ БАТЧЕВОЙ ЗАГРУЗКИ В CLICKHOUSE
# Назначение: Эффективная вставка данных большими батчами для производительности.
# ==============================================================================
def batch_insert(connection, table_name: str, records: List[Dict[str, Any]]) -> None:  # Функция ничего не возвращает
    """  # Начало docstring
    Выполняет батчевую вставку данных в ClickHouse для максимальной производительности.  # Описание
    """  # Конец docstring

    if not records:  # Если список записей пустой
        logger.warning("Нет данных для загрузки")  # Логируем предупреждение
        return  # Завершаем функцию

    logger.info(f"Начало загрузки {len(records)} записей в таблицу {table_name}")  # Логируем старт

    try:  # Пытаемся выполнить вставку
        # Получаем список колонок из первой записи
        columns = list(records[0].keys())  # Берем ключи первого словаря как имена колонок
        columns_str = ', '.join(columns)  # Формируем строку: "col1, col2, col3"

        # Формируем SQL-запрос для вставки
        insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES"  # Шаблон INSERT запроса

        # Разбиваем данные на батчи для эффективной загрузки
        total_batches = (len(records) + BATCH_SIZE - 1) // BATCH_SIZE  # Считаем количество батчей (с округлением вверх)

        for batch_num in range(total_batches):  # Проходим по каждому батчу
            start_idx = batch_num * BATCH_SIZE  # Начальный индекс текущего батча
            end_idx = min((batch_num + 1) * BATCH_SIZE, len(records))  # Конечный индекс (не больше длины списка)
            batch = records[start_idx:end_idx]  # Извлекаем текущий батч

            # Конвертируем список словарей в список кортежей (требование clickhouse-driver)
            batch_tuples = [tuple(record[col] for col in columns) for record in
                            batch]  # [(val1, val2), (val3, val4), ...]

            # Выполняем вставку батча
            connection.execute(insert_query, batch_tuples)  # execute() автоматически формирует VALUES

            logger.info(f"Загружен батч {batch_num + 1}/{total_batches} ({len(batch)} записей)")  # Логируем прогресс

        logger.info(f"Успешно загружено {len(records)} записей в {table_name}")  # Логируем завершение

    except ClickHouseError as e:  # Ловим ошибки ClickHouse
        logger.error(f"Ошибка при загрузке в {table_name}: {e}")  # Логируем ошибку
        raise  # Пробрасываем исключение дальше


# ==============================================================================
# БЛОК 7: ФУНКЦИЯ ВАЛИДАЦИИ ПОСЛЕ ЗАГРУЗКИ
# Назначение: Проверка корректности загрузки данных в ClickHouse.
# ==============================================================================
def validate_load(connection, table_name: str, expected_count: int) -> bool:  # Функция возвращает True/False
    """  # Начало docstring
    Проверяет, что количество загруженных строк соответствует ожидаемому.  # Описание
    """  # Конец docstring

    logger.info(f"Валидация загрузки в таблицу {table_name}")  # Логируем старт

    try:  # Пытаемся выполнить проверку
        # Считаем количество строк в таблице
        result = connection.execute(f"SELECT count() FROM {table_name}")  # Возвращает [(count,)]
        actual_count = result[0][0]  # Извлекаем число из результата

        logger.info(f"Ожидаемое количество: {expected_count}, фактическое: {actual_count}")  # Логируем сравнение

        if actual_count >= expected_count:  # Если фактическое >= ожидаемого (может быть больше из-за предыдущих загрузок)
            logger.info("Валидация загрузки успешно пройдена")  # Логируем успех
            return True  # Возвращаем True
        else:  # Если меньше
            logger.error(f"Загружено меньше записей, чем ожидалось!")  # Логируем ошибку
            return False  # Возвращаем False

    except ClickHouseError as e:  # Ловим ошибки ClickHouse
        logger.error(f"Ошибка при валидации: {e}")  # Логируем ошибку
        return False  # Возвращаем False


# ==============================================================================
# БЛОК 8: ГЛАВНАЯ ФУНКЦИЯ ЗАГРУЗКИ (ОРКЕСТРАЦИЯ ПРОЦЕССА)
# Назначение: Объединяет все этапы загрузки в единый пайплайн.
# ==============================================================================
def load(df: pd.DataFrame) -> None:  # Главная функция, принимает DataFrame, ничего не возвращает
    """  # Начало docstring
    Оркестрирует весь процесс загрузки: подключение -> подготовка -> вставка -> валидация.  # Описание
    """  # Конец docstring

    logger.info("=" * 50)  # Логируем разделитель
    logger.info("НАЧАЛО ПРОЦЕССА ЗАГРУЗКИ")  # Логируем старт
    logger.info("=" * 50)  # Логируем разделитель

    connection = None  # Инициализируем переменную для подключения (чтобы закрыть в finally)

    try:  # Оборачиваем весь процесс в try-except
        # ЭТАП 1: Подключение к ClickHouse
        connection = get_clickhouse_connection()  # Создаем подключение

        # ЭТАП 2: Подготовка данных
        records = prepare_data_for_clickhouse(df)  # Конвертируем DataFrame в список словарей

        if not records:  # Если данных нет
            logger.warning("Нет данных для загрузки. Завершение.")  # Логируем предупреждение
            return  # Завершаем функцию

        # ЭТАП 3: Батчевая загрузка
        batch_insert(connection, CLICKHOUSE_TABLE, records)  # Выполняем вставку

        # ЭТАП 4: Валидация после загрузки
        is_valid = validate_load(connection, CLICKHOUSE_TABLE, len(records))  # Проверяем корректность

        if not is_valid:  # Если валидация не пройдена
            logger.error("Валидация загрузки не пройдена!")  # Логируем ошибку
            raise ValueError("Load validation failed")  # Прерываем выполнение с ошибкой

        logger.info("=" * 50)  # Логируем разделитель
        logger.info("ПРОЦЕСС ЗАГРУЗКИ УСПЕШНО ЗАВЕРШЕН")  # Логируем успешное завершение
        logger.info("=" * 50)  # Логируем разделитель

    except Exception as e:  # Ловим любую ошибку в процессе
        logger.critical(f"Критическая ошибка в процессе загрузки: {e}", exc_info=True)  # Логируем с трейсбеком
        raise  # Пробрасываем ошибку дальше

    finally:  # Выполняется всегда (даже если была ошибка)
        if connection:  # Если подключение было создано
            connection.disconnect()  # Закрываем подключение к ClickHouse
            logger.info("Подключение к ClickHouse закрыто")  # Логируем закрытие


# ==============================================================================
# БЛОК 9: ТОЧКА ВХОДА (MAIN)
# Назначение: Позволяет запускать скрипт напрямую из консоли для тестирования.
# ==============================================================================
if __name__ == "__main__":  # Стандартная проверка: код выполнится только при прямом запуске
    # Пример тестовых данных (в реальности DataFrame придет из transform.py)
    test_data = {  # Создаем тестовый словарь
        'order_id': [1, 2, 3],  # ID заказов
        'customer_id': [100, 101, 102],  # ID клиентов
        'amount': [150.50, 200.00, 75.25],  # Суммы заказов
        'status': ['COMPLETED', 'PENDING', 'CANCELLED'],  # Статусы
        'created_at': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03'])  # Даты создания
    }

    test_df = pd.DataFrame(test_data)  # Создаем DataFrame из тестовых данных

    load(test_df)  # Вызываем главную функцию загрузки с тестовыми данными



#💡 Ключевые особенности этого шаблона для ClickHouse:

    Батчевая загрузка: ClickHouse оптимизирован для вставки большими батчами (100k+ строк). BATCH_SIZE = 100000 — стандарт для production.
    Нативный протокол (порт 9000): Используется вместо HTTP (8123) для максимальной производительности.
    Обработка типов данных: ClickHouse строг к типам. Функция prepare_data_for_clickhouse() конвертирует pandas Timestamp в Python datetime.
    Валидация после загрузки: Проверяем, что данные действительно записались. Это критично для аналитических БД.
    Закрытие подключения в finally: Гарантирует, что подключение закроется даже при ошибке.