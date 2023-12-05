import os

from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI


class OpenAIConfig:
    # openai_api_key = "sk-gV4NdMWNmJ1moFG65d1f816cD3B3467a891841Ed97Cc1bA4"
    openai_api_key = "sk-B3zQDHZPzq1NKnjD7b167c86909944378fC00b4a2369B1Be"

    openai_api_base = "https://api.gptapi.cyou/v1"

    openai_params = {
        "openai_api_key": openai_api_key,
        "openai_api_base": openai_api_base
    }

    @staticmethod
    def defaultLLM():
        # os.environ["OPENAI_API_KEY"] = OpenAIConfig.openai_api_key
        return ChatOpenAI(
            model_name="gpt-3.5-turbo-1106",
            # model_name="gpt-4",
            openai_api_key=OpenAIConfig.openai_api_key,
            openai_api_base=OpenAIConfig.openai_api_base,
            temperature=0
        )