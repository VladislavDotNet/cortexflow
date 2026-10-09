# CortexFlow

ETL-пайплайн для обработки телеметрии автономных роботов с семантическим поиском.

## Что делает

Берёт сырые данные из PostgreSQL (телеметрия GPS, события с камер, лидаров), очищает, генерирует векторные эмбеддинги через MiniLM и раскладывает по двум хранилищам:
- ClickHouse — для аналитики и агрегаций
- Qdrant — для семантического поиска по событиям

Плюс REST API на FastAPI, чтобы робот мог спросить "что происходило когда я видел препятствие?" и получить похожие ситуации из памяти.

## Как запустить

```bash
docker-compose up -d
```

## Что внутри

    src/extract/ — читает из Postgres
    src/transform/ — чистит данные и генерирует эмбеддинги (MiniLM-L6-v2, 384 измерения)
    src/load/ — пишет в ClickHouse и Qdrant
    api/ — FastAPI сервис для семантического поиска
    tests/ — pytest на трансформации
    prefect_flow.py — оркестрация пайплайна через Prefect
    .github/workflows/ — CI на GitHub Actions

## Стек
Postgres → Pandas → ClickHouse + Qdrant → FastAPI → Grafana

Оркестрация: Prefect
CI: GitHub Actions + pytest
Мониторинг: Grafana дашборд по ClickHouse
## Что не сделано

    Healthcheck у Qdrant закомментирован — в официальном образе нет curl, чинить через sidecar-контейнер
    MinIO для data lake не добавлен — проблемы с доступом к Docker-образам из региона
    Данные тестовые, не KITTI — для продакшена нужно подключить реальный датасет

Автор
Vladislav DE


