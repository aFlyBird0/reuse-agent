import random
import sys
import time
from typing import Callable

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

import json
import pickle
import re
import streamlit as st
import streamlit_tags as st_tags
from langchain_core.agents import AgentAction
from core.action_to_module.module_store import default_module_store
from core.conversation import ConversationInfo
from core.module.module import Module, from_python_module_store, Param
from streamlit_component.module import display_module


def save_conversation_info(conversation, filename):
    with open(filename, 'wb') as file:
        pickle.dump(conversation, file)


# 从文件加载ConversationInfo对象
def load_conversation_info(filename):
    with open(filename, 'rb') as file:
        conversation = pickle.load(file)
    return conversation


def extract_content_before_first_action(text):
    pattern = r'(?s)(.*?)\nAction:'
    match = re.search(pattern, text)
    if match:
        content = match.group(1).strip()
        return content

key_confirm_action_to_component = "key_confirm_action_to_component"


def action_to_module_confirm(action: AgentAction, result: str, question: str, index: int):
    # 这里是执行动作的函数钩子
    st.divider()
    st.title("Action to Module")
    st.write(f"正在将当前Action转化为新的组件")
    action_res = result
    st.info(f"action_tool: {action.tool}")
    st.info(f"action_tool_input: ")
    st.json(action.tool_input)

    # st.code(action.tool_input)
    st.info(f"action_tool_result: {action_res}")

    def confirm_action_to_component(confirm: bool):
        st.session_state[key_confirm_action_to_component] = confirm

    with st.container():
        # col1, col2 = st.columns(2)
        # col1.button("Confirm", key="button_confirm_action_to_component", on_click=confirm_action_to_component, args=[True])
        st.button("我要转换", key="button_confirm_action_to_component", on_click=confirm_action_to_component, args=[True])
        # col2.button("Cancel", key="button_cancel_action_to_component", on_click=confirm_action_to_component, args=[False])


def execute_action_to_module(module_generator: Callable[[AgentAction, str, str, int], Module]):
    key_finish_action_to_component = "finish_action_to_component"
    if st.session_state.get(key_confirm_action_to_component, False):
        if not st.session_state.get(key_finish_action_to_component, False):
            action = st.session_state["action_to_component"]["action"]
            result = st.session_state["action_to_component"]["result"]
            question = st.session_state["action_to_component"]["question"]
            index = st.session_state["action_to_component"]["index"]
            module = module_generator(action, result, question, index)
            st.session_state["module"] = module
            st.session_state[key_finish_action_to_component] = True


def show_module():
    if "module" in st.session_state:
        st.title("New Module")
        module = st.session_state["module"]
        display_module(module)


def display_conversation_info(conversation: ConversationInfo):
    st.title('Conversation Information')

    # 展示用户输入的问题
    st.subheader('Question:')
    st.write(conversation.question)

    st.subheader('Actions:')
    # 展示中间的 Action
    if conversation.actions:
        index = 0
        for action, result in conversation.actions:
            index += 1
            with st.container():
                with st.expander("Action " + str(index)):
                    col1, col2 = st.columns(2)
                    col1.write("Action Tool")
                    col1.write("Tool Input")
                    col1.write("Tool Result")
                    col1.write("Log")
                    col2.write(action.tool)
                    col2.write(action.tool_input)
                    col2.write(result)
                    col2.write(extract_content_before_first_action(action.log))
                    with st.container():
                        if action.tool == "python":
                            button_label = f"把当前Action转化为新的组件"
                            kwargs = {"action": action, "result": result, "question": conversation.question,
                                      "index": index}

                            def set_action_to_component():
                                st.session_state[f"action_to_component"] = kwargs

                            button_key = f"extract_to_component_{index}_{action.tool}"
                            col1.button(button_label, key=button_key, on_click=set_action_to_component)
    else:
        st.write("No actions found.")


def test_display_conversation():
    # 从文件加载ConversationInfo对象
    loaded_conversation = load_conversation_info('example_conversation.pkl')
    display_conversation_info(loaded_conversation)
    print(st.session_state)


if __name__ == '__main__':
    # test_display_conversation()
    # if "action_to_component" in st.session_state:
    #     kwargs = st.session_state["action_to_component"]
    #     action_to_module_confirm(**kwargs)
    #     execute_action_to_module(module_generator=from_python_module_store)
    #     show_module()

    print('重新加载')

    if st.button("test"):
        st.write("test")
        if st.button("test3"):
            st.write("test3")

    st.divider()
