#!/usr/bin/env python
from action_to_module.agent import ActionToPythonAgent
from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langserve import add_routes
from react_component import get_all_tools, get_runnable
from test_module.agent import python_test_agent

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
agent = get_runnable(tools)
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

agent_python_test = python_test_agent
add_routes(
    app,
    agent_python_test,
    path="/agent_python_test",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)