from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.streamlit_manager.app import AppData
from core.streamlit_manager.app_manager import AppManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    AppManager.startup_event()
    yield
    AppManager.shutdown_event()


app = FastAPI(lifespan=lifespan)

@app.post("/app/")
async def create_app_endpoint(app: AppData):
    return AppManager.create_app(app)


@app.delete("/app/{id}")
async def delete_app_endpoint(id: str):
    return AppManager.delete_app(id)


@app.get("/app/{id}")
async def get_app_endpoint(id: str):
    return AppManager.get_app(id)


@app.get("/apps/")
async def get_apps_endpoint():
    return AppManager.list_apps()