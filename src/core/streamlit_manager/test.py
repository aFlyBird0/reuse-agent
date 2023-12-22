import json
import time

import requests

python_code = """
import os
import streamlit as st
from fpdf import FPDF
from pathlib import Path

def list_files_and_create_pdf(directory, num_files, output_file):
    # List files
    files = os.listdir(directory)[:num_files]

    # Create instance of FPDF class
    pdf = FPDF()

    # Add a page
    pdf.add_page()

    # Set font
    pdf.set_font('Arial', 'B', 16)

    # Add a cell for each file in the list
    for file in files:
        pdf.cell(200, 10, txt = file, ln = True)

    # Save the pdf with name .pdf
    pdf.output(output_file)

# Streamlit app
st.title('List Files and Create PDF 2')

# Input fields
directory = st.text_input('Directory from which to list files', '.')
num_files = st.number_input('Number of files to list', 5)
output_file = st.text_input('Name of the output PDF file', 'FileList.pdf')

# Button to execute function
if st.button('Create PDF'):
    list_files_and_create_pdf(directory, num_files, output_file)
    st.success('PDF created successfully!')
    st.session_state['pdf_created'] = True

# Button to download PDF
if st.session_state.get('pdf_created', False):
    with open(output_file, 'rb') as file:
        btn = st.download_button(
            label="Download PDF",
            data=file,
            file_name=output_file,
            mime='application/pdf'
        )

"""
dependencies = ["fpdf"]
# Create app
data = {
    'name': '列表文件并创建PDF',
    'description': '列表文件并创建PDF详情',
    'dependencies': dependencies,
    'code': python_code,
    # 'id': 'docker_manager_test_fpdf',
    "image_name": 'docker_manager_test_fpdf_image',
    "container_name": 'docker_manager_test_fpdf_container',
}

def create_app(data=data)->str:

    response = requests.post('http://localhost:8000/app/', json=data)
    print(response)
    if response.status_code != 200:
        print('出错了', response.text)
        exit(0)
    print(response.json())  # Should print the id and access_url

    if response.json().get('status', '') == 'error':
        print(response.json()['message'])
        exit(0)


    id = response.json()['id']
    return id

def get_app():
    # Get app
    id = 'docker_manager_test_fpdf'
    response = requests.get(f'http://localhost:8000/app/{id}')
    print(response.json())  # Should print the id and access_url


def delete_app(id):
    # Delete app
    response = requests.delete(f'http://localhost:8000/app/{id}')
    print(response.json())  # Should print {'status': 'success'}

def list_apps():
    response = requests.get(f'http://localhost:8000/apps/')
    return response.json()

if __name__ == '__main__':
    create_app()
    apps = list_apps()
    for app in apps:
        print(app)
