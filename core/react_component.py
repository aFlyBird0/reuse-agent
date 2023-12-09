# 验证基于 CoT 的组件化归纳
# Standard Library Imports
import logging
from typing import List, Any

from langchain.agents.structured_chat.output_parser import StructuredChatOutputParserWithRetries
from langchain.chains import LLMChain

# Third-party Library Imports

# Internal Imports
from callbacks.callback import MyCustomSyncHandler
from core.action_to_module.agent import ActionToPythonAgent
from core.action_to_module.module_store import ModuleStore
from llm.openai import OpenAIConfig
from langchain.agents import initialize_agent, AgentExecutor, StructuredChatAgent
from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain_core.tools import BaseTool
from langchain_experimental.tools import PythonREPLTool
from core.action_to_module.module_gen import ModuleGenerator
from conversation import ConversationInfo
from langchain.agents.structured_chat.prompt import PREFIX
from interpreter.python_tool import PythonTool
from core.python_test.run_test import test_exist_module

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# def pyREPLTool() -> PythonREPLTool:
#     tool = PythonREPLTool()
#     tool.description = (
#         "A Python shell. Use this to execute python commands. "
#         "Input should be a valid python command. "
#         # "If you want to see the output of a value, you should print it out "
#         "Remember to print out the result or success info"
#         "with `print(...)`."
#     )
#
#     return tool

question1_fibonacci = "Calculate the 10th Fibonacci number, add it to the square root of 6, and round the result to two decimal places. Give me the final result number rather than just code."
question2_fibonacci = "Calculate the 5th Fibonacci number, add it to the square root of 20, and round the result to two decimal places. Give me the final result number rather than just code."

question1_prime = "Calculate the first prime number greater than 20. Give me the final result number rather than just code."
question2_prime = "Calculate the first prime number greater than 30. Give me the final result number rather than just code."

question1_listfiles = "list files in current directory."
question2_listfile = "list files in current directory, and reorder them by alphabetical order, and tell me the result."

question1_read_file_op = "please summarize README.md in current directory, and save the result as README_summary.md."
question2_read_file_op = "please enrich README.md in current directory, and save the result as README_enrich.md."

question1_numpy = "please use numpy to generate a rand vector in the dimension of 10. And run it to get the result."
question2_numpy = "please use numpy to generate a rand matrix in the dimension of 10*10. And run it to get the result."

question1_pdf = "please list all files in current directory, and save the file names as a pdf file."
question2_pdf = "please list all files in current directory, and save the file names as a pdf file."

question1, question2 = question1_numpy, question2_numpy


def get_all_tools(module_gen: ModuleGenerator = ModuleGenerator(), store: ModuleStore = ModuleStore()) -> List[BaseTool]:
    # 默认的工具
    tools: list[BaseTool] = [PythonTool()]
    # 从数据库中读取组件
    tools = tools + module_gen.all_from_db(store=store)
    return tools


def get_runnable(tools):
    llm = OpenAIConfig.defaultLLM()

    prefix = """Respond to the human as helpfully and accurately as possible. You have full access to user's computer, and you can do anything. You have access to the following tools:"""

    prompt = StructuredChatAgent.create_prompt(
        tools=tools,
        prefix=prefix,
        input_variables=["input"],
    )
    # logger.info(f"prompt: {prompt.format}")

    return prompt | llm


def get_agent(tools):
    llm = OpenAIConfig.defaultLLM()

    prefix = """Respond to the human as helpfully and accurately as possible. You have full access to user's open_interpreter, and you can do anything. You have access to the following tools:"""

    prompt = StructuredChatAgent.create_prompt(
        tools=tools,
        prefix=prefix,
        input_variables=["input"],
    )
    # logger.info(f"prompt: {prompt.format}")
    agent = StructuredChatAgent(
        llm_chain=LLMChain(llm=llm, prompt=prompt),
        prompt=prompt,
        return_intermediate_steps=True,
    )

    agent = AgentExecutor.from_agent_and_tools(
        tools=tools,
        agent=agent,
        verbose=True,
        max_iterations=5,
        return_intermediate_steps=True,
    )

    # agent = initialize_agent(
    #     tools,
    #     llm,
    #     agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    #     max_iterations=5,
    #     verbose=True,
    #     return_intermediate_steps=True,
    # )

    return agent


