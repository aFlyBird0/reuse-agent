import sys
from typing import Callable

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

import pickle
import re
import streamlit as st
from langchain_core.agents import AgentAction
from core.conversation import ConversationInfo
from core.module.module import Module, Param
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

key_confirm_action_to_module = "key_confirm_action_to_module"

def get_state_confirm_action_to_module()->bool:
    return st.session_state.get(key_confirm_action_to_module, False)

def set_state_confirm_action_to_module(confirm: bool):
    st.session_state[key_confirm_action_to_module] = confirm

key_finish_action_to_module = "finish_action_to_module"
def get_state_finish_action_to_module()->bool:
    return st.session_state.get(key_finish_action_to_module, False)

def set_state_finish_action_to_module(finish: bool):
    st.session_state[key_finish_action_to_module] = finish

key_action_to_module_args = "key_action_to_module_args"
def get_state_action_to_module_args()->dict:
    return st.session_state.get(key_action_to_module_args, {})
def set_state_action_to_module_args(args: dict):
    st.session_state[key_action_to_module_args] = args
def clear_state_action_to_module_args():
    del st.session_state[key_action_to_module_args]

key_converted_module = "converted_module"
def set_state_converted_module(module: Module):
    st.session_state[key_converted_module] = module
def get_state_converted_module()->Module:
    return st.session_state.get(key_converted_module, None)
def clear_state_converted_module():
    del st.session_state[key_converted_module]

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
                            def on_click_save_args():
                                set_state_action_to_module_args(kwargs)

                            button_key = f"extract_to_component_{index}_{action.tool}"
                            col1.button(button_label, key=button_key, on_click=on_click_save_args)
    else:
        st.write("No actions found.")

def display_action(action: AgentAction, result:str, index: int, container: st.container):
    with container:
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
                    kwargs = {"action": action, "result": result}

                    def on_click_save_args():
                        set_state_action_to_module_args(kwargs)

                    button_key = f"extract_to_component_{index}_{action.tool}"
                    col1.button(button_label, key=button_key, on_click=on_click_save_args)

def action_to_module_confirm(action: AgentAction, result: str, question: str, index: int):
    # 这里是执行动作的函数钩子
    st.divider()
    st.title("Action to Module")
    st.write(f"即将当前Action转化为新的组件，请确认")
    action_res = result
    st.info(f"action_tool: {action.tool}")
    st.info(f"action_tool_input: ")
    st.json(action.tool_input)

    # st.code(action.tool_input)
    st.info(f"action_tool_result: {action_res}")

    st.button("我要转换", key="button_confirm_action_to_component", on_click=set_state_confirm_action_to_module, args=[True])


def execute_action_to_module(module_generator: Callable[[AgentAction, str, str, int], Module]):
    if get_state_confirm_action_to_module():
        action = get_state_action_to_module_args()["action"]
        result = get_state_action_to_module_args()["result"]
        question = get_state_action_to_module_args()["question"]
        index = get_state_action_to_module_args()["index"]
        @st.cache_data
        def module_generator_cached(_action, result, question, index, action_log)->Module:
            """
            action前加_是因为action不能被hash，所以不能作为cache的key
            所以使用一个action_log作为cache的key
            """
            return module_generator(_action, result, question, index)

        module = module_generator_cached(action, result, question, index, action.log)
        set_state_converted_module(module)

def show_module():
    module = get_state_converted_module()
    if module:
        st.title("New Module")
        display_module(module)


if __name__ == '__main__':
    def test_display_conversation():
        # 从文件加载ConversationInfo对象
        loaded_conversation = load_conversation_info('example_conversation.pkl')
        display_conversation_info(loaded_conversation)


    def test_fake_module_generator(action: AgentAction, result: str, question: str, index: int) -> Module:
        st.title("Fake Module Generator")
        st.subheader("Original Action")
        st.write(action)
        st.subheader("Original Result")
        st.write(result)
        st.subheader("Original Question")
        st.write(question)

        st.title("Generated Module")
        params = [
            Param(name="param1", description="param1_description", default_value="param1_default_value", param_type="int"),
            Param(name="param2", description="param2_description", default_value="param2_default_value", param_type="float"),
            Param(name="param3", description="param3_description", default_value="param3_default_value", param_type="str"),
        ]
        module = Module(
            name="fake_module",
            description="fake_module_description",
            params=params,
            code="print('hello world')",
        )
        return module

    test_display_conversation()
    kwargs = get_state_action_to_module_args()
    if kwargs:
        action_to_module_confirm(**kwargs)
        execute_action_to_module(module_generator=test_fake_module_generator)
        show_module()
