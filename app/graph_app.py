import functools, operator, requests, os, json
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict
import gradio as gr
from dotenv import load_dotenv
# Set environment variables
load_dotenv();
# Initialize model
llm = ChatOpenAI(model="gpt-3.5-turbo")

# Define custom tools
@tool("general_facts_search", return_direct=False)
def general_facts_search(query: str) -> str:
    """Searches the internet about general information about the company"""
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=5)]
        return results if results else "No results found."

@tool("financial_data_search", return_direct=False)
def financial_data_search(url: str) -> str:
    """Searches for recent financial data about a company"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()
@tool("generate_solution", return_direct= False)
def generate_solution(general_info: str, financial_info: str, prompt:str) -> str:
    """Generates Solutions based on info about the company and its financial data"""
    prompt = f"General info: {general_info} , Financial data: {financial_info} , Question: {prompt}"

tools = [general_facts_search, financial_data_search, generate_solution]

# Helper function for creating agents
def create_agent(llm: ChatOpenAI, tools: list, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)
    return executor

# Define agent nodes
def agent_node(state, agent, name):
    result = agent.invoke(state)
    return {"messages": [HumanMessage(content=result["output"], name=name)]}

# Create Agent Supervisor
members = ["General_Facts_Agent", "Financial_Data_Agent", "Solutions_Architect"]
system_prompt = (
    "As a supervisor, your role is to oversee a dialogue between these"
    " workers: {members}. Based on the user's request,"
    " determine which worker should take the next action. Each worker is responsible for"
    " executing a specific task and reporting back their findings and progress. Once all tasks are complete,"
    " indicate with 'FINISH'."
)

options = ["FINISH"] + members
function_def = {
    "name": "route",
    "description": "Select the next role.",
    "parameters": {
        "title": "routeSchema",
        "type": "object",
        "properties": {"next": {"title": "Next", "anyOf": [{"enum": options}] }},
        "required": ["next"],
    },
}

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("system", "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}"),
]).partial(options=str(options), members=", ".join(members))

supervisor_chain = (prompt | llm.bind_functions(functions=[function_def], function_call="route") | JsonOutputFunctionsParser())

# Define the Agent State and Graph
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

general_facts_agent = create_agent(llm,tools, "You are a general facts agent, you will search general facts about the specified company. Such as the industry, what products they sell, and recent news.")
general_facts_node = functools.partial(agent_node, agent = general_facts_agent,name = "General_Facts_Agent")

financial_data_agent = create_agent(llm, tools, 
        """You are a financial data agent. You will search up financial data regarding the company
        """)
financial_data_node = functools.partial(agent_node, agent=financial_data_agent, name="Financial_Data_Agent")

solutions_architect_agent = create_agent(llm,tools, "You are the solutions architect, analyzie the general information about the company and its financial data and create a solution for the user's question")
solutions_architect_node = functools.partial(agent_node,agent = solutions_architect_agent, name = "Solutions_Architect")
workflow = StateGraph(AgentState)
workflow.add_node("General_Facts_Agent", general_facts_node)
workflow.add_node("Financial_Data_Agent", financial_data_node)
workflow.add_node("Solutions_Architect" , solutions_architect_node)
workflow.add_node("supervisor", supervisor_chain)


for member in members:
    workflow.add_edge(member, "supervisor")


conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
workflow.set_entry_point("supervisor")

graph = workflow.compile()


def run_graph(input_message):
    response = graph.invoke({
        "messages": [HumanMessage(content=input_message)]
    })
    return json.dumps(response['messages'][1].content, indent=2)

