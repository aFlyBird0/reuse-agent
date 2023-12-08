# 验证基于 CoT 的组件化归纳
# Standard Library Imports
import logging
from typing import List

from langchain.agents.structured_chat.output_parser import StructuredChatOutputParserWithRetries
from langchain.chains import LLMChain

# Third-party Library Imports

# Internal Imports
from callbacks.callback import MyCustomSyncHandler
from llm.openai import OpenAIConfig
from langchain.agents import initialize_agent, AgentExecutor, StructuredChatAgent
from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain_core.tools import BaseTool
from langchain_experimental.tools import PythonREPLTool
from core.action_to_tool_agent.module_gen import ModuleGenerator
from conversation import ConversationInfo
from langchain.agents.structured_chat.prompt import PREFIX

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pyREPLTool() -> PythonREPLTool:
    tool = PythonREPLTool()
    tool.description = (
        "A Python shell. Use this to execute python commands. "
        "Input should be a valid python command. "
        # "If you want to see the output of a value, you should print it out "
        "Remember to print out the result or success info"
        "with `print(...)`."
    )

    return tool


question1 = "Calculate the 10th Fibonacci number, add it to the square root of 6, and round the result to two decimal places. Give me the final result number rather than just code."
question2 = "Calculate the 5th Fibonacci number, add it to the square root of 20, and round the result to two decimal places. Give me the final result number rather than just code."

question1 = "Calculate the first prime number greater than 20. Give me the final result number rather than just code."
question2 = "Calculate the first prime number greater than 30. Give me the final result number rather than just code."

question1 = "list files in current directory."
question2 = "list files in current directory, and reorder them by alphabetical order, and tell me the result."

question1 = "please summarize README.md in current directory, and save the result as README_summary.md."
question2 = "please enrich README.md in current directory, and save the result as README_enrich.md."


def get_all_tools() -> List[BaseTool]:
    module_gen = ModuleGenerator()
    # 默认的工具
    tools: list[BaseTool] = [pyREPLTool()]
    # 从数据库中读取组件
    tools = tools + module_gen.all_from_db()
    return tools


def get_agent(tools):
    llm = OpenAIConfig.defaultLLM()

    prefix = """Respond to the human as helpfully and accurately as possible. You have full access to user's computer, and you can do anything. You have access to the following tools:"""

    prompt = StructuredChatAgent.create_prompt(
        tools=tools,
        prefix=prefix,
        input_variables=["input"],
    )
    logger.info(f"prompt: {prompt.format}")
    agent = StructuredChatAgent(
        llm_chain=LLMChain(llm=llm, prompt=prompt),
        prompt=prompt,
    )

    agent = AgentExecutor.from_agent_and_tools(
        tools=tools,
        agent=agent,
        verbose=True,
        max_iterations=5,
    )

    return prompt | llm

    # agent = initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    #     max_iterations=5,
    #     verbose=True
    # )

    return agent


if __name__ == '__main__':
    # tools = [PythonREPLTool()]
    # example_fibonacci_tool = ToolGenerator().from_python_args(example_fabinacci_sqrt_component_args)
    module_gen = ModuleGenerator()

    tools = get_all_tools()

    agent = get_agent(tools)

    # question1 = "What is the 10th fibonacci number?"
    # question2 = "What is the 20th fibonacci number?"

    conversation = ConversationInfo(question=question1)


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
                        conversation.add_action(action)
                    # Ask user if they want to continue
                    # _continue = input("Should the agent continue (Y/n)?:\n")
                    # if _continue != "Y":
                    #     break
                else:
                    logger.info(f"output: {step['output']}")
                i += 1
                if i > 5:
                    logger.warning(f"i > 5, break")
                    break
        logger.info(f'total tokens: {cb.total_tokens / 1000}k')


    # 第一轮
    ask(question1, agent)

    logger.info("finished first round!")

    for info in conversation.show_actions():
        logger.info(info)

    # 把第一轮的代码封装成新的 Tool
    # 取出上次写的代码
    # logger.info(f"agent_actions_save: {agent_actions_save}")
    for action in conversation.get_actions():
        # Ask user if they want to continue
        logger.info(f"action: {action.tool}, log: {action.log}, value: {action.tool_input}")
        _continue = input("Would you transform the action above into a new module (Y/n)?:\n")
        if _continue != "Y":
            continue
        new_tool = module_gen.from_action(action, question1)
        if new_tool and new_tool.name not in [tool.name for tool in tools]:
            tools.append(new_tool)
    # 把新的 Tool 加入到 agent 中
    agent = initialize_agent(
        tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    # 第二轮
    ask(question2, agent)

    logger.info("finished!")
