from fastapi import FastAPI

from database import init_db
from routes.tasks import router as tasks_router


app = FastAPI(
    title="Officina Lab API",
    version="0.5"
)


@app.get("/")
def home():
    return {
        "project": "Officina Lab",
        "version": "0.5",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


app.include_router(tasks_router)


init_db()