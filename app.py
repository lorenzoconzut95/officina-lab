from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from routes.tasks import router as tasks_router
from routes.activity import router as activity_router
from routes.agents import router as agents_router
from routes.runs import router as runs_router
from routes.memories import router as memories_router
from routes.approvals import router as approvals_router
from routes.tool_calls import router as tool_calls_router
from routes.errors import router as errors_router
from routes.incidents import router as incidents_router


app = FastAPI(
    title="Officina Lab API",
    version="1.3"
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
app.include_router(agents_router)
app.include_router(runs_router)
app.include_router(memories_router)
app.include_router(approvals_router)
app.include_router(tool_calls_router)
app.include_router(errors_router)
app.include_router(incidents_router)


init_db()
