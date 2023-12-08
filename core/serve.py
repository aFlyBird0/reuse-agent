#!/usr/bin/env python
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langserve import add_routes
from react_component import get_all_tools, get_agent
from action_to_tool_agent.agent import ActionToPythonAgent

import llm.openai

app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple api server using Langchain's Runnable interfaces",
)

add_routes(
    app,
    llm.openai.OpenAIConfig.defaultLLM(),
    path="/openai",
)

# add_routes(
#     app,
#     ChatAnthropic(),
#     path="/anthropic",
# )

model = llm.openai.OpenAIConfig.defaultLLM()
prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")
add_routes(
    app,
    prompt | model,
    path="/joke",
)

tools = get_all_tools()
agent = get_agent(tools)
add_routes(
    app,
    agent,
    path="/agent",
)

agent_refactor = ActionToPythonAgent().setup_agent(model)
add_routes(
    app,
    agent_refactor,
    path="/agent_refactor",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)