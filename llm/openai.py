import os

from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.output_parsers import StructuredOutputParser


class OpenAIConfig:
    openai_api_key = "sk-N4Z4qZaCHoNfumWL4f13E49a4e8147Ef9dFd8fFcF9C1547e"

    openai_api_base = "https://api.gptapi.cyou/v1"

    openai_params = {
        "openai_api_key": openai_api_key,
        "openai_api_base": openai_api_base
    }

    @staticmethod
    def defaultLLM():
        # os.environ["OPENAI_API_KEY"] = OpenAIConfig.openai_api_key
        return ChatOpenAI(
            # model_name="gpt-3.5-turbo-1106",
            model_name="gpt-4",
            # model_name="gpt-3.5-turbo",
            openai_api_key=OpenAIConfig.openai_api_key,
            openai_api_base=OpenAIConfig.openai_api_base,
            temperature=0,
        )