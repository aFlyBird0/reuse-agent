import streamlit as st
import requests


def create_app(data):
    response = requests.post('http://localhost:8000/app/', json=data)
    if response.status_code != 200:
        st.error('出错了' + response.text)
        st.stop()
    st.json(response.json())  # Should print the id and access_url


def get_app(id):
    print(id)
    response = requests.get(f'http://localhost:8000/app/{id}')
    print(response)
    st.json(response.json())  # Should print the id and access_url


def delete_app(id):
    print('delete', id)
    response = requests.delete(f'http://localhost:8000/app/{id}')
    st.json(response.json())  # Should print {'status': 'success'}


def list_apps():
    response = requests.get(f'http://localhost:8000/apps/')
    return response.json()


def main():
    st.title('App Management')

    if st.button('添加app'):
        create_app({
            'name': '列表文件并创建PDF',
            'description': '列表文件并创建PDF详情',
            'dependencies': ["fpdf"],
            'code': "xxx",
            "image_name": 'docker_manager_test_fpdf_image',
            "container_name": 'docker_manager_test_fpdf_container'
        })

    apps = list_apps()
    i = 1
    for app in apps:
        col_index, col_name, col_url, col_info, col_delete = st.columns([1, 3, 3, 2, 2])
        info_container = st.empty()
        with col_index:
            st.write(i)
        with col_name:
            st.write(app['name'])
        with col_url:
            st.write(app['access_url'])
        with col_info:
            if st.button(f'查看详情'):
                with info_container:
                    get_app(app["id"])
        with col_delete:
            if st.button(f'删除'):
                delete_app(app["id"])
        i += 1


if __name__ == '__main__':
    main()

