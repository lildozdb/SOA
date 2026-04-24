FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential librdkafka-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aggregator.py .

CMD ["python", "aggregator.py"]