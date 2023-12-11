
from typing import List, Dict, Any, Optional

from langchain.callbacks.manager import CallbackManager
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema.messages import AIMessage


class BaseAgent(LLMChain):
    total_tries: int = 1
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

    def construct_prompt(self, langchain_messages):
        prompt = ChatPromptTemplate.from_messages(messages=[
            AIMessage(content=self.system_template),
            *langchain_messages
        ])
        return prompt

    def postprocess_mesasge(self, message):
        return message

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
        current_try = 0
        while current_try < self.total_tries:
            prompt = self.construct_prompt(messages)
            llm_chain = (prompt | self.llm | self.postprocess_mesasge)

            message = llm_chain.invoke(inputs)
            messages.append(message)
            messages = self.messages_hot_fix(messages)
            current_try += 1
        return messages

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