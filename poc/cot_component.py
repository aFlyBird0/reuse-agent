# 验证基于 CoT 的组件化归纳
# Standard Library Imports
import logging

# Third-party Library Imports

# Internal Imports
from agents_test.callback import MyCustomSyncHandler
from api.openai import OpenAIConfig
from langchain.agents import initialize_agent, AgentExecutor
from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain_core.agents import AgentAction
from langchain_core.tools import BaseTool
from langchain_experimental.tools import PythonREPLTool
from poc.action_to_tool_agent.toolgen import ToolGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    llm = OpenAIConfig.defaultLLM()
    # tools = [PythonREPLTool()]
    # example_fibonacci_tool = ToolGenerator().from_python_args(example_fabinacci_sqrt_component_args)
    tools: list[BaseTool] = [PythonREPLTool()]

    agent = initialize_agent(
        tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    # question1 = "What is the 10th fibonacci number?"
    # question2 = "What is the 20th fibonacci number?"

    question1 = "Calculate the 10th Fibonacci number, add it to the square root of 6, and round the result to two decimal places. Give me the final result number."
    question2 = "Calculate the 5th Fibonacci number, add it to the square root of 20, and round the result to two decimal places. Give me the final result number."

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


    action2tool = ToolGenerator()

    # 第一轮
    ask(question1, agent)

    logger.info("finished first round!")

    # 把第一轮的代码封装成新的 Tool
    # 取出上次写的代码
    logger.info(f"agent_actions_save: {agent_actions_save}")
    for action in agent_actions_save:
        new_tool = action2tool.from_action(action, question1)
        if new_tool and new_tool.name not in [tool.name for tool in tools]:
            tools.append(new_tool)
    # 把新的 Tool 加入到 agent 中
    agent = initialize_agent(
        tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    # 第二轮
    ask(question2, agent)

    logger.info("finished!")
