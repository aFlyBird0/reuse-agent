# 将ConversationInfo对象保存到文件
import json
import pickle
import re

import streamlit as st

import sys

from langchain_core.agents import AgentAction

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

from core.conversation import ConversationInfo


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

def execute_action(action: AgentAction, result: str):
    # 这里是执行动作的函数钩子
    st.write(f"正在将当前Action转化为新的组件")
    st.write(f"Action Input")
    st.markdown(f"```json\n{json.dumps(action.tool_input, indent=4)}\n```")
    st.write(f"Action Result")
    st.write(result)

def display_conversation_info(conversation: ConversationInfo, module_generator):
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
                    if action.tool == "python":
                        button_label = f"把当前Action转化为新的组件"
                        if col1.button(button_label, key=f"extract_to_component_{index}"):
                            print("用户点击了按钮，开始执行将当前Action转化为新的组件的操作")
                            new_component_container = st.empty()
                            # 在容器中渲染新组件
                            with new_component_container:
                                module_generator(action, result=result, question=conversation.question)
                            # st.markdown("---")
    else:
        st.write("No actions found.")



if __name__ == '__main__':
    # 从文件加载ConversationInfo对象
    loaded_conversation = load_conversation_info('example_conversation.pkl')
    display_conversation_info(loaded_conversation, module_generator=execute_action)