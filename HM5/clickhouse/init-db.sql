CREATE DATABASE IF NOT EXISTS cinema_analytics;

USE cinema_analytics;

-- Основная таблица (Склад)
CREATE TABLE movie_events
(
    event_id UUID,
    user_id String,
    movie_id String,
    event_type String,
    timestamp DateTime64(3),
    device_type String,
    session_id String,
    progress_seconds Nullable(Int32)
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp)
PARTITION BY toYYYYMM(timestamp);

-- Таблица-слухач (Труба из Кафки)
CREATE TABLE kafka_movie_events
(
    event_id UUID,
    user_id String,
    movie_id String,
    event_type String,
    timestamp DateTime64(3),
    device_type String,
    session_id String,
    progress_seconds Nullable(Int32)
) ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka-1:29092,kafka-2:29093',
         kafka_topic_list = 'movie-events',
         kafka_group_name = 'clickhouse-consumer',
         kafka_format = 'AvroConfluent',
         format_avro_schema_registry_url = 'http://schema-registry:8081';

-- Насос (Перекладывает из Трубы на Склад)
CREATE MATERIALIZED VIEW movie_events_mv
TO movie_events
AS SELECT * FROM kafka_movie_events;
