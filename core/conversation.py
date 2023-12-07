from typing import List, Dict

from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage


class ConversationInfo:
    question: str
    actions: List[AgentAction] = None
    actions_maps: Dict[str, AgentAction] = None  # nodeID->Action
    messages: List[BaseMessage]

    def __init__(self, question: str):
        self.question = question
        self.actions = []
        self.actions_maps = {}
        self.messages = []

    def add_action(self, action: AgentAction):
        self.actions.append(action)

    def show_actions(self):
        return [action.log for action in self.actions]

    def get_actions(self):
        return self.actions

    def show_messages(self):
        return [message.content for message in self.messages]
