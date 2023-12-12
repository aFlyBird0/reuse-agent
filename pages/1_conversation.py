import logging
import os

import streamlit as st

import sys

from langchain_core.agents import AgentAction
sys.path.append('.')
sys.path.append('..')
# from callbacks.callback import MyCustomSyncHandler
from core.python_test.run_test import test_exist_module
from core.react_component import get_all_tools, get_agent
from llm.openai import OpenAIConfig
from loggers.logs import setup_logger
from streamlit_component.conversation import display_conversation_info, action_to_module_confirm, \
    execute_action_to_module, show_module
from core.react_component import react_and_conversation
from core.action_to_module.agent import ActionToPythonAgent
from core.action_to_module.module_store import default_module_store
from core.action_to_module.module_gen import default_module_generator
from core.module.module import from_python_module_store

logger = setup_logger()

def setup_sidebar():
    with st.sidebar:
        # openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        # "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
        # "[View the source code](https://github.com/timedomain-tech/open-creator/tree/main/creator/app/streamlit_app.py)"
        # os.environ["OPENAI_API_KEY"] = openai_api_key
        model_list = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]
        model = st.selectbox("Model", model_list, key="model")
        temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.05, key="temperature")
        st.session_state["model_v"] = model
        st.session_state["temperature_v"] = temperature


def extract_module_and_test(action: AgentAction, result: str, question: str, index: int):
    old_module_args = ActionToPythonAgent().python_args_from_action(action, question)
    module = from_python_module_store(old_module_args)
    return module


    # test_res = test_exist_module(module_args)

    # 出错，跳过
    # if test_res.stderr is not None:
    #     logger.error(f"test_res.stderr: {test_res.stderr}")
    #     st.error(f"test_res.stderr: {test_res.stderr}")
    #     return
    # # 无错，但输出与预期不符，询问用户
    # if test_res.stderr is None and not test_res.success:
    #     logger.warning(f"test_res.stdout: {test_res.stdout}, expected: {test_res.input.expected_output}")
    #     logger.info(f"full test_res: {test_res}")
    #     st.write("The output is not as expected, would you transform the action above into a new module (Y/n)?:\n")
    #     if st.button('no'):
    #         return
    #     if st.button('yes'):
    #         new_module_tool = default_module_generator.from_python_args(module_args)
    #         if new_module_tool and new_module_tool.name not in [tool.name for tool in tools]:
    #             logger.info(f"new_module has been added: {new_module_tool.name}")
    #             st.info(f"new_module has been added: {new_module_tool.name}")
    #             tools.append(new_module_tool)
    #             default_module_store.add(module_args)

data_key_question = 'question'
data_key_conversation = 'conversation'
data_key_result = 'result'
data_key_total_tokens = 'total_tokens'

# @st.cache_data
def start_conversation(question: str):
    # 新建会话时，删除旧的重构好的模块
    if "module" in st.session_state:
        del st.session_state['module']
    if data_key_question in st.session_state and st.session_state[data_key_question] == question:
        return st.session_state[data_key_result], st.session_state[data_key_conversation], st.session_state[data_key_total_tokens]
    return react_and_conversation(question, agent)

def main():
    st.title('Reuse Agent')  # 设置页面标题

    key_start_question = 'start_question'
    key_finish_question = 'finish_question'

    # 添加一个输入框
    question = st.chat_input('请输入任务，例如：帮我计算15之后的第一个素数', key=key_start_question)

    if (question and key_finish_question not in st.session_state):
        # 当按钮被点击时，调用 process_input 函数，并显示处理后的结果
        processed_result, conversation, total_tokens_k = start_conversation(question)
        st.session_state[data_key_question] = question
        st.write('结果:', processed_result)
        print("conversation!!!!!!!!!!!!!!!!!!:")
        print(conversation.question)
        print(conversation.actions)
        print(total_tokens_k)

        st.session_state[data_key_conversation] = conversation
        st.session_state[data_key_result] = processed_result
        st.session_state[data_key_total_tokens] = total_tokens_k

        logger.info(f"conversation history:")
        for info in conversation.show_actions():
            logger.info(info)
        # st.session_state[key_finish_question] = True

    if data_key_conversation in st.session_state:
        print(f"来自st.session_state[data_key_conversation]: {st.session_state[data_key_conversation]}")
        conversation = st.session_state[data_key_conversation]
        print(f"question: {conversation.question}")
        print(f"actions: {conversation.actions}")
        processed_result = st.session_state[data_key_result]
        total_tokens_k = st.session_state[data_key_total_tokens]

        display_conversation_info(conversation)

        # 展示结果
        st.subheader('Result:')
        st.write(processed_result)
        st.subheader('Total Tokens:')
        st.write(f"{total_tokens_k}k")

        # 保存ConversationInfo对象到文件
        # save_conversation_info(conversation, 'example_conversation.pkl')

        logger.info("finished!")
    if "action_to_component" in st.session_state:
        kwargs = st.session_state["action_to_component"]
        action_to_module_confirm(**kwargs)
        execute_action_to_module(module_generator=extract_module_and_test)
        st.divider()
        show_module()

if __name__ == '__main__':
    setup_sidebar()
    model = st.session_state.get("model_v", "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature_v", 0.0)
    print(f"model: {model}, temperature: {temperature}")
    llm = OpenAIConfig.llm_with_params(model=model, temperature=temperature)

    tools = get_all_tools()

    agent = get_agent(tools)
    logging.basicConfig(level=logging.INFO)
    main()