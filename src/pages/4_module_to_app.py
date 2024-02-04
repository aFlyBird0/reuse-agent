import re

import streamlit as st

from core.module_to_app.agent import module_to_app_code
from core.streamlit_manager.app import AppData
from core.streamlit_manager.app_manager import AppManager
from streamlit_component.module import display_module
from streamlit_component.module_sidebar import (get_sidebar_selected_module,
                                                setup_module_side_bar)


def validate_docker_image_name(image_name):
    pattern = r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$"
    if re.match(pattern, image_name) and 4 <= len(image_name) <= 255:
        return True
    else:
        return False

if __name__ == '__main__':
    st.set_page_config(layout="wide")
    setup_module_side_bar()

    module = get_sidebar_selected_module()
    if module is not None:
        display_module(module)
        request = st.chat_input("transform this module to app, input your request here")
        if request:
            # todo: 把 code 什么的保存到 session state 里面
            code = module_to_app_code(module, request)
            st.session_state['module_to_app_code'] = code
    code = st.session_state.get('module_to_app_code', None)
    if code:
        st.subheader('Streamlit App Code')
        st.code(code, language='python')

        # Allow user to modify app data
        name = st.text_input('App Name', module.name, help="it should be a valid docker image name")
        if not validate_docker_image_name(name):
            st.error("invalid App Name, it should be a valid docker image name")
        description = st.text_area('Description', module.description)
        dependencies = st.text_input('Dependencies', module.dependencies)

        if st.button('Save and Start App'):
            app = AppData(
                name=name,
                description=description,
                author=module.author,
                dependencies=dependencies,
                code=code,
                image_name=module.author + "_" + name + "_image",
                container_name=module.author + "_" + name + "_container",
            )
            st.json(AppManager.create_app(app))