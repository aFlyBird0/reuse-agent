import uuid
from fastapi import FastAPI
from pydantic import BaseModel

from core.streamlit_manager.app import AppData
from core.streamlit_manager.database import DatabaseManager
from core.streamlit_manager.docker import DockerManager

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    for app in DatabaseManager.load_apps():
        # 容器已存在就不启动
        if DockerManager.is_container_exist(app.container_name):
            continue
        # 镜像不存在也不启动
        if not DockerManager.is_image_exist(app.image_name):
            continue
        print('正在启动app', app.id, app.dependencies, app.image_name, app.container_name)
        container = DockerManager.run_container(app.image_name, app.container_name)
        app.container_id = container.id
        app.access_url = DockerManager.get_access_url(container)
        DatabaseManager.save_app(app)

@app.on_event("shutdown")
async def shutdown_event():
    # delete all containers
    for app in DatabaseManager.load_apps():
        print('正在删除app', app.id, app.dependencies, app.image_name, app.container_name)
        DockerManager.delete_container(app.container_id)

@app.post("/app/")
async def create_app(app: AppData):
    code, dependencies, id = app.code, app.dependencies, app.id
    image_name, container_name = app.image_name, app.container_name

    # # check if id is already in use
    # if DatabaseManager.get_app(id):
    #     return {'status': 'error', 'message': 'id already in use'}
    # # check if image_name and container_name is already in use
    # if DockerManager.is_image_exist(image_name):
    #     return {'status': 'error', 'message': 'image_name already in use'}
    # if DockerManager.is_container_exist(container_name):
    #     return {'status': 'error', 'message': 'container_name already in use'}

    if DatabaseManager.get_app_by_image_name(image_name):
        return {'status': 'error', 'message': 'image_name already in use'}
    if DatabaseManager.get_app_by_container_name(container_name):
        return {'status': 'error', 'message': 'container_name already in use'}

    # 先删除容器，再删除镜像
    if DockerManager.is_container_exist(container_name):
        DockerManager.delete_container(container_name)
    if DockerManager.is_image_exist(image_name):
        DockerManager.delete_image(image_name)

    image = DockerManager.create_image(code, dependencies, image_name)
    image_name = image.tags[0]
    container = DockerManager.run_container(image_name, container_name)
    app.container_id = container.id
    app.access_url = DockerManager.get_access_url(container)
    DatabaseManager.save_app(app)
    return {'id': id, 'access_url': app.access_url}


@app.delete("/app/{id}")
async def delete_app(id: str):
    app = DatabaseManager.get_app(id)
    if not app:
        return {'status': 'error', 'message': 'id not found'}
    DockerManager.delete_container(app.container_id)
    DatabaseManager.delete_app(id)
    return {'status': 'success'}

@app.get("/app/{id}")
async def get_app(id: str):
    app = DatabaseManager.get_app(id)
    print(app)
    return app

@app.get("/apps/")
async def get_apps():
    apps = DatabaseManager.load_apps()
    return apps