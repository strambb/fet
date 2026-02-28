from fastapi import FastAPI
from src.iam.api.router import iam_router

app = FastAPI()

app.include_router(iam_router)


@app.get("/healthz")
def get_health():
    return {"status": "ok"}
