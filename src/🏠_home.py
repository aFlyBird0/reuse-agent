import streamlit as st


def read_md_content(filepath: str):
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
    return content

paper_md_path = "paper.md"

@st.cache_data(ttl=10)
def get_paper_md_content():
    return read_md_content(paper_md_path)

if __name__ == '__main__':
    st.header("Reuse Agent")

    st.markdown(get_paper_md_content(), unsafe_allow_html=True)