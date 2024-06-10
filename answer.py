from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

def answer(state):
    question = state[0]
    data = state[1]
    prompt = ("Answer the question using the data. Treat it as if you were a business solutions architect" f"question: {state[0]} Data: {state[1]}")
    answer = ChatOpenAI.invoke(prompt)
    state[4] = answer

    
