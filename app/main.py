from fastapi import *
from pydantic import BaseModel
from graph_app import run_graph 
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers = ["*"]
)

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    response: str



@app.post("/query")
def query(request: QueryRequest):
    try:
        result = run_graph(request.query)
        print("query called")
        return QueryResponse(response=result)
    except:
        print("error")
    

   
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)