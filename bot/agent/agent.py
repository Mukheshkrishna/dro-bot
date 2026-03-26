from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI

from bot.agent.tools import rag_tool

# LLM setup
llm = ChatOpenAI(temperature=0)

# Define tools
tools = [
    Tool(
        name="RAG_Search",
        func=rag_tool,
        description="Use this to answer questions from internal documents"
    )
]

# Create agent
agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

def run_agent(query: str):
    return agent.run(query)
