from typing import Annotated


from fastapi import FastAPI, HTTPException


app = FastAPI()


@app.get("/healthz")
def get_health():
    return {"status": "ok"}
