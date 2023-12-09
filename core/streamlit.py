import logging
import pickle

import streamlit as st
from langchain.agents import AgentExecutor
from langchain.callbacks import get_openai_callback

import sys

from langchain_core.agents import AgentAction
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

# from callbacks.callback import MyCustomSyncHandler
from core.action_to_module.module_gen import ModuleGenerator
from core.action_to_module.module_store import ModuleStore
from core.conversation import ConversationInfo
from core.python_test.run_test import test_exist_module
from core.react_component import get_all_tools, get_agent
from llm.openai import OpenAIConfig
from loggers.logs import setup_logger
from core.streamlit_component import display_conversation_info
from core.react_component import react_and_conversation
from core.action_to_module.agent import ActionToPythonAgent


logger = setup_logger()

def extract_module_and_test(action: AgentAction, **kwargs):
    action_res = kwargs.get('result')
    question = kwargs.get('question')
    logger.info(
        f"action: {action.tool}, log: {action.log}, tool_input: {action.tool_input}, tool_result: {action_res}")
    st.info(
        f"action: {action.tool}, log: {action.log}, tool_input: {action.tool_input}, tool_result: {action_res}")
    option = st.radio("Would you transform the action above into a new module (Y/n)?:\n", ("Y", "N"))
    if option != "Y":
        st.info("Skip")
        return
    module_args = ActionToPythonAgent().python_args_from_action(action, question)
    test_res = test_exist_module(module_args)
    # 出错，跳过
    if test_res.stderr is not None:
        logger.error(f"test_res.stderr: {test_res.stderr}")
        st.error(f"test_res.stderr: {test_res.stderr}")
        return
    # 无错，但输出与预期不符，询问用户
    if test_res.stderr is None and not test_res.success:
        logger.warning(f"test_res.stdout: {test_res.stdout}, expected: {test_res.input.expected_output}")
        logger.info(f"full test_res: {test_res}")
        option = st.radio("The output is not as expected, would you transform the action above into a new "
                          "module (Y/n)?:\n", ("Y", "N"))
        if option != "Y":
            st.info("Skip")
            return
    new_module_tool = module_gen.from_python_args(module_args)

    if new_module_tool and new_module_tool.name not in [tool.name for tool in tools]:
        logger.info(f"new_module has been added: {new_module_tool.name}")
        st.info(f"new_module has been added: {new_module_tool.name}")
        tools.append(new_module_tool)
        module_store.add(module_args)


    # Streamlit 应用程序的主要部分
def main():
    global conversation
    conversation = None
    st.title('Reuse Agent')  # 设置页面标题

    # 添加一个输入框
    question = st.text_input('请输入指令', '')

    # 添加一个按钮
    if st.button('请求'):
        # 当按钮被点击时，调用 process_input 函数，并显示处理后的结果
        processed_result, conversation, total_tokens_k = react_and_conversation(question, agent)
        st.write('结果:', processed_result)

        logger.info(f"conversation history:")
        for info in conversation.show_actions():
            logger.info(info)

        display_conversation_info(conversation, extract_module_and_test)

        # 展示结果
        st.subheader('Result:')
        st.write(processed_result)
        st.subheader('Total Tokens:')
        st.write(f"{total_tokens_k}k")

        # 保存ConversationInfo对象到文件
        # save_conversation_info(conversation, 'example_conversation.pkl')

        #
        # # 第二轮
        # ask(question2, agent)

        logger.info("finished!")

    # 运行应用程序


if __name__ == '__main__':

    llm = OpenAIConfig.defaultLLM()

    tools = get_all_tools()

    agent = get_agent(tools)
    logging.basicConfig(level=logging.INFO)
    main()