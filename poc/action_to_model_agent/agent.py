# 将组件重写成Python代码的Agent

import logging
from typing import Sequence, Callable, Type, Optional, Union

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
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.tools import BaseTool, Tool, StructuredTool
from langchain_experimental.agents.agent_toolkits import create_python_agent
from langchain_experimental.tools import PythonREPLTool
from dataclasses import dataclass
from .prompt import SYSTEM_PROMPT_CN, SYSTEM_PROMPT_CN_TEMPLATE, USER_PROMPT_CN_TEMPLATE
from .example import example_cn
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema.messages import SystemMessage
from .output_parser import split_json_and_code
from loggers.logs import setup_logger

logger = setup_logger()

@dataclass
class PythonREPLArgs:
    name: str
    description: str
    code: str
    args: dict


def fill_python_action_args(action: AgentAction, origin_main_task: str) -> Union[PythonREPLArgs, None]:
    from langchain import hub
    from langchain.agents.format_scratchpad import format_log_to_str
    from langchain.agents.output_parsers import ReActSingleInputOutputParser
    from langchain.tools.render import render_text_description

    # prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT_CN_TEMPLATE)
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_CN_TEMPLATE),
            HumanMessagePromptTemplate.from_template(USER_PROMPT_CN_TEMPLATE)
        ]
    )
    prompt = prompt.partial(
        **example_cn,
        # **{
        #     "code": action.tool_input,
        #     "example_task_log": "this is example_task_log"
        # },
    )

    llm = OpenAIConfig.defaultLLM()

    log = action.log
    messages: Sequence[BaseMessage] = action.messages
    code = action.tool_input
    callbacks = [MyCustomSyncHandler()]

    with get_openai_callback() as cb:
        chat_val = prompt.invoke(
            {
                "code": code,
                "task_log": log,
                "origin_main_task": origin_main_task,
            },
            {
                "callbacks": callbacks
            }
        )

        # print(chat_val)
        msgs = chat_val.to_messages()
        # print(msgs[-1])
        # print(chat_val.to_string())
        msg_return = llm.invoke(msgs)
        # print(msg_return.content)
        #
        args, code = split_json_and_code(msg_return.content)
    print(f"total_tokens: {cb.total_tokens / 1000}k")

    if args is None or code is None:
        logger.error(f"解析Python代码失败，返回的args: {args}, code: {code}")
        return None
    logger.info(args)
    pyREPLArgs =  PythonREPLArgs(
        name=args["name"],
        description=args["description"],
        code=code,
        args=args["args"],
    )

    logger.info(f"重构后的Python代码，name：{pyREPLArgs.name}, description: {pyREPLArgs.description}, args: {pyREPLArgs.args}")
    logger.info(f"重构后的Python代码：\n{pyREPLArgs.code}")

    return pyREPLArgs

    # llm_with_stop = llm.bind(stop=["\nObservation"])
    #
    # agent = (
    #         {
    #             "code": lambda x: x["code"],
    #             "task_log": lambda x: x["task_log"],
    #             "origin_main_task": lambda x: x["origin_main_task"],
    #             # "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
    #         }
    #         | prompt
    #         | llm_with_stop
    #         | ReActSingleInputOutputParser()
    # )
    #
    # from langchain.agents import AgentExecutor
    #
    # agent_executor = AgentExecutor(agent=agent, tools=[], verbose=True)
    #
    # log = action.log
    # messages: Sequence[BaseMessage] = action.messages
    # code = action.tool_input
    #
    # callbacks = [MyCustomSyncHandler()]
    # with get_openai_callback() as cb:
    #     agent_executor.invoke(
    #         {
    #             "code": code,
    #             "task_log": log,
    #             "origin_main_task": origin_main_task,
    #         },
    #         {
    #             "callbacks": callbacks
    #         }
    #     )
    # print(f'total tokens: {cb.total_tokens / 1000}k')


if __name__ == '__main__':
    code_to_test = """
def is_prime():
    number = 10
    if number <= 1.
        return False
    for i in range(2, int(number**0.5) + 1): if number % i == 0: return False.
        if number % i == 0: if number <= 1: return False
            return False
    return True

number_to_check = 100

if is_prime(number_to_check): print(f"{number_to_check}")
    print(f"{number_to_check} is prime")
print(f"{number_to_check} is prime")
    print(f"{number_to_check} is not prime")
"""
    task_log = "I need to check if a number is prime, and print out the result."
    origin_main_task = "find 100th prime number"
    action = AgentAction(
        tool_input=code_to_test,
        log=task_log,
        tool=PythonREPLTool().name,
    )
    fill_python_action_args(action, origin_main_task=origin_main_task)
