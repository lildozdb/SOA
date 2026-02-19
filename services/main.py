from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.get("/")
def read_root():
    return {"message": "Catalog Service is up"}
