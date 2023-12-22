from typing import List

from core.streamlit_manager.app import AppData
from core.streamlit_manager.database import DatabaseManager
from core.streamlit_manager.docker import DockerManager


class AppManager:
    @classmethod
    def startup_event(cls):
        for app in DatabaseManager.load_apps():
            if DockerManager.is_container_exist(app.container_name):
                continue
            if not DockerManager.is_image_exist(app.image_name):
                continue
            print('正在启动app', app.id, app.dependencies, app.image_name, app.container_name)
            container = DockerManager.run_container(app.image_name, app.container_name)
            app.container_id = container.id
            app.access_url = DockerManager.get_access_url(container)
            DatabaseManager.save_app(app)

    @classmethod
    def shutdown_event(cls):
        for app in DatabaseManager.load_apps():
            print('正在删除app', app.id, app.dependencies, app.image_name, app.container_name)
            DockerManager.stop_container(app.container_id)

    @classmethod
    def create_app(cls, app: AppData)->dict:
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

        # delete image and container if already exist
        if DockerManager.is_container_exist(container_name):
            DockerManager.stop_container(container_name)
        if DockerManager.is_image_exist(image_name):
            DockerManager.delete_image(image_name)

        # create image
        image = DockerManager.create_image(code, dependencies, image_name)
        image_name = image.tags[0]
        # create container
        container = DockerManager.run_container(image_name, container_name)
        # save app
        app.container_id = container.id
        app.access_url = DockerManager.get_access_url(container)
        DatabaseManager.save_app(app)
        return {'id': id, 'access_url': app.access_url}

    @classmethod
    def restart_app(cls, app: AppData)->AppData:
        # return DockerManager.restart_container(app.container_id)
        # 因为每次停止容器后，都是默认直接删除，所以要用新建容器，而不是重启容器
        container = DockerManager.run_container(image_name=app.image_name, container_name=app.container_name)
        app.container_id = container.id
        app.access_url = DockerManager.get_access_url(container)
        DatabaseManager.save_app(app)
        return app

    @classmethod
    def delete_app(cls, id: str)->dict:
        app = DatabaseManager.get_app(id)
        if not app:
            return {'status': 'error', 'message': 'id not found'}
        status = cls.get_app_status(app)
        if status == 'running':
            DockerManager.stop_container(app.container_id)
        DatabaseManager.delete_app(id)
        return {'status': 'success'}

    @classmethod
    def stop_app(cls, id: str)->dict:
        app = DatabaseManager.get_app(id)
        if not app:
            return {'status': 'error', 'message': 'id not found'}
        DockerManager.stop_container(app.container_id)
        return {'status': 'success'}

    @classmethod
    def get_app(cls, id: str)->AppData:
        app = DatabaseManager.get_app(id)
        return app

    @classmethod
    def list_apps(cls)->List[AppData]:
        apps = DatabaseManager.load_apps()
        return apps

    @classmethod
    def get_app_status(cls, app: AppData)->str:
        return DockerManager.get_container_status(app.container_id)