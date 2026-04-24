import os
import time
import uuid
import random
import asyncio
from datetime import datetime, timezone
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from confluent_kafka import SerializingProducer
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import StringSerializer

app = FastAPI(title="Movie Service API")

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka-1:29092,kafka-2:29093")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "http://schema-registry:8081")
TOPIC_NAME = "movie-events"

with open("movie_event.avsc", "r") as f:
    schema_str = f.read()

schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)
avro_serializer = AvroSerializer(schema_registry_client, schema_str)

producer_conf = {
    'bootstrap.servers': KAFKA_BROKERS,
    'acks': 'all',                      # Ждем подтверждения от всех реплик
    'retries': 5,                       # Количество попыток при ошибке
    'retry.backoff.ms': 500,            # Задержка между попытками
    'key.serializer': StringSerializer('utf_8'),
    'value.serializer': avro_serializer
}
producer = SerializingProducer(producer_conf)

#Создание топика при старте
def create_topic():
    admin_client = AdminClient({'bootstrap.servers': KAFKA_BROKERS})
    topic_list = []
    topic_list.append(NewTopic(TOPIC_NAME, num_partitions=3, replication_factor=2))
    admin_client.create_topics(topic_list)
    print(f"Topic {TOPIC_NAME} checked/created.")

# Pydantic модель для валидации входящих JSON запросов
class MovieEventPayload(BaseModel):
    user_id: str
    movie_id: str
    event_type: str
    device_type: str
    session_id: str
    progress_seconds: int | None = None

def delivery_report(err, msg):
    """ Коллбэк для логирования статуса отправки """
    if err is not None:
        print(f"Ошибка доставки сообщения: {err}")
    else:
        print(f"Событие доставлено в {msg.topic()} [Партиция: {msg.partition()}]")

@app.on_event("startup")
async def startup_event():
    time.sleep(10)
    create_topic()

@app.post("/publish")
async def publish_event(event: MovieEventPayload):
    event_id = str(uuid.uuid4())
    timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    
    #Cловарь под Avro схему
    avro_payload = {
        "event_id": event_id,
        "user_id": event.user_id,
        "movie_id": event.movie_id,
        "event_type": event.event_type,
        "timestamp": timestamp_ms,
        "device_type": event.device_type,
        "session_id": event.session_id,
        "progress_seconds": event.progress_seconds
    }

    try:
        #Отправляем в Kafka. Ключ партиционирования - user_id!
        producer.produce(
            topic=TOPIC_NAME,
            key=event.user_id,
            value=avro_payload,
            on_delivery=delivery_report
        )
        producer.poll(0)
        return {"status": "success", "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_fake_traffic():
    event_types = ["VIEW_STARTED", "VIEW_FINISHED", "VIEW_PAUSED", "VIEW_RESUMED", "LIKED", "SEARCHED"]
    devices = ["MOBILE", "DESKTOP", "TV", "TABLET"]
    
    while True:
        user_id = f"user_{random.randint(1, 100)}"
        movie_id = f"movie_{random.randint(1, 20)}"
        payload = MovieEventPayload(
            user_id=user_id,
            movie_id=movie_id,
            event_type=random.choice(event_types),
            device_type=random.choice(devices),
            session_id=str(uuid.uuid4()),
            progress_seconds=random.randint(10, 5000) if random.random() > 0.3 else None
        )
        await publish_event(payload)
        await asyncio.sleep(2) # Генерируем событие каждые 2 секунды

@app.post("/start-generator")
async def start_generator(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_fake_traffic)
    return {"status": "Генератор трафика запущен"}