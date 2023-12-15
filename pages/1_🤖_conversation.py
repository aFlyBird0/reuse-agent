import logging

import sys

from core.python_test.model import TestOutput

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

# from callbacks.callback import MyCustomSyncHandler
from core.python_test.run_test import test_exist_module
from core.react_component import get_all_tools, get_agent
from llm.openai import OpenAIConfig
from loggers.logs import setup_logger
from streamlit_component.conversation import display_conversation_info, action_to_module_confirm, \
    execute_action_to_module, show_module, display_action
from core.react_component import react_and_conversation, react_and_conversation_iter
from core.action_to_module.agent import ActionToPythonAgent
from core.action_to_module.module_gen import default_module_generator
from streamlit_component.conversation import get_state_converted_module, clear_state_converted_module, \
    get_state_action_to_module_args, clear_state_action_to_module_args

import streamlit as st
from langchain_core.agents import AgentAction
from core.action_to_module.module_store import default_module_store
from core.conversation import ConversationInfo
from core.module.module import Module

logger = setup_logger()


class StateManager:
    data_key_question: str = 'question'

    @classmethod
    def get_state_question(cls):
        if cls.data_key_question not in st.session_state:
            return None
        return st.session_state[cls.data_key_question]

    @classmethod
    def set_state_question(cls, question: str):
        st.session_state[cls.data_key_question] = question

    data_key_conversation: str = 'conversation'

    @classmethod
    def get_state_conversation(cls):
        if cls.data_key_conversation not in st.session_state:
            return None
        return st.session_state[cls.data_key_conversation]

    @classmethod
    def set_state_conversation(cls, conversation: ConversationInfo):
        st.session_state[cls.data_key_conversation] = conversation

    data_key_result = 'result'

    @classmethod
    def get_state_result(cls):
        if cls.data_key_result not in st.session_state:
            return None
        return st.session_state[cls.data_key_result]

    @classmethod
    def set_state_result(cls, result):
        st.session_state[cls.data_key_result] = result

    data_key_total_tokens = 'total_tokens'

    @classmethod
    def get_state_total_tokens(cls):
        if cls.data_key_total_tokens not in st.session_state:
            return None
        return st.session_state[cls.data_key_total_tokens]

    @classmethod
    def set_state_total_tokens(cls, total_tokens):
        st.session_state[cls.data_key_total_tokens] = total_tokens

    data_key_module_test_result = 'module'
    @classmethod
    def get_state_module_test_result(cls)->TestOutput:
        if cls.data_key_module_test_result not in st.session_state:
            return None
        return st.session_state[cls.data_key_module_test_result]

    @classmethod
    def set_state_module_test_result(cls, res: TestOutput):
        st.session_state[cls.data_key_module_test_result] = res

sm = StateManager


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


def extract_module(action: AgentAction, result: str, question: str, index: int) -> Module:
    """
    action -> module
    """
    return ActionToPythonAgent().python_args_from_action(action, question)


@st.cache_data
def test_module(_module: Module, module_name: str, module_description: str):
    """
    测试Module
    """
    with st.spinner("Testing module..."):
        test_res = test_exist_module(_module)
        sm.set_state_module_test_result(test_res)

def show_test_result(res: TestOutput):
    # 出错，跳过
    if res.success:
        st.success("Success!")
    else:
        st.warning("test failed")
    st.write('input:')
    st.json(res.input.args_input)
    st.write('expected output:')
    st.code(res.input.expected_output)
    st.write('output')
    st.code(res.stdout)
    st.write('error')
    st.code(res.stderr)

    # if res.stderr is not None:
    #     logger.error(f"test_res.stderr: {res.stderr}")
    #     st.error(f"test_res.stderr: {res.stderr}")
    #     return
    # # 无错，但输出与预期不符，询问用户
    # if res.stderr is None and not res.success:
    #     logger.warning(f"test_res.stdout: {res.stdout}, expected: {res.input.expected_output}")
    #     logger.info(f"full test_res: {res}")
    #     st.write("The output is not as expected, would you transform the action above into a new module (Y/n)?:\n")
    #     if st.button('no'):
    #         return
    #     if st.button('yes'):
    #         new_module_tool = default_module_generator.from_python_args(module)
    #         if new_module_tool and new_module_tool.name not in [tool.name for tool in tools]:
    #             logger.info(f"new_module has been added: {new_module_tool.name}")
    #             st.info(f"new_module has been added: {new_module_tool.name}")
    #             tools.append(new_module_tool)
    #             default_module_store.add(module)



