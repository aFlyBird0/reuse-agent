# streamlit_manager.py

from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import MongoClient
import streamlit as st
import json

# MongoDB connection
uri = "mongodb+srv://aflybird0:8ORG2lDRRm36ntP7@cluster0.lh2vpp8.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["cluster0"]
collection = db["apps"]

class StreamlitApp:
    def __init__(self, name, code):
        self.name = name
        self.code = code


class StreamlitAppManager:
    @staticmethod
    def save_app_to_db(app):
        app_data = {"name": app.name, "code": app.code}
        collection.insert_one(app_data)

    @staticmethod
    def load_apps_from_db():
        apps = []
        for app_data in collection.find():
            app = StreamlitApp(name=app_data["name"], code=app_data["code"])
            apps.append(app)
        return apps


app = FastAPI()


class AppInfo(BaseModel):
    name: str
    code: str


@app.post("/create_app")
async def create_app(app_info: AppInfo):
    new_app = StreamlitApp(name=app_info.name, code=app_info.code)
    StreamlitAppManager.save_app_to_db(new_app)
    return {"message": "App created successfully"}


@app.get("/apps")
async def get_apps():
    apps = StreamlitAppManager.load_apps_from_db()
    app_names = [app.name for app in apps]
    return {"apps": app_names}


@app.get("/app/{app_name}")
async def display_app(app_name: str):
    apps = StreamlitAppManager.load_apps_from_db()
    app = next((app for app in apps if app.name == app_name), None)
    if app:
        st.title(app.name)
        exec(app.code)
    else:
        return {"message": "App not found"}