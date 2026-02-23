import os
import re
import json
from groq import Groq
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from src.rag.vector_store import SchemaVectorStorage

load_dotenv()

client = Groq(api_key=os.getenv("API_KEY"))
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

class NL2SQL_Agent:
    def __init__(self,max_retries:int = 3):
        self.max_retries = max_retries
    
    def guardRails(self,sql_query:str) -> bool:
        upper_query = sql_query.upper()
        restricted_words = [
            r"\bDROP\b", r"\bDELETE\b", r"\bUPDATE\b", 
            r"\bINSERT\b", r"\bALTER\b", r"\bTRUNCATE\b", r"\bGRANT\b"
        ]
        #Check the query for the restricted words
        for word in restricted_words:
            if re.search(word,upper_query):
                return False
        return True

    #Execute the SQL query 
    def execute_sql(self,sql_query:str):
        with engine.connect() as connection: # with is used to close any connection that is opened
            result = connection.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()
            return [dict(zip(columns,rows)) for row in rows]

    def run(self, user_question:str, schema_context:str):
        system_prompt = f"""
        You are an expert PostgreSQL developer. 
        Your job is to translate user questions into valid SQL queries.
        
        Here is the schema for the relevant tables:
        {schema_context}
        
        INSTRUCTIONS:
        1. "thought_process": Explain exactly how you will join tables and filter data.
        2. "sql_query": Provide ONLY the raw PostgreSQL query. No markdown formatting.
        
        OUTPUT FORMAT (Strict JSON):
        {{
            "thought_process": "your step-by-step reasoning",
            "sql_query": "SELECT ..."
        }}
        """

        messages = [
            {"role": "system", "content" : system_prompt},
            {"role": "user", "content" : user_question}
        ]

        #Self correction
        for attempt in range(self.max_retries):
            print(f"\n Attempt {attempt + 1} of {self.max_retries}...")

            try:
                response = client.chat.completions.create(
                    model = "openai/gpt-oss-120b",
                    response_format={"type":"json_object"},
                    messages= messages,
                    temperature=0.0
                )
                
                result_json = json.loads(response.choices[0].message.content)
                planner_thought = result_json.get("thought_process", "")
                sql_query = result_json.get("sql_query", "")

                if not self.guardRails(sql_query=sql_query):
                    raise ValueError(f"Security alert: Generated SQL query contains restricted words")
                
                print(f"AI Plan: {planner_thought}")
                print(f"Generated SQL: {sql_query}")

                
                print("Executing Query against postgresql")
                data = self.execute_sql(sql_query)

                print("Success! Query executed successfully")
                return {"status":"success","response":data,"Query":sql_query}
            
            except Exception as e:
                error_msg = str(e)

                print(f"Execution failed: {error_msg}")

                messages.append({
                    "role":"agent","content":response.choices[0].message.content
                })

                messages.append({
                    "role":"user","content":f"The query failed with error: {e}"
                })

        return {"status":"Failed","error":"Max Retries reached. Could not generate valid SQL Query"}

#Test
if __name__ == "__main__":
    agent = NL2SQL_Agent()
    vector_store = SchemaVectorStorage()
    
    question = input("Enter your question to get the result from the Database\n")

    print(f"Retrieving the Schema from the DB for: {question}")
    relevant_tables = vector_store.get_relevant_tables(query = question, number_of_results=2)
    
    schema_context = ""
    for table in relevant_tables:
        schema_context += f"{table['schema_text']}\n\n"

    result = agent.run(question,schema_context)
    
    if result["status"] == "success":
        print("\nFinal Data Retrieved:")
        for row in result["response"]:
            print(row)