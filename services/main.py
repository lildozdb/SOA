from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
def health_check():
    return JSONResponse(content={"status": "working"}, status_code=200)

@app.get("/")
def read_root():
    return {"message": "Catalog Service is up"}
