from typing import List

import streamlit as st
from streamlit_modal import Modal
from core.streamlit_manager.app import AppData
from core.streamlit_manager.app_manager import AppManager


def create_app(app):
    response = AppManager.create_app(app)
    st.json(response)  # Should print the id and access_url


def get_app(id)->AppData:
    app = AppManager.get_app(id)
    return app
def restart_app(app: AppData):
    AppManager.restart_app(app)

def stop_app(id):
    AppManager.stop_app(id)

def delete_app(id):
    response = AppManager.delete_app(id)
    st.json(response)  # Should print {'status': 'success'}


def list_apps()->List[AppData]:
    return AppManager.list_apps()

def get_app_status(app: AppData):
    return AppManager.get_app_status(app)

def show_create_example_app():
    if st.button('添加示例app'):
        example_app = AppData(
            name='Hello World',
            description='Hello World 演示程序',
            dependencies=["fpdf"],
            code = "import streamlit as st\n\nst.title('Hello World')",
            image_name = 'docker_manager_hello_world_image',
            container_name = 'docker_manager_hello_world_container'
        )
        create_app(example_app)


def main():
    st.set_page_config(page_title='App Management', layout='wide')
    st.title('App Management')

    apps = list_apps()
    col_index, col_name, col_url, col_status, col_info, col_action = st.columns([1, 3, 3, 2, 2, 2])
    with col_index:
        st.write('序号')
    with col_name:
        st.write('名称')
    with col_url:
        st.write('地址')
    with col_status:
        st.write('状态')
    with col_info:
        st.write('详情')
    with col_action:
        st.write('操作')
    i = 1
    for app in apps:
        col_index, col_name, col_url, col_status, col_info, col_actions = st.columns([1, 3, 3, 2, 2, 2])
        info_container = st.empty()
        status = get_app_status(app)

        with col_index:
            st.write(i)
        with col_name:
            st.write(app.name)
        with col_url:
            if status == 'running':
                st.write(app.access_url)
        with col_status:
            st.write(status)
        modal = Modal('应用详情', key='应用详情'+app.id, max_width=800)
        with col_info:
            if st.button(f'查看详情', key='查看详情' + app.id):
                # app = get_app(app.id)
                # app.code = '...'
                modal.open()
        app.code = '...'
        if modal.is_open():
            with modal.container():
                st.json(app.json())
        with col_actions:
            def render_buttons(app, status):
                if status == 'stopped':
                    if st.button('重启', key='重启' + app.id):
                        with st.spinner('重启中'):
                            restart_app(app)
                        st.rerun()
                    if st.button('删除', key='删除' + app.id):
                        with st.spinner('删除中'):
                            delete_app(app.id)
                        st.rerun()
                elif status == 'running':
                    if st.button('停止', key='停止' + app.id):
                        with st.spinner('停止中'):
                            stop_app(app.id)
                        st.rerun()
            # if status == 'stopped':
            #     action = st.expander("操作", expanded=False).selectbox("action", ['...', '重启', '删除'], key="操作" + app.id)
            # else:
            #     action = st.expander("操作", expanded=False).selectbox("action", ['...', '停止', '删除'], key="操作" + app.id)
            # on_change(action)
            with st.expander("操作", expanded=False):
                render_buttons(app, status)

        i += 1

    show_create_example_app()


if __name__ == '__main__':
    main()

