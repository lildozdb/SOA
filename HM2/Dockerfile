FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -c "import subprocess; subprocess.run(['fastapi-codegen', '--input', 'src/main/resources/openapi/openapi.yaml', '--output', 'generated_app'], check=True)"
EXPOSE 8000
CMD ["uvicorn", "generated_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
