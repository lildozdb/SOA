import uuid
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer

app = FastAPI(title="WMS Producer Service")

# Настройки Kafka
KAFKA_CONF = {
    'bootstrap.servers': 'kafka:9092',
    'schema.registry.url': 'http://schema-registry:8081'
}

# Загружаем схему Avro из файла
value_schema = avro.load("../schemas/warehouse_event.avsc")
producer = AvroProducer(KAFKA_CONF, default_value_schema=value_schema)

class WarehouseEvent(BaseModel):
    event_type: str  # PRODUCT_RECEIVED, PRODUCT_SHIPPED и т.д.
    product_id: str
    zone_id: str
    quantity: int

@app.post("/publish")
async def publish_event(event: WarehouseEvent):
    """Отправка одного события вручную через Swagger"""
    event_id = str(uuid.uuid4())
    
    # [span_3](start_span)[span_4](start_span)Формируем payload согласно схеме Avro[span_3](end_span)[span_4](end_span)
    payload = {
        "event_id": event_id,
        "event_type": event.event_type,
        "product_id": event.product_id,
        "zone_id": event.zone_id,
        "quantity": event.quantity,
        "timestamp": int(time.time() * 1000)
    }

    try:
        # [span_5](start_span)Используем product_id как ключ партиционирования[span_5](end_span)
        producer.produce(
            topic='warehouse-events',
            value=payload,
            key=event.product_id
        )
        producer.flush()
        return {"status": "sent", "event_id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "alive"}
