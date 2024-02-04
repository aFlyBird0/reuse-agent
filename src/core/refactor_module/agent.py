import json
from typing import List

from langchain.agents import AgentOutputParser
from langchain.schema.messages import HumanMessage
from pydantic.json import pydantic_encoder

from callbacks.callback import MyCustomSyncHandler
from core.module.module import Module
from core.module.module_store import default_module_store
from core.refactor_module.base_agent import BaseAgent
from core.refactor_module.prompt import (SYSTEM_PROMPT_CN_TEMPLATE,
                                         USER_PROMPT_CN_TEMPLATE)
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
        msg_last = messages[-1].content
        print('msg_last', msg_last)
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

def refactor_or_combine(modules: List[Module], request: str)->Module:
    modules_str = json.dumps(modules, indent=2, ensure_ascii=False, default=pydantic_encoder)

    human_messages_module = USER_PROMPT_CN_TEMPLATE.format(modules=modules_str, additional_request=request)

    # messages = [{"role": "user", "text": human_messages_module}]
    messages = [
        HumanMessage(content=human_messages_module)
    ]

    inputs = {"messages": messages}

    agent = create_refactor_agent(OpenAIConfig.defaultLLM())
    module_dict = agent.invoke(inputs, {
        "callbacks": [MyCustomSyncHandler()]
    })[agent.output_key]
    # print("重构后的 Module dict")
    # print(module_dict)
    return Module.from_json(module_dict)