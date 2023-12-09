"""
Deprecated functions
"""
import sys
from io import StringIO
from typing import Sequence

from langchain.agents import AgentExecutor
from langchain_core.tools import BaseTool
from loggers.logs import setup_logger

logger = setup_logger()
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

# def ask(question: str, agent: AgentExecutor):
#     with get_openai_callback() as cb:
#         i = 1
#         for step in agent.iter(question, callbacks=[MyCustomSyncHandler()]):
#             logger.info(f"The {i}th step: {step}")
#             if output := step.get("intermediate_step"):
#                 action, action_result = output[0]
#                 # if action.tool == PythonREPLTool().name:
#                 # logger.info(f"step: {step}")
#                 logger.info(f"action: {action}, value: {action_result}")
#                 conversation.add_action(action, action_result)
#                 # Ask user if they want to continue
#                 # _continue = input("Should the agent continue (Y/n)?:\n")
#                 # if _continue != "Y":
#                 #     break
#             else:
#                 logger.info(f"output: {step['output']}")
#             i += 1
#             if i > 5:
#                 logger.warning(f"i > 5, break")
#                 break
#     logger.info(f'total tokens: {cb.total_tokens / 1000}k')