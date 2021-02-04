from typing import Dict

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home() -> Dict[str, str]:
    return {"hello": "world"}
