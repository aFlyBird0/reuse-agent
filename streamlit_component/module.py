import random
import sys
from typing import List

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

import streamlit as st
from streamlit_tags import st_tags
from core.action_to_module.module_store import default_module_store
from core.module.module import Module, Param
from annotated_text import annotated_text

def show_annotated_params(params: List[Param], prefix: str = "**Params:** ", sep: str = " "):
    param_tuple = [(p.name, p.param_type) for p in params]
    # todo: 将 sep 间隔式插入到 param_tuple 里
    annotated_text(prefix, param_tuple)

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
    # st.markdown("Params: " + ", ".join(colors_params), unsafe_allow_html=True)
    show_annotated_params(params=module.params)

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

def show_and_save_module(module: Module):
    """
    如果模块不为空，展示模块，并提供保存按钮
    """
    if module is None:
        return
    display_module(module)
    if st.button("Save to Database"):
        with st.spinner("Saving..."):
            default_module_store.add(module)
        st.success("Saved!")


if __name__ == '__main__':
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


