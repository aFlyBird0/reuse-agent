# 将组件重写成Python代码的Agent

from typing import Any

from langchain.callbacks import get_openai_callback
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.agents import AgentAction, AgentFinish
from langchain_experimental.tools import PythonREPLTool

# Internal Imports
from callbacks.callback import MyCustomSyncHandler
from llm.openai import OpenAIConfig
from .example import example_cn
from loggers.logs import setup_logger
from .output_parser import ArgsAndCodeOutputParser
from .prompt import SYSTEM_PROMPT_CN_TEMPLATE, USER_PROMPT_CN_TEMPLATE
from .module_define import PythonModule


# Third-party Library Imports

# todo: 改成继承 BaseAgent
class ActionToPythonAgent():

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.logger = setup_logger()
        self.agent = self._setup_agent(OpenAIConfig.defaultLLM())

    @property
    def _chain_type(self):
        return "ActionToPythonAgent"

    def python_args_from_action(self, action: AgentAction, origin_main_task: str) -> PythonModule:
        with get_openai_callback() as cb:
            agent_finish: AgentFinish = self.agent.invoke(
                {
                    "code": action.tool_input,
                    "task_log": action.log,
                    "origin_main_task": origin_main_task,
                },
                {
                    "callbacks": [MyCustomSyncHandler()]
                }
            )

        print(f"total_tokens: {cb.total_tokens / 1000}k")

        pyREPLArgs = agent_finish.return_values["python_args"]

        pyREPLArgs.print(self.logger)

        return pyREPLArgs

    def _setup_agent(self, llm):
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_CN_TEMPLATE),
                HumanMessagePromptTemplate.from_template(USER_PROMPT_CN_TEMPLATE)
            ]
        )
        prompt = prompt.partial(
            **example_cn,
        )

        agent = prompt | llm | ArgsAndCodeOutputParser()

        return agent


action_to_python_agent = ActionToPythonAgent()

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
    args = action_to_python_agent.python_args_from_action(action, origin_main_task=origin_main_task)

    print(f"name: {args.name}")
    print(f"description: {args.description}")
    print(f"args: {args.args}")
    print(f"code: {args.code}")
