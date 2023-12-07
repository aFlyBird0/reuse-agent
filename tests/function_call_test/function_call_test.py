from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.callbacks import get_openai_callback
from langchain_core.prompts import ChatPromptTemplate

from llm.openai import OpenAIConfig

functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    },

    {
        "name": "product_search",
        "description": "Search for product information",
        "parameters": {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "The product to search for"
                },
            },
            "required": ["product_name"]
        }
    }
]

if __name__ == '__main__':
    llm = OpenAIConfig.defaultLLM()
    llm = llm.bind(functions=functions)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}")
        ]
    )

    runnable = prompt | llm | OpenAIFunctionsAgentOutputParser()

    with get_openai_callback() as cb:
        response = runnable.invoke({"input": "北京的天气"})
        print(response)

    print(f'total tokens: {cb.total_tokens / 1000}k')