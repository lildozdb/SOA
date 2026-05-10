CREATE KEYSPACE IF NOT EXISTS warehouse WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE warehouse;

-[span_12](start_span)- 1. Остатки по товару и зоне (Запрос: сколько SKU-1 в ZONE-A?)[span_12](end_span)
CREATE TABLE IF NOT EXISTS inventory_by_product_zone (
    product_id text,
    zone_id text,
    [span_13](start_span)available_quantity counter, -- Используем counter для атомарных изменений[span_13](end_span)
    reserved_quantity counter,
    PRIMARY KEY ((product_id), zone_id)
);

-[span_14](start_span)- 2. Остатки товара в целом (Запрос: сколько всего SKU-1 на складе?)[span_14](end_span)
CREATE TABLE IF NOT EXISTS inventory_by_product (
    product_id text,
    total_available counter,
    PRIMARY KEY (product_id)
);

-[span_15](start_span)- 3. Товары в зоне (Запрос: что лежит в ZONE-A?)[span_15](end_span)
CREATE TABLE IF NOT EXISTS inventory_by_zone (
    zone_id text,
    product_id text,
    available_quantity counter,
    PRIMARY KEY ((zone_id), product_id)
);

-[span_16](start_span)- 4. Таблица для идемпотентности (Запрос: обрабатывали ли мы этот event_id?)[span_16](end_span)
CREATE TABLE IF NOT EXISTS processed_events (
    event_id uuid PRIMARY KEY,
    processed_at timestamp
);
