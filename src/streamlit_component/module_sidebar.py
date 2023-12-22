import sys
from typing import Callable, List

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

import streamlit as st
from streamlit_tags import st_tags

from core.module.module import Module
from core.module.module_store import default_module_store


class StateManager:
    _namespace = "sidebar_"  # 命名空间，防止冲突
    _data_modules_in_sidebar = _namespace + "modules_in_sidebar"
    _data_current_module_in_sidebar = _namespace + "current_module_in_sidebar"
    _data_search_module_name = _namespace + "search_module_name"  # 搜索框里的模块名
    _data_search_tags = _namespace + "search_tags"  # 搜索框里的 tag 名

    @classmethod
    def get_current_module(cls) -> Module:
        if cls._data_current_module_in_sidebar not in st.session_state:
            return None
        return st.session_state[cls._data_current_module_in_sidebar]

    @classmethod
    def set_current_module(cls, module: Module):
        st.session_state[cls._data_current_module_in_sidebar] = module

    @classmethod
    def set_modules_to_state(cls, modules: List[Module]):
        st.session_state[cls._data_modules_in_sidebar] = modules

    @classmethod
    def get_search_module(cls) -> str:
        if cls._data_search_module_name not in st.session_state:
            return ""
        return st.session_state[cls._data_search_module_name]

    @classmethod
    def set_search_module(cls, search: str):
        st.session_state[cls._data_search_module_name] = search

    @classmethod
    def get_search_tags(cls) -> List[str]:
        if cls._data_search_tags not in st.session_state:
            return []
        return st.session_state[cls._data_search_tags]

    @classmethod
    def set_search_tags(cls, tags: List[str]):
        st.session_state[cls._data_search_tags] = tags

    @classmethod
    def get_modules_from_state(cls) -> List[Module]:
        if cls._data_modules_in_sidebar not in st.session_state:
            return []
        return st.session_state[cls._data_modules_in_sidebar]


sm = StateManager()


@st.cache_data(ttl=60)
def _all_modules_from_store() -> List[Module]:
    print("Loading all modules from store")
    return default_module_store.list()


@st.cache_data(ttl=60)
def _search_modules_by_name_and_tags(search: str, tags: List[str]) -> List[Module]:
    if not search and (not tags or len(tags) == 0):
        return _all_modules_from_store()
    search = search.lower()
    modules = default_module_store.list_by_name_and_tags_and(search, tags)
    return modules


def _display_module_brief(module: Module, show_button: bool=False,
                          button_label_fmt: str="Show details for {module.name}",
                          button_callback: Callable[[Module], None]=None,
                          ):
    """
    展示模块的简要信息
    """
    with st.container():
        st.subheader(module.name)
        st.write(f"**Description:** {module.description}")
        st.write(f"**Tags:** {', '.join(module.tags)}")
        if show_button:
            button_label = button_label_fmt.format(module=module)
            if st.button(button_label):
                sm.set_current_module(module)
                if button_callback:
                    button_callback(module)

def _set_default_current_module():
    # 仅在没有当前模块时设置默认模块
    if sm.get_current_module():
        return
    modules = sm.get_modules_from_state()
    if len(modules) > 0:
        sm.set_current_module(modules[0])


def setup_module_side_bar(show_button: bool=True,
                          button_label_fmt: str="Show details for {module.name}",
                          button_callback: Callable[[Module], None]=None):
    # 获取搜索模块名、标签列表，查询模块列表
    name = sm.get_search_module()
    tags = sm.get_search_tags()
    # 保存模块列表到state中
    sm.set_modules_to_state(_search_modules_by_name_and_tags(name, tags))

    # 设置默认展示模块
    _set_default_current_module()

    # 渲染标签页
    with st.sidebar:
        search = st.sidebar.text_input(label="Module Name", placeholder="Type module name to search")
        tags = st_tags(
            label='Tags',
            text='Press enter to add more',
            value=["math"],
            suggestions=["math", "file"],
            maxtags=10,
            key='1')
        # 点击 search 按钮，开始搜索
        if st.button("Search"):
            sm.set_search_module(search)
            sm.set_search_tags(tags)
            sm.set_modules_to_state(_search_modules_by_name_and_tags(search, tags))
        # 展示搜索结果
        st.title("Module List")
        for module in sm.get_modules_from_state():
            _display_module_brief(module, show_button, button_label_fmt, button_callback)
            st.divider()

def get_sidebar_selected_module()->Module:
    return sm.get_current_module()


if __name__ == '__main__':
    setup_module_side_bar()
    print(get_sidebar_selected_module())
