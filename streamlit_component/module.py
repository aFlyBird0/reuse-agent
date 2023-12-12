# 将ConversationInfo对象保存到文件
import random
import sys
from typing import List

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

import json
import pickle
import re
import streamlit as st
from streamlit_tags import st_tags
from langchain_core.agents import AgentAction
from core.action_to_module.module_store import default_module_store
from core.conversation import ConversationInfo
from core.module.module import Module, Param

key_data_modules = "key_data_modules"
key_data_current_module = "key_data_current_module"
key_data_search_module = "key_data_search_module"
key_data_search_tags = "key_data_search_tags"


def display_module(module: Module):
    def colored_strings(strings: List[str]) -> List[str]:
        colors_all = ['red', 'blue', 'green', 'purple', 'orange']
        return [f'<font color="{random.choice(colors_all)}">{string}</font>' for string in strings]

    st.subheader(module.name)
    st.markdown(" **Description:** " + module.description, unsafe_allow_html=True)
    st.markdown(" **Tags:** " + ", ".join(colored_strings(module.tags)), unsafe_allow_html=True)
    st.write("Author:", module.author)
    st.write("Dependencies:", ", ".join(module.dependencies))

    param_names = [param.name for param in module.params]
    colors_params = colored_strings(param_names)
    # st.markdown(", ".join(colors_params), unsafe_allow_html=True)
    st.markdown("Params: " + ", ".join(colors_params), unsafe_allow_html=True)

    # if st.checkbox("Show Params"):
    for param, color in zip(module.params, colors_params):
        expander = st.expander(param.name)
        with expander:
            st.write(f"Type: {param.param_type}")
            st.write(f"Description: {param.description}")
            st.write(f"Required: {param.required}")
            if param.default:
                st.write(f"Default: {param.default}")
    st.write("Code:")
    st.code(module.code)


def display_module_info(module):
    st.write(f"### {module.name}")
    st.write(f"**Description:** {module.description}")
    st.write(f"**Tags:** {', '.join(module.tags)}")
    st.write(f"**Author:** {module.author}")


def show_module_details(module):
    st.write(f"### {module.name} Details")
    st.write(f"**Description:** {module.description}")
    st.write(f"**Tags:** {', '.join(module.tags)}")
    st.write(f"**Author:** {module.author}")

    st.write("**Params:**")
    for param in module.params:
        st.write(f"- {param.name}: {param.description}")
    st.write("**Dependencies:**")
    for dependency in module.dependencies:
        st.write(f"- {dependency}")
    st.write("**Code:**")
    st.code(module.code)

def test_display_module():
    # store = default_module_store
    # module_fibonacci = store.list_by_name('fibonacci')[0]
    # display_module(from_python_module_store(module_fibonacci))

    module = Module(
        name="Test Module",
        description="This is a test module",
        tags=["test", "example"],
        code="print('Hello, World!')",
        params=[
            Param(name="param1", param_type="str", description="The first parameter"),
            Param(name="param2", param_type="int", description="The second parameter", default=42)
        ],
        author="Test Author",
        dependencies=["numpy", "pandas"]
    )
    display_module(module)

def display_module_brief(module: Module):
    with st.container():
        st.subheader(module.name)
        st.write(f"**Description:** {module.description}")
        st.write(f"**Tags:** {', '.join(module.tags)}")
        if st.button(f"Show details for {module.name}"):
            set_current_module(module)


@st.cache_data(ttl=60)
def all_modules_from_store() -> List[Module]:
    print("Loading all modules from store")
    return default_module_store.list()


@st.cache_data(ttl=60)
def search_modules_by_name_and_tags(search: str, tags: List[str]) -> List[Module]:
    if not search and (not tags or len(tags) == 0):
        return all_modules_from_store()
    search = search.lower()
    modules = default_module_store.list_by_name_and_tags_and(search, tags)
    return modules


def get_modules_from_state() -> List[Module]:
    if key_data_modules not in st.session_state:
        return []
    return st.session_state[key_data_modules]


def get_current_module() -> Module:
    if key_data_current_module not in st.session_state:
        return None
    return st.session_state[key_data_current_module]


def set_current_module(module: Module):
    st.session_state[key_data_current_module] = module


def set_modules_to_state(modules: List[Module]):
    st.session_state[key_data_modules] = modules


def get_search_module() -> str:
    if key_data_search_module not in st.session_state:
        return ""
    return st.session_state[key_data_search_module]


def set_search_module(search: str):
    st.session_state[key_data_search_module] = search


def get_search_tags() -> List[str]:
    if key_data_search_tags not in st.session_state:
        return []
    return st.session_state[key_data_search_tags]


def set_search_tags(tags: List[str]):
    st.session_state[key_data_search_tags] = tags


def module_side_bar():
    with st.sidebar:
        search = st.sidebar.text_input(label="Module Name", placeholder="Type module name to search")
        # tags = st.sidebar.multiselect("Tags", ["math", "file"])
        tags = st_tags(
            label='Tags',
            text='Press enter to add more',
            value=["math"],
            suggestions=["math", "file"],
            maxtags=10,
            key='1')
        if st.button("Search"):
            set_search_module(search)
            set_search_tags(tags)
            set_modules_to_state(search_modules_by_name_and_tags(search, tags))
        st.title("Module List")
        for module in get_modules_from_state():
            display_module_brief(module)
            st.divider()


if __name__ == '__main__':
    # set_modules_to_state(all_modules_from_store())
    name = get_search_module()
    tags = get_search_tags()
    set_modules_to_state(search_modules_by_name_and_tags(name, tags))
    module_side_bar()
    # test_display_module()
    # test_side_bar()
    # test_show_modules()
    if get_current_module() is not None:
        display_module(get_current_module())
