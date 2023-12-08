import json

from langchain.agents import AgentOutputParser
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

import core.action_to_module.example
from core.interpreter.python_tool import PythonTool
from core.python_test.model import TestParams
from core.python_test.prompt import get_tool_description, example_code, example_args_schema_dict, \
    SYSTEM_PROMPT_CN, USER_PROMPT_CN, example_tool_description, example_response_schema
from llm.openai import OpenAIConfig


class RemoveCodeBlockBorderOutputParser(AgentOutputParser):
    def parse(self, output) -> str:
        output = output.strip()
        output = output.lstrip("```json")
        output = output.rstrip("```")
        output = output.strip()
        return output


class JsonOutputParser(JSONAgentOutputParser):
    def parse(self, output) -> TestParams:
        return TestParams.parse_obj(json.loads(output))


def get_python_test_agent(llm):
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate.from_template(SYSTEM_PROMPT_CN),
            HumanMessagePromptTemplate.from_template(USER_PROMPT_CN)
        ]
    )

    prompt = prompt.partial(tool_description=example_tool_description, response_schema_example=example_response_schema)
    # prompt = prompt.format_messages(code=example_code, code_args=json.dumps(example_args_schema_dict))

    # print(prompt.format())

    llm.bind(input_keys=["code", "code_args"])

    agent = prompt | llm | RemoveCodeBlockBorderOutputParser() | JsonOutputParser()

    return agent


python_test_agent = get_python_test_agent(OpenAIConfig.defaultLLM())


def get_python_test_args(code: str, args_schema, agent=python_test_agent):
    res = agent.invoke({
        "code": code,
        "code_args": json.dumps(args_schema)
    })
    return res


if __name__ == '__main__':
    print(get_tool_description(PythonTool()))

    # res = llm.invoke(prompt)
    # print(res)

    from langchain.agents.structured_chat.output_parser import StructuredChatOutputParser

    llm = OpenAIConfig.defaultLLM()
    agent = get_python_test_agent(llm)

    res = agent.invoke({
        "code": example_code,
        "code_args": json.dumps(example_args_schema_dict)
    })

    print(res)

    # agent.invoke()
