import sys

from core.module.module import Module
from core.module_to_app.agent import module_to_app_code
from core.streamlit_manager.app import AppData
from core.streamlit_manager.app_manager import AppManager
from streamlit_component.module import display_module

sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')

from streamlit_component.module_sidebar import setup_module_side_bar, get_sidebar_selected_module

import streamlit as st

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    setup_module_side_bar()

    module = get_sidebar_selected_module()
    if module is not None:
        display_module(module)
        request = st.chat_input("transform this module to app, input your request here")
        if request:
            code = module_to_app_code(module, request)
            st.subheader('Streamlit App Code')
            st.code(code, language='python')
            st.button('save and start app')
            app = AppData(
                name=module.name,
                description=module.description,
                dependencies=module.dependencies,
                code = code,
                image_name = module.name + "_image",
                container_name = module.name + "_container",
            )
            st.json(AppManager.create_app(app))