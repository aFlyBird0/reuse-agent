from langchain.agents import Tool
from langchain.chains import LLMMathChain
from langchain.utilities import SerpAPIWrapper, SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

from llm.openai import OpenAIConfig

if __name__ == '__main__':
    llm = OpenAIConfig.defaultLLM()
    search = SerpAPIWrapper()
    llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
    db = SQLDatabase.from_uri("sqlite:///../../../../../notebooks/Chinook.db")
    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events. You should ask targeted questions",
        ),
        Tool(
            name="Calculator",
            func=llm_math_chain.run,
            description="useful for when you need to answer questions about math",
        ),
        Tool(
            name="FooBar-DB",
            func=db_chain.run,
            description="useful for when you need to answer questions about FooBar. Input should be in the form of a question containing full context",
        ),
    ]

    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful assistant"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    from langchain.tools.render import format_tool_to_openai_function

    llm_with_tools = llm.bind(functions=[format_tool_to_openai_function(t) for t in tools])

    from langchain.agents.format_scratchpad import format_to_openai_function_messages
    from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser

    agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | llm_with_tools
            | OpenAIFunctionsAgentOutputParser()
    )

    from langchain.agents import AgentExecutor

    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    agent_executor.invoke(
        {
            "input": "Who is Leo DiCaprio's girlfriend? What is her current age raised to the 0.43 power?"
        }
    )