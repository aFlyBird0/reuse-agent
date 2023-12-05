from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI

llm = OpenAI(temperature=0)

tools = load_tools(["serpapi", "llm-math"], llm=llm)

from langchain import hub
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.tools.render import render_text_description

prompt = hub.pull("hwchase17/react")
prompt = prompt.partial(
    tools=render_text_description(tools),
    tool_names=", ".join([t.name for t in tools]),
)

llm_with_stop = llm.bind(stop=["\nObservation"])


agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
    }
    | prompt
    | llm_with_stop
    | ReActSingleInputOutputParser()
)

from langchain.agents import AgentExecutor

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_executor.invoke(
    {
        "input": "Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?"
    }
)

def weather():
    import requests

    url = "https://api.serpwow.com/live/search"

    params = {
        "q": "weather in new york",
        "api_key": "demo",
    }

    response = requests.get(url, params=params)
    return response.json()["answer_box"]["answer"]

def weather_of_city(city):
    import requests

    url = "https://api.serpwow.com/live/search"

    params = {
        "q": f"weather in {city}",
        "api_key": "demo",
    }

    response = requests.get(url, params=params)
    return response.json()["answer_box"]["answer"]