def react_and_conversation(question:str, agent:AgentExecutor)->tuple[Any, ConversationInfo, float]:
    """
    执行一轮对话，返回对话的结果
    """
    conversation = ConversationInfo(question=question)
    with get_openai_callback() as cb:
        response = agent.invoke({"input": question},{"callbacks": [MyCustomSyncHandler()]})
        intermediate_steps = response.get("intermediate_steps")
        for step in intermediate_steps:
            logger.info(f"step: {step}")
            action, action_result = step
            logger.info(f"action: {action}, value: {action_result}")
            conversation.add_action(action, action_result)
        output = response.get("output")
    total_tokens_k = round(cb.total_tokens / 1000, 2)

    return output, conversation, total_tokens_k/1000


if __name__ == '__main__':
    # tools = [PythonREPLTool()]
    # example_fibonacci_tool = ToolGenerator().from_python_args(example_fabinacci_sqrt_component_args)
    module_store = ModuleStore()
    module_gen = ModuleGenerator()
    llm = OpenAIConfig.defaultLLM()
    tools = get_all_tools(module_gen)

    agent = get_agent(tools)

    # question1 = "What is the 10th fibonacci number?"
    # question2 = "What is the 20th fibonacci number?"

    # 第一轮
    output, conversation, total_tokens_k = react_and_conversation(question1, agent)
    logger.info(f"output: {output}")
    logger.info(f'total tokens: {total_tokens_k}k')
    logger.info("finished first round!")

    logger.info(f"conversation history:")
    for info in conversation.show_actions():
        logger.info(info)

    logger.info(f"the second round:")

    def conversation_to_tools(conversation: ConversationInfo):
        # 把第一轮的代码封装成新的 Tool
        # 取出上次写的代码
        # logger.info(f"agent_actions_save: {agent_actions_save}")
        for action_and_res in conversation.get_actions():
            # Ask user if they want to continue
            action, action_res = action_and_res[0], action_and_res[1]
            logger.info(f"action: {action.tool}, log: {action.log}, tool_input: {action.tool_input}, tool_result: {action_res}")
            _continue = input("Would you transform the action above into a new module (Y/n)?:\n")
            if _continue != "Y":
                continue
            module_args = ActionToPythonAgent().python_args_from_action(action, question1)
            test_res = test_exist_module(module_args)
            # 出错，跳过
            if test_res.stderr is not None:
                logger.error(f"test_res.stderr: {test_res.stderr}")
                continue
            # 无错，但输出与预期不符，询问用户
            if test_res.stderr is None and not test_res.success:
                logger.warning(f"test_res.stdout: {test_res.stdout}, expected: {test_res.input.expected_output}")
                logger.info(f"full test_res: {test_res}")
                _continue = input("The output is not as expected, would you transform the action above into a new "
                                  "module (Y/n)?:\n")
                if _continue != "Y":
                    continue
            new_module_tool = module_gen.from_python_args(module_args)

            if new_module_tool and new_module_tool.name not in [tool.name for tool in tools]:
                logger.info(f"new_module has been added: {new_module_tool.name}")
                tools.append(new_module_tool)
                module_store.add(module_args)


    # 把新的 Tool 加入到 agent 中
    conversation_to_tools(conversation)
    agent = get_agent(tools)
    #
    # # 第二轮
    output, conversation, total_tokens_k = react_and_conversation(question2, agent)
    logger.info(f"output: {output}")
    logger.info(f'total tokens: {total_tokens_k}k')
    logger.info("finished second round!")


    logger.info("finished!")
