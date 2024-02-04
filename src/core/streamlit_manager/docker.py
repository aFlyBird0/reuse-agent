import os.path
import time

from docker import DockerClient, errors

from config.settings import get_settings

DOCKER_FILE = """
FROM python:3.11
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py ./
CMD ["streamlit", "run", "app.py"]
"""

client = DockerClient.from_env()

tmp_dir = ".streamlit_docker_tmp"
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

class DockerManager:
    @staticmethod
    def create_image(code: str, dependencies: list, image_name):
        # Create Dockerfile
        with open(os.path.join(tmp_dir, 'Dockerfile'), 'w') as f:
            f.write(DOCKER_FILE)

        # Save code to app.py
        with open(os.path.join(tmp_dir, 'app.py'), 'w') as f:
            f.write(code)

        # Save dependencies to requirements.txt
        with open(os.path.join(tmp_dir, 'requirements.txt'), 'w') as f:
            f.write('streamlit\n')
            for dependency in dependencies:
                f.write(dependency + '\n')

        # Build Docker image
        image, build_logs = client.images.build(path=tmp_dir, tag=image_name)

        return image

    @staticmethod
    def run_container(image_name, container_name):
        container = client.containers.run(image_name, detach=True, ports={'8501/tcp': None}, name=container_name, auto_remove=True)
        container = client.containers.get(container.id)  # Refresh the container object
        print('ports, ', container.ports)  # Add this line to print the container's port mapping
        return container

    @staticmethod
    def restart_container(container_id):
        container = client.containers.get(container_id)
        container.restart()

    @staticmethod
    def stop_container(container_id):
        container = client.containers.get(container_id)
        print('stopping container', container_id)
        container.stop(timeout=3)

        print('removing container', container_id)
        # 因为有 auto_remove，所以不用删除
        # container.remove(force=True)

    @staticmethod
    def delete_image(image_name):
        client.images.remove(image_name)

    @staticmethod
    def is_image_exist(image_name):
        try:
            client.images.get(image_name)
            return True
        except errors.ImageNotFound:
            return False

    @staticmethod
    def is_container_exist(container_name):
        try:
            client.containers.get(container_name)
            return True
        except errors.NotFound:
            return False

    @staticmethod
    def get_access_url(container):
        host = "http://"+str.removeprefix(get_settings().docker.docker_host, "http://")
        port = container.ports["8501/tcp"][0]["HostPort"]
        return f'{host}:{port}'

    @staticmethod
    def get_container_status(container_id):
        try:
            container = client.containers.get(container_id)
        except errors.NotFound:
            return "stopped"
        return container.status