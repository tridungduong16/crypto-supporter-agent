from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from typing import Optional
from langchain_community.tools import DuckDuckGoSearchRun
import os
from dotenv import load_dotenv

load_dotenv()

def check_weather(location: str, at_time: Optional[datetime] = None) -> str:
    return f"It's always sunny in {location}"

def multiply(a: int, b: int) -> int:
    """Multiply a and b.
    Args:
        a: first int
        b: second int
    """
    return a * b
# This will be a tool
def add(a: int, b: int) -> int:
    """Adds a and b.
    Args:
        a: first int
        b: second int
    """
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a and b.
    Args:
        a: first int
        b: second int
    """
    return a / b

search = DuckDuckGoSearchRun()

tools = [check_weather, multiply, add, divide]

openai_api_key=os.getenv("openai_api_key"),

model = ChatOpenAI(model="gpt-4o", openai_api_key=)
llm_with_tools = model.bind_tools(tools)
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage


# System message
sys_msg = SystemMessage(content="You are a helpful assistant tasked with using search and performing arithmetic on a set of inputs.")

def reasoner(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition # this is the checker for the if you got a tool back
from langgraph.prebuilt import ToolNode
from IPython.display import Image, display

# Graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("reasoner", reasoner)
builder.add_node("tools", ToolNode(tools)) # for the tools

# Add edges
builder.add_edge(START, "reasoner")
builder.add_conditional_edges(
    "reasoner",
    # If the latest message (result) from node reasoner is a tool call -> tools_condition routes to tools
    # If the latest message (result) from node reasoner is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "reasoner")
react_graph = builder.compile()

messages = [HumanMessage(content="What is 2 times Brad Pitt's age?")]
messages = react_graph.invoke({"messages": messages})
#Displaying the response
for m in messages['messages']:
    m.pretty_print()

# Display the graph
# display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))

# graph = create_react_agent(model, tools=tools)
# inputs = {"messages": [("user", "what is the weather in sf")]}
# for s in graph.stream(inputs, stream_mode="values"):
#     message = s["messages"][-1]
#     if isinstance(message, tuple):
#         print(message)
#     else:
#         message.pretty_print()