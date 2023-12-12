from typing import List

from pydantic import BaseModel

from core.module.module import Param


def create_pydantic_model_from_params(self, param_list: List[Param]):
    """
    Create a Pydantic model from a list of parameters.

    Args:
    - param_list (list): A list of dictionaries, each representing a parameter with keys: name, description, required, type, etc.

    Returns:
    - Pydantic model: A Pydantic BaseModel class representing the parameters.
    """

    # Define a dynamic class for the Pydantic model
    class DynamicModel(BaseModel):
        pass

        # Iterate through the parameter list and add fields to the model

    for param in param_list:
        param_name = param.name
        param_type = param.param_type
        param_required = param.param_type
        param_description = param.description

        # Add the field to the model dynamically
        DynamicModel.__annotations__[param_name] = param_type
        if param_required:
            DynamicModel.__config__.schema_extra = {
                "required": [param_name]
            }
        setattr(DynamicModel, param_name, (..., param_description))

    return DynamicModel


def create_pydantic_model(self, param_list: List[Param]):
    # 定义一个空的字典，用于存储参数名和对应的pydantic类型
    fields = {}

    for param in param_list:
        # 将参数名和对应的类型添加到字典中
        fields[param.name] = (param.param_type, ...)

        # 使用type函数动态创建一个继承自pydantic BaseModel的子类
    model = type('DynamicModel', (BaseModel,), fields)

    return model