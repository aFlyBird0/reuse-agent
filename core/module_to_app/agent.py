from core.module.module_store import default_module_store
from core.module.module import Module
from core.refactor_module.base_agent import BaseAgent
from langchain.agents import AgentOutputParser
from core.module_to_app.prompt import SYSTEM_PROMPT_CN_TEMPLATE, USER_PROMPT_CN_TEMPLATE
from langchain.schema.messages import HumanMessage

from llm.openai import OpenAIConfig


class PythonCodeOutputParser(AgentOutputParser):
    def parse(self, output) -> str:
        # use re to extract json in ```python ... ```
        import re
        python_code = re.search(r"```python(.*)```", output, re.DOTALL).group(1)
        return python_code

class ModuleToAppAgent(BaseAgent):
    output_key: str = "app_code"
    @property
    def _chain_type(self):
        return "ModuleToAppAgent"

    def parse_output(self, messages):
        msg_last = messages[-1].content
        app_code = PythonCodeOutputParser().parse(msg_last)
        return {"messages": messages, "app_code": app_code}


def create_module_to_app_agent(llm) -> ModuleToAppAgent:
    template = SYSTEM_PROMPT_CN_TEMPLATE

    agent = ModuleToAppAgent(
        llm=llm,
        system_template=template,
        verbose=True,
    )
    return agent

def module_to_app(module: Module, additional_request: str="")->str:
    module_str = module.to_dict()

    if additional_request:
        additional_request = f"用户额外要求：{additional_request}"

    human_messages_module = USER_PROMPT_CN_TEMPLATE.format(module=module_str, additional_request=additional_request)

    messages = [
        HumanMessage(content=human_messages_module)
    ]

    inputs = {"messages": messages}

    agent = create_module_to_app_agent(OpenAIConfig.defaultLLM())
    app_code = agent(inputs)["app_code"]
    return app_code

if __name__ == "__main__":
    module = default_module_store.list_by_name("list_files_and_create_pdf")[0]
    app_code = module_to_app(module=module, additional_request="提供一个按钮，点击后可以下载生成的pdf文件。")

    # app_code = module_to_app(module=module, additional_request="限制输入的范围，最小为1，最大为100。并且界面应该是中文的。")

    print(app_code)