-- =============================================
-- ФАЙЛ: init_tables.sql
-- НАЗНАЧЕНИЕ: Создание таблиц для проекта CortexFlow
-- ОПИСАНИЕ: Инициализация схемы БД для хранения
--           телеметрии, событий и эмбеддингов.
-- =============================================

-- Таблица 1: Сырая телеметрия с автомобилей (KITTI)
CREATE TABLE IF NOT EXISTS robot_telemetry (
    timestamp TIMESTAMPTZ NOT NULL,
    vehicle_id UUID NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    altitude DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    sensor_id VARCHAR(50) NOT NULL,
    reading_json JSONB,
    PRIMARY KEY (timestamp, vehicle_id, sensor_id)
);

-- Таблица 2: События (маневры, препятствия, ошибки)
CREATE TABLE IF NOT EXISTS robot_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    vehicle_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'info',
    description TEXT,
    raw_data JSONB
);

-- Таблица 3: Эмбеддинги для AI (векторная память)
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL,
    vehicle_id UUID NOT NULL,
    event_id UUID REFERENCES robot_events(id),
    context TEXT,
    embedding JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Индексы для ускорения поиска (закрепляем классический DE)
CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle ON robot_telemetry(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_events_vehicle ON robot_events(vehicle_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON robot_events(event_type);
CREATE INDEX IF NOT EXISTS idx_embeddings_vehicle ON embeddings(vehicle_id);