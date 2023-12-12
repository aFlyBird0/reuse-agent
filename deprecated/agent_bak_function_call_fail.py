
from typing import List, Dict, Any, Optional
import json

from langchain.agents import AgentOutputParser
from langchain.chains import LLMChain
from langchain.callbacks.manager import CallbackManager
from langchain.tools.base import BaseTool
from langchain.adapters.openai import convert_message_to_dict
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers.json import parse_partial_json
from langchain.schema.messages import FunctionMessage, HumanMessage, AIMessage
from core.refactor_module.prompt import SYSTEM_PROMPT_CN_TEMPLATE, USER_PROMPT_CN_TEMPLATE
from llm.openai import OpenAIConfig
from core.action_to_module.module_store import default_module_store
from core.module.module import Module, from_python_module_store


class ExtractJsonOutputParser(AgentOutputParser):
    def parse(self, output) -> dict:
        # use re to extract json in ```json ... ```
        import re
        json_str = re.search(r"```json(.*)```", output, re.DOTALL).group(1)
        return json.loads(json_str)

class BaseAgent(LLMChain):
    total_tries: int = 1
    tools: List[BaseTool] = []
    function_schemas: List[dict] = []
    output_key: str = "messages"
    system_template: str = ""
    allow_user_confirm: bool = False
    prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(messages=["system", ""])

    @property
    def _chain_type(self):
        return "BaseAgent"

    @property
    def input_keys(self) -> List[str]:
        return ["messages"]

    # def construct_prompt(self, langchain_messages: Dict[str, Any]):
    #     prompt = ChatPromptTemplate.from_messages(messages=[
    #         ("system", self.system_template),
    #         *langchain_messages
    #     ])
    #     return prompt

    def construct_prompt(self, langchain_messages):
        prompt = ChatPromptTemplate.from_messages(messages=[
            AIMessage(content=self.system_template),
            *langchain_messages
        ])
        return prompt

    def postprocess_mesasge(self, message):
        return message

    def tool_result_to_str(self, tool_result) -> str:
        if isinstance(tool_result, dict):
            return json.dumps(tool_result, ensure_ascii=False)
        return str(tool_result)

    def run_tool(self, function_call: Dict[str, Any]):
        function_name = function_call.get("name", "")
        arguments = parse_partial_json(function_call.get("arguments", "{}"))
        tool_result = None
        for tool in self.tools:
            if tool.name == function_name:
                if self.human_confirm():
                    tool_result = tool.run(arguments)
                    tool_result = self.tool_result_to_str(tool_result)
                    tool_result = FunctionMessage(name=function_name, content=tool_result)
                break
        return tool_result

    def human_confirm(self):
        can_run_tool = True
        if self.allow_user_confirm:
            def ask_run_code_confirm():
                print("Do you want to run this code? (y/n)")
                answer = input()
                if answer == "y":
                    return True
                return False
            can_run_tool = ask_run_code_confirm()
        return can_run_tool

    def messages_hot_fix(self, langchain_messages):
        return langchain_messages

    def preprocess_inputs(self, inputs: Dict[str, Any]):
        return inputs

    def run_workflow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        inputs = self.preprocess_inputs(inputs)
        messages = inputs.pop("messages")
        # langchain_messages = convert_openai_messages(messages)
        langchain_messages = messages
        llm_with_functions = self.llm.bind(functions=self.function_schemas)
        current_try = 0
        while current_try < self.total_tries:
            prompt = self.construct_prompt(langchain_messages)
            llm_chain = (prompt | llm_with_functions | self.postprocess_mesasge)

            message = llm_chain.invoke(inputs)
            langchain_messages.append(message)
            function_call = message.additional_kwargs.get("function_call", None)
            if function_call is None:
                break

            tool_result = self.run_tool(function_call)
            if tool_result is None:
                break
            langchain_messages.append(tool_result)
            langchain_messages = self.messages_hot_fix(langchain_messages)
            current_try += 1
        openai_messages = list(map(convert_message_to_dict, langchain_messages))
        return openai_messages

    def parse_output(self, messages):
        return {"messages": messages}

    def _call(
        self,
        inputs: Dict[str, Any],
        run_manager: Optional[CallbackManager] = None,
    ) -> Dict[str, Any]:
        output = {self.output_key: None}
        try:
            messages = self.run_workflow(inputs)
            output = self.parse_output(messages)
        except Exception as e:
            raise e
        return output

def create_base_agent(llm)->BaseAgent:
    template = SYSTEM_PROMPT_CN_TEMPLATE.format(schema=json.dumps(Module.schema()["properties"], indent=2))
    function_schema = {
        "name": "refactor_module",
        "description": "a function to combine modules",
        "parameters": {
            "properties": {
                "refactor_module": Module.schema_json(indent=2),
                "type": "object",
            },
            "type": "object",
            "required": ["refactor_module"]
        }
    }
    agent = BaseAgent(
        llm=llm,
        system_template=template,
        # function_schemas=[function_schema],
        verbose=True,
    )
    return agent

def test_refactor_or_combine(module_names: List[str], request: str):
    agent = create_base_agent(OpenAIConfig.defaultLLM())

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

    output = agent(inputs)
    messages = output["messages"]
    msg = messages[-1]["content"]
    module_dict = ExtractJsonOutputParser().parse(msg)
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


