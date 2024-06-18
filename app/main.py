from fastapi import *
from pydantic import BaseModel
from graph_app import run_graph 
app = FastAPI()

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    response: str



@app.post("/query")
def query(request: QueryRequest):
    try:
        result = run_graph(request.query)
        return QueryResponse(response=result)
    except:
        print("error")
    

   
