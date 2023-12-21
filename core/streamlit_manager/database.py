from typing import List

from bson import ObjectId

from core.streamlit_manager.app import AppData
from database.mongo import default_db

collection = default_db["streamlit_apps"]

class DatabaseManager:

    @staticmethod
    def get_app(id)->AppData:
        col = collection.find_one({'_id': ObjectId(id)})
        if col:
            return DatabaseManager._col_to_app(col)

    @staticmethod
    def get_app_by_image_name(image_name: str)->AppData:
        col = collection.find_one({'image_name': image_name})
        if col:
            return DatabaseManager._col_to_app(col)

    @staticmethod
    def get_app_by_container_name(container_name: str)->AppData:
        col = collection.find_one({'container_name': container_name})
        if col:
            return DatabaseManager._col_to_app(col)

    @staticmethod
    def save_app(app: AppData):
        # # save or update
        # id = app.id
        # code = app.code
        # dependencies = app.dependencies
        # image_name = app.image_name
        # container_id = app.container_id
        # access_url = app.access_url
        #
        # print('正在保存app', id, dependencies, image_name, container_id, access_url)
        #
        # res= collection.update_one({'_id': id}, {'$set': {'code': code, 'dependencies': dependencies, 'image_name': image_name, 'container_id': container_id, 'access_url': access_url}}, upsert=True)
        # print(res.raw_result)

        app_data_dict = app.dict()
        id = app_data_dict.pop("id")

        print('正在保存app', id, app_data_dict)

        # # 使用upsert参数，如果没有找到符合条件的记录，就创建一个新的记录
        collection.update_one({"_id": ObjectId(id)}, {"$set": app_data_dict}, upsert=True)

        # 检查是否已经有一个相同id的记录
        # existing_record = collection.find_one({"_id": ObjectId(id)})
        #
        # if existing_record is None:
        #     # 如果没有相同id的记录，创建一个新的记录
        #     print('正在保存app', id, app_data_dict)
        #     collection.insert_one(app_data_dict)
        # else:
        #     # 如果已经有一个相同id的记录，更新这个记录
        #     print('正在更新app', id, app_data_dict)
        #     collection.update_one({"_id": id}, {"$set": app_data_dict})

    @staticmethod
    def load_apps()->List[AppData]:
        return [DatabaseManager._col_to_app(col) for col in collection.find()]

    @staticmethod
    def delete_app(id):
        collection.delete_one({'_id': ObjectId(id)})

    @staticmethod
    def _col_to_app(col):
        col['id'] = str(col['_id'])
        return AppData(**col)