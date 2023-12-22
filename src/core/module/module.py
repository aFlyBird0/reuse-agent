from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Param(BaseModel):
    name: str = Field(description="The name of the param")
    param_type: str = Field(description="the type, only support string, integer, float, boolean, array, object",
                            enum=["str", "int", "float", "bool", "list", "dict", "object"])
    default: Optional[Any] = Field(description="The default value of the param",default=None)
    description: str = Field(description="The description of the param")
    required: bool = Field(description="Whether the param is required", default=True)

    def to_json_schema(self):
        json_schema = {
            "type": self.param_type,
            "description": self.description,
        }
        if self.default:
            json_schema["default"] = self.default
        return json_schema


class Module(BaseModel):
    name: str = Field(description="The name of the module")
    description: str = Field(description="The description of the module")
    tags: List[str] = Field(default_factory=List[str], description="用于描述函数的功能/用途/特性/分类等等",
                            example=["math", "fibonacci"])
    code: str = Field(description="The code of the module, now only support Python")
    # args: dict[str,str] = Field(default_factory=dict[str,str], description="The args of the module", example={"a": "1", "b": "2"})
    params: List[Param] = Field(default_factory=List[Param], description="The params of the module")
    author: str = Field(default="admin", description="The author of the module")
    # id: str = ""
    # kind: str = "Python"
    dependencies: List[str] = Field(description="需要使用pip安装的python包", default_factory=list[str])

    id: str = Field(description="The id of the module, only used for database", default="")

    # def print(self, logger):
    #     logger.info(f"重构后的Python代码信息，name：{self.name}, description: {self.description}, args: {self.args}")
    #     logger.info(f"重构后的Python代码内容：\n{self.code}")

    # def to_json_schema(self):
    #     json_schema = {
    #         "type": "object",
    #         "properties": {},
    #         "required": [],
    #         "description": self.description,
    #     }
    #     for param in self.params:
    #         json_schema["properties"][param.name] = param.to_json_schema()
    #         if param.required:
    #             json_schema["required"].append(param.name)
    #     return json_schema

    def to_json_schema_without_code(self):
        return Module.schema()["properties"]

    def schema_only_params(self)->BaseModel:
        parameters = {
            "type": "object",
            "properties": {},
            "name": "params",
        }
        if self.params:
            parameters["properties"] = {param.name: param.to_json_schema() for param in self.params}
            parameters["required"] = [param.name for param in self.params if param.required]

        return BaseModel(**parameters)

    # get basemodel of params


    # def to_python_module_store(self) -> PythonModule:
    #     args = {}
    #     for param in self.params:
    #         args[param.name] = param.type
    #     return PythonModule(
    #         name=self.name,
    #         description=self.description,
    #         tags=self.tags,
    #         code=self.code,
    #         args=args,
    #         author=self.author,
    #         dependencies=self.dependencies
    #     )

    def to_dict(self):
        return self.dict()

    def to_dict_only_core_field(self):
        return self.dict(exclude={"code", "id", "author"})

    @classmethod
    def from_json(cls, json_dict: dict):
        return cls.parse_obj(json_dict)


# def from_python_module_store(m: PythonModule) -> Module:
#     params = []
#     for k, v in m.args.items():
#         params.append(Param(name=k, type=v, description=""))
#     return Module(
#         name=m.name,
#         description=m.description,
#         tags=m.tags,
#         code=m.code,
#         params=params,
#         author=m.author,
#         dependencies=m.dependencies
#     )


if __name__ == '__main__':
    print(Module.schema_json(indent=4))
