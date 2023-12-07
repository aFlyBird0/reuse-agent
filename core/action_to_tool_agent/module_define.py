from dataclasses import dataclass
from typing import List
from .example import example_refactored_code, example_args_extracted_json


# class BaseModule:
#     name: str
#     author: str = "admin"
#     description: str
#     tags: list[str]
#     kind: str
#
#     def __init__(self, name, description, tags, kind, author="admin", **kwargs):
#         self.name = name
#         self.author = author
#         self.description = description
#         self.tags = tags
#         self.kind = kind

class PythonModule:
    def __init__(self, name, description, tags, code, args, author="admin", **kwargs):
        self.name = name
        self.author = author
        self.description = description
        self.tags = tags
        self.kind = "Python"
        self.code = code
        self.args = args

    def print(self, logger):
        logger.info(f"重构后的Python代码信息，name：{self.name}, description: {self.description}, args: {self.args}")
        logger.info(f"重构后的Python代码内容：\n{self.code}")


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

MODULE_COLLECTION = "module"


def example_fibonacci() -> PythonModule:
    args = PythonModule(
        name=example_args_extracted_json["name"],
        description=example_args_extracted_json["description"],
        code=example_refactored_code,
        args=example_args_extracted_json["args"],
        tags=example_args_extracted_json["tags"]
    )
    return args


class ModuleStore:
    """
    save/load modules from mongodb
    """

    def __init__(self):
        self.modules = []
        uri = "mongodb+srv://aflybird0:8ORG2lDRRm36ntP7@cluster0.lh2vpp8.mongodb.net/?retryWrites=true&w=majority"
        # Create a new client and connect to the server
        self.client = MongoClient(uri, server_api=ServerApi('1'))
        # Send a ping to confirm a successful connection
        try:
            self.client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)
        # print(self.client.list_databases())
        self.db = self.client["cluster0"]
        self.col = self.db.get_collection(MODULE_COLLECTION)

    def add(self, module: PythonModule):
        # insert if name not exist
        if not self.col.find_one({"name": module.name, "author": module.author}):
            self.col.insert_one(module.__dict__)
            print(f"已经成功添加模块：{module.author}/{module.name}")

    def list_by_filter(self, **filter) -> List[PythonModule]:
        cols = self.col.find(filter)
        # for col in cols:
        #     print(col)
        return [PythonModule(**col) for col in cols]

    def list(self) -> List[PythonModule]:
        return self.list_by_filter()

    def list_by_name(self, module_name: str) -> List[PythonModule]:
        return self.list_by_filter(name=module_name)

    def list_by_author(self, module_author: str) -> List[PythonModule]:
        return self.list_by_filter(author=module_author)

    def list_by_tags_or(self, tags_list_or: list) -> List[PythonModule]:
        # tag in module_tags
        tags_filter = {"tags": {"$in": tags_list_or}}
        return self.list_by_filter(**tags_filter)

    def list_by_tags_and(self, tags_list_and: list) -> List[PythonModule]:
        # tag in module_tags
        tags_filter = {"tags": {"$all": tags_list_and}}
        return self.list_by_filter(**tags_filter)

    def list_by_kind(self, kind: str) -> List[PythonModule]:
        modules = []
        for module in self.modules:
            if module.kind == kind:
                modules.append(module)
        return modules

    def print_all(self, logger):
        for module in self.modules:
            module.print(logger)


if __name__ == "__main__":
    m = ModuleStore()
    python_module = PythonModule(
        name="test_py_math",
        description="xxx",
        author="admin",
        tags=["test", "math"],
        code="print('hello world')",
        args={},
    )

    m.add(example_fibonacci())

    # for v in m.list_modules_by_filter():
    #     print(vars(v))

    print("tags or")
    for v in m.list_by_tags_or(["test", "math"]):
        print(vars(v))

    print("tags and")
    for v in m.list_by_tags_and(["test", "math"]):
        print(vars(v))
