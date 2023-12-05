# 验证基于 CoT 的组件化归纳
# Standard Library Imports
import logging
import sys
from io import StringIO
from typing import Sequence, Callable, Type, Optional, Union

from langchain_experimental.utilities import PythonREPL
# Third-party Library Imports
from pydantic.v1 import BaseModel, create_model

# Internal Imports
from agents_test.callback import MyCustomSyncHandler
from api.openai import OpenAIConfig
from langchain.agents import initialize_agent, AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool, Tool, StructuredTool
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools import PythonREPLTool
from action_to_model_agent.agent import fill_python_action_args, PythonREPLArgs
from example_component import example_fabinacci_sqrt_component_args

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def append_tools_to_agent(agent: AgentExecutor, tools: Sequence[BaseTool]):
    # tools_copy = list(agent.tools)
    #
    # tools_copy.extend(tool for tool in tools if tool.name not in tools_copy)
    #
    # agent.tools = tools_copy
    agent.tools = tools
    logger.info(f"agent.tools: ")
    for tool in agent.tools:
        logger.info(f"{tool.name}: {tool.description}, {tool.args}")

    return agent


def examle_fibonacci_args() -> PythonREPLArgs:
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
    args = {
        "n": {
            "type": "int",
            "description": "the number of fibonacci"
        }
    }

    return PythonREPLArgs(name=name, description=description, code=code, args=args)


def intermidate_step_to_tool(action: AgentAction, question: str = "") -> Union[BaseTool, None]:
    if action.tool != PythonREPLTool().name:
        logger.error(f"only support PythonREPLTool, but got {action.tool}")
        return None

    args: PythonREPLArgs = fill_python_action_args(action, question)
    # args: PythonREPLArgs = examle_fibonacci_args()

    if args is None:
        return None

    return python_tool_from_args(args)


# 将形如 {"tool_input": {"type": "string"}} 的形参字典转换为 pydantic 模型
# 注：后面临时改成了更简单的形式，形如 {"tool_input": "string"}
def create_args_schema(args_dict: dict, model_name: str = "DynamicModel") -> Type[BaseModel]:
    model_fields = {}

    logger.info(f"start to create args schema, args_dict: {args_dict}")

    for arg_name, arg_info in args_dict.items():
        # arg_type = arg_info["type"]
        arg_type = arg_info
        model_fields[arg_name] = (eval(arg_type), ...)

    dynamic_model = create_model(model_name, **model_fields)
    # dynamic_model = type(model_name, (BaseModel,), model_fields)
    return dynamic_model


def my_exec(code: str, globals: dict = None, locals: dict = None):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    if globals is None:
        globals = {}
    try:
        exec(code, globals, globals)
        sys.stdout = old_stdout
        return mystdout.getvalue()
    except Exception as e:
        sys.stdout = old_stdout
        return repr(e)


def python_tool_from_args(args: PythonREPLArgs) -> StructuredTool:
    name = args.name
    description = args.description
    code = args.code
    args = args.args

    def funcWrapper(code: str) -> Callable:
        # 上层调用的时候，tool_input 是字典，对应 **kwargs
        def func(*args, **kwargs):
            print(f"\n正在执行Python模块化后的代码:\n{code}")
            # 将所有的参数解包，传入代码中，实现形参和实参的动态绑定
            return my_exec(code, globals=kwargs)
            # return PythonREPL(_globals=globals(), _locals=kwargs).run(code)
            # return exec(code)

        return func

    tool = StructuredTool(
        name=name,
        description=description,
        args_schema=create_args_schema(args),
        func=funcWrapper(code)
    )

    return tool


if __name__ == '__main__':
    llm = OpenAIConfig.defaultLLM()
    # tools = [PythonREPLTool()]
    tools : list[BaseTool] = [PythonREPLTool(), python_tool_from_args(example_fabinacci_sqrt_component_args)]

    agent = initialize_agent(
        tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    # question1 = "What is the 10th fibonacci number?"
    # question2 = "What is the 20th fibonacci number?"

    question1 = "Calculate the 10th Fibonacci number, add it to the square root of 6, and round the result to two decimal places. Give me the result."
    question2 = "Calculate the 5th Fibonacci number, add it to the square root of 20, and round the result to two decimal places. Give me the result."

    agent_actions_save: list[AgentAction] = []


    def ask(question: str, agent: AgentExecutor):
        with get_openai_callback() as cb:
            i = 1
            for step in agent.iter(question, callbacks=[MyCustomSyncHandler()]):
                logger.info(f"The {i}th step: {step}")
                if output := step.get("intermediate_step"):
                    action, value = output[0]
                    if action.tool == PythonREPLTool().name:
                        logger.info(f"step: {step}")
                        logger.info(f"action: {action}, value: {value}")
                        agent_actions_save.append(action)
                    # Ask user if they want to continue
                    # _continue = input("Should the agent continue (Y/n)?:\n")
                    # if _continue != "Y":
                    #     break
                else:
                    logger.info(f"output: {step['output']}")
                i += 1
                if i > 5:
                    logger.warning(f"i > 3, break")
                    break
        logger.info(f'total tokens: {cb.total_tokens / 1000}k')


    # 第一轮
    ask(question1, agent)

    logger.info("finished first round!")

    # 把第一轮的代码封装成新的 Tool
    # 取出上次写的代码
    logger.info(f"agent_actions_save: {agent_actions_save}")
    for action in agent_actions_save:
        new_tool = intermidate_step_to_tool(action)
        if new_tool and new_tool.name not in [tool.name for tool in tools]:
            tools.append(new_tool)
    # 把新的 Tool 加入到 agent 中
    agent = initialize_agent(
        tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    # 第二轮
    ask(question2, agent)

    logger.info("finished!")
