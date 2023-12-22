import uuid

import bson
from bson import ObjectId
from pydantic import BaseModel, Field


class AppData(BaseModel):
    name: str = Field(description='应用名称')
    description: str = Field(description='应用描述')
    # icon: str = Field(description='应用图标', default='📊')
    code: str
    dependencies: list = None
    id: str = Field(default_factory=lambda: str(ObjectId()), description='应用ID')
    image_name: str = id
    container_name: str = id
    container_id: str = None
    access_url: str = None