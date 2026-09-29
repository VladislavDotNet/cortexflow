-- =============================================
-- ФАЙЛ: clickhouse_init.sql
-- НАЗНАЧЕНИЕ: Создание таблиц в ClickHouse
-- ОПИСАНИЕ: Аналитические таблицы для CortexFlow
-- =============================================

-- Таблица телеметрии (оптимизирована под аналитику)
CREATE TABLE IF NOT EXISTS cortexflow_analytics.telemetry_analytics (
    timestamp DateTime,
    vehicle_id String,
    latitude Float64,
    longitude Float64,
    altitude Float64,
    speed Float64,
    sensor_id String,
    speed_zone String,
    sensor_accuracy Float64
) ENGINE = MergeTree()
ORDER BY (timestamp, vehicle_id, sensor_id);