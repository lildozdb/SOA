import time
import uuid
import requests

API_URL = "http://movie-service:8000/publish"
CLICKHOUSE_URL = "http://clickhouse:8123/"

def test_pipeline():
    print("Запуск интеграционного теста...")
    
    test_session_id = f"test_session_{uuid.uuid4()}"
    
    test_event = {
        "user_id": "test_user",
        "movie_id": "test_movie",
        "event_type": "VIEW_STARTED",
        "device_type": "DESKTOP",
        "session_id": test_session_id,
        "progress_seconds": 0
    }

    print("Отправка события в Kafka...")
    response = requests.post(API_URL, json=test_event)
    assert response.status_code == 200, f"Ошибка API: {response.text}"
    print("Событие успешно отправлено!")

    print("Ожидание обработки данных (3 секунды)...")
    time.sleep(3)

    print("Поиск события в ClickHouse...")
    query = f"SELECT count() FROM cinema_analytics.movie_events WHERE session_id = '{test_session_id}'"
    
    ch_response = requests.get(
        CLICKHOUSE_URL, 
        params={"query": query},
        auth=("default", "password")
    )
    
    assert ch_response.status_code == 200, f"Ошибка ClickHouse: {ch_response.text}"
    
    count = int(ch_response.text.strip())
    
    if count > 0:
        print("ТЕСТ ПРОЙДЕН: Событие найдено в базе данных!")
    else:
        print("ТЕСТ ПРОВАЛЕН: Событие не найдено.")

if __name__ == "__main__":
    test_pipeline()