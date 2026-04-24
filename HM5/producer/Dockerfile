FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential librdkafka-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем наш код и схему
COPY main.py .
COPY movie_event.avsc .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
