import sys

from core.refactor_module.agent import refactor_or_combine
from streamlit_component.module import display_module, show_and_save_module
from streamlit_component.module_sidebar import get_sidebar_selected_module, setup_module_side_bar

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

import streamlit as st
from core.module.module import Module

key_data_refactored_module = "refactored_module"


def get_refactored_module() -> Module:
    if key_data_refactored_module not in st.session_state:
        return None
    return st.session_state[key_data_refactored_module]


def set_refactored_module(module: Module):
    st.session_state[key_data_refactored_module] = module


def refactor_one_module(module: Module, request: str):
    # 保存一下当前是在重构哪个模块
    set_which_module_to_refactor(module.name)
    with st.spinner("Refactoring..."):
        module = refactor_or_combine([module], request)
        set_refactored_module(module)


# 记录当前是重构了哪个模块
key_data_which_module_to_refactor = "which_module_to_refactor"


def get_which_module_to_refactor() -> str:
    return st.session_state.get(key_data_which_module_to_refactor, None)


def set_which_module_to_refactor(module_name: str):
    st.session_state[key_data_which_module_to_refactor] = module_name


def show_refactored_module():
    module = get_refactored_module()
    # 重构了的module不为空，且重构的module是当前选择的module
    if module is None or get_sidebar_selected_module().name != get_which_module_to_refactor():
        return
    st.header("Refactored Module")
    show_and_save_module(module)


if __name__ == '__main__':
    setup_module_side_bar()
    module = get_sidebar_selected_module()
    if module  is not None:
        display_module(module)
        request = st.chat_input("Refactor or Combine modules, input your request here")
        if request:
            st.subheader("Request")
            st.write(request)
            refactor_one_module(module, request)
    show_refactored_module()