-- =============================================
-- ФАЙЛ: insert_test_data.sql
-- НАЗНАЧЕНИЕ: Тестовые данные для CortexFlow
-- ОПИСАНИЕ: Примеры записей для всех трех таблиц
-- =============================================

-- ============================================
-- 1. ТЕЛЕМЕТРИЯ (robot_telemetry)
-- ============================================
-- Формат: timestamp, vehicle_id, lat, lon, alt, speed, sensor_id, reading_json

INSERT INTO robot_telemetry
(timestamp, vehicle_id, latitude, longitude, altitude, speed, sensor_id, reading_json)
VALUES
    -- Автомобиль 1: едет по Москве
    ('2026-09-22 10:00:00+00', '550e8400-e29b-41d4-a716-446655440001', 55.751244, 37.618423, 156.0, 45.5, 'gps', '{"accuracy": 2.5}'),
    ('2026-09-22 10:00:01+00', '550e8400-e29b-41d4-a716-446655440001', 55.751250, 37.618430, 156.0, 46.2, 'gps', '{"accuracy": 2.3}'),
    ('2026-09-22 10:00:02+00', '550e8400-e29b-41d4-a716-446655440001', 55.751260, 37.618440, 156.0, 47.0, 'gps', '{"accuracy": 2.4}'),

    -- Автомобиль 1: камера видит препятствие
    ('2026-09-22 10:00:02+00', '550e8400-e29b-41d4-a716-446655440001', 55.751260, 37.618440, 156.0, 47.0, 'camera', '{"objects_detected": 3, "distance_m": 15.5}'),
    ('2026-09-22 10:00:03+00', '550e8400-e29b-41d4-a716-446655440001', 55.751270, 37.618450, 156.0, 42.0, 'camera', '{"objects_detected": 2, "distance_m": 12.0}'),

    -- Автомобиль 2: стоит на месте
    ('2026-09-22 10:00:00+00', '550e8400-e29b-41d4-a716-446655440002', 55.755000, 37.620000, 150.0, 0.0, 'gps', '{"accuracy": 1.8}'),
    ('2026-09-22 10:00:01+00', '550e8400-e29b-41d4-a716-446655440002', 55.755000, 37.620000, 150.0, 0.0, 'imu', '{"accel_x": 0.01, "accel_y": 0.02, "accel_z": 9.81}'),

    -- Автомобиль 3: быстрая езда
    ('2026-09-22 10:00:00+00', '550e8400-e29b-41d4-a716-446655440003', 55.760000, 37.625000, 145.0, 85.5, 'gps', '{"accuracy": 3.1}'),
    ('2026-09-22 10:00:01+00', '550e8400-e29b-41d4-a716-446655440003', 55.760100, 37.625200, 145.0, 87.2, 'lidar', '{"points_count": 15000, "obstacles": 5}'),
    ('2026-09-22 10:00:02+00', '550e8400-e29b-41d4-a716-446655440003', 55.760200, 37.625400, 145.0, 88.0, 'lidar', '{"points_count": 14800, "obstacles": 4}')
;

-- ============================================
-- 2. СОБЫТИЯ (robot_events)
-- ============================================
-- Формат: timestamp, vehicle_id, event_type, severity, description, raw_data

INSERT INTO robot_events
(timestamp, vehicle_id, event_type, severity, description, raw_data)
VALUES
    ('2026-09-22 10:00:02+00', '550e8400-e29b-41d4-a716-446655440001', 'obstacle_detected', 'warning', 'Camera detected obstacle at distance 15.5 meters', '{"distance_m": 15.5, "confidence": 0.85}'),
    ('2026-09-22 10:00:03+00', '550e8400-e29b-41d4-a716-446655440001', 'braking', 'info', 'Automatic braking activated, speed reduced from 47 to 42 km/h', '{"speed_before": 47.0, "speed_after": 42.0}'),
    ('2026-09-22 10:00:01+00', '550e8400-e29b-41d4-a716-446655440003', 'high_speed', 'warning', 'Speed limit exceeded: 87.2 km/h in 60 km/h zone', '{"speed": 87.2, "limit": 60}'),
    ('2026-09-22 10:00:00+00', '550e8400-e29b-41d4-a716-446655440002', 'system_start', 'info', 'Autonomous driving system activated', '{"mode": "autonomous"}')
;

-- ============================================
-- 3. ЭМБЕДДИНГИ (embeddings)
-- ============================================
-- Формат: timestamp, vehicle_id, event_id, context, embedding
-- embedding - это вектор (массив чисел), здесь упрощенно 4 числа

INSERT INTO embeddings
(timestamp, vehicle_id, event_id, context, embedding)
VALUES
    ('2026-09-22 10:00:02+00', '550e8400-e29b-41d4-a716-446655440001',
     (SELECT id FROM robot_events WHERE event_type = 'obstacle_detected' AND vehicle_id = '550e8400-e29b-41d4-a716-446655440001' LIMIT 1),
     'Vehicle detected an obstacle on the road and started braking',
     '[0.85, 0.12, 0.45, 0.67]'),

    ('2026-09-22 10:00:01+00', '550e8400-e29b-41d4-a716-446655440003',
     (SELECT id FROM robot_events WHERE event_type = 'high_speed' AND vehicle_id = '550e8400-e29b-41d4-a716-446655440003' LIMIT 1),
     'Speed limit exceeded in urban zone, warning required',
     '[0.92, 0.08, 0.33, 0.71]')
;