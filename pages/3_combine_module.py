import sys

from core.module.module import Module

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

from streamlit_component.combine_module import show_combined_module, combine_modules, get_modules_to_combine, \
    show_modules_to_combine, add_module_to_combine, show_modules_to_combine_names
from streamlit_component.module_sidebar import setup_module_side_bar

import streamlit as st

if __name__ == '__main__':
    st.set_page_config(layout="wide")

    button_label_fmt = "Add {module.name} to combine"
    def print_module(module: Module):
        add_module_to_combine(module=module)
    setup_module_side_bar(show_button=True, button_label_fmt=button_label_fmt, button_callback=print_module)

    # 把屏幕5等分，右边留出一份用来展示已选中的内容
    col1, col2 = st.columns([4, 1])
    with col2:
        show_modules_to_combine_names()
    with col1:
        show_modules_to_combine()
    request = st.chat_input("Combine modules above, input your request here")
    if request:
        combine_modules(get_modules_to_combine(), request)
    with col1:
        show_combined_module()