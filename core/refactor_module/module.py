from typing import Optional, Any

from pydantic import BaseModel, Field

from core.action_to_module.module_define import PythonModule


class Param(BaseModel):
    name: str = Field(description="The name of the param")
    type: str = Field(description="the type, only support string, integer, float, boolean, array, object",
                      enum=["string", "integer", "float", "boolean", "array", "object"])
    default: Optional[Any] = Field(description="The default value of the param",default=None)
    description: str = Field(description="The description of the param")
    required: bool = Field(description="Whether the param is required", default=True)

    def to_json_schema(self):
        json_schema = {
            "type": self.type,
            "description": self.description,
        }
        if self.default:
            json_schema["default"] = self.default
        return json_schema


class Module(BaseModel):
    name: str = Field(description="The name of the module")
    description: str = Field(description="The description of the module")
    tags: list[str] = Field(default_factory=list[str], description="用于描述函数的功能/用途/特性/分类等等",
                            example=["math", "fibonacci"])
    code: str = Field(description="The code of the module, now only support Python")
    # args: dict[str,str] = Field(default_factory=dict[str,str], description="The args of the module", example={"a": "1", "b": "2"})
    params: list[Param] = Field(default_factory=list[Param], description="The params of the module")
    author: str = Field(default="admin", description="The author of the module")
    # id: str = ""
    # kind: str = "Python"
    dependencies: list = Field(description="需要使用pip安装的python包", default_factory=list[str])

    # def print(self, logger):
    #     logger.info(f"重构后的Python代码信息，name：{self.name}, description: {self.description}, args: {self.args}")
    #     logger.info(f"重构后的Python代码内容：\n{self.code}")

    def to_json_schema(self):
        json_schema = {
            "type": "object",
            "properties": {},
            "required": [],
            "description": self.description,
        }
        for param in self.params:
            json_schema["properties"][param.name] = param.to_json_schema()
            if param.required:
                json_schema["required"].append(param.name)
        return json_schema

    def to_python_module_store(self) -> PythonModule:
        args = {}
        for param in self.params:
            args[param.name] = param.type
        return PythonModule(
            name=self.name,
            description=self.description,
            tags=self.tags,
            code=self.code,
            args=args,
            author=self.author,
            dependencies=self.dependencies
        )

    def to_json(self):
        return self.dict()


def from_python_module_store(m: PythonModule) -> Module:
    params = []
    for k, v in m.args.items():
        params.append(Param(name=k, type=v, description=""))
    return Module(
        name=m.name,
        description=m.description,
        tags=m.tags,
        code=m.code,
        params=params,
        author=m.author,
        dependencies=m.dependencies
    )


if __name__ == '__main__':
    print(Module.schema_json(indent=4))
