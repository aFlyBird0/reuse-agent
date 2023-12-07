# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from llm.openai import OpenAIConfig

chat = ChatOpenAI(openai_api_key=OpenAIConfig.openai_api_key, openai_api_base=OpenAIConfig.openai_api_base)

llm = OpenAI(openai_api_key=OpenAIConfig.openai_api_key, openai_api_base=OpenAIConfig.openai_api_base)

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.

def llm_model_test():
    text = "What would be a good company name for a company that makes colorful socks?"
    m = llm.invoke(text)
    print(m)

def chat_model_test():
    from langchain.schema.messages import HumanMessage, SystemMessage

    messages = [
        SystemMessage(content="You're a helpful assistant"),
        HumanMessage(content="What is the purpose of model regularization?"),
    ]

    m = chat.invoke(messages)
    print(m)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    llm_model_test()
    # chat_model_test()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
