from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.agents.sql_agent import NL2SQL_Agent
from src.rag.vector_store import SchemaVectorStorage

app = FastAPI(title="NL2SQL")
agent = NL2SQL_Agent()
vector_store = SchemaVectorStorage()

class QueryRequest(BaseModel):
    question:str

@app.post('/ask')
async def askDatabase(request: QueryRequest):
    try:
        relevent_table = vector_store.get_relevant_tables(request.question,number_of_results=3)
        
        schema_context = ""
        for table in relevent_table:
            schema_context += f"{table['schema_text']}\n\n"

        result = agent.run(request.question,schema_context=schema_context)

        if result['status'] == 'failed':
            raise HTTPException(status_code=400 , detail=result['error'])
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

