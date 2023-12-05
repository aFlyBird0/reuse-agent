import logging
import time
from typing import Sequence, Callable

from langchain.agents import initialize_agent, AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from langchain_core.tools import BaseTool, Tool, StructuredTool
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools import PythonREPLTool
from langchain_core.agents import AgentAction

from agents_test.callback import MyCustomSyncHandler
from api.openai import OpenAIConfig
from pydantic.v1 import BaseModel, create_model
from typing import Type
from langchain_experimental.utilities.python import PythonREPL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def intermidate_step_to_tool(action: AgentAction) -> BaseTool:
    # if action.tool == PythonREPLTool().name:
    #     return PythonREPLTool()

    name = "calculate_fibonacci"
    description = "calculate fibonacci"
    code = """
def fibonacci(n):
    if n <= 1:
        return n

    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b

    return b
print(fibonacci(n))
    """

    args_schema = {
        "n": {
            "type": "int",
            # "description": "the number of fibonacci"
        }
    }

    return python_tool_from_args(name, description, code, args_schema)

# 将形如 {"tool_input": {"type": "string"}} 的形参字典转换为 pydantic 模型
def create_args_schema(args_dict: dict, model_name: str = "DynamicModel") -> Type[BaseModel]:
    model_fields = {}

    for arg_name, arg_info in args_dict.items():
        arg_type = arg_info["type"]
        model_fields[arg_name] = (eval(arg_type), ...)

    dynamic_model = create_model(model_name, **model_fields)
    # dynamic_model = type(model_name, (BaseModel,), model_fields)
    return dynamic_model

def python_tool_from_args(name: str, description: str, code: str, args_schema: dict) -> StructuredTool:
    def funcWrapper(code: str) -> Callable:
        def func(*args, **kwargs):
            logger.info(f"args: {args}")
            logger.info(f"kwargs: {kwargs}")
            # codeWithArgs = "args = " + str(kwargs) + "\n" + code
            print(f"\n正在执行Python转写后的代码:\n{code}")
            # return PythonREPL().run(code)
            return exec(code, kwargs)
        return func
    tool = StructuredTool(
        name=name,
        description=description,
        args_schema=create_args_schema(args_schema),
        func=funcWrapper(code)
    )

    return tool

if __name__ == "__main__":
    # 初始化 agent
    tool = intermidate_step_to_tool(None)
    tool_input = {"n": 11}
    time.sleep(3)
    tool.run(tool_input)
    print("hello world2")



