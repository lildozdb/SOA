FROM python:3.10-slim

RUN apt-get update && apt-get install -y libpq-dev gcc
WORKDIR /app
COPY . /app/
RUN pip install grpcio grpcio-tools sqlalchemy psycopg2-binary protobuf

CMD ["python", "main.py"]