from langchain.agents import AgentType, initialize_agent
from langchain.agents.tools import Tool
from langchain.chains import LLMMathChain
from pydantic.v1 import BaseModel, Field
from llm.openai import OpenAIConfig
from callbacks.callback import MyCustomSyncHandler

# Uncomment if you have a .env in root of repo contains OPENAI_API_KEY
# dotenv.load_dotenv("../../../../../.env")

# need to use GPT-4 here as GPT-3.5 does not understand, however hard you insist, that
# it should use the calculator to perform the final calculation
llm = OpenAIConfig.defaultLLM()
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)

primes = {998: 7901, 999: 7907, 1000: 7919}


class CalculatorInput(BaseModel):
    question: str = Field()


class PrimeInput(BaseModel):
    n: int = Field()


def is_prime(n: int) -> bool:
    if n <= 1 or (n % 2 == 0 and n > 2):
        return False
    for i in range(3, int(n**0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def get_prime(n: int, primes: dict = primes) -> str:
    return str(primes.get(int(n)))


async def aget_prime(n: int, primes: dict = primes) -> str:
    return str(primes.get(int(n)))


tools = [
    Tool(
        name="GetPrime",
        func=get_prime,
        description="A tool that returns the `n`th prime number",
        args_schema=PrimeInput,
        coroutine=aget_prime,
    ),
    Tool.from_function(
        func=llm_math_chain.run,
        name="Calculator",
        description="Useful for when you need to compute mathematical expressions",
        args_schema=CalculatorInput,
        coroutine=llm_math_chain.arun,
    ),
]

if __name__ == "__main__":
    agent = initialize_agent(
        tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )

    question = "What is the product of the 998th, 999th and 1000th prime numbers?"

    for step in agent.iter(question, callbacks=[MyCustomSyncHandler()]):
        if output := step.get("intermediate_step"):
            action, value = output[0]
            if action.tool == "GetPrime":
                print(f"Checking whether {value} is prime...")
                assert is_prime(int(value))
            # Ask user if they want to continue
            _continue = input("Should the agent continue (Y/n)?:\n")
            if _continue != "Y":
                break
        else:
            print(step["output"])