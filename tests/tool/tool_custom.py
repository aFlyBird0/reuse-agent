from langchain.callbacks import get_openai_callback
from langchain.tools import StructuredTool
from langchain.agents import AgentType, initialize_agent

from tests.agents_test import MyCustomSyncHandler
from llm.openai import OpenAIConfig

def multiplier(a: float, b: float) -> float:
    """Multiply the provided floats."""
    return a * b

def weather(city: str) -> str:
    """Get the weather in the provided city."""
    return f"The weather in {city} is sunny."

def captical_of(country: str) -> str:
    """Get the captical of the provided country."""
    return f"The captical of {country} is Beijing."

if __name__ == '__main__':
    llm = OpenAIConfig.defaultLLM()

    funcs_to_be_used = [multiplier, weather, captical_of]
    tools = [StructuredTool.from_function(f) for f in funcs_to_be_used]

    # Structured tools are compatible with the STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION agent type.
    agent_executor = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )

    with get_openai_callback() as cb:
        agent_executor.run("What is the weather of capital of China?", callbacks=[MyCustomSyncHandler()])
    print(f'total tokens: {cb.total_tokens/1000}k')