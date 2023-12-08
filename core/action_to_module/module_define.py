import json
from dataclasses import dataclass
from typing import List

from langchain_core.load import Serializable

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

# extend from dict to support json serialization
# class PythonModule(dict):
#     def __init__(self, name, description, tags, code, args, author="admin", id="", dependencies=None, **kwargs):
#         super().__init__(name=name, author=author, description=description, tags=tags, kind="Python", code=code,
#                          args=args, id=id, dependencies=dependencies)
#         if dependencies is None:
#             dependencies = []
#         self.name = name
#         self.author = author
#         self.description = description
#         self.tags = tags
#         self.kind = "Python"
#         self.code = code
#         self.args = args
#         self.id = id
#         self.dependencies = []
#
#     def print(self, logger):
#         logger.info(f"重构后的Python代码信息，name：{self.name}, description: {self.description}, args: {self.args}")
#         logger.info(f"重构后的Python代码内容：\n{self.code}")
#
#     def __to_dict__(self):
#         return {
#             "name": self.name,
#             "author": self.author,
#             "description": self.description,
#             "tags": self.tags,
#             "kind": self.kind,
#             "code": self.code,
#             "args": self.args,
#             "id": self.id,
#             "dependencies": self.dependencies
#         }
#
#     def __to_json__(self):
#         print("触发序列化")
#         return json.dumps(self.__to_dict__(), indent=4)
#
#     def toJson(self):
#         return self.__to_json__()

from pydantic import BaseModel, Field
import json


class PythonModule(BaseModel):
    name: str
    description: str
    tags: list
    code: str
    args: dict[str,str] = Field(default_factory=dict[str,str], description="The args of the module", example={"a": "1", "b": "2"})
    author: str = Field(default="admin", description="The author of the module")
    id: str = ""
    kind: str = "Python"
    dependencies: list = []

    def print(self, logger):
        logger.info(f"重构后的Python代码信息，name：{self.name}, description: {self.description}, args: {self.args}")
        logger.info(f"重构后的Python代码内容：\n{self.code}")

    def to_dict(self):
        return self.dict()

    def to_json(self):
        return self.json(indent=4)

def example_fibonacci() -> PythonModule:
    args = PythonModule(
        name=example_args_extracted_json["name"],
        description=example_args_extracted_json["description"],
        code=example_refactored_code,
        args=example_args_extracted_json["args"],
        tags=example_args_extracted_json["tags"]
    )
    return args