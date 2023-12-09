import logging
from typing import Callable, Type, Union, List

# Internal Imports
from langchain_core.agents import AgentAction
from langchain_core.tools import BaseTool, StructuredTool
from langchain_experimental.tools import PythonREPLTool
from langchain_experimental.utilities import PythonREPL
# Third-party Library Imports
from pydantic import BaseModel, create_model
from .agent import ActionToPythonAgent
from .module_define import PythonModule
from .module_store import ModuleStore, default_module_store
from loggers.logs import setup_logger
from .example import example_refactored_code, example_args_extracted_json
from ..interpreter.python import PythonInterpreter


class ModuleGenerator:
    def __init__(self, logger: logging.Logger = None, ):
        if logger is None:
            self.logger = setup_logger()

        self.agent = ActionToPythonAgent()

    def all_from_db(self, store: ModuleStore = default_module_store) -> List[StructuredTool]:
        return [self.from_python_args(args) for args in store.list()]

    def from_action(self, action: AgentAction, question: str = "") -> Union[BaseTool, None]:
        if action.tool == PythonREPLTool().name:
            return self.from_python_action(action, question)

        self.logger.error(f"only support PythonREPLTool, but got {action.tool}")
        return None

    def from_python_action(self, action: AgentAction, question: str = "") -> Union[BaseTool, None]:
        args: PythonModule = self.agent.python_args_from_action(action, question)

        # self.store.add(args)

        return self.from_python_args(args)

    def example_fibonacci_tool(self) -> StructuredTool:
        args = PythonModule(
            name=example_args_extracted_json["name"],
            description=example_args_extracted_json["description"],
            code=example_refactored_code,
            args=example_args_extracted_json["args"],
            tags=example_args_extracted_json["tags"]
        )
        return self.from_python_args(args)

    def from_python_args(self, args: PythonModule) -> StructuredTool:
        name = args.name
        description = args.description
        code = args.code
        args = args.args

        def funcWrapper(code: str) -> Callable:
            # 上层调用的时候，tool_input 是字典，对应 **kwargs
            def func(*args, **kwargs):
                print(f"\n正在执行Python模块化代码:\n{code}")
                # 将所有的参数解包，传入代码中，实现形参和实参的动态绑定
                return PythonInterpreter().run(code, **kwargs)
                # return PythonREPL(_globals=globals(), _locals=kwargs).run(code)
                # return exec(code)

            return func

        tool = StructuredTool(
            name=name,
            description=description,
            args_schema=self._create_args_schema(args),
            func=funcWrapper(code)
        )

        return tool

    # 将形如 {"tool_input": {"type": "string"}} 的形参字典转换为 pydantic 模型
    # 注：后面临时改成了更简单的形式，形如 {"tool_input": "string"}
    def _create_args_schema(self, args_dict: dict, model_name: str = "DynamicModel") -> Type[BaseModel]:
        model_fields = {}

        # self.logger.info(f"start to create args schema, args_dict: {args_dict}")

        for arg_name, arg_info in args_dict.items():
            # arg_type = arg_info["type"]
            arg_type = arg_info
            model_fields[arg_name] = (eval(arg_type), ...)

        dynamic_model = create_model(model_name, **model_fields)
        # dynamic_model = type(model_name, (BaseModel,), model_fields)
        return dynamic_model


default_module_generator = ModuleGenerator()
