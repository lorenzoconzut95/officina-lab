from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from routes.tasks import router as tasks_router
from routes.activity import router as activity_router


app = FastAPI(
    title="Officina Lab API",
    version="0.7"
)


app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


@app.get("/")
def home():
    return FileResponse(
        "static/index.html",
        media_type="text/html"
    )


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


app.include_router(tasks_router)
app.include_router(activity_router)


init_db()
