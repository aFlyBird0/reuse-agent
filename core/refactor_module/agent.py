import json
from typing import List

from langchain.agents import AgentOutputParser
from langchain.schema.messages import HumanMessage

from core.action_to_module.module_store import default_module_store
from core.refactor_module.base_agent import BaseAgent
from core.refactor_module.module import Module, from_python_module_store
from core.refactor_module.prompt import SYSTEM_PROMPT_CN_TEMPLATE, USER_PROMPT_CN_TEMPLATE
from llm.openai import OpenAIConfig


class ExtractJsonOutputParser(AgentOutputParser):
    def parse(self, output) -> dict:
        # use re to extract json in ```json ... ```
        import re
        json_str = re.search(r"```json(.*)```", output, re.DOTALL).group(1)
        return json.loads(json_str)


class RefactorAgent(BaseAgent):
    output_key: str = "module"
    @property
    def _chain_type(self):
        return "RefactorAgent"

    def parse_output(self, messages):
        msg_last = messages[-1]["content"]
        module_dict = ExtractJsonOutputParser().parse(msg_last)
        return {"messages": messages, "module": module_dict}


def create_refactor_agent(llm) -> RefactorAgent:
    pydentic_schema = Module.schema()["properties"]
    template = SYSTEM_PROMPT_CN_TEMPLATE.format(schema=json.dumps(pydentic_schema, indent=2))
    agent = RefactorAgent(
        llm=llm,
        system_template=template,
        # function_schemas=[function_schema],
        verbose=True,
    )
    return agent


def test_refactor_or_combine(module_names: List[str], request: str):
    agent = create_refactor_agent(OpenAIConfig.defaultLLM())

    store = default_module_store

    modules_in_store = [store.list_by_name(name)[0] for name in module_names]

    for m in modules_in_store:
        print(f"模块名:{m.name}, 描述：{m.description}, 参数：{m.args}")
        print(f"代码：{m.code}")
        print("--------------------------------")

    modules = [from_python_module_store(m).to_json() for m in modules_in_store]

    modules_str = json.dumps(modules, indent=2, ensure_ascii=False)

    human_messages_module = USER_PROMPT_CN_TEMPLATE.format(modules=modules_str, additional_request=request)

    # messages = [{"role": "user", "text": human_messages_module}]
    messages = [
        HumanMessage(content=human_messages_module)
    ]

    inputs = {"messages": messages}

    module_dict = agent(inputs)["module"]
    msg = json.dumps(module_dict, indent=2)
    print(msg)
    print(module_dict["code"])


def test_combine():
    modules = ["list_files", "read_file_content"]
    request = "我希望先列出文件列表，然后读取前n个文件的内容"
    test_refactor_or_combine(module_names=modules, request=request)


def test_refactor():
    modules = ["list_files"]
    request = "我希望能指定，只列出前n个文件"
    test_refactor_or_combine(module_names=modules, request=request)


if __name__ == '__main__':
    # test_refactor()
    test_combine()
