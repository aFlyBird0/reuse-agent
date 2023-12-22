from langchain.chat_models import ChatOpenAI

from config.settings import get_settings

openai_api_key = get_settings().llm.api_key
openai_api_base = get_settings().llm.api_base
default_model = get_settings().llm.default_model

class OpenAIConfig:

    openai_params = {
        "openai_api_key": openai_api_key,
        "openai_api_base": openai_api_base
    }

    @staticmethod
    def defaultLLM():
        # os.environ["OPENAI_API_KEY"] = OpenAIConfig.openai_api_key
        return ChatOpenAI(
            # model_name="gpt-3.5-turbo-1106",
            model_name=default_model,
            # model_name="gpt-3.5-turbo",
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base,
            temperature=0,
        )
    @staticmethod
    def llm_with_params(model: str, temperature: float):
        return ChatOpenAI(
            model_name=model,
            openai_api_key=openai_api_key,
            openai_api_base=openai_api_base,
            temperature=temperature,
        )