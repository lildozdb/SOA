import logging
from confluent_kafka import avro
from confluent_kafka.avro import AvroConsumer
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

# Настройка логов для фиксации факта обработки (требование 1.4)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("warehouse-consumer")

# Настройки
KAFKA_CONF = {
    'bootstrap.servers': 'kafka:9092',
    [span_6](start_span)'group.id': 'warehouse-state-consumer',  # Осмысленное имя группы[span_6](end_span)
    'schema.registry.url': 'http://schema-registry:8081',
    [span_7](start_span)'auto.offset.commit': False,  # Manual commit для At-least-once[span_7](end_span)
    'offset.store.method': 'broker'
}

# Подключение к Cassandra
cassandra_cluster = Cluster(['cassandra'])
session = cassandra_cluster.connect('warehouse')

def is_event_processed(event_id):
    [span_8](start_span)"""Проверка идемпотентности: было ли событие уже обработано[span_8](end_span)"""
    query = "SELECT event_id FROM processed_events WHERE event_id = %s"
    result = session.execute(query, [event_id])
    return result.one() is not None

def update_inventory(event):
    [span_9](start_span)[span_10](start_span)"""Логика обновления остатков в таблицах[span_9](end_span)[span_10](end_span)"""
    e_type = event['event_type']
    pid = event['product_id']
    zid = event['zone_id']
    qty = event['quantity']

    # [span_11](start_span)Базовая логика для 1-4 баллов: меняем доступное количество[span_11](end_span)
    # [span_12](start_span)На 5-7 баллов здесь будет использоваться BATCH[span_12](end_span)
    if e_type == 'PRODUCT_RECEIVED':
        op = "+"
    elif e_type == 'PRODUCT_SHIPPED':
        op = "-"
    else:
        return # Пока обрабатываем только простые типы

    # [span_13](start_span)[span_14](start_span)Обновляем все денормализованные таблицы[span_13](end_span)[span_14](end_span)
    queries = [
        f"UPDATE inventory_by_product_zone SET available_quantity = available_quantity {op} {qty} WHERE product_id='{pid}' AND zone_id='{zid}'",
        f"UPDATE inventory_by_product SET total_available = total_available {op} {qty} WHERE product_id='{pid}'",
        f"UPDATE inventory_by_zone SET available_quantity = available_quantity {op} {qty} WHERE zone_id='{zid}' AND product_id='{pid}'"
    ]
    
    for q in queries:
        session.execute(SimpleStatement(q))

def run_consumer():
    consumer = AvroConsumer(KAFKA_CONF)
    consumer.subscribe(['warehouse-events'])

    logger.info("Consumer started, waiting for events...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None: continue
            if msg.error():
                logger.error(f"Kafka error: {msg.error()}")
                continue

            event = msg.value()
            event_id = event['event_id']

            # 1. [span_15](start_span)[span_16](start_span)Проверка на дубликаты (Идемпотентность)[span_15](end_span)[span_16](end_span)
            if is_event_processed(event_id):
                logger.info(f"Skipping duplicate event: {event_id}")
                consumer.commit(msg) # Подтверждаем, чтобы не читать снова
                continue

            # 2. [span_17](start_span)Обработка и запись в Cassandra[span_17](end_span)
            try:
                update_inventory(event)
                # Помечаем событие как обработанное
                session.execute("INSERT INTO processed_events (event_id, processed_at) VALUES (%s, toTimestamp(now()))", [event_id])
                
                # 3. [span_18](start_span)At-least-once: коммитим только ПОСЛЕ успешной записи в БД[span_18](end_span)
                consumer.commit(msg)
                logger.info(f"Processed {event['event_type']} | ID: {event_id} | Offset: {msg.offset()}")
            
            except Exception as e:
                logger.error(f"Error processing event {event_id}: {e}")
                # [span_19](start_span)Если упали здесь, оффсет не закоммитится, и после рестарта мы попробуем снова[span_19](end_span)

    finally:
        consumer.close()

if __name__ == "__main__":
    run_consumer()
