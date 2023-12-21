import time

from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
from docker import DockerClient
import os
import uuid

DOCKER_FILE = """
FROM python:3.11
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
CMD ["streamlit", "run", "app.py"]
"""

app = FastAPI()
client = DockerClient.from_env()
uri = "mongodb+srv://aflybird0:8ORG2lDRRm36ntP7@cluster0.lh2vpp8.mongodb.net/?retryWrites=true&w=majority"
mongo_client = MongoClient(uri)
db = mongo_client["cluster0"]
collection = db["streamlit_apps"]


# @app.on_event("startup")
# async def startup_event():
#     for app in DatabaseManager.load_apps():
#         container = DockerManager.start_container(app['container_id'])
#         app['container_id'] = container.id
#         DatabaseManager.save_app(app['_id'], app['container_id'])

class AppData(BaseModel):
    code: str
    dependencies: list = None
    code_id: str = str(uuid.uuid4())

@app.post("/app/")
async def create_app(app: AppData):
    code, dependencies, code_id = app.code, app.dependencies, app.code_id

    # check if code_id is already in use
    if DatabaseManager.get_app(code_id):
        return {'status': 'error', 'message': 'code_id already in use'}

    image = DockerManager.create_image(code, dependencies, code_id)
    print('image', image)
    print('image.tags', image.tags)
    container = DockerManager.start_container(image)
    DatabaseManager.save_app(code_id, container.id)
    return {'code_id': code_id, 'access_url': f'http://localhost:{container.ports["8501/tcp"][0]["HostPort"]}'}


@app.delete("/app/{code_id}")
async def delete_app(code_id: str):
    DockerManager.delete_container(collection.find_one({'_id': code_id})['container_id'])
    DatabaseManager.delete_app(code_id)
    return {'status': 'success'}


class DockerManager:
    @staticmethod
    def create_image(code: str, dependencies: list, code_id):
        # Create Dockerfile
        with open('Dockerfile', 'w') as f:
            f.write(DOCKER_FILE)

        # Save code to app.py
        with open('app.py', 'w') as f:
            f.write(code)

        # Save dependencies to requirements.txt
        with open('requirements.txt', 'w') as f:
            f.write('streamlit\n')
            for dependency in dependencies:
                f.write(dependency + '\n')

        # Build Docker image
        image, build_logs = client.images.build(path='.', tag=code_id)

        return image

    @staticmethod
    def start_container(image):
        container = client.containers.run(image.tags[0], detach=True, ports={'8501/tcp': None})
        container = client.containers.get(container.id)  # Refresh the container object
        print('ports, ', container.ports)  # Add this line to print the container's port mapping
        return container

    @staticmethod
    def delete_container(container_id):
        container = client.containers.get(container_id)
        container.stop()
        container.remove()

class DatabaseManager:
    @staticmethod
    def get_app(code_id):
        return collection.find_one({'_id': code_id})

    @staticmethod
    def save_app(code_id, container_id):
        collection.insert_one({'_id': code_id, 'container_id': container_id})

    @staticmethod
    def load_apps():
        return list(collection.find())

    @staticmethod
    def delete_app(code_id):
        collection.delete_one({'_id': code_id})