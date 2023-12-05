from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI
from api.openai import OpenAIConfig
from callback import MyCustomSyncHandler

from langchain.callbacks import get_openai_callback

# set env SERPAPI_API_KEY=DEMO
import os
os.environ["SERPAPI_API_KEY"] = "57693466681cf12b89d0fef4fe280052ddbf45349737345d3b446fd818a49d21"

llm = OpenAIConfig.defaultLLM()

# llm = OpenAI(**OpenAIConfig.openai_params)

tools = load_tools(["serpapi", "llm-math"], llm=llm)

# question = "what is sin(3.14) + cos(1.14) + sqrt(5)"
question = "what is sin(3.14)"
# question = "Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?"

def ICEL():

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

    callbacks = [MyCustomSyncHandler()]
    with get_openai_callback() as cb:
        agent_executor.invoke(
            {
                "input": question
            },
            {
                "callbacks": callbacks
            }
        )
    print(f'total tokens: {cb.total_tokens/1000}k')

def off_the_shell():
    agent_executor = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )
    agent_executor.invoke(
        {
            "input": question
        }
    )

if __name__ == "__main__":
    ICEL()
    # off_the_shell()