def save_module_to_store():
    @st.cache_data
    def save(_module: Module, module_name: str, module_description: str):
        print(f"save module: {_module}")
        st.success(f"已保存模块{module.name}至数据库")
        default_module_store.add(module=_module)
    test_res = sm.get_state_module_test_result()
    module = get_state_converted_module()
    if test_res and module:
        if st.button(f"保存模块{module.name}至数据库"):
            save(module, module_name=module.name, module_description=module.description)

# @st.cache_data
def start_conversation(question: str):
    # 新建会话时，删除旧的重构好的模块
    if get_state_converted_module():
        clear_state_action_to_module_args()
        clear_state_converted_module()
    if sm.get_state_question() == question:
        return sm.get_state_result(), sm.get_state_question(), sm.get_state_total_tokens()
    return react_and_conversation(question, agent)

def start_conversation_iter(question: str):
    # 新建会话时，删除旧的重构好的模块
    if get_state_converted_module():
        clear_state_action_to_module_args()
        clear_state_converted_module()
    if sm.get_state_question() == question:
        return sm.get_state_result(), sm.get_state_question(), sm.get_state_total_tokens()

    return react_and_conversation_iter(question, agent)


def main():
    st.title('Reuse Agent')  # 设置页面标题

    key_start_question = 'start_question'
    key_finish_question = 'finish_question'

    # 添加一个输入框
    question = st.chat_input('请输入任务，例如：帮我计算15之后的第一个素数', key=key_start_question)

    # 是否是实时渲染
    if_render_realtime = False
    # 输入问题，点击按钮
    if (question and key_finish_question not in st.session_state):
        # 当按钮被点击时，调用 process_input 函数，并显示处理后的结果
        spinner = st.spinner('正在处理中...')
        if_render_realtime = True
        # 展示用户输入的问题
        st.subheader('Question:')
        st.write(question)

        st.subheader('Actions:')
        action_container = st.container()
        with spinner:
            # processed_result, conversation, total_tokens_k = start_conversation(question)
            i = 0
            for result in start_conversation_iter(question):
                # st.info(result)
                if len(result) == 3:  # 检查是否为最终结果
                    processed_result, conversation, total_tokens_k = result
                    # print("对话结束：", processed_result, conversation, total_tokens_k)
                else:
                    i += 1
                    action, action_result = result
                    display_action(action, action_result, i, action_container)
                    # print("动作信息：", action, action_result)
        sm.set_state_question(question)
        # st.write('结果:', processed_result)

        sm.set_state_conversation(conversation)
        sm.set_state_result(processed_result)
        sm.set_state_total_tokens(total_tokens_k)

        logger.info(f"conversation history:")
        for info in conversation.show_actions():
            logger.info(info)
        # st.session_state[key_finish_question] = True

    # 展示对话过程
    conversation = sm.get_state_conversation()
    if conversation:
        # 防止重复渲染
        if not if_render_realtime:
            processed_result = sm.get_state_result()
            total_tokens_k = sm.get_state_total_tokens()

            display_conversation_info(conversation)

        # 展示结果
        st.subheader('Result:')
        st.write(processed_result)
        st.subheader('Total Tokens:')
        st.write(f"{total_tokens_k}k")

        # 保存ConversationInfo对象到文件
        # save_conversation_info(conversation, 'example_conversation.pkl')

    # action 到 module 的转换
    kwargs = get_state_action_to_module_args()
    if kwargs:
        # 确认转换
        action_to_module_confirm(**kwargs)
        # 转换过程
        execute_action_to_module(module_generator=extract_module)
        # 展示转换结果
        show_module()
        # 测试
        module = get_state_converted_module()
        if module:
            test_module(module, module_name=module.name, module_description=module.description)
            test_res = sm.get_state_module_test_result()
            if test_res:
                st.title('Test Result')
                show_test_result(test_res)
        # 保存到数据库
        save_module_to_store()


if __name__ == '__main__':
    st.set_page_config(layout="centered")
    setup_sidebar()
    model = st.session_state.get("model_v", "gpt-3.5-turbo")
    temperature = st.session_state.get("temperature_v", 0.0)
    print(f"model: {model}, temperature: {temperature}")
    llm = OpenAIConfig.llm_with_params(model=model, temperature=temperature)

    tools = get_all_tools()

    agent = get_agent(tools)
    logging.basicConfig(level=logging.INFO)
    main()
