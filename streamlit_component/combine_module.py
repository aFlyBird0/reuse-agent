from typing import List

import streamlit as st

from core.action_to_module.module_store import default_module_store
from core.module.module import Module
from core.refactor_module.agent import refactor_or_combine
from streamlit_component.module import display_module, show_and_save_module

key_data_combined_module = "combined_module"

def get_combined_module() -> Module:
    if key_data_combined_module not in st.session_state:
        return None
    return st.session_state[key_data_combined_module]


def set_combined_module(module: Module):
    st.session_state[key_data_combined_module] = module

def combine_modules(modules: List[Module], request: str):
    with st.spinner("Combining..."):
        module = refactor_or_combine(modules, request)
        set_combined_module(module)

def show_combined_module():
    module = get_combined_module()
    if not module:
        return
    st.header("Combined Module")
    show_and_save_module(module)

# key_data_combine_module_enable = "combine_module_enable"
#
# def set_data_combine_module_enable(status: bool):
#     st.session_state[key_data_combine_module_enable] = status
# def get_data_combine_module_enable():
#     return st.session_state.get(key_data_combine_module_enable, False)

key_data_modules_to_combine = "modules_to_combine"


def add_module_to_combine(module: Module):
    modules = st.session_state.get(key_data_modules_to_combine, [])

    # 检查是否已存在相同作者和名称的模块
    exists = any(m.author == module.author and m.name == module.name for m in modules)

    if not exists:
        modules.append(module)
        st.session_state[key_data_modules_to_combine] = modules

def get_modules_to_combine():
    return st.session_state.get(key_data_modules_to_combine, [])


def remove_module(module: Module):
    modules = st.session_state.get(key_data_modules_to_combine, [])

    # 保留那些作者和名称匹配的模块
    filtered_modules = [m for m in modules if not (m.author == module.author and m.name == module.name)]

    st.session_state[key_data_modules_to_combine] = filtered_modules


def clear_modules_to_combine():
    st.session_state[key_data_modules_to_combine] = []

# def show_combine_modules_toggle():
#     enable = st.toggle("Combine Modules", value=get_data_combine_module_enable())
#     set_data_combine_module_enable(enable)

def show_modules_to_combine():
    modules = get_modules_to_combine()
    if len(modules) == 0:
        return
    for module in modules:
        display_module(module)
        st.divider()

def show_modules_to_combine_names():
    modules = get_modules_to_combine()
    if len(modules) == 0:
        return
    st.subheader("Modules to Combine")
    for module in modules:
        col_button, col_name = st.columns([1, 5])
        with col_button:
            button_help = "Remove this module from the list"
            button_key = f"remove_module_{module.author}_{module.name}"
            if st.button("X", type="secondary", help=button_help, use_container_width=True, key=button_key):
                remove_module(module)
        with col_name:
            st.write(module.name)
        # st.divider()
    if st.button("Clear All"):
        clear_modules_to_combine()

if __name__ == '__main__':
    pass

