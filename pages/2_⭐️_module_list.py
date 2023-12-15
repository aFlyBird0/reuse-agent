from streamlit_component.module import display_module
from streamlit_component.refactor_module import refactor_one_module, show_refactored_module
from streamlit_component.module_sidebar import setup_module_side_bar, get_sidebar_selected_module
import streamlit as st

if __name__ == '__main__':
    setup_module_side_bar()
    module = get_sidebar_selected_module()
    if module is not None:
        display_module(module)
        request = st.chat_input("Refactor this module, input your request here")
        if request:
            refactor_one_module(module, request)
    show_refactored_module()