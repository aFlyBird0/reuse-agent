import streamlit as st

from streamlit_component.module import display_module
from streamlit_component.module_sidebar import (get_sidebar_selected_module,
                                                setup_module_side_bar)
from streamlit_component.refactor_module import (refactor_one_module,
                                                 show_refactored_module)

if __name__ == '__main__':
    st.set_page_config(layout="centered")
    setup_module_side_bar()
    module = get_sidebar_selected_module()
    if module is not None:
        display_module(module)
        request = st.chat_input("Refactor this module, input your request here")
        if request:
            refactor_one_module(module, request)
    show_refactored_module()