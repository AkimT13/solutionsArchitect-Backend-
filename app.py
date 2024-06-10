import functools, operator, requests, json, os
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END 
from langchain.tools import tool
from langchain_openai import ChatOpenAI
import gradio as gr
from dotenv import load_dotenv

llm = ChatOpenAI(model = 'gpt-3.5-turbo')

@tool("internet_search", return_direct=False)
def internet_search(query: str) -> str:
    """Searches the Internet using DuckDuckGo"""
    with DDGS as ddgs:
        results = [r for r in ddgs.text(query, max_results=5)]
        return results if results else "No results found"

@tool("process_content" , return_direct = False)
def process_content(url: str) -> str:
    """Processes content from the webpage"""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.get_text()
    

@tool("load_data", return_direct=False)
def load_data(path:str) -> str:
    """Loads company data"""
    with open(path, 'r') as file:
        data = json.load(path)
        data_string = json.dumps(data, indent=4)
    return data_string




tools = [internet_search, process_content, load_data]

def create_agent(llm: ChatOpenAI, tools:list, system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
         MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    agent = create_openai_tools_agent(llm, tools, prompt)
    executer = AgentExecutor(agent = agent, tools = tools)
    return executer


members = ["Web Searcher", "Solutions Maker"]





