# main.py

from fastapi import FastAPI
from streamlit_manager import app as streamlit_manager_app

if __name__ == "__main__":

    app = FastAPI()

    # Mount the streamlit_manager app
    app.mount("/streamlit", streamlit_manager_app)