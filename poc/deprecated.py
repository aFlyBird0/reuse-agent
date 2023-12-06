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