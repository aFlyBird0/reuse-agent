import time

import requests

if __name__ == '__main__':
    # Replace with your actual python code and dependencies
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
st.title('List Files and Create PDF')

# Input fields
directory = st.text_input('Directory from which to list files', '.')
num_files = st.number_input('Number of files to list', 5)
output_file = st.text_input('Name of the output PDF file', 'FileList.pdf')

# Button to execute function
if st.button('Create PDF'):
    list_files_and_create_pdf(directory, num_files, output_file)
    st.success('PDF created successfully!')

# Button to download PDF
if st.button('Download PDF'):
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
        'dependencies': dependencies,
        'code': python_code,
        'code_id': 'docker_manager_test_fpdf'
    }
    response = requests.post('http://localhost:8000/app/', json=data)
    print(response)
    print(response.json())  # Should print the code_id and access_url

    time.sleep(60) # 等待60秒，自动删除

    # Delete app
    code_id = response.json()['code_id']
    response = requests.delete(f'http://localhost:8000/app/{code_id}')
    print(response.json())  # Should print {'status': 'success'}
