import streamlit as st
import os
from fpdf import FPDF

# 设置页面标题
st.title('List Files and Create PDF App')

# 用户输入参数
directory = st.text_input('Enter the directory:', '.')
num_files = st.number_input('Enter the number of files to list:', min_value=1, value=5)
output_file = st.text_input('Enter the output PDF file name:', 'FileList.pdf')

# 创建按钮来触发操作
if st.button('Create PDF'):
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
        pdf.cell(200, 10, txt=file, ln=True)

        # Save the pdf with the specified name
    pdf.output(output_file)
    st.success(f'PDF "{output_file}" has been created with the list of files.')