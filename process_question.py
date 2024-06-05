from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(temperature = 0.0)

def process_question(question):
   prompt = (
    "Classify the following question as 'General' or 'Abstract':\n\n"
    "General means the question can be answered directly by looking at the given dataset and providing a straightforward answer.\n"
    "Abstract means the question requires you to come up with a solution as if you were a business architect, needing creativity and deeper analysis.\n\n"
    "Respond with only either 'General' or 'Abstract'.\n\n"
    f"Question: {question}"
)