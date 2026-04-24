import os
import time
import psycopg2
from datetime import datetime
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka-1:29092,kafka-2:29093")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")
TOPIC_NAME = "movie-events"

PG_HOST = os.getenv("PG_HOST", "postgres")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "password")
PG_DB = os.getenv("PG_DB", "cinema_metrics")

time.sleep(20) 

#Настраиваем чтение схемы из Schema Registry
sr_client = SchemaRegistryClient({'url': SCHEMA_REGISTRY_URL})
avro_deserializer = AvroDeserializer(sr_client)

consumer_conf = {
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'metrics-aggregator',
    'auto.offset.reset': 'earliest',
    'value.deserializer': avro_deserializer
}
consumer = DeserializingConsumer(consumer_conf)
consumer.subscribe([TOPIC_NAME])

def update_metrics(dau, total_events):
    """Обновляет метрики в PostgreSQL"""
    try:
        conn = psycopg2.connect(host=PG_HOST, dbname=PG_DB, user=PG_USER, password=PG_PASSWORD)
        cur = conn.cursor()
        today = datetime.now().date()
        
        #Upsert: Вставляем новую строку или обновляем существующую
        cur.execute("""
            INSERT INTO daily_metrics (metric_date, dau, total_events)
            VALUES (%s, %s, %s)
            ON CONFLICT (metric_date) 
            DO UPDATE SET 
                dau = daily_metrics.dau + EXCLUDED.dau,
                total_events = daily_metrics.total_events + EXCLUDED.total_events;
        """, (today, dau, total_events))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"Метрики обновлены: +{dau} уник. юзеров, +{total_events} событий.")
    except Exception as e:
        print(f"Ошибка записи в БД: {e}")

print("Агрегатор запущен и читает данные...")

while True:
    users_seen = set()
    events_count = 0
    start_time = time.time()
    
    #Собираем окно из 10 секунд
    while time.time() - start_time < 10:
        msg = consumer.poll(1.0)
        if msg is None or msg.error():
            continue
        
        event = msg.value()
        if event:
            users_seen.add(event['user_id'])
            events_count += 1
            
    #Записываем пачку в базу
    if events_count > 0:
        update_metrics(len(users_seen), events_count)
